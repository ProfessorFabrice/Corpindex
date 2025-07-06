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

# exception declaration
class XmlError(Exception):
	pass
