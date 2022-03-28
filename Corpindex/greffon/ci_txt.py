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
		if "cqpl" in param:
			self.cqpl = True
		else:
			self.cqpl = False
		self.attaff = param["att"]
		self.res = []
		
	def traite(self,conc,pre=""):
		if self.cqpl:
			pl = conc.getLeftCqpl(self.attaff)
			pv = conc.getPivotCqpl(self.attaff)
			pr = conc.getRightCqpl(self.attaff)
		else:
			pl = conc.getLeftString(self.attaff)
			pv = conc.getPivotString(self.attaff)
			pr = conc.getRightString(self.attaff)
		infodiv = conc.getDiv()
		res = "_top"
		if len(infodiv) > 0:
			if infodiv[0] != '':
				#res = infodiv[-1][0]
				res = ":".join([x[0] for x in infodiv])
		res += "\t"+"\t".join([str(conc.getOffset()),pl,pv,pr]) 
		#res += "\t"+str(conc.getOffset())
		self.ficout.write(pre+"\t"+res+"\n")
				
	def close(self):
		if self.closeFic:
			self.ficout.close()
		
