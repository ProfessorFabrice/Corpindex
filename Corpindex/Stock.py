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
try:
	import dbm.ndbm
except ImportError:
	pass
try:
	from kyotocabinet import *
except ImportError:
	sys.stderr.write("pas de prise en charge du module kyotocabinet\n")
try:
	import bsddb3 as bsddb
except ImportError:
	try:
		import bsddb
	except ImportError:
		sys.stderr.write("pas de prise en charge du module bsddb\n")

class Stock(dict):
	def __init__(self,nature="kc"):
		self.nature = nature
		self.dico = {}

	def open(self,name,mode="r"):
		try:
			if self.nature == "kc":
				if mode == "w":
					mode = DB.OWRITER | DB.OCREATE | DB.OTRUNCATE
				else:
					mode = DB.OREADER
				self.dico = DB()
				self.dico.open(name+".kcf", mode)
			elif self.nature == "dbm":
				if mode == "w":
					mode = "c"
				self.dico = dbm.ndbm.open(name,mode)
			elif self.nature == "bsd":
				self.dico = bsddb.btopen(name+".bsd",mode)
		except:
			sys.stderr.write("impossible d'ouvrir : "+name+"\n")
			raise

	def close(self):
		if self.nature == "bsd":
			self.dico.close()
	def keys(self):
		if self.nature == "kc":
			return [x for x in self.dico]
		else:
			return list(self.dico.keys())

	def __setitem__(self,c,v):
		try:
			self.dico[c]=v
		except TypeError:
			print("c="+str(type(c))+" "+str(c))
			#print("v="+str(type(v))+" "+str(v))
			#raise
		
	def __getitem__(self,c):
		return self.dico[c]
		
	def sync(self):
		if self.nature == "bsd":
			self.dico.sync()

if __name__ == '__main__':
		pass

