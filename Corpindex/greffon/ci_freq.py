#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import operator

# création de l'instance
def createInstance(conf):
	return Freq(conf)

# greffon

class Freq(object):
	def __init__(self,conf):
		self.attaff = conf["att"]
		self.nomfic = conf["value"]
		self.resfinal = {}
		
	def traite(self,conc,pre=""):
		res = []
		if self.attaff != 'f':
			for dicp in conc[1][0][1]:
				res.append(dicp[self.attaff])
			for dicp in conc[1][-1][1]:
				res.append(dicp[self.attaff])
		else:
			res.append(conc[1][0][0])
			res.append(conc[1][-1][0])
		chaine = " ".join(res)
		try:
			self.resfinal[chaine] = self.resfinal[chaine] + 1
		except:
			self.resfinal[chaine] = 1

	def printResult(self,nomfic):
		comparateur = lambda a : a[1]
		if self.nomfic != "":
			ficout = open(self.nomfic,"w",encoding="utf-8")
		else:
			ficout = sys.stdout
		ressort = sorted(self.resfinal.items(), key=comparateur, reverse=True)
		#ressort = sorted(self.resfinal.iteritems(), reverse=False, key=operator.itemgetter(1))
		for elt in ressort:
			ficout.write(str(elt[0])+"\t"+str(elt[1])+"\n")

	def close(self):
		pass

