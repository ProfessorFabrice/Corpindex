#!/usr/bin/python3

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


class Stock(dict):
	def __init__(self):
		self.dico = {}
		self.ficdico = None
		self.nomfic = ""
		self.mode = ""
		
	def open(self,name,mode="r"):
		self.mode = mode
		self.nomfic = name+".dpy"
		if mode == "r":
			f = open(self.nomfic,"rb")
			self.dico = pickle.load(f)
			f.close()

	def close(self):
		if self.mode == "w":
			f = open(self.nomfic,"wb")
			pickle.dump(self.dico,f)
			f.close()
		self.dico = {}
		
	def keys(self):
		return list(self.dico.keys())

	def __setitem__(self,c,v):
		self.dico[c]=v
		
	def __getitem__(self,c):
		return self.dico[c]
		
	def sync(self):
		pass

if __name__ == '__main__':
		DATA_SIZE = 94
		TABCAR = [chr(x) for x in range(33,127)]
		import random
		s = Stock()
		s.open("test","w")
		for x in range(1,10):
			s[str("".join(random.sample(TABCAR,DATA_SIZE)))] = 1
		s.close()
		t = Stock()
		t.open("test","r")
		for i in t.keys():
			print(t[i])
