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
		\\usepackage{ulem}
		\\begin{document}
		\\newcommand{\Rac}[3]{\\ensuremath{\\sqrt{#2}}}
		\\newcommand{\Bar}[1]{\\ensuremath{\\bar{#1}}}
		\\newcommand{\Frac}[2]{\\ensuremath{\\frac{#1}{#2}}}
		\\newcommand{\Ensuremath}[1]{\\ensuremath{#1}}
		\\newcommand{\pb}{}
		\\begin{landscape}
		\\noindent\\begin{longtable}{|l|l|p{6cm}|l|p{6cm}|}
		\\hline
		Div & Off & Cg & pivot & Cd \\\\
		\\hline
		\\endhead
		\\hline
		\\endfoot

		""")
	
	def transforme(self,txt):
		txt = re.sub("\\\\bar","\\\\Bar",txt)
		txt = re.sub("\\\\frac","\\\\Frac",txt)
		txt = re.sub("\\\\ensuremath","\\\\Ensuremath",txt)
		txt = re.sub("\\\\[a-z]+\{[^}]*\}","",txt)
		txt = re.sub("\$","",txt)
		return txt
		
	def traite(self,conc,pre=""):
		pl = self.transforme(conc.getLeftString(self.attaff))
		pv = re.sub("\$","",conc.getPivotString(self.attaff))
		pr = self.transforme(conc.getRightString(self.attaff))
		res = re.sub("_","",conc.getDiv()[-1][0])
		res += "&"+"&".join([str(":".join([str(x) for x in conc.getOffsets()])),pl,pv,pr]) 
		#self.ficout.write("&".join(["\\verb+"+x+"+" for x in pre])+"&"+res+"\\\\\n")
		self.ficout.write(res+"\\\\\n")
				
	def close(self):
		self.ficout.write("""
		\\end{longtable}
		\\end{landscape}
		\\end{document}\n
		""")
		pass
