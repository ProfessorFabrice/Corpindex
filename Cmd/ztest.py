#!/usr/bin/python3

import argparse
import sys
import glob
import os.path
import os
import math

# ztest

# lecture paramètres
parser = argparse.ArgumentParser(description="interrogation d'un index (information mutuelle)\n MESURE\tFREQ\t")
parser.add_argument("-v", "--verbose", help="active affichage informations",action="store_true",default=False)
parser.add_argument("-l", "--large", help="active le mode 'grand nombre de fichiers'",action="store_true",default=False)
parser.add_argument('-a', "--antidico", type=str, default="",help='anti dictionnaire')
parser.add_argument('-i', "--index", type=str, nargs='+',help='fichiers index')
parser.add_argument("-q", "--query", type=str, help="requête(s) CQPL",required=True)
parser.add_argument("-f", "--feature", help="nature du trait",choices=['f','l','c','r','t'],default='f')

args = parser.parse_args()
args = vars(args)

base = os.path.dirname(os.path.abspath(__file__))+"/.."

sys.path.append(base+"/Corpindex")
sys.path.append(base+"/Corpindex/greffon")

from Cquery import *

verb = args['verbose']
index = args['index']
query = args['query'] 
feature = args["feature"]
anti = args["antidico"]

antidico = set()
if anti != "":
	antidico = set([x for x in open(anti).read().split("\n")])

cq = Cquery()
cq.dbMode = "bsd"
cq.verbose = verb
dicoC = {} # collocation
infos = {}
total = 0

# calcul du match et rangement dans un tableau assoc
def calc(index):
	for f in index:
		cq.open(f)
		motsAFaire = {}
		for t in cq.cqpl(query):
			if feature != "f":
				m1 = cq.getElement(t[0]).getFeat(feature)
				m2 = cq.getElement(t[1]).getFeat(feature)
			else:
				m1 = cq.getElement(t[0]).getForme()
				m2 = cq.getElement(t[1]).getForme()
			if m1 not in antidico and m2 not in antidico:
				if m1 not in dicoC:
					dicoC[m1] = {}
				if m2 not in dicoC[m1]:
					dicoC[m1][m2] = 1
				else:
					dicoC[m1][m2] += 1
	return dicoC

# calcul des fréquences
def calculfreqPred(dicoC):
	for m1 in dicoC:
		infos[m1] = {}
		somme = 0
		nbelt = 0
		for m2 in dicoC[m1]:
			somme = somme + dicoC[m1][m2]
		infos[m1]["somme"] = somme
		infos[m1]["nb"] = len(dicoC[m1])
		infos[m1]["moyenne"] = somme/infos[m1]["nb"]
	return infos

# calcul du z-test
def calculTest(dicoC,infos):
	res = []
	for m1 in dicoC:
		s1 = 0
		for m2 in dicoC[m1]:
			val = dicoC[m1][m2]
			diff = val - infos[m1]["moyenne"]
			s1 = s1 + diff*diff
		ecarttype = math.sqrt(s1/len(dicoC))
		#infos[m1]["ecarttype"] = ecarttype
		for m2 in dicoC[m1]:
			val = dicoC[m1][m2]
			if ecarttype != 0:
				mesure = (val - infos[m1]["moyenne"])/ecarttype
				freq = dicoC[m1][m2]
				res.append([mesure,freq,m1,m2,freq*mesure]) 
	return res
	
dic = calc(index)
inf = calculfreqPred(dic)
resultat = calculTest(dic,inf)
resultat = sorted(resultat,key=lambda x:x[4],reverse=True)
for elt in resultat:
	print("\t".join([str(x) for x in elt]))
