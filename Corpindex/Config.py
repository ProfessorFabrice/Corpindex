#!/usr/bin/python
# -*- coding: utf-8 -*-

##
# LDI 2008
# Fabrice Issac
# Classe Config
##
# Lecture du fichier de configuration et accesseurs


import sys
import re

from xml.dom.minidom import parse, parseString

class Config(object):
	def __init__(self,nomFic,ficlog=sys.stderr):
		self.nomFic = nomFic
		self.ficlog = ficlog
		self.tabReq = []
		self.tabFic = []
		self.tabPost = []
		self.tabRulesTrans = []
		self.index = False
		self.verb = False
		self.tag = False
		self.both = False
		self.t = 'txt'
		self.taille = 0
		self.att = 'f'
		self.out = -1
		self.dico = ""
		self.langDico = "df"
		self.amp = re.compile('&amp;')


	# lecture fichir xml
	def read(self):
		try:
			d = parse(self.nomFic)
		except:
			self.ficlog.write('impossible de lire '+self.nomFic+'\n')
			sys.exit(0)
		racine = d.childNodes[0]
		config = {}
		for tag in ["param","display","query","post","rules","file"]:
			config[tag] = racine.getElementsByTagName(tag)
		# traitement <param>
		self.version = self.getTagTag(config["param"],"version","val","new")
		self.typebase = self.getTagTag(config["param"],"base","val","kc")
		self.verb = self.getTagTagBool(config["param"],"verb","val","")
		self.index = self.getTagTagBool(config["param"],"index","val","")
		self.tag = self.getTagTagBool(config["param"],"tag","val","")
		self.both = self.getTagTagBool(config["param"],"both","val","")
		self.replace = self.getTagTag(config["param"],"replace","val","")
		self.ficout = self.getTagTag(config["param"],"ficout","val","stdout")
		self.listetiq = self.getTagTag(config["param"],"lstag","val","f:l:c")
		self.out = int(self.getTagTag(config["param"],"out","val","-1"))
		self.listeDico = []
		self.listeDicoMc = []
		try:
			self.typeDico = self.getTagTag(config["param"],"dico","type","")
			self.langDico = self.getTagTag(config["param"],"dico","lang","")
			if self.langDico == "":
				self.langDico = "df"
			for i in config["param"][0].getElementsByTagName("item"):
				if i.getAttribute("type") == 'mc':
					self.listeDicoMc.append(i.firstChild.nodeValue)
				else:
					self.listeDico.append(i.firstChild.nodeValue)
				
		except:
			self.typeDico = ""
		# recuperation <display>
		self.att = self.getTagTag(config["display"],"att","val","")
		self.t = self.getTagTag(config["display"],"type","val","")
		self.taille = int(self.getTagTag(config["display"],"range","val","0"))
		# recuperation <query>
		try:
			for i in config["query"][0].getElementsByTagName("item"):
				self.tabReq.append([i.getAttribute("id"),self.amp.sub('&',i.firstChild.nodeValue)])
		except:
			pass		
		# recuperation <file>
		try:
			for i in config["file"][0].getElementsByTagName("item"):
				self.tabFic.append(i.firstChild.nodeValue)
		except:
			pass
		# recuperation <post>
		try:
			for i in config["post"][0].getElementsByTagName("item"):
				post = {}
				for att in i.attributes.keys():
					post[att] = self.getAttTag(i,att,"")
				post["value"] = self.getTagVal(i,"")
				self.tabPost.append(post)
		except:
			pass
		# recuperation <rules>
		try:
			#print config["rules"]
			for i in config["rules"][0].getElementsByTagName("item"):
				self.tabRulesTrans.append(i.firstChild.nodeValue)
		except:
			pass
							
	# recuperation attribut d'un tag dans un noeud retourne un booleen
	def getTagTagBool(self,noeud,tag,attribut,defaut):
		try:
			return (noeud[0].getElementsByTagName(tag)[0].getAttribute(attribut) == "True")
		except:
			return defaut
		
	# recuperation attribut d'un tag à partir d'un noeud retourne une valeur si elle existe ou une valeur par défaut
	def getTagTag(self,noeud,tag,attribut,defaut):
		try:
			return noeud[0].getElementsByTagName(tag)[0].getAttribute(attribut)
		except:
			return defaut
			
	# recuperation attribut d'un noeud retourne une valeur si elle existe ou une valeur par défaut
	def getAttTag(self,noeud,attribut,defaut):
		try:
			return noeud.getAttribute(attribut)
		except:
			return defaut
			
	# recuperation attribut d'un noeud retourne une valeur si elle existe ou une valeur par défaut
	def getTagVal(self,noeud,defaut):
		try:
			return noeud.firstChild.nodeValue
		except:
			return defaut
			
	# accesseurs
	def getQuery(self):
		return self.tabReq
	
	def getFiles(self):
		return self.tabFic
	
	def getVerbose(self):
		return self.verb
	
	def getOutputType(self):
		return self.t
	
	def getRange(self):
		return self.taille
	
	def getIndex(self):
		return self.index
	
	def getTag(self):
		return self.tag
	
	def getBoth(self):
		return self.both
	
	def getOutputTag(self):
		return self.att	
	
	def getOut(self):
		return self.out
		
	def getFicout(self):
		return self.ficout
		
	def getPost(self):
		return self.tabPost
		
	def getTypeDico(self):
		return self.typeDico
		
	def getListeDico(self):
		return self.listeDico
	
	def getListeDicoMc(self):
		return self.listeDicoMc
		
	def getLangDico(self):
		return self.langDico
	
	def getRulesTrans(self):
		return self.tabRulesTrans
		
	def getReplace(self):
		return self.replace.split("|")
		
	def getVersion(self):
		return self.version
		
	def getTypeBase(self):
		return self.typebase
		
	def getListeEtiquettes(self):
		return self.listetiq.split(":")
		
if __name__ == '__main__':
	pass
