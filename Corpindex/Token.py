#!/usr/bin/python3

##
# 2014
# Fabrice Issac
# Classe Token
##
# gestion des affichages des concordances

import string
import re
import sys
import json

class Token(object):
	'Classe Token'
	def __init__(self,tok):
		'Constructeur de l\'objet'
		self.__tok = tok
		self.toto = tok

	def getForme(self):
		'Retourne la forme'
		return self.__tok[0]

	def setForme(self,f):
		self.__tok[0] = f
		
	# retourne le groupe de traits num
	def getAllFeat(self,num):
		return self.__tok[1][num]

	# ne concerne que le premier par défaut
	def getFeat(self,att,num=0):
		if not self.isDiv():
			if att == "f":
				return self.getForme()
			else:
				num = min(num,len(self.__tok[1]) - 1)
				if att in self.__tok[1][num]:
					return self.__tok[1][num][att]
				else:
					return "_"
		else:
			return ""

	def getNbFeat(self):
		return len(self.__tok[1]) 
		
	def getDiv(self):
		if self.isDiv():
			return self.__tok[0][0] 
		else:
			return None

	def isDiv(self):
		return (len(self.__tok) == 1)

	def getLowStruct(self):
		'return the <i>low level</i> structure'
		return self.__tok

	def getLstFeat(self,num=0):
		'return the list of the features'
		try:
			lst = sorted(list(self.__tok[1][num].keys()))
		except:
			print(self.__tok)
			print(self.__tok[1][0].__tok)
			raise
		return lst
		
	# retourne l'ensemble des traits associés à une forme
	# soit un tableau (de dictionnaires), soit un dictionnaire
	def getFeatVal(self,num=-1):
		if num == -1:
			return self.__tok[1]
		else:
			return self.__tok[1][num]
			
	# ajoute un ensemble de traits/valeurs sous forme d'un dictionnaire		
	def setFeatVal(self,d):
		self.__tok[1].append(d)

	# ajoute un attribut à un groupe
	def setAttValFeat(self,num,att,val):
		self.__tok[1][num][att] = val
			
	# ajoute un attribut à tous les groupes
	def setAttValAllFeat(self,att,val):
		try:
			for i in range(0,len(self.__tok[1])):
				self.__tok[1][i][att] = val
		except:
			print("erreur",self.__tok,att,val)
			
	def getJson(self):
		return json.dumps(self.__tok)
		
	def clone(self):
		'return a copy of the token'
		return Token(self.getLowStruct())
		
	def cloneSet(self,lst):
		res = [self.getForme()]
		for elt in lst:
			res.append(self.getLstFeat(elt))
		return res
		
	def copyFeat(self,n):
		res = {}
		for elt in self.getLstFeat(n):
			res[elt] = self.getFeat(elt,n)
		return res
	
	def getNum(self):
		if self.isDiv():
			return 0
		else:
			return len(self.__tok[1])
		
	# vérifie si un attribut est présent
	def attExist(self,n,att):
		return att in self.__tok[1][n]
		
	# suppression d'un groupe de traits
	def delFeat(self,n):
		del self.__tok[1][n]
		
	# suppression d'un trait dans un groupe de traits
	def delFeatGroup(self,n,trait):
		del self.__tok[1][n][trait]
		
	# suppression traits 'select'	
	def delFeatAllGroups(self,trait):
		for i in range(0,self.getNum()): 
			if self.attExist(i,trait):
				self.delFeatGroup(i,'select')							

	# ne garder que les groupes avec le trait 'level' max
	def sortFiltre(self):
		#print("sortFiltre",self.__tok)
		if 'level' in self.__tok[1][0]: # le trait est présent dans le premier groupe (sinon on fait rien)
			traits = sorted(self.__tok[1],key=lambda x:x["level"],reverse=True)
			i = 1
			lmax = int(traits[0]['level'])
			while i<len(traits) and int(traits[i]['level']) == lmax:
				i += 1
			self.__tok = [self.__tok[0],traits[:i]]
		
if __name__ == '__main__':
	pass			



