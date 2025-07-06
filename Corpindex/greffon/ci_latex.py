#!/usr/bin/python3

import sys
import io
import re

# création de l'instance
def createInstance(conf):
	return Texte(conf)

# greffon
class Texte(object):
	def __init__(self,param):
		self.ficout = sys.stdout
		self.attaff = param["att"]
		self.res = []
		self.ficout.write("""\\documentclass[11pt,paper=a4,]{article}
		\\usepackage{longtable}
		\\usepackage{pdflscape}
		\\begin{document}
		\\begin{landscape}
		\\noindent\\begin{longtable}{|l|l|l|l|l|l|l|}
		\hline
		Fic & Req & Div & Off & Cg & pivot & Cd \\\\
		\hline
		""")
		
	def traite(self,conc,pre=""):
		pl = conc.getLeftString(self.attaff)
		pv = conc.getPivotString(self.attaff)
		pr = conc.getRightString(self.attaff)
		res = re.sub("_","",conc.getDiv()[-1][0])
		res += "&"+"&".join([str(":".join([str(x) for x in conc.getOffsets()])),pl,pv,pr]) 
		self.ficout.write("&".join(["\\verb+"+x+"+" for x in pre])+"&"+res+"\\\\\n")
				
	def close(self):
		self.ficout.write("""
		\\end{longtable}
		\\end{landscape}
		\\end{document}\n
		""")
		pass
