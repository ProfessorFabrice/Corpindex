#!/usr/bin/env python3

import argparse
import sys
import glob
import os.path
import os
import pandas as pd
import re

# construire une matrice de coocurence
# pour un résultat d'une requête si la fenêtre est de x je prends x avant et x après
# dans cette fenêtre je regarde les bigrammes

# lecture paramètres
parser = argparse.ArgumentParser(description="interrogation d'un index (version 0.9)")
parser.add_argument("-v", "--verbose", help="active affichage informations",action="store_true",default=False)
parser.add_argument('-i', "--input", type=str, nargs='+',help='fichiers à index',required=True)
parser.add_argument("-q", "--query", type=str, help="requête(s) CQPL",required=True)
parser.add_argument('-s', "--seuil", type=float,help='seuil de coocurence',default=20.0)
parser.add_argument('-w', "--window", type=int,help='taille de la fenêtre',default=10)
parser.add_argument('-f', "--feature", type=str,help='trait de sortie',default="f")
parser.add_argument('-fr', "--filtreRe", type=str, nargs='+',help='filtre regexp',default=[])
parser.add_argument("-o", "--output", help="type de sortie",choices=['csv','std'],default="std")
args = parser.parse_args()
args = vars(args)

#print(args)
#exit(0)
index = args['input']
fenetre = args["window"]
verb = args["verbose"]
feature = args["feature"]
requete = args["query"]
output = args["output"]
seuil = args["seuil"]
filtreR = args["filtreRe"]
tabF = []
if len(filtreR) != 0:
	for elt in filtreR:		
		try:
			[t,regexp] = elt.split(":")
		except ValueError:
			sys.stderr.write("erreur dans les filtres\n")
			[t,regexp] =  ["",""]
		tabF.append([t,regexp])
	

base = os.path.dirname(os.path.abspath(__file__))+"/.."
sys.path.append(base+"/Corpindex")
sys.path.append(base+"/Corpindex/greffon")

from RequeteIndex import RequeteIndex as Requete
from Transduction import Transduction
from Index import Index
from Cquery import Cquery

# retourne vrai si le token correspond à la regexp
def appFiltre(tok):
	for elt in tabF:
		[t,regexp] = elt
		if t != "":
			if re.search(regexp,tok.getFeat(t)):
				return True
	return False
	
dicCooc = {}
for i in index:
	if verb:
		sys.stderr.write(f+'\n')
	cq = Cquery()
	cq.open(i)
	#  récupération des offset de la requête
	res = cq.cqpl(requete)
	for off in res:
		debut = max(off[0]-fenetre,1)
		fin = min(off[1]+fenetre,cq.getMaxWord())	
		w = [x for x in range(debut,fin)]
		for j in range(0,len(w)-1):
			if not appFiltre(cq.getToken(w[j])) and not appFiltre(cq.getToken(w[j+1])):
				c = cq.getToken(w[j]).getFeat(feature)+"\t"+cq.getToken(w[j+1]).getFeat(feature)
				if c not in dicCooc:
					dicCooc[c] = 0
				dicCooc[c] += 1

mat = {}
for elt in dicCooc:
	[m1,m2] = elt.split("\t")
	val = dicCooc[elt]
	if val>seuil:
		if m1 not in mat:
			mat[m1] = {}
		if m2 not in mat[m1]:
			mat[m1][m2] = 0
		mat[m1][m2] = val
	
df = pd.DataFrame(mat)
df = df.fillna(0)
if output == 'csv':
	df.to_csv("cooc"+requete+".csv",sep='\t')
else:
	print(df)
