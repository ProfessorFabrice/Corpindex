#!/usr/bin/env python3
# -*- coding: utf8 -*- 

# -----------------------------------------------------------------------------
# analyse de la requete avec ply
# -----------------------------------------------------------------------------
# TODO
#	- negation (en fait je ne sais pas trop. En complexite cela risque d'etre long)
# 	- fonctions (cf. CQP)

import sys

import os
import re

#sys.path.append("Corpindex")

from .Cqpl import Cqpl

class RequeteIndex(object):
	def __init__(self):
		self.index = {}
		self.tableauRequete = []
		self.requete = ''
		self.ensRequete = {}
		self.opt = False
		self.analyseurCqp = Cqpl()
		self.listeFct = []
		self.zone = {} # mémorisation des position des zones
		self.listeEtiquette = {}
		# a garder pour debug

	# appel principal
	def calculRequete(self):
		arbre = self.analyseurCqp.creationArbre()
		ana = self.analyse(arbre)
		return ana[1]

	# retourne un tableau à deux elements 
	# 0 : drapeau (utilisé pour gérer les '?' et les parenthèses)
	# 1 : liste d'offsets
	# a est une liste de la forme [num regle, sous arbre1, sous arbre 2]
	def analyse(self,a):
		ensRequete = []
		# appel recursif suivant la regle a appliquer
		#print 'a='+str(a)
		if a[0] not in [46,45,42]: # au moins un sous arbre
			a1 = self.analyse(a[1]) 
			if a[0] in [3,9,36,39]: # 2 sous arbres
				a2 = self.analyse(a[2])
		# gestion regles
		if a[0] == 1:		# regle ensmot : ensmot WITHIN GROUPE
			#print 'within='+str(a[2])
			ensRequete = [0,self.within(a1,a[2])]
		elif a[0] == 3:		#regle ensmot : ensmot ensmot %prec ET
			if a2[0] & 2 != 0: # la liste 2 est parenthese
				listeinter = self.intersectionBorne(a1[1],a2[1],1)
			else:
				listeinter = self.intersection(a1[1],a2[1],1)
			if a2[0] & 1 != 0: # la liste 2 est optionnellle
				ensRequete = [0,self.union(a1[1],listeinter)]
			elif a1[0] & 1 != 0:# la liste 1 est optionnellle
				ensRequete = [0,self.union(a2[1],listeinter)]
			else:
				ensRequete = [0,listeinter]
		elif a[0] == 9:		# regle ensmot :  ensmot "|" ensmot
			ensRequete = [a2[0],self.union(a1[1],a2[1])]
		elif a[0] == 12:	# regle ensmot : "(" ensmot ")"
			ensRequete = [2,a1[1]]
		elif a[0] == 15:	# regle ensmot : "(" ensmot ")" "?"
			ensRequete = [3,a1[1]]
		elif a[0] == 18:	# regle ensmot : mot
			ensRequete = [a1[0],a1[1]]
		elif a[0] == 21:	# regle mot : "[" defmot "]"
			ensRequete = [0,a1[1]]
		elif a[0] == 24:	# regle mot : "[" defmot "]" "?"
			ensRequete = [1,a1[1]]
		elif a[0] == 27:	# règle motmod : defmot
			ensRequete = [0,a1[1]]
		elif a[0] == 30:	# règle motmod : defmot "/" modif
			ensRequete = [0,a1[1]]
		elif a[0] == 31:	# règle motmod : defmot ZONE NUM
			#for x in a1[1]:
			#	if x not in self.zone:
			#		self.zone[x] = {}
			#	self.zone[x]=a[2]
			ensRequete = [0,a1[1]]
		elif a[0] == 33:	# regle defmot : attval
			ensRequete = [0,a1[1]]
		elif a[0] == 34:	# regle defmot : "(" defmot ")"
			ensRequete = [0,a1[1]]	
		elif a[0] == 36:	# regle defmot : defmot '&' defmot  %prec ET
			ensRequete = [0,self.intersection(a1[1],a2[1],0)]
		elif a[0] == 39:	# regle defmot : defmot '|' defmot 
			ensRequete = [0,self.union(a1[1],a2[1])]
		elif a[0] == 42:	# regle attval : ATT '=' VALATT 
			ensRequete = [0,self.construitListeOffset(a[1],a[2],'e')]
		elif a[0] == 45:	# regle attval : ATT '~' VALATT 
			ensRequete = [0,self.construitListeOffset(a[1],a[2],'r')]
		elif a[0] == 47:	# regle attval : '@' ATT
			ensRequete = [0,self.getListFeature(a[1])] 
		elif a[0] == 46:	# regle attval : MOT
			ensRequete = [0,{'mot':-1}] 	# [-1] -> n'importe quel mot
		else:	# erreur retourne vide
			ensRequete = [0,{}]
		return ensRequete		
		
	
	## fin analyseur
	## fonction permettant l'acces à l'index
	
	def getListFeature(trait):
		return {}
	
	# liste d'offset par rapport a une etiquette, une valeur (fixe ou regexp) et un operateur
	def construitListeOffset(self,etiquette,valeur,flag):
		listeRes = {}
		if flag == 'r': # i.e. expression reguliere
			for element in self.index.getTagIndex(etiquette):
				try: # beurk
					#valBool = re.search(valeur.encode(),element)
					valBool = re.search(valeur,element.decode('utf-8'))
				except TypeError:
					valBool = re.search(valeur,element)
				if valBool != None:
					for e in self.index.getGlobalIndex(etiquette,element):
						listeRes[e] = e
		elif flag == 'e': # i.e. valeur fixe
			for e in self.index.getGlobalIndex(etiquette,valeur):
				listeRes[e] = e
		return listeRes
			
	# gestion du {deb,fin}
	def ajoutOp(self,l,deb,fin):
		res = self.repete(l,int(deb))
		for i in range(deb,fin):
			tmp = self.intersection(res,l,1)
			res = self.union(res,tmp)
		return res
		
	# union de deux listes (dictionnaires)
	def union(self,l1,l2):
		l1.update(l2)
		#return dict(l1, **l2)
		return l1
	
	# intersection de deux listes (dictionnaires) 
	def intersection(self,l1,l2,pas):
		res = {}
		if 'mot' in l2:
			for e in list(l1.keys()):
				res[e+pas] = l1[e]
		else:	
			if len(l1)<len(l2):
				for e in list(l1.keys()):
					if e+pas in l2:
						res[e+pas] = l1[e]
			else:
				for e in list(l2.keys()):
					if e-pas in l1:
						res[e] = l1[e-pas]
		return res
						
	# intersection de deux listes (dictionnaires) 
	def intersectionBorne(self,l1,l2,pas):
		res = {}
		l2 = self.invert_dict_fast(l2)
		for e in list(l1.keys()):
			if e+pas in l2:
				res[l2[e+pas]] = l1[e]
		return res			
				
	# retourne 
	def ajout(self,l,pas):
		res = {}
		if pas == 0:
			return l
		else:
			for e in list(l.keys()):
				res[e+pas] = l[e]
		return res
			
	# ...(inutile je pense)
	def repete(self,l,nb):
		res = l
		#print "repete "+str(nb)
		#print `res`
		for i in range(1,nb):
			res = self.intersection(res,l,1)
			#print 'bcl repete '+`res`
		return res
		
	# gestion within
	# dico : ensemble requete comme fct analyse
	# div : etiquette de la division
	def within(self,dico,div):
		if div[0]=="~":
			div = div[2:-1] 
			tabPos = self.index.getPosDivRegExp(div)
		else:
			tabPos = self.index.getPosDiv(div)
		res = {}
		#print("tabPos=",tabPos)
		for elt in dico[1]:
			deb=dico[1][elt]
			fin = elt
			#print("concordance debut="+str(deb)+" fin="+str(fin)) ###
			for interval in tabPos:
				if interval[0] <= deb and interval[1] >=fin:
					#print("debut="+str(interval[0])+" fin="+str(interval[1]))
					#print("match","concordance debut="+str(deb)+" fin="+str(fin))
					res[fin] = deb
					break
		return res
	

    # accesseur
	def putRequete(self,requete):
		self.analyseurCqp.putRequete(requete)
		
	def putIndex(self,index):
		self.index = index
		
	def getZone(self):
		return self.zone
	
	# inverse clef/valeur dans un dictionnaire
	def invert_dict_fast(self,d):
		return dict(zip(iter(d.values( )), iter(d.keys( ))))
		
		
if __name__ == '__main__':
	c = RequeteIndex()
	c.putIndex()
 
