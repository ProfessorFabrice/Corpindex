#!/usr/bin/python3

import argparse
import sys
import glob
import os.path
import os

# lecture paramètres
parser = argparse.ArgumentParser(description="interrogation d'un index")
parser.add_argument("-v", "--verbose", help="active affichage informations",action="store_true",default=False)
parser.add_argument("-l", "--large", help="active le mode 'grand nombre de fichiers'",action="store_true",default=False)
parser.add_argument('-i', "--index", type=str, nargs='+',help='fichiers index')
parser.add_argument("-q", "--query", type=str, nargs='+', help="requête(s) CQPL/nom d'un fichier",required=True)
parser.add_argument("-w", "--word", help="recherche de la forme", action="store_true",default=False)
parser.add_argument("-c", "--calc", help="uniquement calcul de la taille du résultat", action="store_true",default=False)
parser.add_argument("-o", "--output", help="type de sortie",default="txt",choices=['txt','txtmax',"cqpl","latex","chuquet"])
parser.add_argument("-r", "--range", help="taille du contexte",default=5,type=int)
parser.add_argument("-f", "--feature",type=str, nargs='+', help="nature du trait",default=['f'])
parser.add_argument("-pt", "--typepost", help="nature du post traitement",choices=['out','proc','procout'],default='out')
parser.add_argument("-pp", "--postparam", help="paramètres supplémentaires pour le post traitement", type=str, nargs='+')
args = parser.parse_args()
args = vars(args)

#base = os.path.dirname(os.path.abspath(__file__))+"/.."

#sys.path.append(base+"/Corpindex")
#sys.path.append(base+"/Corpindex/greffon")

from Corpindex import RequeteIndex as Requete
from Corpindex import Post
from Corpindex import Index

verb = args['verbose']
index = args['index']
range = args['range']
output = args['output']
word = args["word"]
calc = args["calc"]
if len(args["query"])==1 and os.path.isfile(args["query"][0]):
	if word:
		query = ['[f="'+x.rstrip()+'"]' for x in open(args["query"][0]) if x[0] != "#"]	
	else:
		query = [x.rstrip() for x in open(args["query"][0]) if x[0] != "#"]
else:
	query = args['query'] 
large = args['large']
feature = args["feature"]
typepost = args["typepost"]
lstparam = args["postparam"]

req = Requete()
restotal = []
nbrestotal = 0

try:
	for f in index:
		if verb:
			sys.stderr.write(f+'\n')
		idx = Index(f,"",verb)
		idx.lectureBase()
		if verb:
			sys.stderr.write('fin initialisation base\n')
		nbq = 0
		for q in query:
			q += " " # sentinelle
			nbq += 1
			if q[0]!=" " and q[0] != "#":
				req.putIndex(idx)
				req.putRequete(q)
				if verb:
					vq = req.analyseurCqp.requete # 'vrai' requête
					sys.stderr.write("Requête "+str(nbq)+": "+q+" ("+vq+")\n")
				res = req.calculRequete()
				nbrestotal += len(res)
				q = q.rstrip()
				if verb:
					sys.stderr.write('resultat : '+str(len(res))+'\n')
				restotal.append([idx,res,q])
		if large:
			idx.close()
	if not calc:
		if verb:
			sys.stderr.write('Calcul concordances... \n')
		tabconc = []
		tabinfo = []
		nbres = len(restotal)
		for elt in restotal:
			[idx,res,ident] = elt
			if large:
				idx.lectureBase()
			tabinfo.append([os.path.basename(idx.getName()),ident])
			info = len(tabinfo) - 1
			for pos in idx.getTabConc(res,range,-1):
				tabconc.append([info,pos])
			if large:
				idx.close()
		if verb:
			sys.stderr.write('Filtres... \n')
		params = {'att': feature, 'type':typepost, 'id': '1', 'value': '', 'name': 'ci_'+output}
		if lstparam:
			for p in lstparam:
				[c,v] = p.split(":")
				params[c] = v
		post = Post(params,tabconc,tabinfo)
		post.process()
		tabconc = post.getConc()
	else:
		print(nbrestotal)
except Exception as err:
	if err.args[0] == 24:
		print("Too many open files, try the '-l' option")
	else:
		raise
		print("Error !")






