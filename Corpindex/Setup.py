#!/usr/bin/python3

##
# 2014
# Farid Djaïdja
# Classe SetUp
##
# Récupération de données système et verification de l'intégrité de l'architecture

import sys
import os
import locale

class Setup (object):
	"""The Setup class gets and stocks informations about the system, 
	such as the language. 
	It also tests the integrity of the folders"""

	def __init__(self):
		"""The initialization gets the language set in the OS and 
		sets the encoding as UTF-8. It also creates a series of variables
		 where the paths of the directories are saved."""
		self.language = locale.getdefaultlocale()[0][0:2]	
		locale.getpreferredencoding ='UTF-8'
		self.path = Path()
		self.architecture = self.path.getArchitecture()

		
		
	def createConfigFile(self):
		"""creates a configuration file for the menu accordingly to the language
		 set in the OS. French and English are the only supported languages. 
		 The default language is English."""
		
		configFile = open(self.path.guiConf+"/menu.en.conf", "a")
		configItems = """FILE	File
NEW	New File
OPEN	Open File
RECENT	Recent Files
CLOSE	Close File
IMPORT	Import Index
EXPORT	Export Index
QUIT	Quit
EDIT	Edit
UNDO	Undo
REDO	Redo
CUT	Cut
COPY	Copy
PASTE	Paste
PARAMETERS	Parameters
CONCORDANCER	Concordancer
SAVE	Save
OPTIONS	Options
VIEW	View
CONSOLE	Console
HISTORY	History
ZOOM_IN	Zoom In
ZOOM_OUT	Zoom Out
RESET	Reset
TOOLS	Tools
FILTER	Filter
STAT	Statistics
DIC	Dictionaries
HELP	Help
DOC	Documentation
ERRORS	Errors
WEBSITE	Website
ABOUT	About
KEY_WORDS	Key Words
LEFT_CONTXT	Left Context
RIGHT_CONTXT	Right Context
QUERY	Query
LAUNCH	Launching of the query
ERROR1	Error 1 - Configuration file is missing
ERROR2	Error 2 - Recent files could not be loaded"""
		configFile.write(configItems)
		configFile.close()

	
	def localization(self):
		"""adapts the localization according to the language of the OS. 
		If the system is not in French, the default language is English"""
		if self.language == "fr":
			
			for elt in open(self.path.guiConf+"/menu."+self.language+".conf",encoding="UTF-8"):
				if elt[0] != "#": # excludes comments
					tab = elt.rstrip().split("\t") # Creates a dynamic menu 
					key = tab[0]
					value = tab[1]
					self.rsc[key] = value
		else:
			for elt in open(self.path.guiConf+"/menu.en.conf",encoding="UTF-8"):
				if elt[0] != "#": # excludes comments
					tab = elt.rstrip().split("\t") # Creates a dynamic menu 
					key = tab[0]
					value = tab[1]
					self.rsc[key] = value
	
	def dirTest(self):
		"""checks the architecture of the software. It also generates any
		missing directory or configuration file."""
		for directory in self.architecture:
			if not os.path.exists(directory):
				os.mkdir(directory)
			if not os.path.exists(self.configFile):
				createConfigFile()
				#raise("The "+directory+" was missing.")


class Path(object):
	"""The Path class stores the architecture of the Setup class."""

	
	def __init__(self):
		# je voulais pas polluer le nom des variables de Path()
		self.cmd = os.path.dirname(os.path.abspath(__file__))+"/Cmd"
		self.conf = os.path.dirname(os.path.abspath(__file__))+"/Conf"
		self.template = os.path.dirname(os.path.abspath(__file__))+"/Template"
		self.corpindex = os.path.dirname(os.path.abspath(__file__))+"/Corpindex"
		self.corpus = os.path.dirname(os.path.abspath(__file__))+"/Corpus"
		self.dic = os.path.dirname(os.path.abspath(__file__))+"/Dictionaries"
		self.index = os.path.dirname(os.path.abspath(__file__))+"/.Index"
		self.gui = os.path.dirname(os.path.abspath(__file__))+"/Gui"
		self.guiConf = self.gui+"/.conf"
		self.rules = os.path.dirname(os.path.abspath(__file__))+"/Rules"
		if locale.getdefaultlocale()[0][0:2] == "fr":
			self.configFile = self.guiConf+"/menu.fr.conf"
		else:
			self.configFile = self.guiConf+"/menu.en.conf"
	
	def getArchitecture(self):
		"""returns the absolute paths of the Corpindex directories and 
		of the configuration file."""
		return self.__dict__.values()

