#!/usr/bin/env python3

import argparse
import sys
import glob
import os.path
import os

from .RequeteIndex import RequeteIndex as Requete
from .Post import Post
from .Index import  Index

# récupère des informations sur l'index

def main():
	# lecture paramètres
	parser = argparse.ArgumentParser(description="informations sur un index")
	parser.add_argument("-v", "--verbose", help="active affichage informations",action="store_true",default=False)
	parser.add_argument("-d", "--div", help="liste des id des balises <div>",action="store_true",default=False)
	parser.add_argument('-t', "--total",help='Affiche uniquement le total',action="store_true",default=False)
	parser.add_argument('-i', "--index", type=str, nargs='+',help='fichiers index')
	args = parser.parse_args()
	args = vars(args)


	verb = args['verbose']
	index = args['index']
	div = args["div"]
	total = args["total"]

	restotal = []
	nbrestotal = 0
	try:
		for f in index:
			idx = Index(f,"",verb)
			idx.lectureBase()
			if verb:
				sys.stderr.write('fin initialisation base\n')
			nbrestotal += idx.getMaxMot()
			if not total:
				print("nb\t"+f+"\t"+str(idx.getMaxMot()))
			if div:
				for elt in idx.getAllDiv(): 
					print("id\t"+f+"\t"+elt)
		print("nb\ttotal\t"+str(nbrestotal))
	except Exception as err:
		if err.args[0] == 24:
			print("Too many open files, try the '-l' option")
		else:
			raise
			print("Error !")






