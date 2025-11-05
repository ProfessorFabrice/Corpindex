#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

# création de l'instance
def createInstance(conf):
	return Csv(conf)

# greffon
class Csv(object):
	def __init__(self,param):
		if param["value"] != "":
			self.ficout = open(param["value"] ,"w",encoding="utf-8")
		else:
			self.ficout = sys.stdout
		self.attaff = param["att"]
		self.res = []
		self.sepw = " "
		self.sepp = " "
		if param["w"] == "1":
			self.sepw = "\t"
			self.sepp = "\t"
		elif param["w"] == "2":
			self.sepw = "\t"
			self.sepp = " "

			
		
	def traite(self,conc,pre):
		res = pre+"\t"
		res = res + self.affiche(conc[0],self.sepw)
		res = res + "\t<r>\t"
		res = res + self.affiche(conc[1],self.sepp)
		res = res + "\t</r>\t"
		res = res + self.affiche(conc[2],self.sepw)
		self.ficout.write(res+"\n")
		

	def affiche(self,part,separateur):
		res = []
		for elt in part:
			#print elt[1]
			for a in self.attaff.split(":"):
				if a!= 'f':
					for dicp in elt[1]:
						res.append(dicp[a])
				else:
					res.append(elt[0])
		return separateur.join(res)

		
	def close(self):
		if self.ficout != sys.stdout:
			self.ficout.close()
		
