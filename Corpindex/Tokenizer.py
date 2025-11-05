#!/usr/bin/python3

##
# LDI 2008
# Fabrice Issac
# Classe Tokenize
##
# tokenization d'un texte
# le dictionnaire est de la fome :
#           forme<tab>lemme<tab>etiquette...

import sys
import os
import re
import codecs
import string

from ply import *
from .Dico import Dico
from .Token import Token
from .CorpException import *


class Tokenizer(object):
	def __init__(self,dicoMs,typeMs,dicoMc=[],verbose=False,ldict=None):
		self.verbose = verbose
		#self.dico = Dico(self.verbose)
		self.listeDicoMs = dicoMs
		self.typeMs = typeMs
		self.listeDicoMc = dicoMc
		self.lexer = None
		self.listeToken = []
		self.etiquettes = []
		self.lexer = lex.lex(object=self,reflags=re.UNICODE)
		#self.dictr = dict((ord(x), y) for (x, y) in zip('ABCDEFGHIJKLMNOPQRSTUVWXYZÂÀÉÈÊËÎÏÔÛÙÇ','abcdefghijklmnopqrstuvwxyzâàéèêëîïôûùç'))
		self.pileRes = []
		if ldict != None:
			self.dicoMs = ldict
		else:
			self.dicoMs = None
		self.dicoMc = {}
		self.pileBalise = []
		
	# List of token names.   This is always required
	tokens = (
		'ABREV',
		'MOT',
		'WOUV',
		'WFER',
		'ATT',
		'VAL1',
		'VAL2',
		'FORME',
		'DIVOUV',
		'BALOUV',
		'BALSTA',
		'DIVFER',
		'NUM',
		'PONCT_FAIBLE',
		'PONCT_FORT',
		'GUILLEMET',
		'OUVR',
		'FERM',
		'TIRET',
		'QUOT',
		'APOS',
		'SYM'
	)
	# définition du mot
	matchmot = {}
	langue = 'df' # par defaut
	#matchmot['df'] = r"[^-<> .!?,;:|({\[)}\]0-9_%'\"\n\t\r+/@»*°=&]+'?" 
	matchmot['df'] = r"[^-<> .!?,;:…|({\[)}\]_%'’\"\n\t\r+/«»*°=`“ㆍ‘” ‘’ⓒ~ €£$§]+[’']?" #' avec espace insécable
	

	
	def t_DIVOUV(self,t):
		r'<[^/][^>]* id *= *["\'][^>]*["\']>'
		reg = re.match('<[^/][^>]* id *= *.([^"\']+).',t.value)
		info = reg.group(1) #.decode('utf8')
		self.pileBalise.append(True)
		t.value = [[info]]
		#print("DIVOUV="+str(t.value)) #####
		return t
		
	def t_BALSTA(self,t):
		r'<[^/][^>]*/>'
		#print "DIVOUV="+t.value
		#print("BALISE STA "+t.value)####
		t.value = [t.value,[{'l':'TAG','c':'TAG'}]]
		#print(t)###
		return t
		
	def t_BALOUV(self,t):
		r'<[^/][^>]*>'
		#print "DIVOUV="+t.value
		#print("ELIMINATION BALISE "+t.value)####
		self.pileBalise.append(False)
		#t.value = [info]
		#return t
		
	def t_DIVFER(self,t):
		r'</[^>]*>'
		if len(self.pileBalise)>0:
			ferme = self.pileBalise.pop(-1)
		else:
			raise XmlError("Balance tag error "+t.value)
		if ferme:
			t.value = ['/']
			return t

	#def t_NUMMA(self,t):
	#	r'\.[0-9]+\.'
	#	t.value = [t.value,[{'l':'0','c':'1'}]]
	#	return t

	def t_NUM(self,t):
		r'[-+.]?[0-9]+\.?'
		t.value = [t.value,[{'l':'0','c':'0'}]]
		return t

		
	def t_PONCT_FORT(self,t):
		r'(\.\.)?[.!?:;]|¿|¡'
		#r'(\.\.)?[.!?;:]|…'
		t.value = [t.value,[{'l':t.value,'c':'Fs'}]]
		return t

	def t_PONCT_FAIBLE(self,t):
		r','
		t.value = [t.value,[{'l':t.value,'c':'Fw'}]]
		return t
		
	def t_OUVR(self,t):
		r'[({\[]|«'
		#r'[({\[]|«'
		t.value = [t.value,[{'l':t.value,'c':'Fo'}]]
		return t
		
	def t_FERM(self,t):
		r'[)}\]]|»'
		#r'[)}\]]'
		t.value = [t.value,[{'l':t.value,'c':'Fc'}]]
		return t
		
	#def t_NUM(self,t):
	#	r'[-+]?\d+'
	#	#r'[-+]?\d+([\.,]\d+)?'
	#	t.value = [t.value,[{'l':'0','c':'0'}]]
	#	return t
				
				
	def t_TIRET(self,t):
		r'[-—_]'
		t.value = [t.value,[{'l':'-','c':'Ft'}]]
		return t
		
	def t_APOS(self,t):
		r"[`'’]"
		t.value = ["'",[{'l':"'",'c':'Fq'}]]
		return t
		
	#def t_QUOT(self,t):
	#	r"'"
	#	t.value = [t.value,[{'l':"'",'c':'Fq'}]]
	#	return t
		
	def t_GUILLEMET(self,t):
		r'"'
		t.value = ['"',[{'l':'"','c':'Fg'}]]
		return t
		
	def t_SYM(self,t):
		r"[%\+*/&|=@$§]"
		t.value = [t.value,[{'l':t.value,'c':'Fy'}]]
		return t
		
	# reconnaissance des mots
	def t_MOT(self,t):
		mot = t.value
		listeInfos = self.dicoMs.get(mot)
		motmin = mot.lower()
		if motmin != mot:
			listeInfos = self.dicoMs.get(motmin) + listeInfos 
		t.value = [t.value,listeInfos]
		return t

	t_MOT.__doc__ = matchmot[langue]
		
	# A string containing ignored characters (spaces and tabs)
	t_ignore  = ' \t\n\r\f\v'
	
	def t_error(self,t):
		#sys.stderr.write("Illegal character '%s'\n" % t.value[0])
		#sys.stderr.write("Illegal character '%s'" % t.value[0])
		#sys.stderr.write(" dans '%s'\n" % t.value)
		t.lexer.skip(1)
		
	# entree de la chaine a analyser
	def init(self,texte,preproc=None):
		#self.lexer.input(texte.lower())
		if preproc:
			for elt in preproc:
				[regexp,motif] = elt
				#if re.search(regexp,texte):
				#	print(texte)
				texte = re.sub(regexp,motif,texte)
		self.lexer.input(texte)
		self.texte = texte
	
	# recuperation du token suivant
	def getNextToken(self):
		tok = self.lexer.token()
		#print("gnt1 "+str(tok))###
		if not tok:
			#raise Exception("oups : "+self.texte) 
			raise TokError("oups : "+self.texte) 
		#print("gnt2 "+str(tok))
		return tok
	
	# recuperation dans un tableau de tous les tokens
	# ATTENTION pour les UPL ne marche pas si les tokens ne sont pas dans la même chaîne (pileLoc est remis à [])
	# pas génial !!!
	def calcTokens(self):
		forme=""
		infos = ""
		self.pileRes = []
		pileLoc = []
		dic = self.dicoMc.getDictCw() # initialisation dictionnaire des UPL
		lectNouv = True # 
		upl = False # pour savoir si on est en train de lire une UPL
		nt = None
		while True:
			try:
				if lectNouv: # booléen pour gérer le cas ou le début d'une UPL est reconnu puis ne l'est plus (il faut retraiter le token courant)
					nt = self.getNextToken() # récupération du token suivant
				lectNouv = True # sauf contre indication on lira un token
				forme = nt.value[0]
				#print(nt)
				if len(nt.value) != 1: # c'est un mot
					infos = nt.value[1] # listes informations
					#clef = forme.translate(self.dictr) # par defaut la clef est la forme
					clef = forme.lower()
					#print(clef,forme)
					if (clef in dic): # si appartient à UPL
						upl = True
						pileLoc.append([forme,infos])
						infupl = dic[clef][0]
						dic = dic[clef][1]
						if len(dic)==0: # fin de mot
							infupl[0]['level'] = '0'
							self.pileRes.append([self.depileMots(pileLoc),infupl])
							nt = None
							#print("---sortie1--->",self.pileRes[-1])
							pileLoc = []
							dic = self.dicoMc.getDictCw()
					else: # n'est pas un élément d'une UPL
						upl = False
						#print("PileLoc",pileLoc)
						for elt in pileLoc:
							#print("---sortie2--->",elt)
							self.pileRes.append(elt)
						if len(pileLoc) != 0: # UPL en cours de lecture il faut reverifier que le token courant n'est pas dans une UPL
							pileLoc = []
							dic = self.dicoMc.getDictCw()
							lectNouv = False # force à rerevérifier en bloquant la lecture d'un nouveau token
						else: # on ajoute à la sortie 
							self.pileRes.append([forme,infos])
							nt = None
							#print("---sortie3--->",[forme,infos])
				else: # une balise
					self.pileRes.append([forme])
					nt = None
					#print("---sortie4--->",[forme])
			except TokError as e:
				break
		#print(upl)
		#print("upl",upl,"pileLoc",pileLoc,"reste",forme,infos)
		#print(self.pileRes)
		if upl: # il reste des tokens dans pileLoc
			for elt in pileLoc:
				self.pileRes.append(elt)
				#print("---sortie fin--->",elt)
		#print("----->",self.pileRes)
		return [Token(x) for x in self.pileRes]

	
	# depile une pile de mot pour former un mot compose
	def depileMots(self,pile):
		forme = " ".join([x[0] for x in pile])
		forme = re.sub(" - ","-",forme)
		return forme
		
	# lecture du dictionnaire des mots simples
	def readMs(self,force=False):
		if self.dicoMs == None or force:
			self.dicoMs = Dico(self.verbose)
			self.dicoMs.load(self.listeDicoMs,self.typeMs)
				
	# lecture du dictionnaire des mots composés
	def readMc(self):
		self.dicoMc = Dico(self.verbose)
		self.dicoMc.load(self.listeDicoMc,"dicomc")
					

if __name__ == '__main__':
	t = Tokenizer([],"",[])
	t.readMs()
	t.readMc()
	while True:
		print(">",end="")
		x = input()
		t.init(x)
		for tok in t.calcTokens():
			print(tok.getLowStruct())

