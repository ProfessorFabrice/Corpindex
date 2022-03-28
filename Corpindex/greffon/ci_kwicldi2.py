#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import operator
import math
import re

# création de l'instance
def createInstance(conf):
	return Kwicldi(conf)

# greffon
class Kwicldi(object):
	def __init__(self,conf):
		self.att = conf["att"]
		self.nomfic = conf["value"]
		self.pp = int(conf["pp"])
		self.pa = int(conf["pa"])
		self.resfinal = {}
		self.tabPA = {}
		self.lP = {}
		self.lA = {}
		self.lC = []
		self.ptrficout = 0
		
	def traite(self,conc):
		req = conc[0]+conc[1]+conc[2]
		if self.att =='f':
			pred = req[self.pp][0]
			arg = req[self.pa][0]
		else:
			pred = req[self.pp][1][0][self.att]
			arg = req[self.pa][1][0][self.att]
		self.lP[pred] = 1
		self.lA[arg] = 1
		try:
			self.tabPA[pred][arg] = self.tabPA[pred][arg] + 1
		except:
			try:
				self.tabPA[pred][arg] = 1
			except:
				self.tabPA[pred] = {}
				self.tabPA[pred][arg] = 1

	def calculfreqPred(self):
		for pred in self.lP.keys():
			somme = 0
			nbelt = 0
			for arg in self.lA.keys():
				try:
					somme = somme + self.tabPA[pred][arg]
				except:
					pass
			self.tabPA[pred]["sPred"] = somme
			self.tabPA[pred]["nb"] = len(self.lA.keys())
			self.tabPA[pred]["moyenne"] = float(somme)/float(len(self.lA.keys()))
		self.lC.append("nb")
		self.lC.append("moyenne")
		self.lC.append("sPred")
		
	def calculNbArg(self):
		for pred in self.lP.keys():
			somme = 0
			for arg in self.lA.keys():
				if arg in self.tabPA[pred]:
					somme = somme + 1
			self.tabPA[pred]["sArg"] = somme
		self.lC.append("sArg")
		

	def calculArgMax(self):
		nbelt = len(self.lA)
		for pred in self.lP.keys():
			maxi = 0
			nomArg = ""
			for arg in self.lA.keys():
				if arg in self.tabPA[pred]:
					if self.tabPA[pred][arg]>maxi:
						maxi = self.tabPA[pred][arg]
						nomArg = arg
			self.tabPA[pred]["maxPred"] = nomArg
			#print self.tabPA[pred]["sPred"]
			#print maxi
			#print nbelt
			self.tabPA[pred]["zTestMax"] = re.sub('\.',',',str(maxi))
			mesure = self.tabPA[pred]["sPred"]*maxi/self.tabPA[pred]["sArg"]
			self.tabPA[pred]["Mesure"] = re.sub('\.',',',str(mesure))
		self.lC.append("zTestMax")
		self.lC.append("Mesure")
		self.lC.insert(0,"maxPred")
		
	def calculTest(self):
		for pred in self.lP.keys():
			s1 = 0
			for arg in self.lA.keys():
				if arg in self.tabPA[pred]:
					val = self.tabPA[pred][arg]
				else:
					val = 0
				diff = val - self.tabPA[pred]["moyenne"]
				s1 = s1 + diff*diff
			ecarttype = math.sqrt(float(s1)/float(len(self.lA.keys())))
			self.tabPA[pred]["ecarttype"] = ecarttype
			for arg in self.lA.keys():
				if arg in self.tabPA[pred]:
					val = self.tabPA[pred][arg]
				else:
					val = 0
				try:
					self.tabPA[pred][arg] = float(val - self.tabPA[pred]["moyenne"])/ecarttype
				except:
					self.tabPA[pred][arg] = 0
		self.lC.append("ecarttype")
		self.lC.append("moyenne")
			
		
	def calcul(self):
		self.calculfreqPred()
		self.calculNbArg()
		self.calculTest()
		self.calculArgMax()
		
		


	def printResult(self,nomfic):
		self.calcul()
		if self.nomfic != "":
			ficout = open(self.nomfic,"w",encoding="utf-8")
		else:
			ficout = sys.stdout
		#print self.lC+self.lA.keys()
		for arg in self.lC+list(self.lA.keys()):
			ficout.write('\t'+arg)
		ficout.write('\n')
		for pred in self.lP.keys():
			ficout.write(pred)
			for arg in self.lC+list(self.lA.keys()):
				ficout.write('\t')
				try:
					ficout.write(str(self.tabPA[pred][arg]))
				except:
					ficout.write('0')
			ficout.write('\n')

	def close(self):
		pass


