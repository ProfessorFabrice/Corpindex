#!/usr/bin/python3

import re
import sys
import os

from .Index import Index
from .RequeteIndex import RequeteIndex as Requete
from .Post import Post
from .Transduction import Transduction
from .Cqpl import Cqpl
from .Token import Token
# a wrapper to corpindex library

class Cquery(object):
	def __init__(self):
		self.verbose = False
		self.dbMode = "bsd"
		self.featureList = ['f', 'l', 'c']
		self.dicts = []
		self.dictc = []
		self.trans = None
		self.defaultIdx = None
		self.filename = ""
		
	# read configuration file (.cquery.conf)
	# pas implémenté
	def readConfiguration(self):
		if os.path.isfile(".cquery.conf"):
			for elt in open(".cquery.conf"):
				if elt[0] != "#":
					t = elt.rstrip().split("=")
					if t[0] == "dbMode":
						self.dbMode = t[1]
					elif t[0] == "featureList":
						self.featureList = t[1].split(",")
					elif t[0] == "dicts":
						self.dicts.append(t[1])
					elif t[0] == "dictc":
						self.dictc.append(t[1])
					else:
						print("configuration file error")
		
	# open index from filename, create if not exist 
	#   filename : filename path
	#   mode : "f" (force create), "c" (create if note exist) (default)
	def open(self,filename,mode="c",ldict=None):
		if not os.path.isfile(filename):
			sys.stderr.write(filename+" : file doesn't exist\n")
			exit(0)
		else:
			self.filename = filename
			idx = Index(filename,self.dbMode,self.verbose)
			if not os.path.exists(filename+"_idx") or mode == "f": # create index if not exist or force creation
				idx.initDB()
				idx.initFicDocument()
				idx.createBase(self.featureList)
				idx.initTokenizer('txt',self.dicts,'dico',self.dictc,ldict=ldict)
				idx.indexTexte(self.trans)
				idx.sauveBase()
				idx.renameFicDocument()
				idx.closeBase()
				idx.createMeta()
			idx.lectureBase()
		self.defaultIdx = idx
	
	# create a new directory index
	#   filename : filename path
	def createNewIndex(self,filename):
		open(filename,"w").close()
		idx = Index(filename,self.dbMode,self.verbose)
		idx.initDB()
		idx.initFicDocument()
		idx.createBase(self.featureList)
		return idx
	
	# save opened index
	#   filename : filename path
	def saveNewIndex(self,idx):
		idx.sauveBase()
		idx.renameFicDocument()
		idx.closeBase()
		idx.createMeta()
	
	# apply transduction rules on the index
	#	transTabFiles : a list of rules files		
	def reindex(self,transTabFiles):
		self.setTransduction(transTabFiles)
		nidx = Index(self.filename,self.dbMode,self.verbose)
		nidx.initFicDocument()
		nidx.createBase(self.featureList)
		nidx.indexTokenTrans(self.defaultIdx,self.trans)
		nidx.sauveBase()
		self.close()
		nidx.renameFicDocument()
		nidx.closeBase()
		nidx.createMeta()
		self.open(self.filename)
	
	# apply dictionary on the index
	#	dicts : an array of dictionaries		
	def reindexDico(self,dicts):
		nidx = Index(self.filename,self.dbMode,self.verbose)
		nidx.initFicDocument()
		nidx.createBase(self.featureList)
		if self.verbose:
			sys.stderr.write("\n".join(dicts)+"\n")
		nidx.indexTokenDico(self.defaultIdx,dicts)
		nidx.sauveBase()
		self.close()
		nidx.renameFicDocument()
		nidx.closeBase()
		nidx.createMeta()
		self.open(self.filename)
	
	# close default index	
	def close(self):
		self.defaultIdx.close()

	# test Cqpl request
	#    cqplRequest : cqpl request
	#  return
	#    True if the request is syntacticaly correct False otherwise
	def testCqpl(self,cqplRequest,err=True):
		resultat = False
		cq = Cqpl(err)
		try:
			cq.putRequete(cqplRequest)
			if len(cq.creationArbre())>0:
				resultat = True
		except:
			pass
		return resultat
	
	# test Cqpl request
	#    cqplRequest : cqpl request
	#  return
	#    True if the request is syntacticaly correct False otherwise
	def getCqpl(self,cqplRequest,err=True):
		cq = Cqpl()
		cq.putRequete(cqplRequest)
		return cq.creationArbre()
	
	# apply a CQPL request on an index
	#    cqplRequest : cqpl request
	#    idx : index handle (use default if not define)
	#  return
	#    list of index offset
	def cqpl(self,cqplRequest,idx=None):
		if idx == None:
			idx = self.defaultIdx
		req = Requete()
		req.putIndex(idx)
		req.putRequete(cqplRequest)
		try:
			res = [(b,e) for e,b in req.calculRequete().items()]
		except:
			sys.stderr.write("error")
			exit(0)
		return res
		
	# set transduction file list
	#	lst : list of transduction files
	def setTransduction(self,lst):
		self.trans = Transduction()
		for rf in lst:
			if os.path.isfile(rf):
				with open(rf) as tf:
					for r in tf:
						if r[0] != "#":
							r = r.rstrip()
							if self.verbose:
								sys.stderr.write('add rule : '+r+'\n')
							self.trans.addRules(r)
			else:
				sys.stderr("file "+rf+"unknown\n")
		
	# get the maximal offset in an index 
	#  return
	#    maximal offset for an index
	def getMaxWord(self):
		return self.defaultIdx.getMaxMot()
		
	# return raw token from an offset
	#    offset : an offset
	#  return
	#    token
	def getElement(self,offset):
		return Token(self.defaultIdx.getElement(offset))

	# return token (Token) from an offset
	#    offset : an offset
	#  return
	#    token
	def getToken(self,offset):
		return Token(self.defaultIdx.getElement(offset))

	# return graphical form from an offset
	#    offset : an offset
	#  return
	#    graphical token form
	def getGraph(self,offset):
		return self.defaultIdx.getElement(offset)[0]
		
	# return text span from an offset couple
	#    span : an array off size 2
	#  return
	#    a text
	def getText(self,span):
		res = []
		d = max(1,span[0])
		f = min(self.defaultIdx.maxMot-1,span[1])
		for p in range(d,f+1):
			res.append(self.getGraph(p))
		return res
		
	# return divisions from an offset
	#    offset : an offset
	#  return
	#    a triplet [division,initial offset,final offset]
	def getDivFromOffset(self,offset):
		return self.defaultIdx.getDivPos(offset)[0]

	# return offset of a div
	#   div : a divison
	# return
	#   offsets of the division (begin, end)
	def getPosDiv(self,div):
		return self.defaultIdx.getPosDiv(div)

	# return all divs of the index
	#  return
	#	a list of triplet 
	def getAllDivs(self):
		return self.defaultIdx.getAllDiv()

	# return all divisions from an offset
	#    offset : an offset
	#  return
	#    a list of div
	def getAllDivFromOffset(self,offset):
		return self.defaultIdx.getDivPos(offset)

	# return offsets span from a divison
	#    div : division (string)
	#  return
	#    a couple [initial offset,final offset]
	def getAllOffsetsFromDiv(self,div):
		return self.defaultIdx.getPosDiv(div)

	# return offsets span from a regexp divison
	#    div : division (regexp)
	#  return
	#    a couple [initial offset,final offset]
	def getAllOffsetsFromDivRegexp(self,div):
		return cq.getPosDivRegExp(div)


	#return self.defaultIdx.getPosDivRegExp(div)
	# return offsets span from a divison
	#    div : division (string)
	#  return
	#    a couple [initial offset,final offset]
	def getOffsetsFromDiv(self,div):
		s = self.defaultIdx.getPosDiv(div)
		if len(s)>0:
			return (s[0][0],s[0][1])
		else:
			return ()

		
	# return a concordance as an array (left,query,right)
	#	query : a CQPL query
	#	nb : number of results (default = 25)
	#	size : size of the contexts (left and right) (default = 10)
	#	tsort : type of sort
	#		"alpha" (default)
	#	colsort : on which column the sort is apply ("l","q","r") (default = "q")
	# return
	#	an array of 3-sized arrays
	def getConcordance(self,query,nb=25,size=10,tsort="alpha",colsort="q"):
		if self.testCqpl(query):
			lstres = self.cqpl(query)
			conc = []
			for off in lstres[:nb]:
				pg = [off[0]-size,off[0]-1]
				pd = [off[1]+1,off[1]+size]
				conc.append({"l":self.getText(pg),"q":self.getText(off),"r":self.getText(pd)})
			if colsort == "q" or colsort == "r":
				conc = sorted(conc,key=lambda x:"".join(x[colsort]))
			else:
				conc = sorted(conc,key=lambda x:"".join([x[colsort][i] for i in range(len(x[colsort])-1,-1,-1)]))
		else:
			conc = ["error"]
		return conc
		
		
	# return the list of each differents features of tokens
	# retourne la liste des offsets par rapport a une etiquette et sa valeur
	def getGlobalIndex(self,e):
		return self.defaultIdx.globalIndex[e]

	# iterator initialization
	def initPosOffset(self):
		self.defaultIdx.initPosOffset()
		
	# return the next token
	def getNextToken(self):
		return self.defaultIdx.getNextToken()

	# return the offset of the current token
	def getCurrentOffset(self):
		return self.defaultIdx.getCurrentOffset()



if __name__ == '__main__':
	cq = Cquery()
	cq.open("/home/fabrice/CorpusLoc/Romans/allais-extrait2.txt","c")	
	print(cq.getConcordance('[l="."]',colsort="l"))
