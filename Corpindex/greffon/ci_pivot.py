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
		self.fin=int(param["pvf"])
		self.debut=int(param["pvd"])
		if "sep" in param:
			self.sep = param["sep"]
		else:
			self.sep = " "
		if "t" in param:
			self.t = param["t"]
		else:
			self.t = "from"
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
		self.attaff = param["att"]
		self.res = []
		
	def traite(self,conc,pre=""):
		pv = conc.getPivot()
		infodiv = conc.getDiv()
		res = "_top"
		pvtab = []
		if self.t == "from":
			if self.fin<0:
				fin = len(pv) + self.fin
			else:
				fin = self.fin
			for t in range(self.debut,fin+1):
				pvtab.append(pv[t].getFeat(self.attaff))
		else:
			pvtab=[pv[self.debut].getFeat(self.attaff),pv[self.fin].getFeat(self.attaff)]
		pvstr = self.sep.join(pvtab)
		if len(infodiv) > 0:
			if infodiv[0] != '':
				res = infodiv[0][0]
		res += "\t"+"\t".join([str(conc.getOffset()),pvstr]) 
		#res += "\t"+str(conc.getOffset())
		self.ficout.write(pre+"\t"+res+"\n")
				
	def close(self):
		if self.closeFic:
			self.ficout.close()
		
