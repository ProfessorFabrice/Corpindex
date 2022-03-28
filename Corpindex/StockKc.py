#!/usr/bin/python3
# -*- coding: utf-8 -*-

##
# LDI 2010
# Fabrice Issac
# Classe Stock
##

import re
import pickle
import sys
import random
import time
#try:
#	from kyotocabinet import *
#except ImportError:
#	sys.stderr.write("pas de prise en charge du module kyotocabinet\n")

class Stock(dict):
	def __init__(self):
		self.dico = {}

	def open(self,name,mode="r"):
		try:
			if mode == "w":
				mode = DB.OWRITER | DB.OCREATE | DB.OTRUNCATE
			else:
				mode = DB.OREADER
			self.dico = DB()
			self.dico.open(name+".kcf", mode)
		except:
			sys.stderr.write("impossible d'ouvrir : "+name+"\n")
			raise

	def close(self):
		pass
		
	def keys(self):
		return [x for x in self.dico]

	def __setitem__(self,c,v):
		self.dico[c]=v
		
	def __getitem__(self,c):
		return self.dico[c]
		
	def sync(self):
		pass

if __name__ == '__main__':
		pass

