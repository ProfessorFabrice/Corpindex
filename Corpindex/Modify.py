#!/usr/bin/env python3

from abc import ABC, abstractmethod

from Cquery import Cquery
from Token import Token


class Modify(ABC):
	def __init__(self,index,verbose=False):
		self.cq = Cquery()
		self.cq.open(index)
		self.res = []
		
	@abstractmethod
	def parcours(self):
		pass

	@abstractmethod
	def modifications(self,tok,off):
		return tok
		
	# iteration sur l'index
	def iteraDoc(self):
		off = 0
		for tok in self.cq.defaultIdx.getIndexTokens():
			if not tok.isDiv():
				off += 1
			tok = self.modifications(tok,off)
			yield tok

	
	# création et écriture du nouvel index
	def createNewIndex(self,out,fl=[]):
		cq = Cquery()
		cq.featureList += fl
		nidx = cq.createNewIndex(out)
		cptMot = nidx.indexation(self.iteraDoc(),0)
		nidx.maxMot = cptMot
		cq.saveNewIndex(nidx)

