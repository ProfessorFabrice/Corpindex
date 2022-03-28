#!/usr/bin/python3

import re
import string
import sys

sys.path.append('Corpindex/greffon')

class Post(object):
	def __init__(self,conf,tabconc,tabinfo):
		nom = conf["name"]
		self.gref = __import__(nom).createInstance(conf)
		self.tabconc = tabconc
		self.typeg = conf["type"]
		self.conf = conf
		self.tabinfo = tabinfo
	
	def process(self):
		if self.typeg == "filter":
			res = []
			for elt in self.tabconc:
				if self.gref.traite(elt[1]):
					res.append(elt)
			self.tabconc = res
		elif self.typeg == "out":
			for elt in self.tabconc:
				pre = "\t".join(self.tabinfo[elt[0]])
				self.gref.traite(elt[1],pre)
		elif self.typeg == "proc":
			for elt in self.tabconc:
				self.gref.traite(elt[1])
		elif self.typeg == "procout":
			for elt in self.tabconc:
				self.gref.traite(elt[1])
			self.gref.printResult(self.conf["value"])
		self.gref.close()
		
	def getConc(self):
		return self.tabconc
