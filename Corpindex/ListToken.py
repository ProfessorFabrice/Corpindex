#!/usr/bin/python3

##
# 2014
# Fabrice Issac
# Classe ListToken
##
# gestion des affichages des concordances

import string
import re
import sys

from Token import Token

class ListToken(object):
	def __init__(self,lst):
		self.lstok = lst
		
	def __iter__(self):
		self.pos = 0
		return self

	def __next__(self):
		pos = self.pos
		if pos > len(self.lstok):
			raise StopIteration
		self.pos += 1
		return Token(self.lstok[pos])
