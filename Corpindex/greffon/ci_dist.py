#!/usr/bin/python3

import sys
import io

# création de l'instance
def createInstance(conf):
	return Texte(conf)

# greffon
class Texte(object):
	def __init__(self,param):
		valret = param["value"]
		self.taille = int(param["size"])
		self.closeFic = False
		if isinstance(valret,str):
			if param["value"] != "":
				self.ficout = open(param["value"] ,"w",encoding="UTF-8")
				self.closeFic = True
			else:
				self.ficout = sys.stdout
		elif isinstance(valret,io.StringIO):
			self.ficout = valret
		else:
			self.ficout = sys.stdout
		self.res = {}
		
	def traite(self,conc,pre=""):
		offset = conc.getOffset()
		k = offset // self.taille
		if k not in self.res:
			self.res[k] = 1
		else:
			self.res[k] += 1
	def printResult(self,nomfic):
		lstk = sorted([x for x in self.res])
		for i in range(0,lstk[-1]):
			if i not in lstk:
				self.ficout.write(str(i)+"\t0\n")
			else:
				self.ficout.write(str(i)+"\t"+str(self.res[i])+"\n")
						
	def close(self):
		if self.closeFic:
			self.ficout.close()
		
