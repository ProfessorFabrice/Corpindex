#!/usr/bin/python3

import sys

# création de l'instance
def createInstance(conf):
	return Texte(conf)

# greffon
class Texte(object):
	def __init__(self,param):
		if param["value"] != "":
			self.ficout = open(param["value"] ,"w",encoding="UTF-8")
		else:
			self.ficout = sys.stdout
		self.attaff = param["att"]
		self.res = {}
		
	def traite(self,conc,pre):
		pl = conc.getLeftString(self.attaff)
		pv = conc.getPivotString(self.attaff)
		pr = conc.getRightString(self.attaff)
		infodiv = conc.getDiv()
		if len(infodiv) > 0:
			res = infodiv[0][0]
		else:
			res = ""
		res += "\t"+"\t".join([str(conc.getOffset()),pl,pv,pr])
		self.res[str(conc.getOffset())] = pre+"\t"+res
		#res += "\t"+str(conc.getOffset())
		#self.ficout.write(pre+"\t"+res+"\n")
				
	def close(self):
		for elt in self.res:
			self.ficout.write(self.res[elt]+"\n")
		if self.ficout != sys.stdout:
			self.ficout.close()
		
