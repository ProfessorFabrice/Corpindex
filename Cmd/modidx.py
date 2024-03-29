#!/usr/bin/python3

import argparse
import sys
import glob
import os.path
import os

# lecture paramètres
parser = argparse.ArgumentParser(description="modification de l'index")
parser.add_argument("-v", "--verbose", help="active affichage informations",action="store_true",default=False)
parser.add_argument("-db", "--database", help="type de bdd",default='bsd',choices=['bsd','dbm','dpy'])
parser.add_argument("-lf", "--listfeature", help="liste de traits",default=['f','l','c'],type=str, nargs='+',choices=['f','l','c','r','p','d','s','m'])
parser.add_argument("-l", "--log", help="fichier de log",default="stderr",type=str)
parser.add_argument('-i', "--input", type=str, nargs='+',help='fichiers à index',required=True)
parser.add_argument('-o', "--output", type=str,help='nom de la copie',required=True)
parser.add_argument('-r', "--rules", type=str, nargs='+',help='fichiers de règles de transduction',required=True)
args = parser.parse_args()
args = vars(args)

base = os.path.dirname(os.path.abspath(__file__))+"/.."
sys.path.append(base+"/Corpindex")
sys.path.append(base+"/Corpindex/greffon")

from RequeteIndex import RequeteIndex as Requete
from Transduction import Transduction
from Index import Index

# ATTENTION ne marche pas !!! (changer l'index complètement et pas seulement le .document)

verb = args['verbose']
input = args['input']
output = args['output']
rules = args['rules'] 
listfeature = args['listfeature']
log = args["log"]
database = args['database']

if log == "stderr":
	ficlog = sys.stderr
elif log == "stdout":
	ficlog = sys.stdout
else:
	ficlog = open(log,"w")
trans = None
if rules:
	trans = Transduction()
	for elt in rules:
		if verb:
			ficlog.write(elt+"\n")
		if os.path.isfile(elt):
			for r in open(elt):
				if r[0] != "#":
					r = r.rstrip()
					if verb:
						ficlog.write('ajout de la règle : '+r+'\n')
					trans.addRules(r)
		else:
			if verb:
				ficlog.write("fichier inexistant\n")

for file in input:
	if verb:
		ficlog.write(file+'\n')
	idx = Index(file,"",verb,ficlog)
	idx.lectureBase()
	nidx = Index(output,database,verb,ficlog)
	nidx.initDB()
	nidx.initFicDocument()
	nidx.createBase(listfeature)
	nidx.indexTokenTrans(idx,trans)
	nidx.sauveBase()
	idx.closeBase()
	nidx.renameFicDocument()
	nidx.closeBase()
	nidx.createMeta()


