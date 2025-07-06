#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

# création de l'instance
def createInstance(conf):
	return Grep(conf)


class Grep(object):
	def __init__(self,conf):
		self.att = conf["att"]
		self.position = ('00'+bin(int(conf["part"]))[2:])[-3:]
		self.compregexp = re.compile(conf["regexp"])
		
		
	def traite(self,conc):
		for i in range(0,3):
			if self.position[i] == '1':
				if self.verifPart(conc[i]):
					return True
		return False

	def verifPart(self,part):
		for elt in part:
			if self.att == 'f':
				if self.compregexp.search(elt[0]):
					return True
			else:
				for selt in part:
					for dicp in selt[1]:
						if self.compregexp.search(dicp[self.att]):
							return True
		return False


	def close(self):
		pass





