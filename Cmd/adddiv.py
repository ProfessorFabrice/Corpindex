#!/usr/bin/python3

import argparse
import sys
import glob
import os.path
import os

# permet d'ajouter des divsision par rapport à des offet
# les divs à ajouter sont de la forme :
#	offset_depart_1<tab>offset_fin_1<tab>étiquette_1
#	offset_depart_2<tab>offset_fin_2<tab>étiquette_2
#	offset_depart_3<tab>offset_fin_3<tab>étiquette_3
#	...
# 
# l'index est transformé (on ne rajoute pas de token donc ok)
# ex:
#	echo -e "1 5\n15" |idxoffsets.py -i Textes/total.tex


# lecture paramètres
parser = argparse.ArgumentParser(description="modification de l'index par ajout de divisions")
parser.add_argument("-v", "--verbose", help="active affichage informations",action="store_true",default=False)
parser.add_argument("-db", "--database", help="type de bdd",default='bsd',choices=['bsd','dbm','dpy'])
parser.add_argument("-l", "--log", help="fichier de log",default="stderr",type=str)
parser.add_argument('-i', "--input", type=str, help='fichiers à index',required=True)
parser.add_argument('-fd', "--divs", type=str, help='fichiers de divisions',required=True)
args = parser.parse_args()
args = vars(args)

base = os.path.dirname(os.path.abspath(__file__))+"/.."
sys.path.append(base+"/Corpindex")
sys.path.append(base+"/Corpindex/greffon")

from Index import Index

verb = args['verbose']
input = args['input']
log = args["log"]
ficd = args["divs"]

if log == "stderr":
	ficlog = sys.stderr
elif log == "stdout":
	ficlog = sys.stdout
else:
	ficlog = open(log,"w")
trans = None

if verb:
	ficlog.write(input+'\n')
idx = Index(input,"",verb,ficlog)
idx.lectureBase()
lstd = []
with open(ficd) as fd:
	for elt in fd:
		try: 
			[s,e,t] = elt.rstrip().split("\t")
			lstd.append([int(s),int(e),t])
		except ValueError:
			ficlog.write("ERROR: "+elt.rstrip()+"\n")
idx.addDiv(lstd)
idx.closeBase()


