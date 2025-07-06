#!/usr/bin/python3

import sys
import io

# création de l'instance
def createInstance(conf):
	return Texte(conf)

# greffon
class Texte(object):
	def __init__(self,param):
		self.ficout = sys.stdout
		self.attaff = param["att"]
		self.res = []
		
	def traite(self,conc,pre=""):
		pl = conc.getLeftString(self.attaff)
		pv = conc.getPivotString(self.attaff)
		pr = conc.getRightString(self.attaff)
		res = conc.getDiv()[-1][0]
		res += "\t"+"\t".join([str(":".join([str(x) for x in conc.getOffsets()])),pl,pv,pr]) 
		self.ficout.write("\t".join(pre)+"\t"+res+"\n")
				
	def close(self):
		pass
