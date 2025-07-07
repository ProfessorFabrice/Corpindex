#!/usr/bin/python3

##
# 2008
# Fabrice Issac
# Classe Index
##


from struct import *
import string
import zlib
import sys
import re

import pickle
import os
import glob
import shutil
import timeit

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append("Corpindex")

#import Debug

from .Token import Token
from .Tokenizer import Tokenizer
from .Concordance import Concordance
from .Tokxml import Tokxml
from .Tokcsv import Tokcsv
from .Dico import Dico
#from Corpindex import Debug

#from Node import Node
from intervaltree import Interval, IntervalTree

class Index(object):
	'The index class processes the indexation of the tokens in a corpus'
	def __init__(self,fileName,nature="bsd",verbose=False,ficlog=sys.stderr):
		self.ficlog = ficlog
		#self.length = length
		self.verbose = verbose
		self.fileName = fileName # ancien nomFichier
		self.tagList = []	 # ancien listeEtiquette
		self.tags = []		 # ancien etiquettes
		self.tagIndex = {}	 # ancien indexEtiquette
		self.globalIndexDB = {} # table persistante
		self.globalIndex = {"f":{}}
		#self.globalIndex["f"] = {}
		#self.indexGroupe = {} 					variable relique 
		#self.regexpMot = re.compile('<w ?[^>]*>[^<]*')		variable relique
		#self.regexpAttributs = re.compile('[^= ]*="[^"]*"')	variable relique
		self.maxMot = 0
		self.debug = ''
		self.nomRes = re.sub('^.*[\/\\\]','',self.fileName)
		self.nomRes = re.sub('\..*$','',self.nomRes)
		self.dirName = self.fileName+"_idx"	#ancien nomRep
		self.indexBD = None
		self.tokenizer = None
		#self.indexGroupeK = [] 				variable relique
		#self.documentOffset = None 				variable relique
		#self.document = None 					variable relique
		self.pileDiv = []
		self.indexDiv = {}
		self.indexDivDebFin = {}
		self.indexElement = {}
		self.indexPosElement = None
		self.numElement = 0
		self.treeDiv = None
		self.zone = {} # fiouuu c'est vieux ça... !
		self.divBD = None
		self.carrousel = "-\|/" # pour faire un carrousel
		# chargement du bon module en fonction de la nature de la BdD persistante utilisée
		n = self.getNature()
		if n != "" and nature == "": # index déjà créé
			nature = n
		#print("nature="+nature) ####
		if nature == "bsd":
			self.stock = __import__("StockBsddb")
		elif nature == "kcf":
			self.stock = __import__("StockKc")
		elif nature == "dpy":
			self.stock = __import__("StockDictPy")
		elif nature == "dbm" or nature =="dbm.db":
			self.stock = __import__("StockDbm")
		self.nature = nature
		#print(self.nature)
		self.positer = 0 # pointeur pour gérer l'itérateur

	# retourne le nom de l'index
	def getName(self):
		return self.fileName
		
	# initialisation du tokenizer
	def initTokenizer(self,type,listeD,typeD='dico',listeMc=[],lang="df",ldict=None):
		if type == "txt":
			Tokenizer.langue = lang
			self.tokenizer = Tokenizer(listeD,typeD,listeMc,self.verbose,ldict)
			self.tokenizer.readMs()
			self.ficlog.write("end init sw\n")
			self.tokenizer.readMc()
			self.ficlog.write("end init cw\n")
		elif type == "csv":
			self.tokenizer = Tokcsv()
		else:
			self.tokenizer = Tokxml()
		if self.verbose:
			self.ficlog.write("end init dictionaries\n")
	
	# initialisation du dossier pour la sauvegarde (effacement et création)
	def initDB(self): 			#ancien initBase
		"""Creates the directory where the index database is stored.
If a directory named "fileName_idx" already exists, it is overwritten.
Otherwise, a "fileName_idx" directory is created."""
		if os.path.isdir(self.dirName):
			try:
				shutil.rmtree(self.dirName)
			except OSError:
				self.ficlog.write("error 1: cannot delete directory\n")
		try:
			os.mkdir(self.dirName)
		except OSError: 
			self.ficlog.write("error 2: cannot create directory\n")
			exit(0)
				
	# creation des fichiers (index, document) en utilisant des tables de hachage persistantes 
	# gérées par l'objet "Stock" le jeu d'étiquette est nécessaire sous forme d'un tableau
	def createBase(self,tags):
		#self.tags = tags
		
		self.tags.append('level')
		self.divBD = self.stock.Stock()
		self.divBD.open(self.dirName+'/'+self.nomRes+'_div','w')
		self.indexBD = self.stock.Stock()
		self.indexBD.open(self.dirName+'/'+self.nomRes+'_index','w')
		self.indexBD['___listetiquette___'] = pickle.dumps(tags)
		self.indexBD['___nombremots___'] = "0"
		self.globalIndexDB = {}
		for e in tags:
			self.globalIndexDB[e] = self.stock.Stock()
			self.globalIndexDB[e].open(self.dirName+'/'+self.nomRes+'.'+e,'w')
		self.indexElement = {}
		self.numElement = 0
		
	# retourne le type de base utilise pour stocker l'index (bsd, kcf)
	def getNature(self):
		nat = glob.glob(self.dirName+'/'+self.nomRes+'_index.*')
		if len(nat) > 0:
			return nat[0][-3:]
		else:
			return ""
		
	# sauvegarde de l'indexation
	def updateDB(self):
		lstEtiq = {'f':1}
		for e in self.tagList:
			self.tagIndex[e] = list(self.globalIndex[e].keys())
			lstEtiq[e] = 1
		self.tagIndex["f"] = list(self.globalIndex["f"].keys())
		for e in lstEtiq:
			for v in self.tagIndex[e]:
				try:
					tmpvar = self.globalIndexDB[e][v]
					if tmpvar != None:
						prec = pickle.loads(tmpvar)
					else:
						prec = []
				except (TypeError,KeyError):
					#raise
					prec = []
				nouv = self.globalIndex[e][v]+prec
				try:
					p = pickle.dumps(nouv,2)
				except:
					sys.stderr.write(len(nouv))
					raise
				try:
					self.globalIndexDB[e][v] = p
				except KeyError:
					self.globalIndexDB[e] = self.stock.Stock()
					self.globalIndexDB[e].open(self.dirName+'/'+self.nomRes+'.'+e,'w')
					self.globalIndexDB[e][v] = p
			del self.globalIndex[e]
			self.globalIndex[e] = {}
		for e in list(self.globalIndexDB.keys()):
			self.globalIndexDB[e].sync()

		
	# création de l'index
	def indexation(self,tabTok,cptMot,filtre=False):
		for tokv in tabTok:
			#Debug.debug(cptMot,str(tokv.getLowStruct()))
			if self.verbose:
				self.ficlog.write(' '+str(cptMot)+'                      '+chr(13))
				#self.ficlog.write(self.carrousel[cptMot%4]+chr(13))
			forme = tokv.getForme()
			if not tokv.isDiv():
				cptMot += 1
				#Debug.debug("tok",cptMot,str(tokv.getLowStruct()))
				if filtre:
					tokv.sortFiltre()  
				self.addTokenDocument(tokv)
				self.debug = forme
				if forme not in self.globalIndex["f"]:
					self.globalIndex["f"][forme] = [cptMot]
				else:
					self.globalIndex["f"][forme].append(cptMot)
				info = {}
				info["f"] = forme
				numetiquette = 0
				for i in range(0,tokv.getNbFeat()):
					for etiquette in tokv.getLstFeat(i):
						val = tokv.getFeat(etiquette,i)
						if etiquette not in self.globalIndex:
							self.tagList.append(etiquette)
							self.globalIndex[etiquette] = {}
						if val not in self.globalIndex[etiquette]:
							self.globalIndex[etiquette][val] = []
						self.globalIndex[etiquette][val].append(cptMot)
			else: # division
				#Debug.debug("div",cptMot,str(tokv.getLowStruct()))
				forme = tokv.getDiv()
				if forme == "/": # fin division
					#print("pilediv=",self.pileDiv)
					[div,debut] = self.pileDiv.pop(-1)
					debut += 1
					#print("debut=",div,debut)
					if div in self.indexDiv:
						if debut in self.indexDiv[div]:
							#self.indexDiv[div][debut].append(cptMot+1)
							self.indexDiv[div][debut].append(cptMot)
						else:
							#self.indexDiv[div][debut] = [cptMot+1]
							self.indexDiv[div][debut] = [cptMot]
					else:
						self.indexDiv[div] = {}
						self.indexDiv[div][debut] = [cptMot+1]
						#self.indexDiv[div][debut] = [cptMot]
					#print("indexdiv=",div,debut,cptMot+1)
				else: # debut division
					#self.pileDiv.append([forme,cptMot+1])
					self.pileDiv.append([forme,cptMot])
					#print("pilediv = ",self.pileDiv)
		return cptMot
		
	# indexation
	def indexTexte(self,trans=None,filtre=False,preproc=False):
		ptrfic = open(self.fileName,encoding='utf-8')
		cptMot = 0
		nbLigne = 0
		self.tagList = []
		offsetTotal = 0
		self.globalIndex = {}
		self.globalIndex["f"] = {}
		for ligne in ptrfic:
			nbLigne = nbLigne + 1
			if self.verbose:
				#self.ficlog.write(str(nbLigne)+'    '+str(cptMot)+'                   '+chr(13))
				self.ficlog.write(self.carrousel[cptMot%4]+chr(13))
			if ligne == "":
				break;
			# call tokeniser
			self.tokenizer.init(ligne,preproc)
			try:
				res = self.tokenizer.calcTokens()
			except XmlError as msg:
				sys.stderr.write("Xml error ("+str(msg)+") in line "+str(nbLigne)+"\n")
				exit(0)
			#print("token res = "+str(res)) ######
			# if transduction rules
			if trans:
				#for x in res:
				#/80	print("XX=",x.getLowStruct())
				res = trans.checkTabToken(res)
			#print("token trans = "+str(res)) ######
			cptMot = self.indexation(res,cptMot,filtre)
			#print(self.tagList)
			if cptMot % 1000000 == 0:
				#print("mise à jour") #####
				self.updateDB()
		self.updateDB()
		#print "-->"+str(self.globalIndexDB["f"].keys())
		cptMot = self.indexation([Token(['EOT',[{'l':'_','c':'_'}]])],cptMot) # je ne sais plus trop pourquoi
		#print("cptMot=",cptMot)
		self.maxMot = cptMot
		# modif ici	
		for e in self.tagList:
			self.tagIndex[e] = list(self.globalIndexDB[e].keys())
		self.tagIndex["f"] = list(self.globalIndexDB["f"].keys())
		self.sauveBase()


	# lecture du fichier non etiquete
	def indexTexteBrut(self,trans=None):
		ptrfic = open(self.fileName,encoding='utf-8')
		cptMot = 0
		nbLigne = 0
		self.tagList = []
		offsetTotal = 0
		self.globalIndex = {}
		self.globalIndex["f"] = {}
		for ligne in ptrfic:
			nbLigne = nbLigne + 1
			if self.verbose:
				#self.ficlog.write(str(nbLigne)+'    '+str(cptMot)+'                   ') #+chr(13))
				self.ficlog.write(self.carrousel[cptMot%4]+chr(13))
			if ligne == "":
				break;
			#print(ligne)####
			# appel tokeniser
			self.tokenizer.init(ligne)
			res = self.tokenizer.calcTokens()
			#print("token res = "+str(res)) ######
			# si règle de transduction
			if trans:
				res = trans.checkTabToken(res)
			cptMot = self.indexation(res,cptMot)
			if cptMot % 1000000 == 0:
				#print("mise à jour") #####
				self.updateDB()
		self.updateDB()
		#print "-->"+str(self.globalIndexDB["f"].keys())
		#cptMot = self.indexation([Token(['SENT',[{'l':'','c':''}]])],cptMot)
		self.maxMot = cptMot
		# modif ici	
		for e in self.tagList:
			self.tagIndex[e] = list(self.globalIndexDB[e].keys())
		self.tagIndex["f"] = list(self.globalIndexDB["f"].keys())
		self.sauveBase()
		
	# transforme le texte XML en index
	def indexTexteXml(self):
		ptrfic = open(self.fileName,encoding='utf-8')
		self.tagList = []
		nbLigne = 0
		offsetTotal = 0
		while 1:
			try:
				ligne = ptrfic.readline()
				ligne = io.StringIO(ligne)
			except Exception(msg):
				self.ficlog.write("erreur lecture fichier ici :"+ligne+"\n")
				sys.exit(0)
			nbLigne = nbLigne + 1
			if nbLigne % 500000 == 0:
				print("mise à jour") #####
				self.updateDB()
			#if self.verbose:
			#	self.ficlog.write(str(nbLigne)+'                  '+chr(13))
			if ligne == "":
				break;
			#self.tokenizer.init()
			for element in self.tokenizer.parse(ligne):
				offsetTotal += 1
				if self.verbose:
					#self.ficlog.write("yoo "+str(offsetTotal)+'                  '+chr(13))
					self.ficlog.write(self.carrousel[offsetTotal%4]+chr(13))
				tok = []
				infos = {}
				for av in element:
					if av[0] == 'f':
						tok.append(av[1])
					else:
						infos[av[0]] = av[1] 
				tok.append([infos])
				self.addTokenDocument(tok)
				for attval in element:
					self.ajouteIndex(attval[0],attval[1],attval[2])
		self.maxMot = attval[2]
		for e in self.tagList:
			self.tagIndex[e] = list(self.globalIndex[e].keys())
		self.tagIndex["f"] = list(self.globalIndex["f"].keys())

		
	# creation d'un index d'un tableau de token
	# par rapport à un index déjà créé et une table de modifications (transduction)
	def indexTokenTrans(self,idx,trans):
		cptMot = 0
		tagList = idx.getTagLists()
		tabTok = []
		cpt = 0
		cptMot = 0
		for tok in idx.getIndexTokens():
			cpt  += 1
			tabTok.append(tok)
			if cpt % 1000 == 0:
				res = trans.checkTabToken(tabTok)
				cptMot = self.indexation(res,cptMot)
				tabTok = []
		res = trans.checkTabToken(tabTok)
		cptMot = self.indexation(res,cptMot)
		#cptMot = self.indexation([Token(['SENT',[{'l':'SENT','c':'SENT'}]])],cptMot)
		self.maxMot = cptMot
		for e in self.tagList:
			self.tagIndex[e] = list(self.globalIndex[e].keys())
		self.tagIndex["f"] = list(self.globalIndex["f"].keys())
				
	# creation d'un index d'un tableau de token
	# par rapport à un index déjà créé et des dictionnaires (sous forme d'un tableau)
	def indexTokenDico(self,idx,dico):
		cptMot = 0
		tagList = idx.getTagLists()
		dicoMs = Dico()
		dicoMs.load(dico,"dico")
		for tabTokv in idx.getTokens():
			res = []
			for tok in tabTokv:
				#print(tok)###
				if not tok.isDiv():
					tokres = dicoMs.get(tok.getForme())
					if len(tokres)>0: 
						res.append(Token([tok.getForme(),tokres]))
					else:
						res.append(tok)
				else:
					res.append(tok)
			cptMot = self.indexation(res,cptMot)
			if self.verbose:
				#self.ficlog.write(str(cptMot)+'                       '+chr(13))
				self.ficlog.write(self.carrousel[cptMot%4]+chr(13))
			res = None
		#cptMot = self.indexation([Token(['SENT',[{'l':'SENT','c':'SENT'}]])],cptMot)
		self.maxMot = cptMot
		for e in self.tagList:
			self.tagIndex[e] = list(self.globalIndex[e].keys())
		self.tagIndex["f"] = list(self.globalIndex["f"].keys())
		
	# sauvegarde de l'indexation
	def sauveBase(self):
		# sauvegarde des divisions
		for d in self.indexDiv:
			self.divBD[d] = pickle.dumps(self.indexDiv[d])
		self.updateDB()
		self.indexBD['___listetiquette___'] = pickle.dumps(list(self.tagIndex.keys()))
		self.indexBD['___nombremots___'] = str(self.maxMot)
		for e in list(self.globalIndexDB.keys()):
			clef = open(self.dirName+'/'+self.nomRes+'.'+e+'_k','wb')
			pickle.dump(list(self.globalIndexDB[e].keys()),clef,2)
		self.indexPosElement = self.stock.Stock()
		self.indexPosElement.open(self.dirName+'/'+self.nomRes+'_element','w')
		for elt in self.indexElement:
			val = str(self.indexElement[elt])
			self.indexPosElement[val] = elt
	
	# lecture base
	def lectureBase(self,startt=0):
		#print(self.dirName+'/'+self.nomRes+'_index')####
		self.indexBD = self.stock.Stock()
		self.indexBD.open(self.dirName+'/'+self.nomRes+'_index')
		self.maxMot = int(self.indexBD['___nombremots___'])
		# lecture fichiers documents
		self.fdocument = open(self.dirName+'/'+self.nomRes+'_document','rb')
		self.indexPosElement = self.stock.Stock()
		self.indexPosElement.open(self.dirName+'/'+self.nomRes+'_element')
		for e in pickle.loads(self.indexBD['___listetiquette___']):
			#e = e.decode()
			self.globalIndexDB[e] = self.stock.Stock()
			self.globalIndexDB[e].open(self.dirName+'/'+self.nomRes+'.'+e)
			if self.verbose:
				self.ficlog.write("init "+e+"\n")
			clef = open(self.dirName+'/'+self.nomRes+'.'+e+'_k','rb')
			self.globalIndex[e] = pickle.loads(clef.read())
		self.lectureDivs(startt)
		
	def lectureDivs(self,startt=0):
		if self.verbose:
			self.ficlog.write("init divs\n")
		#self.treeDiv = Node(['_top',1,self.maxMot])
		self.treeDiv = IntervalTree()
		self.treeDiv[1:self.maxMot] = '_top'
		self.indexDiv = self.stock.Stock()
		self.indexDiv.open(self.dirName+'/'+self.nomRes+'_div')
		lstDivs = list(self.indexDiv.keys())
		for div in lstDivs:
			if isinstance(div,bytes):
				div = div.decode('utf8')
			tabDiv = pickle.loads(self.indexDiv[div])
			for deb in tabDiv:
				if deb not in self.indexDivDebFin:
					self.indexDivDebFin[deb] = {}
				for fin in tabDiv[deb]:
					if fin not in self.indexDivDebFin[deb]:
						self.indexDivDebFin[deb][fin] = []
					self.indexDivDebFin[deb][fin].insert(0,div)
					#self.treeDiv.insert([div,deb,fin])
					if deb<fin+1:
						self.treeDiv[deb:fin+1] = div
		self.lstDivDebSort = sorted(list(self.indexDivDebFin.keys()))
		self.lstDivDebSort.append(self.maxMot) # sentinelle
		if self.verbose:
			self.ficlog.write("fin init divs\n")
		
	
	def close(self):
		if (self.verbose):
			sys.stderr.write("fermeture\n")
		for e in pickle.loads(self.indexBD['___listetiquette___']):
			self.globalIndexDB[e].close()
		self.fdocument.close()
		self.indexPosElement.close()
		self.indexBD.close()
		self.indexDiv.close()
		
	# ajoute de nouvelles division dans l'index (attention l'index n'est pas rechargé)
	# pas hyper efficace mais bon ça ira (on pourrait éviter les pickle en rafale)
	# divs : un tableau de la forme [offstart,offend,tag]
	def addDiv(self,divs):
		self.indexDiv = self.stock.Stock()
		self.indexDiv.open(self.dirName+'/'+self.nomRes+'_div','w')
		lstdivs = {x for x in self.indexDiv.keys()}
		tmpDivs = {}
		for d in divs:
			[s,e,t] = d 
			e += 1 # pour correctement fermer la balise il fautindiquer le token suivant
			if t not in lstdivs:
				tmpDivs[t] = {s:[e]}
				lstdivs.add(t)
			else:
				if t not in tmpDivs:
					tmpDivs[t] = pickle.loads(self.indexDiv[t])
				if s not in tmpDivs[t]:
					tmpDivs[t][s] = []
				tmpDivs[t][s].append(e)
		for t in tmpDivs:
			self.indexDiv[t] = pickle.dumps(tmpDivs[t])
		self.indexDiv.close()
		self.lectureDivs()
		
	# ajoute element dans la structure ??
	def ajouteIndex(self,etiquette,valeur,pos):
		if etiquette not in self.globalIndex:
			self.globalIndex[etiquette] = {}
			self.globalIndex[etiquette][valeur] = [pos]
			self.tagList.append(etiquette)
		else:
			if valeur not in self.globalIndex[etiquette]:
				self.globalIndex[etiquette][valeur] = [pos]
			else:
				self.globalIndex[etiquette][valeur].append(pos)
				
	# retourne la liste des valeurs possible de chaque etiquette (forme comprise)
	def getTagIndex(self,e):
		return self.globalIndex[e]
		#return self.globalIndexDB[e].keys()
		
	# retourne la liste des offsets par rapport a une etiquette et sa valeur
	def getGlobalIndex(self,e,elt):
		try: # bof
			return pickle.loads(self.globalIndexDB[e][elt])
		except Exception as exc:
			#print(exc)
			return []
	
	# retourne les divisions à la position pos
	# sous forme d'un tableau de triplets [div,deb,fin]
	def getDivPos(self,pos):
		return  [[q[2],q[0],q[1]] for q in sorted(list(self.treeDiv[pos]),key=lambda x:int(x[1])-int(x[0]),reverse=True)]
		
	# retourne les position de la division 'div'
	# sous forme d'un tableau de couples debut,fin	
	# NE SEMBLE PAS MARCHER (problème encodage avec bsddb3)
	# marche un peu mais pas efficace
	def getPosDiv(self,div):
		res = []
		div = div.encode() # j'ai l'impression que bsddb3 converti en byte automatiquement
		#print(list(self.indexDiv.keys()))
		if div in self.indexDiv.keys():
			tabDiv = pickle.loads(self.indexDiv[div])
			#print("-->",tabDiv)
			for debut in tabDiv:
				for fin in tabDiv[debut]:
					res.append([debut,fin])
		return res
		
	# retourne les position de la division 'div'
	# sous forme d'un tableau de couples debut,fin	
	def getPosDivRegExp(self,rediv):
		res = []
		lstDiv = []
		#idxDivKeys = self.indexDiv.keys()
		#for i in list(self.indexDiv.keys()):
		for i in self.indexDiv.keys():
			#print(type(rediv),rediv,i,type(i))###
			if re.search(rediv,i.decode('utf-8')):
			#if re.search(rediv,str(i)):
				try:
					tabDiv = pickle.loads(self.indexDiv[i])
					for debut in tabDiv:
						for fin in tabDiv[debut]:
							res.append([debut,fin])
				except:
					raise
					pass			
		return res
		
	# retourne l'ensemble des divisions d'un index
	# sous forme d'un tableau
	def getAllDiv(self):
		return self.indexDiv.keys()
		
	# retourn le nom du dossier contenant les indexes
	def getIndexDirectory(self):
		return self.dirName		
		
	# retourne la liste possible des étiquettes
	def getTagLists(self):
		return pickle.loads(self.indexBD['___listetiquette___'])
		
	# enlever un élément dans l'index à un offset donné
	def removeglobalIndex(self,e,elt,offset):
		tabtmp = self.getGlobalIndex(e,elt)
		try:
			tabtmp.remove(offset)
		except:
			pass
		self.globalIndexDB[e][elt] = pickle.dumps(tabtmp)
	
	# def intialisation fichiers documents
	def initFicDocument(self):
		for fic in glob.glob(self.dirName+'/'+self.nomRes+'.*'):
			os.remove(fic)
		self.fdocument = open(self.dirName+'/'+self.nomRes+'_document_tmp','wb')
		
	# création fichier document version 3 (current)
	def addTokenDocument(self,tok):
		lltok = tok.getLowStruct()
		val = zlib.compress(pickle.dumps(lltok))
		if val in self.indexElement:
			self.fdocument.write(pack("i",int(self.indexElement[val])))
		else:
			self.numElement += 1
			self.indexElement[val] = str(self.numElement)
			self.fdocument.write(pack("i",self.numElement))

	# changement nom fichiers documents
	def renameFicDocument(self):
		#print(self.fdocument.name)####
		self.fdocument.close()
		chemin = self.dirName+'/'+self.nomRes
		if os.path.isfile(chemin+'_document'):
			os.remove(chemin+'_document')
		os.rename(chemin+'_document_tmp',chemin+'_document')
	
	def closeBase(self):
		self.indexBD.close()
		for e in list(self.globalIndexDB.keys()):
			self.globalIndexDB[e].close()
		self.indexPosElement.close()
		#print(self.divBD)####
		if self.divBD != None:
			self.divBD.close()
		self.fdocument.close()
		#self.documentOffset.close()
	
	# creation fichier de méta informations
	def createMeta(self):
		meta = open(self.dirName+'/'+self.nomRes+"_meta.xml","w",encoding='utf-8')
		meta.write("<meta>\n")
		meta.write("\t<list>\n")
		meta.write("\t\t<item k='tag' v='f:"+":".join(self.tagList)+"'>\n")
		meta.write("\t</list>\n")
		meta.write("</meta>\n")
		meta.close()
	
	# retourne une information (forme ou etiquette) par rapport a son offset et le type de l'etiquette
	def getElement(self,offset):
		format = calcsize("i")
		self.fdocument.seek((int(offset)-1)*format)
		elt = self.fdocument.read(format)
		pos = unpack("i",elt)[0]
		res = pickle.loads(zlib.decompress(self.indexPosElement[str(pos)]))
		try:
			res.append(self.zone[offset])
		except KeyError:
			pass
		return res

	# retourne la requete dans un contexte
	# debut : debut
	# fin : fin
	# taille : nb mots contextes
	def getResultat(self,debut,fin,taille,zone=[]):
		res = []
		pg = []
		pd = []
		#print("zone="+str(zone)) #####
		for i in range(max(1,debut-taille),max(1,debut)):
			pg.append(self.getElement(i))
		for i in range(debut,fin+1):
			#print(debut,fin,i)#####
			elt = self.getElement(i)
			#if i in zone:
			#	#print ("=-=-=->"+str(elt)) ###
			#	elt.append(zone[i])
			res.append(elt)
		for i in range(fin+1,min(fin+taille+1,self.maxMot)):
			pd.append(self.getElement(i))
		#print(res) ####
		try:
			divPos = self.getDivPos(debut)
		except IndexError:
			#raise
			divPos = []
		return [pg,res,pd,divPos]
		
	# retourne la requete dans un contexte dans un tableau associatif
	# debut : debut
	# fin : fin
	# taille : nb mots contextes
	def getResultConc(self,debut,fin,taille,zone=[]):
		pv = []
		pl = []
		pr = []
		for i in range(max(1,debut-taille),max(1,debut)):
			pl.append(Token(self.getElement(i)))
		for i in range(debut,fin+1):
			pv.append(Token(self.getElement(i)))
		for i in range(fin+1,min(fin+taille+1,self.maxMot)):
			pr.append(Token(self.getElement(i)))
		try:
			pdeb = self.getDivPos(debut)
			pfin = self.getDivPos(fin)
			if pdeb == pfin:
				divPos = pdeb
			else:
				divPos = [pdeb[0]]
			#divPos = self.getDivPos(debut)
		except (IndexError,KeyError): 
			raise
			divPos = [""]
		return Concordance(pl,pv,pr,divPos,debut,fin)
	
	# retourne le nombre de mots du document
	def getMaxMot(self):
		return self.maxMot
		
	# retourne 
	def getTabConc(self,tabres,taille,nb):
		"""
	retourne un tableau de concordances
	tabres : tableau de résultats
	taille : taille du contexte
	nb : nombre de concordance
		"""
		res = []
		resort = list(tabres.keys())
		resort.sort()
		if nb !=-1:
			resort = resort[:nb]
		for rk in resort:
			#print(rk)####
			if rk<self.maxMot:
				yield self.getResultConc(tabres[rk],rk,taille)
		
	# retourne l'ensemble du document via un iterateur
	# par paquet de 10000 (par defaut)
	def getTokens(self,fenetre=1000):
		pileFin = [-1] # sentinelle
		le = self.getTagLists()
		le.remove('f')
		cpt = 0
		ret = []
		for offset in range(1,self.getMaxMot()):
			#print "offset="+str(offset)
			cpt = cpt + 1
			if offset in self.indexDivDebFin: # si balise ouvrant ici
				#print offset
				for fin in sorted(self.indexDivDebFin[offset].keys()):
					for div in self.indexDivDebFin[offset][fin]:
						ret.append(Token([self.indexDivDebFin[offset][fin]]))
					pileFin.append(fin)
			tok = self.getElement(offset)
			ret.append(Token(tok))
			while offset in pileFin:
				ret.append(Token(['/']))
				pileFin.remove(offset)
			if cpt == fenetre:
				yield ret
				ret = []
				cpt = 0
		yield ret
		
	# retourne l'ensemble du document via un iterateur
	# par paquet de 10000 (par defaut)
	def getIndexTokens(self):
		offset = 1
		pileFin = [-1] # sentinelle
		while offset <= self.getMaxMot():
			if offset in self.indexDivDebFin: # si balise ouvrant ici
				for fin in sorted(self.indexDivDebFin[offset].keys(), reverse=True):
					for div in self.indexDivDebFin[offset][fin]:
						yield Token([[div]]) # balise ouvrante
						pileFin.append(fin)
			tok = self.getElement(offset)
			offset += 1
			yield Token(tok) # token
			while offset >= pileFin[-1] and pileFin[-1] != -1:  # c'est moche
				del pileFin[-1]
				yield Token([['/']])	# balise fermante
	
	# intialisation du pointeur d'itérateur
	def initPosOffset(self):
		self.positer = 0

	# retourne le token suivant par rapport à une position géré par self.positer  (permet de faire un itérateur)
	def getNextToken(self):
		self.positer += 1
		if self.positer >= self.maxMot:
			return None
		else:
			return Token(self.getElement(self.positer))

	# retourne l'offset courant
	def getCurrentOffset(self):
		return self.positer
		
	# associer des zones à un index (old)
	def putZone(self,zone):
		self.zone = zone

if __name__ == '__main__':
	pass

