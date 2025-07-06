#!/usr/bin/env python3

##
# 2023
# Fabrice Issac
##
import re
import sys
import os
import argparse
import json
import random
import shutil

# parcourir l'index avec un automate à pile
# ATTENTION on maximise ! donc on ne repère pas les empans internes
# les requêtes sont de la forme (p. ex.):
#	[f~"\Rac"/s="D"][f="{",f="}"][f="{",f="}"][f="{",f="}"/s="F"]
#	[f~"\Rac"] est un requête sur un token "classique" type CQPL
#	[f="{",f="}"] on cherche un empan qui commence par '{' et termine par '}' en tenant compte du fait
#		qu'il peut y avoir "à l'interieur" des '{'. Dans ce cas on compte les '{' (+1) et les '}' (-1)
# Pas de modification sur l'interieur des empans, uniquement sur sur la fin de l'empan

# path to library
#base = "/home/fabrice/Developpe/corpindex-dev"
#sys.path.append(base+"/Corpindex")

from .Cquery import Cquery
from .Token import Token

class Hquery(object):
	
	def __init__(self,index,query,verb=False,bugv=False,unverify=False,out="",remplace=False,maximum=100,minimum=1,noshow=False,efface=False,concat=False,traits="",separateur=""):
		self.ar = []
		self.index = index
		self.verb = verb
		self.out = out
		self.remplace = remplace
		self.bugv = bugv
		self.noshow = noshow
		self.query = query
		self.maximum = maximum
		self.minimum = minimum
		self.unverify = unverify
		self.bug = False
		self.efface = efface
		self.concat = concat
		self.traits = {x.split(":")[0]:x.split(":")[1] for x in traits.split("_")}
		self.separateur = separateur 


	# analyse de la "requête" le résultat est de la forme d'un tableau
	# 0 -> cqpl égal
	# 1 -> cqpl tilde
	# 2 -> empan
	# le résultat est donc de la forme
	# 	
	# parcours arbre 
	def parcours(self,arbre,valeur):
		resultat = []
		def _parcours(a,val):
			if len(a)>0:
				if a[0] == val:
					resultat.append(a)
				else:
					for elt in a[1:]:
						_parcours(elt,val)
		_parcours(arbre,valeur)
		return resultat
		
	# analyse
	# ne gère pas l'optionnalité "?" -> A Faire
	def anaReq(self,req,cq):
		res = []
		if cq.testCqpl(req,False):
			for elt in self.parcours(cq.getCqpl(req),21): # on regarde tous les éléments
				modif = self.parcours(elt,48)
				empan = self.parcours(elt,37)
				egal = self.parcours(elt,42)
				tilde = self.parcours(elt,45)
				if len(modif)>0:
					egal.pop()
					modif = modif[0][1][1:] # le [1:] permet d'éliminer le code CQPL généré par l'analyseur
				if len(empan)>0:
					egal = egal[:-2]
					empan = empan[0]
				if len(egal)>0:
					egal = egal[0]
				if len(tilde)>0:
					tilde = tilde[0]
				if len(egal)>0:
					res.append([0]+[egal[1:]]+[modif])
				elif len(tilde)>0:
					res.append([1]+[tilde[1:]]+[modif])
				elif len(empan)>0:
					res.append([2]+[x[1:] for x in self.parcours(empan,42)]+[modif])
				else:
					print("erreur req",elt)
		return res

	# vérification égalité du token
	# retourne True|False si match ou pas
	def checkTokenCqplEgal(self,tok):
		res= False
		q =self.ar[self.setat][1]
		if q[1] == tok.getFeat(q[0]):
			res = True
		return res

	# vérification égalité du token
	# retourne True|False si match ou pas
	def checkTokenCqplTilde(self,tok):
		res= False
		q = self.ar[self.setat][1]
		if re.search(q[1],tok.getFeat(q[0])):
			res = True
		return res

	# recherche empan
	# retourne None|offset du premier match
	def checkTokenEmpan(self,tok,cq):	
		res = None
		etat = 0
		nb = 0
		m = 0
		if self.ar[self.setat][0] == 2: # type Empan
			qo = self.ar[self.setat][1]
			qf = self.ar[self.setat][2]
			if qo[1] == tok.getFeat(qo[0]):
				res = cq.getCurrentOffset()
				nb += 1
				while nb>0:
					tok = cq.getNextToken()
					m += 1
					if m > self.maximum:
						self.bug = True
						break
					if qo[1] == tok.getFeat(qo[0]) and not self.unverify: # de nouveau
						nb += 1
					elif qf[1] == tok.getFeat(qf[0]): # fermeture
						nb -= 1
		return res


	# iteration sur l'index et modification au besoin du premier et dernier token (à faire suppression de tout ou partie)
	def iteraDoc(self,ind,dico):
		off = 0
		conc = ""
		for tok in ind.getIndexTokens():
			if not tok.isDiv():
				off += 1
				if off in dico:
					if dico[off][0] == "conc":
						conc += tok.getForme()+self.separateur
					elif dico[off][0] == "concf":
						conc += tok.getForme()
						tok = Token([conc,[self.traits]])
						conc = ""
						yield tok
					elif dico[off][0] != "supp":
						tok.setAttValAllFeat(dico[off][0],dico[off][1])
						yield tok
				else:
					yield tok
			else:
				yield tok

	# création d'un nouvel index
	def createNewIndex(self):
		rep = ""
		if self.out != "":
			out = self.out
		else:
			out = os.path.dirname(self.index)+"/"+str(random.random())+".txt"
			bn = os.path.dirname(self.index)
			name = os.path.basename(self.index)
			rep = bn+"/"+str(random.random())
			#rep = "Out"
			os.mkdir(rep)
			out = rep+"/"+name
		cqn = Cquery()
		cqn.featureList = self.cq.featureList+['s','d','r','m','fm','o']
		nidx = cqn.createNewIndex(out)
		cptMot = nidx.indexation(self.iteraDoc(self.cq.defaultIdx,self.dicoModif),0)
		nidx.maxMot = cptMot
		cqn.saveNewIndex(nidx)
		if rep != "":
			shutil.rmtree(self.index+"_idx")
			shutil.move(out+"_idx",bn)
			shutil.rmtree(rep)
		
	# affichage résultat
	def affiche(self):
		for elt in self.output:
			print(elt)
			
	# récupère le résultat
	def getRes(self):
		return self.output
		
	# ferme
	def close(self):
		self.cq.close()

	def main(self):
		output = []
		if self.verb:
			sys.stderr.write(self.index+'\n')
		self.cq = Cquery()
		self.cq.open(self.index)
		self.ar = self.anaReq(self.query,self.cq)
		self.setat = 0
		etat = 0
		res = []
		self.bug = False
		tok = self.cq.getNextToken()
		dicoModif = {}
		while tok != None:
			r0 = False
			r1 = False
			r2 = False
			if self.ar[self.setat][0] == 0:
				r0 = self.checkTokenCqplEgal(tok)
			elif self.ar[self.setat][0] == 1:
				r1 = self.checkTokenCqplTilde(tok)
			else:
				r2 = self.checkTokenEmpan(tok,self.cq)
			if r0 or r1:
				res.append((self.cq.getCurrentOffset(),self.ar[self.setat][2]))
				self.setat += 1
			elif r2:
				res.append((r2,self.ar[self.setat][3]))	
				res.append((self.cq.getCurrentOffset(),self.ar[self.setat][3]))	
				self.setat += 1
			else:
				self.setat = 0
				res = []
			if self.setat == len(self.ar):
				self.setat = 0
				debut = res[0][0]
				fin = res[-1][0]
				if (fin-debut) > self.minimum:
					modd = res[0][1]
					modf = res[-1][1]
					if not self.noshow and not self.bug:
						output.append(str(debut)+":"+str(fin)+"\t"+self.cq.getAllDivFromOffset(debut)[-1][0]+"\t"+" ".join(self.cq.getText((debut,fin))))
					if self.bug and self.bugv:
						output.append(str(debut)+":"+str(fin)+"\t"+"BUG")
					if self.remplace:
						if self.efface:
							for i in range(debut,fin+1):
								dicoModif[i] = ["supp",""]
						elif self.concat:
							for i in range(debut,fin+1):
								dicoModif[i] = ["conc",modd]
							dicoModif[fin] = ["concf",modd]				
						else:
							if len(modd)>0:
								dicoModif[debut] = modd
							if len(modf)>0:
								dicoModif[fin] = modf
				res = []
				self.bug = False
			tok = self.cq.getNextToken()
		self.dicoModif = dicoModif
		self.output = output
 

