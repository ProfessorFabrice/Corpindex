#!/usr/bin/env python3

import argparse
import sys
import glob
import os.path
import os
import random
import shutil

from .Cquery import Cquery
from .Token import Token
from .Index import Index

# modification d'un offset par rapport à des empans d'offsets et création d'un nouvel index

# iteration sur l'index et modification au besoin 
def iteraDoc(ind,dicoff,traits):
	off = 0
	conc = ""
	for tok in ind.getIndexTokens():
		if not tok.isDiv():
			off += 1
			if off in dicoff:
				conc = tok.getForme()
				traitsOrigs = tok.getAllFeat()
				for k in traits:
					traitsOrigs[k] = traits[k]
				tok = Token([conc,[traitsOrigs]])
				yield tok
			else:
				yield tok
		else:
			yield tok

def main():
	# lecture paramètres
	parser = argparse.ArgumentParser(description="modification de l'index")
	parser.add_argument("-v", "--verbose", help="active affichage informations",action="store_true",default=False)
	parser.add_argument("-db", "--database", help="type de bdd",default='bsd',choices=['bsd','dbm','dpy'])
	parser.add_argument('-i', "--index", type=str, help='fichier à modifier',required=True)
	parser.add_argument('-o', "--output", type=str,help='nom de la copie',default="")
	parser.add_argument('-O', "--offsets", type=str,help='fichier liste offset',default="")
	parser.add_argument('-p', "--python", type=str,help='code python',default="")
	parser.add_argument("-s", "--serializer", help="type de serializer",default='pickle',choices=['pickle','json','msgpack'])
	parser.add_argument('-t', "--traits",type=str, help="traits à ajouter (si 'concat') de la forma t1:v1_t2:v2",default="l:X_c:Z")
	args = parser.parse_args()
	args = vars(args)

	verb = args['verbose']
	index = args['index']
	out = args['output']
	python = args["python"]
	database = args['database']
	serializer = args["serializer"]
	ficoffsets = args["offsets"]
	traits = {x.split(":")[0]:x.split(":")[1] for x in args["traits"].split("_")}

	if python !="":
		sys.path.append(os.getcwd())
		import importlib
		XXX = importlib.import_module(python,"*")
	else:
		XXX = None

	# lecture du fichier d'empan et création d'un ensemble d'offsets à modifier
	dicoff = set()
	with open(ficoffsets) as fic:
		for ligne in fic:
			[deb,fin] = ligne.rstrip().split(":")
			for i in range(int(deb),int(fin)+1):
				dicoff.add(i)

	output = []
	if verb:
		sys.stderr.write(index+'\n')
	cq = Cquery()
	cq.open(index)
	rep = ""
	if out == "":
		out = os.path.dirname(index)+"/"+str(random.random())+".txt"
		bn = os.path.dirname(index)
		name = os.path.basename(index)
		rep = bn+"/"+str(random.random())
		os.mkdir(rep)
		out = rep+"/"+name
	cqn = Cquery()
	cqn.featureList = cq.featureList+['s','d','r','m','fm','o']
	nidx = cqn.createNewIndex(out)
	cptMot = nidx.indexation(iteraDoc(cq.defaultIdx,dicoff,traits),0)
	nidx.maxMot = cptMot
	cqn.saveNewIndex(nidx)
	if rep != "":
		shutil.rmtree(index+"_idx")
		shutil.move(out+"_idx",bn)
		shutil.rmtree(rep)
