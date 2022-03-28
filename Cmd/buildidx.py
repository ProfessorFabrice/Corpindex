#!/usr/bin/python3

import argparse
import sys
import glob
import os.path
import os

# lecture paramètres
parser = argparse.ArgumentParser(description="interrogation d'un index (version 0.9)")
parser.add_argument("-v", "--verbose", help="active affichage informations",action="store_true",default=False)
parser.add_argument("-x", "--xml", help="fichier déjà étiqueté",action="store_true",default=False)
parser.add_argument("-db", "--database", help="type de bdd",default='bsd',choices=['bsd','dbm','dpy'])
parser.add_argument("-lf", "--listfeature", help="liste de traits",default=['f','l','c','d','m','q'],type=str, nargs='+')
parser.add_argument("-l", "--log", help="fichier de log",default="stderr",type=str)
parser.add_argument("-d", "--dicts", type=str, nargs='+',help="dictionaries simple words",default=[],required=False)
parser.add_argument("-dc", "--dictc", type=str, nargs='+',help="dictionaries compound words",default=[],required=False)
parser.add_argument('-i', "--input", type=str, nargs='+',help='fichiers à index',required=True)
parser.add_argument('-f', "--filtre", help='filtre sur "level"',action="store_true",default=False)
parser.add_argument('-r', "--rules", type=str, nargs='+',help='fichiers de règles de transduction')
args = parser.parse_args()
args = vars(args)

#print(args)
#exit(0)

base = os.path.dirname(os.path.abspath(__file__))+"/.."
#base = "/home/fabrice/Developpe/Corpindex"
sys.path.append(base+"/Corpindex")
sys.path.append(base+"/Corpindex/greffon")

from RequeteIndex import RequeteIndex as Requete
from Transduction import Transduction
from Index import Index

verb = args['verbose']
input = args['input']
xml = args['xml']
database = args['database']
dicts = args['dicts'] 
dictc = args['dictc']
rules = args['rules'] 
filtre = args['filtre'] 
listfeature = args['listfeature']
log = args["log"]

if dicts==None and not xml:
	parser.print_help()
	print("buildidx.py: error: the following arguments are required: -d/--dicts")
	exit(0)

if log == "stderr":
	ficlog = sys.stderr
elif log == "stdout":
	ficlog = sys.stdout
else:
	ficlog = open(log,"w")
trans = None
if rules:
	trans = Transduction(verb=verb)
	for elt in rules:
		if verb:
			ficlog.write(elt+"\n")
		if os.path.isfile(elt):
			for r in open(elt):
				if r!= "":
					if r[0] != "#":
						r = r.rstrip()
						if verb:
							ficlog.write('ajout de la règle : '+r+'\n')
						trans.addRules(r)
		else:
			if verb:
				ficlog.write("fichier inexistant\n")
ficlog.write("fin lectures règles\n")
for file in input:
	if verb:
		ficlog.write(file+'\n')
	idx = Index(file,database,verb,ficlog)
	idx.initDB()
	idx.initFicDocument()
	idx.createBase(listfeature)
	if not xml:
		idx.initTokenizer('txt',dicts,'dico',dictc)
	else:
		idx.initTokenizer('xml','')
	idx.indexTexte(trans,filtre)
	idx.sauveBase()
	idx.renameFicDocument()
	idx.closeBase()
	idx.createMeta()

