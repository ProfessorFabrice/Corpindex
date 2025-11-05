#!/usr/bin/python3

##
# LDI 2014
# Fabrice Issac
# Classe Tokxml
##
# lecture d'un fichier xml deja tokenize de la forme
#  A REVOIR !!!
# <corpus>
# <text>
# ...
# <div id="">
# <tok>
#	<infos>
#		 <item c="A--fs" l="un"/>
#		 <item c="Difs--" l="un"/>
#		 <item c="N-fs" l="une"/>
#		 <item c="Pifs--" l="un"/> 
#	</infos>
#	<w>une</w>
# </tok>
# ...
# </div>
# ...
# </text>
# </corpus>
# Attention : du fait de PLY il ne faut pas couper les balises ouvrantes et fermantes

import sys
import os
import re
import io

sys.path.append("Corpindex")

from ply import *
from .Token import Token

class Tokxml(object):
	def __init__(self):
		self.lex = None
		self.text = ""
		# a garder pour debug
		self.debugl = False
		self.debugp = 0	
		# Build the lexer and parser
		self.lex = lex.lex(module=self, debug=self.debugl)
		yacc.yacc(module=self
			,debug=self.debugp
			#,debugfile=self.debugfile,
			#,tabmodule=".parsetab.py"
			)
		
	def init(self,text,preproc=None):
		self.text = text
		
	def calcTokens(self):
		res = yacc.parse(self.text)
		if res == None:
			print("------->"+self.text)
			res = []
		tres = [Token(x) for x in res]
		return tres
	
	def lexi(self,ligne):
		self.lex.input(ligne)
		while True:
			tok = self.lex.token()
			if not tok: break      # No more input
			print(tok)
	
	# etats
	states = (
			('item','exclusive'),
			('valeur','exclusive')
		)
	
	# List of token names.   This is always required
	tokens = (
		'TXTO',
		'TXTC',
		'INFOSO',
		'INFOSC',
		'TOKO',
		'TOKC',
		'DIVO',
		'DIVC',
		'WORD',
		'ITO',
		'ITC',
		'ATT',
		'VAL'
	)
	# litteraux
	
	t_TXTO	= r"<[Tt][Ee][Xx][Tt]>"
	t_TXTC	= r"</[Tt][Ee][Xx][Tt]>"
	t_INFOSO	= r"<[Ii][Nn][Ff][Oo][Ss]>"
	t_INFOSC	= r"</[Ii][Nn][Ff][Oo][Ss]>"
	t_TOKO	= r"<[Tt][oO][kK]>"
	t_TOKC	= r"</[Tt][oO][kK]>"
	t_DIVC	= r"</[dD][iI][vV]>"
		
	# methodes
	
	def t_DIVO(self,t):
		r'<[dD][iI][Vv].[iI][dD]=".*?">'
		t.value = t.value[9:-2]
		return t
	
	def t_ITO(self,t):
		r"<[Ii][Tt][Ee][Mm]"
		t.lexer.begin('item')
		return t
		
	def t_item_ATT(self,t):
		r"[a-z]+"
		return t
	
	def t_item_EGAL(self,t):
		r'="'
		t.lexer.begin('valeur')
		pass
	
	def t_valeur_VAL(self,t):
		r'[^"]+"'
		t.value = t.value[:-1]
		t.lexer.begin('item')
		return t
	
	
	def t_item_ITC(self,t):
		r'/>'
		t.lexer.begin('INITIAL')
		return t
		
	def t_WORD(self,t):
		r"<[wW]>[^<]*</[wW]>"
		t.value = t.value[3:-4]
		return t
		
			
    # A string containing ignored characters (spaces and tabs)
	t_item_ignore  = ' \t\n\r\f\v'
	t_valeur_ignore  = ' \t\n\r\f\v'
	t_ignore  = ' \t\n\r\f\v'
	
	# erreur
	def t_valeur_error(self,t):
		sys.stderr.write("(valeur) Illegal character '%s'\n" % t.value[0])
		t.lexer.skip(1)
				
	def t_item_error(self,t):
		sys.stderr.write("(item) Illegal character '%s'\n" % t.value[0])
		t.lexer.skip(1)
				
	def t_error(self,t):
		sys.stderr.write("(gene) Illegal character '%s'\n" % t.value[0])
		sys.stderr.write(" error--->"+t.value)
		t.lexer.skip(1)
	
	# parser
		
	def p_text(self,p):
		'''
		text : TXTO lsttok TXTC
				| lsttok
		'''
		if len(p)==3:
			p[0] = p[2]
		else:
			p[0] = p[1]
		
	def p_lsttok(self,p):
		'''
		lsttok : tok lsttok 
				| DIVO lsttok DIVC lsttok
				|
		'''
		if len(p) == 3:
			p[0] = p[1] + p[2]
		elif len(p) == 5:
			p[0] = [[[p[1]]]] + p[2] + [['/']] + p[4]
		else:
			p[0] = []


	def p_tok(self,p):
		'''
		tok : TOKO infos WORD TOKC
		'''
		p[0]=[[p[3],p[2]]]
		self.tinfos = {}
		self.word = ""
		self.lstinfos = []
		
	def p_infos(self,p):
		'''
		infos : INFOSO lstitems INFOSC
		'''
		p[0] = p[2]
			
	def p_lstitems(self,p):
		'''
		lstitems : items lstitems
				| 
		'''
		if len(p) == 3:
			p[0] = p[1] + p[2]
		else:
			p[0] = []
		
	def p_items(self,p):
		'''
		items : ITO lstattval ITC
		'''
		p[0] = [p[2]]
		
	def p_lstattval(self,p):
		'''
		lstattval : attval lstattval
				| 
		'''
		if len(p) == 3:
			p[2][p[1][0]] = p[1][1]
			p[0] = p[2]
		else:
			p[0] = {}

	
			
	def p_attval(self,p):
		'''
		attval : ATT VAL
		'''
		p[0] = [p[1],p[2]]

		
	def p_error(self, p):
		try:
			sys.stderr.write("Syntax error at '%s'\n" % p.value)
		except:
			pass
		tok = yacc.token()
		sys.stderr.write(str(tok))

if __name__ == '__main__':
	tx = Tokxml()
	for elt in open(sys.argv[1]):
		tx.init(elt)
		res = tx.calcTokens()
		for t in res:
			print(t.getLowStruct())
	#print(tx.parse("""
	#<corpus>
	#<text>
	#<tok>
	#<infos>
		 #<item c="Da---i" l="de"/> <item c="Di----" l="de"/> <item c="Sp" l="de"/> 
	#</infos>
	#<w>d'</w>
#</tok>
#<div id="milieu">
#<tok>
	#<infos>
		 #<item c="A--fs" l="un"/> <item c="Difs--" l="un"/> <item c="N-fs" l="une"/> <item c="Pifs--" l="un"/> 
	#</infos>
	#<w>une</w>
#</tok>
#</div>
#<tok>
	#<infos>
		 #<item c="A--fs" l="profond"/> <item c="N-fs" l="profonde"/> 
	#</infos>
	#<w>profonde</w>
#</tok>
#</text>
#</corpus>
	#"""))
