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
import os

import bsddb3 as bsddb

class Stock(dict):
	def __init__(self):
		self.dico = {}
		self.dkeys = {}

	def open(self,name,mode="r"):
		try:
			self.dico = bsddb.btopen(name+".bsd",mode)
		except:
			sys.stderr.write("impossible d'ouvrir : "+name+"\n")
			raise
			
		
	def close(self):
		self.dico.close()
		
	def keys(self):
		return list(self.dico.keys())
		
	def __contains__(self,c):
		if c in self.dkeys:
			return True
		else:
			return False
	
	# A VERIFIER l'utilité du truc (presque certain que non)
	def __setitem__(self,c,v):
		try:
			self.dico[c] = v
		except:
			self.dico[c.encode()]=v
		
	def __getitem__(self,c):
		try:
			ret = self.dico[c]
		except TypeError:
			ret = self.dico[c.encode()]
		return ret
		
	def sync(self):
		self.dico.sync()
		self.dkeys = dict([(x.decode("utf-8"),'') for x in list(self.dico.keys())])

if __name__ == '__main__':
		pass

