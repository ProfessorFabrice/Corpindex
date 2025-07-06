#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from Transduction import *

# création de l'instance
def createInstance(conf):
	return Texte(conf)

# greffon
class Texte(object):
	def __init__(self,param):
		if param["value"] != "":
			self.ficout = open(param["value"] ,"w",encoding="utf-8")
		else:
			self.ficout = sys.stdout
		self.attaff = param["att"]
		self.res = []
		self.trans = Transduction()
		self.trans.addRules(param["r"])
		
	def traite(self,conc,pre):
		try:
			#res = []
			res = pre+"\t"
			res = res + self.affiche(conc[0])
			res = res + " (("
			res = res + self.affiche(self.trans.checkTabToken(conc[1]))
			#print (conc[1]) #####
			#res = res + self.trans.checkTabToken(conc[1])
			res = res + ")) "
			res = res + self.affiche(conc[2])
		except:
			raise
			res = str(conc)
		self.ficout.write(str(res)+"\n")
		

	def affiche(self,part):
		res = []
		for elt in part:
			for a in self.attaff.split(":"):
				if a!= 'f':
					for dicp in elt[1]:
						if a in dicp:
							res.append(dicp[a])
				else:
					res.append(elt[0])
		#print (res) #####
		return " ".join(res)
		
