#!/usr/bin/env python3

import re
import pickle
import sys
import random
import time
import dbm


class StockDbm(dict):
	def __init__(self):
		self.dico = {}

	def open(self,name,mode="c"):
		mode = "c"
		try:
			self.dico = dbm.open(name+".dbm",mode)
		except:
			sys.stderr.write("Open impossible d'ouvrir : "+name+"\n")
			raise

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
