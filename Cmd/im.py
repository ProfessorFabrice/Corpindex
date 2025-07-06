#!/usr/bin/python3

import argparse
import sys
import glob
import os.path
import os
import math

# information mutuelle

# lecture paramètres
parser = argparse.ArgumentParser(description="interrogation d'un index ()information mutuelle)")
parser.add_argument("-v", "--verbose", help="active affichage informations",action="store_true",default=False)
parser.add_argument("-l", "--large", help="active le mode 'grand nombre de fichiers'",action="store_true",default=False)
parser.add_argument('-a', "--antidico", type=str, default="",help='anti dictionnaire')
parser.add_argument('-i', "--index", type=str, nargs='+',help='fichiers index')
parser.add_argument("-q", "--query", type=str, help="requête(s) CQPL",required=True)
parser.add_argument("-m", "--minfreq", type=int, help="fréquence minimal",default=2)
parser.add_argument("-3", "--trois", action="store_true", help="3 mots",default=False)
parser.add_argument("-s", "--stop", type=float, help="seuil d'arrêt",default=0.01)

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
minfreq = args["minfreq"]
anti = args["antidico"]
trois = args["trois"]
stop = args["stop"]

antidico = set()
if anti != "":
	antidico = set([x for x in open(anti).read().split("\n")])

cq = Cquery()
cq.dbMode = "bsd"
cq.verbose = verb
dicoC = {} # collocation
dicoM = {} # mots
total = 0
for f in index:
	cq.open(f)
	motsAFaire = {}
	for t in cq.cqpl(query):
		if feature != "f":
			mot1 = cq.getElement(t[0]).getFeat(feature)
			mot2 = cq.getElement(t[1]).getFeat(feature)
		else:
			mot1 = cq.getElement(t[0]).getForme()
			mot2 = cq.getElement(t[1]).getForme()
		if mot1 not in antidico and mot2 not in antidico:
			motsAFaire[mot1] = 1
			motsAFaire[mot2] = 1
			k = mot1+"\t"+mot2
			if k in dicoC:
				dicoC[k] += 1
			else:
				dicoC[k] = 1
	for m in motsAFaire:
		nbm = len(cq.cqpl('['+feature+'="'+m+'"]'))
		if m in dicoM:
			dicoM[m] += nbm
		else:
			dicoM[m] = nbm
	total += cq.getMaxWord()
	cq.close()
resultat = []
for elt in dicoC:
	[m1,m2] = elt.split("\t")
	pm1 = dicoM[m1]/total
	pm2 = dicoM[m2]/total
	pm1m2 = dicoC[elt]/total
	if dicoM[m1]>=minfreq and dicoM[m2]>=minfreq and dicoC[elt]>=minfreq:
		affiche = [math.log(pm1m2/(pm1*pm2)),dicoC[elt],m1,m2,math.log(pm1m2/(pm1*pm2))*dicoC[elt]]
		resultat.append(affiche)

resultat = sorted(resultat,key= lambda x:x[4],reverse=True)
sortie = []
prec = resultat[0][4]+stop*2
cpt = 0
for elt in resultat:
	if prec-elt[4]>stop or prec == elt[4]:
		cpt += 1
		sortie.append("\t".join([str(x) for x in elt]))
		prec = elt[4]
	else:
		break
print(cpt)
if not trois:
	for elt in sortie:
		print(elt)
else: # trois termes
	prec = {}
	succ = {}
	for elt in resultat[:cpt]:
		m1 = elt[1]
		m2 = elt[2]
		if m1 not in succ:
			succ[m1] = {}
		succ[m1][m2] = elt[6]
	for m in succ:
		for ms in succ[m]:
			if ms in succ:
				for mss in succ[ms]:
					me1 = succ[m][ms]
					me2 = succ[ms][mss]
					ratio = min(me1,me2)/max(me1,me2)
					if ratio>0.9:
						print(m,ms,mss,me1,me2)
