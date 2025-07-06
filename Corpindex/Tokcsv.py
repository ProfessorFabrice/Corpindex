#!/usr/bin/python3

import re
import sys
from .Token import Token

##
# LDI 2014
# Fabrice Issac
# Classe Tokxml
##
# lecture d'un fichier csv deja tokenize de la forme

class Tokcsv(object):
	def __init__(self):
		self.text = ""
		self.lstFeatures = []
		self.sep = ";"
		self.encadre = '"' 
		self.setSeps(self.sep,self.encadre)
		self.premier = True
			
	def init(self,text,preproc=None):
		self.text = text.rstrip()+self.sep
		
	def setSeps(self,sep,encadre):
		self.sep = sep
		self.encadre = encadre
		self.csvreg = self.encadre+"?([^"+self.encadre+"]*?)"+self.encadre+"?"+self.sep
		
	def splitLine(self,chaine):
		res = re.findall(self.csvreg,chaine)
		return res
		
	def calcTokens(self):
		tres = []
		res = self.splitLine(self.text)
		if self.premier:
			self.lstFeatures = res
			self.premier = False
		else:
			forme = res[0]
			traits = {}
			for i in range(1,len(self.lstFeatures)):
				traits[self.lstFeatures[i]] = res[i]
			tres = [Token([forme,[traits]])]
		return tres

if __name__ == '__main__':
	tx = Tokcsv()
	for elt in open(sys.argv[1]):
		tx.init(elt)
		res = tx.calcTokens()
		for t in res:
			print(t.getLowStruct())
	
