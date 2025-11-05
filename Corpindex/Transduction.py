#!/usr/bin/env python3

# ne marche pas bien avec les divisions 
# si une règle est "à cheval" alors ça coince... 
# à vérifier : suppression du dernier token...

import sys

import os
import re
import codecs
import gc

from xml.dom.minidom import parse, parseString

from .Cqpl import Cqpl
from .Token import Token

class Transduction(object):
	
	def __init__(self,nomFic="",verb=False, module = None):
		self.cqpl = []
		self.action = []
		self.nomFic = nomFic
		self.listeTransition = []
		self.tableTransition = {}
		self.etat = 1
		self.tableauRequete = []
		self.requete = ''
		self.opt = False
		self.analyseurCqp = Cqpl()
		self.ltt = []
		self.verb = verb
		self.module = module

	# appel principal
	def addRules(self,r):
		if len(r.rstrip())>0:
			self.analyseurCqp.putRequete(r)
			arbre = self.analyseurCqp.creationArbre()
			self.initAnalyse()
			self.analyse(arbre,0,1)
			self.afnd2afd()
			self.modifAutomate()
			#print("Rules = ",[self.listeTransition,self.tableTransition,self.modif])
			self.ltt.append([self.listeTransition,self.tableTransition,self.modif])
	
	# initialisation de l'automate
	def initAnalyse(self):
		self.listeTransition = []
		self.tableTransition = {}
		self.modif = {}
		self.etat = 1 # 0 etat de depart 1 etat d'arrive, on commence a 2
		

	# construction de l'automate
	# le resultat est un dictionnaire à double entree ou :
	# 	- tab[etatdep][etatfin] = trans
	#	- si trans vaut -1, c'est une epsilon-transition
	# a est une liste de la forme [num regle, sous arbre1, sous arbre 2]
	# voir classe Cqpl pour les valeurs de a[0]
	def analyse(self,a,deb,fin):
		# gestion regles
		if a[0] == 1:		# regle ensmot : ensmot WITHIN GROUPE
			self.analyse(a[1])
		elif a[0] == 3:		#regle ensmot : ensmot ensmot %prec ET
			self.etat = self.etat + 1
			nv = self.etat
			self.analyse(a[1],deb,nv)
			self.analyse(a[2],nv,fin)
		elif a[0] == 9:		# regle ensmot :  ensmot "|" ensmot
			self.analyse(a[1],deb,fin)
			self.analyse(a[2],deb,fin)
		elif a[0] == 12:	# regle ensmot : "(" ensmot ")"
			self.analyse(a[1],deb,fin)
		elif a[0] == 15:	# regle ensmot : "(" ensmot ")" "?"
			self.analyse(a[1],deb,fin)
			self.ajouteTransition(deb,-1,fin)
		elif a[0] == 18:	# regle ensmot : mot
			self.analyse(a[1],deb,fin)
		elif a[0] == 21:	# regle mot : "[" motmod "]"
			self.analyse(a[1],deb,fin)
		elif a[0] == 27:	# regle motmod : defmot 
			if not a[1] in self.listeTransition:
				self.listeTransition.append(a[1])
			self.ajouteTransition(deb,self.listeTransition.index(a[1]),fin)
		elif a[0] == 30:	# regle motmod :  defmot "/" modif 
			if not a[1] in self.listeTransition:
				self.listeTransition.append(a[1])
			self.ajouteTransition(deb,self.listeTransition.index(a[1]),fin)
			posTr = self.listeTransition.index(a[1])
			self.lectureModification(a[2],posTr)
		elif a[0] == 24:		# regle mot : "[" motmod "]" "?"
			self.analyse(a[1],deb,fin)
			self.ajouteTransition(deb,-1,fin)

	# parcours de l'automate pour mettre la règle [*] en dernière position
	# pour minimiser les règles du type [*]{x,y}
	def modifAutomate(self):
		for etat in self.tableTransition:
			nt = []
			jok = False
			for t in self.tableTransition[etat]:
				if not self.listeTransition[t[1]][1][0] == 46: # règle [*]
					nt.append(t)
				else:
					jok = True
					tr = t
			self.tableTransition[etat] = nt
			if jok:
				self.tableTransition[etat].append(tr)
			
			
	# ajout d'une modification
	# dans le tableau de modification une modif est de la forme :
	# {num : {etiq:val,etiq:val,...}}
	def lectureModification(self,a,tr):
		pile = [a]
		res = {}
		cpt = 0
		if a[0] != 52:
			while len(pile)>0:
				a = pile.pop(0)
				#print("lecture modification a="+str(a)) ####
				if a[0] == 51:	# regle modif : attval ',' attval
					pile.append(a[2])
					pile.append(a[1])
				elif a[0] == 48:	# regle modif : attval
					pile.append(a[1])
				elif a[0] == 46:
					res[a[1]] = a[1]
				else:
					if a[1] in res: # gestion d'appels multiples à une même clef
						memo = res[a[1]]
						cpt+=1
						res[a[1]+str(cpt)] = memo
					res[a[1]] = a[2]
		#print("lecture modification res final=",res) ####
		if tr not in self.modif:
			self.modif[tr] = []
			self.modif[tr].append(res)		
		else:
			self.modif[tr].append(res)

	
	# lecture modification et memorisation dans une table d'identificateurs
	# lmod  est de la forme [token,modif]
	# BUG si deux fois la même étiquette -> problème [c~"A"][l="et"][c~"^A"]
	# Il semble que si à l'interieur de la requete on trouve plusieurs fois la même définition de token ça plante (mais des fois ça marche ...) 
	# le problème n'est donc pas dans cette fonction mais plutôt au moment de l'élaboration de la table de transition
	# marche pas :[l~"^.frac"/otag="frac",r="frac"][l="{"][c="NUM"][l="}"][l="{"][c="NUM"][l="}"/ctag="frac",r="frac"]
	# marche     :[l~"^.frac"/otag="frac",r="frac"][l="{"][c="NUM"][*]{2}[c="NUM"][l="}"/ctag="frac",r="frac"]
	# faut tout réécrire..., c'est le bazar ... flemme 
	#
	# calcul, à partir des valeurs mémorisées, des valeurs modifiées
	# en entrée :
	#	lmod : suite de token d'origine à transformer
	def checkModif(self,lmod,modif):
		tableIdent = {}
		tableTrans = {}
		#print("modif=",modif) #####
		#print("eltbrut=",lmod) #####
		#print("elt=",[x[0].getLowStruct() for x in lmod]) ####
		for elt in lmod:
			tok = elt[0]
			if elt[1] in modif:
				mod = modif[elt[1]]
				#print("tablTrans=",elt[1],tableTrans)
				if elt[1] in tableTrans:
					tableTrans[elt[1]] += 1
				else:
					tableTrans[elt[1]] = 0
				#print("tablTrans=",elt[1],tableTrans)
				pos = tableTrans[elt[1]]
				#print("mod=",mod,pos) ############
				for et in mod[pos]:
					if mod[pos][et][0] == '$':
						#et = et[0] # bidouille !!!!!!!!!!!!!!
						#print("mod=",mod[pos][et],et)
						ident = mod[pos][et][1:]
						tableIdent[ident] = tok.getFeat(et)
						#if et[0] == 'f':
						#	tableIdent[ident] = tok.getForme()
						#else:
						#	tableIdent[ident] = tok.getFeat(et)
		#tableTrans = None
		modif = None
		mod = None
		#print("tableIdent=",tableIdent)
		return tableIdent				
					

	# méthode principale d'application des règles
	# la liste est une version filtrée (par la règle) des tokens de l'index
	# ATTENTION la fonction fait obligatoirement une selection d'un seul ensemble d'étiquettes
	# -> 1) sortir la transformation elle même
	# -> 2) appliquer des transformations sur un ensemble de traits



	# calcul de la nouvelle valeur à stocker dans un trait
	#	- eval 
	#	- variables (grace à ti)
	#	- valeur simple
	def calculValeur(self,valeur,ti):
		#print("calculvaleur=",valeur,ti)
		if "#" in valeur:
			for var in ti:
				valeur = valeur.replace("#"+var,ti[var])
		valeur = re.sub("#[0-9]","",valeur)
		try: #on tente d'évaluer la transformation comme si c'était du python (on cast en str au cas où le token est un nombre) ATTENTION bordelique et cause d'erreurs
			nouvelleValeur = str(eval(valeur))
		except (NameError,SyntaxError,TypeError) as e: # si eval échoue
			#raise
			nouvelleValeur = valeur
		return nouvelleValeur

	# effectue la transformation
	# 	modification : dictionnaire représentant les modifications
	#	token : liste de tokens
	#	etiqs : groupe d'étiquettes qui doit être modifié

	def modificationToken(self,modification,token,etiqs,ti):
		#print("modificationToken=",modification,token,etiqs,ti)
		if '*' in modification: # suppression du token (on met la forme à None)
			token.setForme(None)
		else:
			for trait in modification:
				if trait not in {"otag","ctag","ntok"}:
					#print("modif=",modification[trait],trait)
					if "$" not in modification[trait][0]: #si ce n'est pas de la mémorisation	
						ntrait = re.sub("[0-9]+$","",trait)
						#print("ntrait=",ntrait)
						if ntrait == "f": # si une modification porte sur la forme
								token.setForme(self.calculValeur(modification[trait],ti))
						else: # si pas 'f'
							if trait[0] == "I": # gestion de l'incrément du trait 'level'
								increment = int(trait[1:])
								etiqs['level'] = str(int(etiqs['level'])+increment)
							elif trait[0] == "D": # gestion de décrément du trait 'level'
								decrement = int(trait[1:])
								etiqs['level'] = str(int(etiqs['level'])-decrement)
							else:
								#ntrait = re.sub("[0-9]+$","",trait)
								etiqs[ntrait] = self.calculValeur(modification[trait],ti)
			

					
	# après la selection d'une suite de token
	# application des modifications
	# si un groupe de traits possède 'select' alors 1) on garde 2) on modifie (True) ou pas (False)	

	def appliqueModif(self,ltok,modif):
		res = []
		ti = self.checkModif(ltok,modif)
		tableTrans = {}
		indiceModif = {x:0 for x in modif if len(modif[x])>1} # gestion quand plusiseurs token pour un même état
		#print("modif=",modif)
		#print("appliq modif ltok=",[[x[0].getLowStruct(),x[1]] for x in ltok])
		for elt in ltok: # pour chaque token 
			[token,position] = elt
			otag = ""
			ctag = ""
			ntok = None
			if position in modif: # si le token est soumis à modification
				modifsToken = modif[position]
				# pour tous les groupes de traits qui possède le trait 'select' à True
				i = 0
				ASupprimer = [] # pour supprimer les groupes après la boucle (sinon ça plante)
				for i in range(token.getNum()): # pour chaque groupe
					if token.attExist(i,'select'): # on vérifie si le select est présent (dans le cas contraire on l'élimine de la liste des groupes de traits
						if token.getFeat('select',i): # si 'select' à True (donc groupe à modifier)
							etiqs = token.getAllFeat(i)
							if position in indiceModif: # si on est en présence de plusieurs transformation avec une seule clef
								modification = modifsToken[indiceModif[position]] # on prend la première modification (ça se fait dans l'ordre si 2 motifs sont identiques
							else: # sinon on prends la première (la seule)
								modification = modifsToken[0]
							#print("modification=",modification)
							if 'otag' in modification: # si ajout d'une balise ouvrante
								otag = modification['otag']
							if 'ctag' in modification: # si ajout d'une balise ouvrante
								ctag = modification['ctag']
							if 'ntok' in modification: # gestion de l'ajout de nouveaux tokens
								ntok = modification['ntok']
							self.modificationToken(modification,token,etiqs,ti)
						elif token.getFeat('select',i) == None: # si 'select' est à None on supprime (ou pas)
							ASupprimer.append(i-len(ASupprimer))
						token.delFeatGroup(i,'select')				
					else: # suppression du groupe de token 
						ASupprimer.append(i-len(ASupprimer))
				for indice in ASupprimer:
					token.delFeat(indice)
			else: # suppression des 'select'
				for i in range(token.getNum()):
					if token.attExist(i,'select'):
						token.delFeatGroup(i,'select')
			if position in indiceModif: # si on est en présence de plusieurs transformation avec une seule clef
				indiceModif[position] += 1 # du coup la prochaine fois on passe à la modif suivante			
			if otag != "":
				res.append(Token([[otag]]))
			if token.getForme() != None: # on teste si on élimine le token
				res.append(token)
			if ntok != None:
				for nt in eval(ntok):
					res.append(Token(nt))
			if ctag != "":
				res.append(Token(['/']))
		return res


		
	# arbre d'analyse
	# noeud : forme,[{},{}]
	# retourne True/False
	# A REPRENDRE : LA CONJONCTION NE SE FAIT PAS CAR IL FAUT FAIRE UNE INTERSECTION DES TRAITS
	# EN ATTENDANT METTRE LE FILTRE LE PLUS "RESTRICTIF" EN PREMIER
	# par defaut l'fait de selectionner un noeud ne garde que les valeurs validées par le filtre l'opérateur '+' permet de 
	# au contraire garder une valeur non selectionnée
	#def anaTrans(self,noeud,arbre):
	def anaTrans(self,arbre,select=True):
		noeud = self.matchNoeud
		#print("nn=",noeud.getLowStruct())
		#print("anatrans="+str(noeud.getLowStruct()),arbre,select)
		if noeud != None:
			if arbre[0] == 46:  # mot quelconque (*)
				return True
			elif arbre[0] == 33:	# regle defmot : attval
				#return self.anaTrans(noeud,arbre[1])
				return self.anaTrans(arbre[1],select)
			elif arbre[0] == 36:	# regle defmot : attval '&' attval %prec ET
				op1 = self.anaTrans(arbre[1],select)
				op2 = self.anaTrans(arbre[2],select)
				return op1 and op2
			elif arbre[0] == 39:	# regle defmot : attval '|' attval
				op1 = self.anaTrans(arbre[1],select)
				op2 = self.anaTrans(arbre[2],select)
				return op1 or op2
			elif arbre[0] == 43:	# regle attval : '+' attval (on selectionne, on garde mais sans modification)
				return self.anaTrans(arbre[1],select=False)
			elif arbre[0] == 44:	# regle attval : '-' attval (on selectionne, mais on garde pas)()
				return self.anaTrans(arbre[1],select=None)
			elif arbre[0] == 42:	# regle attval : ATT '=' VALATT
				return self.verifEgal(noeud,arbre[1],arbre[2],select)
			elif arbre[0] == 45:	# regle attval : ATT '~' VALATT
				return self.verifEreg(noeud,arbre[1],arbre[2],select)
			elif arbre[0] == 47: 	# regle attval : '@' ATT
				return self.attExist(noeud,arbre[1],select)
			elif arbre[0] == 40:	# regle attval : '!' defmot
				if noeud.isDiv():
					return False
				else:
					return not self.anaTrans(arbre[1])
		else: # balise
			return False
	
	# test si un noeud verifie l'égalite 
	def verifEgal(self,noeud,att,val,select=True):
		valRet = False
		res = noeud
		if not noeud.isDiv():
			if att=='f':
				if val==noeud.getForme():
					valRet = True
					for i in range(0,noeud.getNbFeat()):
						res.setAttValFeat(i,'select',select)
			else:
				f = []
				for i in range(0,noeud.getNbFeat()):
					copyTraits = noeud.copyFeat(i)
					if noeud.getFeat(att,i) == val:
						copyTraits["select"] = select
						valRet = True
					f.append(copyTraits)
				if valRet:
					res = Token([noeud.getForme(),f])
		self.matchNoeud = res
		return valRet
					
	
	# test si un noeud verifie l'égalite 
	def verifEreg(self,noeud,att,val,select=True):
		valRet = False
		res = noeud
		if not noeud.isDiv():
			#print("n=",noeud.getLowStruct())
			if att=='f':
				#print(val,noeud.getForme(),type(noeud.getForme()))
				if re.search(val,noeud.getForme()):
					#li = [x for x in range(noeud.getNbFeat())]
					#res = noeud.clone()
					valRet = True
					for i in range(0,noeud.getNbFeat()):
						res.setAttValFeat(i,'select',select)
			else:
				f = []
				for i in range(0,noeud.getNbFeat()):
					copyTraits = noeud.copyFeat(i)
					if re.search(val,noeud.getFeat(att,i)):
						copyTraits["select"] = select
						valRet = True
					f.append(copyTraits)
				if valRet:
					res = Token([noeud.getForme(),f])
		self.matchNoeud = res
		return valRet
		
	# vérification de la présence d'un trait particulier	
	def attExist(self,noeud,att,select=True):
		valRet = False
		res = noeud
		if not noeud.isDiv():
			if att=='f':
				#res = noeud.clone()
				valRet = True
				for i in range(0,noeud.getNbFeat()):
					res.setAttValFeat(i,'select',select)
			else:
				f = []
				for i in range(0,noeud.getNbFeat()):
					copyTraits = noeud.copyFeat(i)
					if att in noeud.getLstFeat():
						copyTraits["select"] = select
						valRet = True
					f.append(noeud.copyFeat(i))
				if valRet:
					res = Token([noeud.getForme(),f])
		self.matchNoeud = res
		return valRet
		
	
	## fin analyseur
	
	# algo AFN -> AFD (Dragon)
	# flemme de faire minimisation ... à faire (ou pas)
	# creation d'un tableau de transition de la forme :
	# {etat1:[[etatarr1,trans1],[etatarr2,trans2],...],etat2:[...],...}
	# l'ensemble des transitions sont stockes dans un tableau
	def epsilonSucc(self,T):
		res = []
		while len(T)>0:
			q = T.pop(0)
			if not q in res:
				res.append(q)
			if q in self.tableTransition:
				for e in self.tableTransition[q]:
					if e[1] == -1: # epsilon-transition
						if not e in res:
							res.append(e[0])
						if not e in T:
							T.append(e[0])
		res.sort()
		return res
		
	def calcTransition(self,E,tr):
		res = []
		for e in E:
			if e in self.tableTransition:
				for q in self.tableTransition[e]:
					if q[1] == tr:
						res.append(q[0])
		res.sort()
		return res
		
	def inListe(self,ll,l):
		for elt in ll:
			if (str(elt)==str(l)):
				return True
		return False
		
	def afnd2afd(self):
		Qp = []
		marque = []
		D = []
		q0 = self.epsilonSucc([0])	
		Qp.append(q0)
		marque.append(q0)
		while len(marque)>0:
			S = marque.pop(0)
			for a in range(0,len(self.listeTransition)):
				T = self.epsilonSucc(self.calcTransition(S,a))
				if len(T)>0:
					if not self.inListe(Qp,T):
						Qp.append(T)
						marque.append(T)
					D.append([str(S),a,str(T)])
		self.tableTransition = {}
		listeEtats = {'[0]':0,'[1]':1}
		numEtat = 2
		for t in D:
			if not t[0] in listeEtats:
				listeEtats[t[0]] = numEtat
				numEtat = numEtat + 1
			if not t[2] in listeEtats:
				listeEtats[t[2]] = numEtat
				numEtat = numEtat + 1
			self.ajouteTransition(listeEtats[t[0]],t[1],listeEtats[t[2]])

		
	## fct utils
	def ajouteTransition(self,edeb,trans,efin):
		if edeb in self.tableTransition:
			self.tableTransition[edeb].append([efin,trans])
		else:
			self.tableTransition[edeb] = []
			self.tableTransition[edeb].append([efin,trans])
				
	# accesseur
	def putRequete(self,requete):
		self.analyseurCqp.putRequete(requete)
	
	def getTableTransition(self):
		return self.ltt
		
	# parcours d'un flux de token et application de l'automate
	# pas de retour arrière pour l'analyse
	def checkTabToken(self,tabTok):
		#tabTok = [x.getLowStruct() for x in tabTok] # transformation temporaire
		#print("tabtok=",[x.getLowStruct() for x in tabTok]) ###
		res = tabTok # table de règles vide
		#longueurTab = len(tabTok)
		#print("tabTok="+str(len(tabTok))) ####
		#print("element tabtok"+str(tabTok)) ###
		#print("table transition=",self.getTableTransition())
		for t in self.getTableTransition(): # pour chaque regle de transformation
			lTrans = t[0]	# regle transformation
			tTrans = t[1]	# table transition
			modif = t[2]	# modification
			#print("\ntransformation=",t[0])
			#print("transition=",t[1])
			#print("modification=",t[2])
			n = 0		# etat de depart
			ptemp = 0
			ptok = -1	# position du token courant
			ltemp = []	# ensemble des tokens recouvrant une  regle *************
			res = []	# resultat d'une transformation
			rtemp = [] 	# tableau token temporaire
			while ptok <  len(tabTok)-1: 	# parcours de l'ensemble des tokens
				#print("------ etat="+str(n)) ########
				ptok = ptok + 1 	# position token suivant
				tokv = tabTok[ptok]	# recuperation du token
				#print("--->tokv="+str(tokv.getLowStruct())) ###########
				#ptemp = ptemp + 1	# position temporaire
				if False: #len(tokv) == 1:	# si balise MIS à FALSE POUR TESTER
					#ptemp = ptemp - 1 	# décrémente position temporaire
					res.append(tokv) 	# on remet le token courant dans le flux resultat
				else:			# sinon 
					trouve = False 	# booleen 'True' s'il existe une transition
					for nc in tTrans[n]: # pour un etat on test tous les etats accessibles
						suivant = nc[0]		# etat atteignable
						transition = nc[1] 	# via la transition
						#print("nc="+str(nc)) ####
						#print("anatrans=",tokv.getLowStruct(),lTrans[transition])
						#print("--------------------")
						self.matchNoeud = tokv
						if self.anaTrans(lTrans[transition]):	# si match
							#print("-----> match",self.matchNoeud.getLowStruct())
						#if self.anaTrans(tokv,lTrans[transition]):	# si match
						#if self.anaTrans(tokv.getLowStruct(),lTrans[transition]):	# si match
							if transition in modif:
								infos = self.matchNoeud
							else:
								infos = tokv
							ltemp.append([infos,transition]) #****************							
							#print("transition=",transition,self.matchNoeud.getLowStruct())
							#ltemp.append([self.matchNoeud,transition])
							n = suivant
							trouve = True
							break		# des que match on sort de la boucle
					if trouve:	# si match on enregistre le token
						#print ("A") ######
						#print("etat="+str(n)) #####
						rtemp.append(tokv)
						#print("tok=",tokv.getLowStruct())
						#print("==>ltemp=",[(x[0].getLowStruct(),x[1]) for x in ltemp]) ##########
						if n == 1: # match et transformation (fin automate)
							#print("modif=",modif) ##########
							#print("==== ltemp=",[(x[0].getLowStruct(),x[1]) for x in ltemp]) ##########
							#print("match=",self.matchNoeud.getLowStruct()) ##########
							ltok = None
							ltok = self.appliqueModif(ltemp,modif)
							#print("==== restok=",[x.getLowStruct() for x in ltok])######
							res = res + ltok
							ptemp = 0
							ltemp = [] #***************
							rtemp = []
							n = 0
					else:		# si non match alors
						ltemp = [] #***************
						#print("rtemp=",[x.getLowStruct() for x in rtemp]) ########
						#print("B "+str(n)+ " ptok="+str(ptok)+" rtemp="+str(len(rtemp))) #########
						if not tokv.isDiv():
							tokv.delFeatAllGroups('select')
							#for i in range(0,tokv.getNum()): # enlève les 'select'
							#	if tokv.attExist(i,'select'):
							#		tokv.delFeatGroup(i,'select')
						if n == 0: # parcours normal (debut automate)
							res.append(tokv)
							#print ("ajout1="+str(tokv.getLowStruct()))
						else: # le coup precedent etait dans l'automate
							#print ("ajout2=",rtemp[0].getLowStruct()) ###
							rtemp[0].delFeatAllGroups('select')
							#for i in range(0,rtemp[0].getNum()): # enlève les 'select'
							#	if rtemp[0].attExist(i,'select'):
							#		rtemp[0].delFeatGroup(i,'select')							
							#print ("ajout3=",rtemp[0].getLowStruct()) ###
							res.append(rtemp[0])
							ptok = ptok - len(rtemp) 
							n = 0		# reinitialisation de l'automate
						rtemp = []

			#for toktok in res:###
				#print("toktok="+str(toktok))###
			#for toktok in rtemp:###
				#print("rtemp="+str(toktok))###
			if len(rtemp) != 0:
				for tokv in rtemp:
					tokv.delFeatAllGroups('select')
				res = res + rtemp # <---------------------- c'est là !!! grrr faire un methode dans Token (FAIT)
			tabTok = res
		return res
		
	# accessuer pour le token courant
	def putTok(self,t):
		self.matchNoeud = t
			
		
		
		
if __name__ == '__main__':
	from Tokenize import Tokenizer
	from Cquery import Cquery
	cq = Cquery()
	a = cq.getCqpl('[c="M"]')
	t = Token(['1 .', [{'c': 'M', 'l': '1', 's': '_', 'r': 'nb2'}]])
	c = Transduction()
	c.putTok(t)
	print(c.anaTrans(a))
	
	

