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

# parameters
parser = argparse.ArgumentParser(description="interrogation d'un index")
parser.add_argument("-v", "--verbose", help="active affichage informations",action="store_true",default=False)
parser.add_argument("-n", "--nosep", help="résultat sur une seule ligne",action="store_true",default=False)
parser.add_argument("-d", "--div", help="affichage des div",action="store_true",default=False)
parser.add_argument("-l", "--level", help="ne retient que les traits avec le level le plus élevé",action="store_true",default=False)
parser.add_argument("-o", "--output", help="type de sortie",default="txt",choices=['txt','xml','json','dico','brut','txtsep'])
parser.add_argument('-i', "--index", type=str, nargs='+', help='fichiers index')
parser.add_argument("-f", "--feature",type=str, nargs='+', help="nature des traits",default='f')
parser.add_argument('-ident', "--identifiant", help='identifiant',default = "")
args = parser.parse_args()
args = vars(args)

index = args['index']
output = args['output']
ident = args['identifiant']
verb = args["verbose"]
nosep = args["nosep"]
feature = args["feature"]
divAff = args["div"]
level = args["level"]
tabul = '\t'
nl = '\n'
if nosep:
	tabul = ''
	nl = ''

divs = []

# path to library
sys.path.append(os.path.dirname(sys.argv[0])+"/../Corpindex")

from Index import Index
from Token import Token

def getMaxLevel(token):
	i = 0
	ml = -10
	tm = token.getFeatVal(0)
	while i<token.getNum():
		t = token.getFeatVal(i)
		if 'level' in t:
			if ml < int(t['level']):
				tm = t
				ml = int(t['level'])
		i += 1
	return Token([token.getForme(),[tm]])
				


for elt in index:
	if verb:
		sys.stderr.write(elt)
	idx = Index(elt,"")
	idx.lectureBase()
	op = ""
	div = ""
	if output == "xml":
		print("<text>",end=nl)
		if ident != "":
			print('<div id="'+ident+'">',end=nl)
	elif output == "json":
		print("[")
	for tok in idx.getIndexTokens():
		#print(tok.getLowStruct())
		if level and not tok.isDiv():
			tok = getMaxLevel(tok)
		if output == "json":
			print(tok.getJson(),",",end=nl)
		elif output[:3] == "txt":
			if tok.isDiv() and divAff:
				div = tok.getDiv()
				if div == "/":
					op += "</div>\n"
				else:
					op += '<div id=\"'+tok.getDiv()+'">\n'
			else:
				op += tok.getFeat(feature[0])+" "
			if tok.getFeat("f") in [".",";","?","!"]:
				if len(output)==3:
					op = re.sub(" ([,.])","\\1",op)
					op = re.sub("(') ","\\1",op)
				op = re.sub(" - ","-",op)
				print(op,end=nl)
				op = ""
		elif output == "xml":
			if tok.isDiv(): 
				if divAff:
					div = tok.getDiv()
					if div == "/":
						print("</div>",end=nl)
					else:
						print('<div id=\"'+tok.getDiv()+'">',end=nl)
			else:
				print("<tok>"+nl+tabul+"<infos>",end=nl)
				for i in range(0,tok.getNum()):
					print(tabul*2+"<item ",end="")
					print(" ".join([att+'="'+tok.getFeat(att,i)+'"' if tok.getFeat(att,i)!='"' else att+"=\"''\"" for att in tok.getLstFeat(i)]),end="")
					print("/>",end=nl)
				print(tabul+"</infos>"+nl+tabul+"<w>"+tok.getForme()+"</w>",end=nl)
				print("</tok>",end=nl)
		elif output == "dico":
			if tok.isDiv() and divAff:
				div = tok.getDiv()
				print("---------->",div)
				if div == "/":
					divs.pop()
				else:
					divs.append(div)
			else:
				if divAff:
					print(":".join(divs)+"\t",end="")
				print("\t".join([tok.getFeat(x) for x in feature]))
				#print(div+"\t".join([tok.getFeat(x) for x in tok.getLstFeat()]))
				#print(div+"\t".join([tok.getFeat("f"),tok.getFeat("l"),tok.getFeat("c")]))
		else:
			tokenBrut = tok.getLowStruct()
			if len(tokenBrut)>1:
				print(len(tokenBrut[1]),tokenBrut)
			else:
				print(0,tokenBrut)
	if output == "xml":
		if ident != "":
			print("</div>",end=nl)
		print("</text>")
	elif output == "json":
		print('["FIN"]\n]')
if op !="": # reliquat version txt
	print(op,end=nl)

