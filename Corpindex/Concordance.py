#!/usr/bin/python3

##
# 2014
# Fabrice Issac
# Classe Concordance
##
# gestion des concordances
# une concordance c'est : une partie gauche, un pivot, une partie droite et des divisions

import string
import re
import sys

class Concordance(object):
	'''
	Stockage d'une concordance 
	'''
	def __init__(self,pl,pv,pr,div,offset,fin=None):
		self.__pl = pl
		self.__pv = pv
		self.__pr = pr
		self.__div = [x.decode('utf8') if isinstance(x,bytes) else x for x in div]
		self.__offset = offset
		self.__fin = fin
	
	def getLeft(self):
		return self.__pl

	def getLeftString(self,att=["f"]):
		return " ".join(["_".join([x.getFeat(a) for a in att]) for x in self.__pl])

	def getLeftCqpl(self,att=["f"]):
		res= ""
		for t in self.__pl:
			res += "["+"&".join([f'{a}="{t.getFeat(a)}"' for a in att])+"]"
		return res

	def getRight(self):
		return self.__pr

	def getRightString(self,att=["f"]):
		return " ".join(["_".join([x.getFeat(a) for a in att]) for x in self.__pr])

	def getRightCqpl(self,att=["f"]):
		res= ""
		for t in self.__pr:
			res += "["+"&".join([f'{a}="{t.getFeat(a)}"' for a in att])+"]"
		return res

	def getPivot(self):
		return self.__pv

	def getPivotString(self,att=["f"]):
		return " ".join(["_".join([x.getFeat(a) for a in att]) for x in self.__pv])

	def getPivotCqpl(self,att="f"):
		res= ""
		for t in self.__pv:
			res += "["+"&".join([f'{a}="{t.getFeat(a)}"' for a in att])+"]"
		return res

	def getDiv(self):
		return self.__div #+[self.__pv[0].getForme()]
	
	# on garde pour le moment mais à supprimer
	def getOffset(self):
		return self.__offset

	def getOffsets(self):
		return [self.__offset,self.__fin]

