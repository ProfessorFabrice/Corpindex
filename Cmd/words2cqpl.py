#!/usr/bin/env python3

import sys
import argparse

# génération d'une requête CQPL

# parameters
parser = argparse.ArgumentParser(description="interrogation d'un index")
parser.add_argument("-v", "--verbose", help="active affichage informations",action="store_true",default=False)
parser.add_argument("-f", "--feature", help="type de traits",default='f',type=str, choices=['f','l','c','r','t'])
parser.add_argument("-i", "--insert", help="motif à insérer",default='',type=str)
parser.add_argument("-p", "--position", help="position du motif",default=-1,type=int)

args = parser.parse_args()
args = vars(args)

f = args["feature"]
ins = args["insert"]
pos = args["position"]

for elt in sys.stdin:
	tabW = list(map(lambda x: '['+f+'="'+x+'"]' ,elt.rstrip().split(" ")))
	if pos != -1 and ins != "":
		tabW.insert(pos,ins)
	res = "".join(tabW)
	print(res)
