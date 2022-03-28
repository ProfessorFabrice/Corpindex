#!/usr/bin/python3

import re
import sys

# création de l'instance
def createInstance(conf):
	return Sep(conf)


class Sep(object):
	def __init__(self,conf):
		if conf["value"] != "":
			self.ficout = open(conf["value"] ,"w",encoding="UTF-8")
		else:
			self.ficout = sys.stdout
		self.txt = conf["txt"]
		
		
	def traite(self,conc,pre):
		pass


	def close(self):
		self.ficout.write("\n"+self.txt+"\n\n")
		if self.ficout != sys.stdout:
			self.ficout.close()
		





