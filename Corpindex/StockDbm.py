#!/usr/bin/python3
# -*- coding: utf-8 -*-

##
# LDI 2011
# Fabrice Issac
# Classe StockBsddb
##

import re
import pickle
import sys
import random
import time
import dbm


class Stock(dict):
	def __init__(self):
		self.dico = {}

	def open(self,name,mode="c"):
		mode = "c"
		try:
			self.dico = dbm.open(name+".dbm",mode)
		except:
			sys.stderr.write("Open impossible d'ouvrir : "+name+"\n")
			#exit(0)
			raise
#			try:
#				self.dico = dbm.open(name+".dbm.db",mode)
#			except:
#				sys.stderr.write("impossible d'ouvrir : "+name+"\n")
				#exit(0)
#				raise

	def close(self):
		self.dico.close()
		
	def keys(self):
		#return list(self.dico.keys())
		return [x.decode("utf8") for x in self.dico.keys()]

	def __setitem__(self,c,v):
		self.dico[c] = v
		
	def __getitem__(self,c):
		return self.dico[c]
		
	def sync(self):
		pass

if __name__ == '__main__':
	pass