def main():
	# parameters
	parser = argparse.ArgumentParser(description="interrogation d'un index")
	parser.add_argument('-i', "--index", type=str, nargs='+',help='fichiers index')
	parser.add_argument('-q', "--query", type=str, help='requête (non CQPL)')
	parser.add_argument("-v", "--verbose", help="active affichage informations",action="store_true",default=False)
	parser.add_argument("-b", "--bug", help="active affichage bugs",action="store_true",default=False)
	parser.add_argument("-u", "--unverify", help="active recherche sans empilement de début d'empan (genre *? de regexp)",action="store_true",default=False)
	parser.add_argument('-o', "--output", type=str, help='nom du fichier index transformé',default="")
	parser.add_argument('-M', "--max", type=int, help="taille max de l'empan",default=100)
	parser.add_argument('-m', "--min", type=int, help="taille min de l'empan",default=1)
	parser.add_argument('-r', "--remplace",action="store_true", help="remplace l'index (si -o avec nouveau nom sinon le même)",default=False)
	parser.add_argument('-n', "--noshow",action="store_true", help="pas d'affichage du résultat à l'écran",default=False)
	parser.add_argument('-e', "--efface",action="store_true", help="efface l'empan",default=False)
	parser.add_argument('-c', "--concat",action="store_true", help="concaténation de l'empan",default=False)
	parser.add_argument('-t', "--traits",type=str, help="traits à ajouter (si 'concat') de la forma t1:v1_t2:v2",default="l:X_c:Z")
	parser.add_argument('-s', "--separateur",type=str, help="separateur si concaténation",default="")

	args = parser.parse_args()
	args = vars(args)

	indexes = args['index']
	verb = args["verbose"]
	out = args["output"]
	bugv = args["bug"]
	remplace = args["remplace"]
	noshow = args["noshow"]
	query = args["query"]
	maximum = args["max"]
	minimum = args["min"]
	unverify = args["unverify"]
	efface = args["efface"]
	concat = args["concat"]
	trait = args["traits"]
	separateur = args["separateur"]

	if indexes:
		for index in indexes:
			hq = Hquery(index,query,verb,bugv,unverify,out,remplace,maximum,minimum,noshow,efface,concat,trait,separateur)
			hq.main()
			if remplace:
				hq.createNewIndex()
			else:
				hq.affiche()


