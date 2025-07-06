#!/usr/bin/python3

import sys
import re

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
		self.ficout.write("<res>\n")
		self.attaff = param["att"]
		self.res = []
		
	def traite(self,conc,pre):
		#print(conc)
		try:
			[fic,idr] = re.split('\t',pre)
			res = '<c><file>'+fic+'</file><idr>'+idr+'</idr>'
			try:
				res += '<id>'+conc[-1][0][0].decode('utf8')+"</id>" # division
			except IndexError:
				pass
			res += '<l>'+self.affiche(conc[0])+'</l>'
			res += "<m>"
			res += self.affiche(conc[1])
			res += "</m>"
			res += '<r>'+self.affiche(conc[2])+'</r>'
		except:
			raise
			res = str(conc)
		self.ficout.write(res+"</c>\n")
		

	def affiche(self,part):
		res = []
		for elt in part:
			restmp = []
			for a in self.attaff.split(":"):
				if a!= 'f':
					for dicp in elt[1]:
						if a in dicp:
							restmp.append(dicp[a])
				else:
					restmp.append(elt[0])
			res = res + restmp
		return " ".join(res)
		
	def close(self):
		self.ficout.write("</res>\n")
		if self.ficout != sys.stdout:
			self.ficout.close()
		
