#!/usr/bin/python3

##
# 2017
# Fabrice Issac
##
import re
import sys
import os
import argparse
import json
import timeit

# export en effectuant des transformations

# parameters
parser = argparse.ArgumentParser(description="interrogation d'un index")
parser.add_argument("-v", "--verbose", help="active affichage informations",action="store_true",default=False)
parser.add_argument('-i', "--index", type=str, nargs='+', help='fichiers index')
parser.add_argument('-n', "--newline", type=int, help='nombre de token par ligne',default=20)

args = parser.parse_args()
args = vars(args)

index = args['index']
verb = args["verbose"]
nlmax = args["newline"]


# path to library
sys.path.append(os.path.dirname(sys.argv[0])+"/../Corpindex")

from Index import Index
from Token import Token

def getMaxLevel(token):
	i = 0
	ml = -10
	tm = token.getFeatVal(0)
	while i<token.getNum():
		t = token.getFeatVal(i)
		if 'level' in t:
			if ml < int(t['level']):
				tm = t
				ml = int(t['level'])
		i += 1
	return Token([token.getForme(),[tm]])
				

startt = timeit.default_timer()
nl = 0
mm = False
for elt in index:
	if verb:
		sys.stderr.write(elt+"\n")
	idx = Index(elt,"")
	idx.lectureBase(startt)
	for tok in idx.getIndexTokens():
		if not tok.isDiv():
			nl += 1
			tok = getMaxLevel(tok)
			if tok.getForme() == "$":
				if not mm:
					print(" \\ensuremath{",end="")
				else:
					print("}",end=" ")
				mm = not mm
			else:
				print(tok.getForme(),end=" ")
			if nl == nlmax:
				nl = 0
				print()
				
				
				
				
				
				
				
				
