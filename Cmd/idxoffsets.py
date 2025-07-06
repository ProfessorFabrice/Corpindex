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

# retourne des tokens par rapport à une liste d'offsets
# le format d'entrée des offsets est de la forme :
# 	offset1
#	offset2
#	...
# ou
#	offset_debut_1 offset_fin_1
#	offset_debut_2 offset_fin_2
#	...
# dans le premier cas on affiche uniquement le token de l'offset, dans le deuxième cas on affiche l'empan

# parameters
parser = argparse.ArgumentParser(description="interrogation d'un index")
parser.add_argument("-v", "--verbose", help="active affichage informations",action="store_true",default=False)
parser.add_argument('-d', "--dec", type=int, help='décalage',default=0)
parser.add_argument('-i', "--index", type=str, help='fichiers index')
parser.add_argument("-lf", "--listfeature", help="liste de traits",default=['f'],type=str, nargs='+',choices=['f','l','c','r','t'])

args = parser.parse_args()
args = vars(args)

index = args['index']
verb = args["verbose"]
dec = args["dec"]
listfeature = args['listfeature']

# path to library
sys.path.append(os.path.dirname(sys.argv[0])+"/../Corpindex")

from Index import Index

if verb:
	sys.stderr.write(index)

idx = Index(index,"")
idx.lectureBase()
for ligne in sys.stdin:
	lstoff = ligne.rstrip().replace("\t"," ").split(" ")
	if len(lstoff)>1:
		lstoff = [int(x) for x in range(int(lstoff[0]),int(lstoff[-1])+1)]
	else:
		lstoff[0] = int(lstoff[0])
	res = []
	for o in lstoff:
		t = idx.getElement(int(o)+dec)
		resf = []
		for f in listfeature:
			if f == "f":
				resf.append(t[0])
			else:
				if f in t[1][0]:
					resf.append(t[1][0][f])
				else:
					resf.append("~")
		res.append("\t".join(resf))
	print("\t".join(res))

