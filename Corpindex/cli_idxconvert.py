#!/usr/bin/python3

import argparse
import sys
import glob
import os.path
import os
import json
import xml.etree.ElementTree as ET
from pathlib import Path

from .RequeteIndex import RequeteIndex as Requete
from .Transduction import Transduction
from .Index import Index
from .Token import Token

class Convert(object):
    def __init__(self,ficIn,ficOut):
        self.contFic = None
        self.typeFic = None
        self.idx = None
        self.ficIn = ficIn
        self.ficOut = ficOut
        self.lstFeat = []
        if not ficOut:
            self.ficOut = "out.idx"
            
    # fonction récursive de parcours du fichier xml
    def parcourir(self,elt, resultat):
        for enfant in elt:
            if enfant.tag == "div":
                div = enfant.get("id")
                resultat.append([[div]])
                self.parcourir(enfant, resultat)
                resultat.append([["/"]])

            elif enfant.tag == "tok":
                forme = enfant.findtext("w")
                attribut = []
                for item in enfant.findall("./feat/item"):
                    attribut.append({cle: valeur for cle, valeur in item.attrib.items()})
                resultat.append([forme, attribut])
            else:
                self.parcourir(enfant, resultat)
            
    # transformer Xml en structure python
    def loadXml(self,nom):
        root = ET.fromstring(open(nom, "rb").read())
        resultat = []
        self.parcourir(root,resultat)
        return resultat
        
    # guesser de type de fichier et charger le contenu
    def guessType(self):
        nom = self.ficIn
        self.typeFic = None
        try:
            self.contFic = json.load(open(nom, "rb"))
            self.typeFic = "JSON"
        except json.JSONDecodeError:
            try:
                self.contFic = self.loadXml(nom)
                self.typeFic = "XML"
            except ET.ParseError:
                dossier = Path(nom+"_idx")
                if dossier.is_dir():
                    self.typeFic = "IDX"
                else:
                    print("erreur")
                    
    # guesser les traits d'un JSON
    def guessFeat(self):
        if self.typeFic == "JSON":
            tmp = set()
            for i in range(0,min(10,len(self.contFic))):
                try:
                    for elt in list(self.contFic[i][1][0].keys()):
                        tmp.add(elt)
                except:
                    pass
            tmp.discard("level")
            self.lstFeat = list(tmp)
    
    # conversion json -> idx
    def fromJson(self):
        self.idx = Index(self.ficOut)
        self.idx.initDB()
        self.idx.initFicDocument()
        self.idx.createBase(self.lstFeat)
        tabTok = [Token(x) for x in self.contFic]
        lstFeat = tabTok[2].getLstFeat()
        self.idx.maxMot = self.idx.indexation(tabTok,0)
        self.idx.sauveBase()
        self.idx.renameFicDocument()
        self.idx.closeBase()
        self.idx.createMeta()
        Path(self.ficOut).touch()
           
            

def main():
    # lecture paramètres
    parser = argparse.ArgumentParser(description="conversion d'index")
    parser.add_argument("-v", "--verbose", help="active affichage informations",action="store_true",default=False)
    parser.add_argument("-o", "--out", type=str, help="nom d'index en sortie")
    parser.add_argument("-i", "--in", type=str, help="nom d'index en entrée",required=True)
    parser.add_argument("-t", "--type", type=str, help="type d'index en sortie",default="json",choices=["idx","xml","json"])    
    args = parser.parse_args()
    args = vars(args)
    conv = Convert(args["in"],args["out"])
    conv.guessType()
    conv.guessFeat()
    conv.fromJson()
    
