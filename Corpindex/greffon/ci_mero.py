#!/usr/bin/python3

import sys
import operator

# création de l'instance
def createInstance(conf):
	return Freq(conf)

# greffon

class Freq(object):
	def __init__(self,conf):
		self.resfinal = {}
		
	def traite(self,conc,pre=""):
		res = []
		for dicp in conc[0]:
			if dicp[1][0]["c"][0] == "N":
				if not dicp[1][0]["l"] in self.resfinal:
					self.resfinal[dicp[1][0]["l"]] = 0
				self.resfinal[dicp[1][0]["l"]] += 1
		for dicp in conc[2]:
			if dicp[1][0]["c"][0] == "N":
				if not dicp[1][0]["l"] in self.resfinal:
					self.resfinal[dicp[1][0]["l"]] = 0
				self.resfinal[dicp[1][0]["l"]] += 1

	def printResult(self,nomfic):
		for elt in self.resfinal:
			if self.resfinal[elt]>20:
				print('<item freq="'+str(self.resfinal[elt])+'">'+elt+'</item>')
			
	def close(self):
		pass

