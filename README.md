# Corpindex

**Corpindex** est une bibliothèque Python pour la manipulation de corpus textuels. 
Elle permet de transformer un corpus en un *index* afin de pouvoir l’interroger très efficacement via un langage de requêtes étendues (CQPL).

Pensée pour le traitement de corpus volumineux enrichis de ressources dictionnairiques, Corpindex permet de travailler 
aussi bien sur des textes bruts que sur des textes déjà étiquetés. Elle offre une architecture modulaire adaptée à 
la construction d'outils spécialisés (concordanciers, moteurs de requêtes, chaînes de transduction, etc.).


---

## Fonctionnalités principales

- Indexation rapide et extensible de corpus textuels
- Langage de requêtes puissantes (conjonctions, filtres, transductions…)
- Intégration de dictionnaires et règles locales
- Support des formats bruts, XML, tabulés, Proteus, etc.
- Greffons configurables pour des chaînes de traitement personnalisées
- Utilisation possible en ligne de commande ou dans des applications Python

---

## Installation

La bibliothèque peut être installée directement depuis GitHub :

```bash
pip install git+https://github.com/ProfessorFabrice/corpindex.git
```

### Dépendances

- [`ply`](https://pypi.org/project/ply/)
- [`bsddb3`](https://pypi.org/project/bsddb3/)
- [`intervaltree`](https://pypi.org/project/intervaltree/)

---

## Architecture générale

```text
Textes ───► Indexation ───► Index
                              │
                     +--------┴--------+
                     │                 │
             Moteur de requêtes   Transduction
                     │                 │
                 Requêtes         Règles/TRS
                     │
                 Résultats
```

La bibliothèque repose sur trois modules principaux :
- Indexation du corpus et dictionnaires
- Moteur de requêtes** avec langage spécifique
- Transduction (marquage, modification de l’index)

Les ressources manipulées :
- Textes (bruts ou étiquetés, XML)
- Dictionnaires (tabulés ou format Proteus)
- Index (stockés sous forme de bases clé/valeur)
- Requêtes et règles (langages internes dédiés)

---

## Utilisation via CLI

Une fois installée, Corpindex expose plusieurs outils en ligne de commande :

| Commande       | Description                                                                 |
|----------------|-----------------------------------------------------------------------------|
| `buildidx`     | Construit un index à partir d’un corpus brut ou pré-analysé                |
| `query`        | Interroge un index avec une requête                                 |
| `hquery`       | Exécute des requêtes étendues (modification, marquage…)                    |
| `modidx`       | Applique des règles de transduction pour modifier un index                 |
| `idxexport`    | Exporte un index vers un format lisible ou exploitable (JSON, texte, etc.) |

### Exemples

**Indexer un corpus :**

```bash
usage: buildidx [-h] [-v] [-t {txt,xml,csv}] [-db {bsd,dbm,dpy}] [-lf LISTFEATURE [LISTFEATURE ...]] [-l LOG] [-d DICTS [DICTS ...]] [-dc DICTC [DICTC ...]] -i
                INPUT [INPUT ...] [-p PREPROC] [-f] [-r RULES [RULES ...]]

interrogation d'un index (version 0.9)

options:
  -h, --help            show this help message and exit
  -v, --verbose         active affichage informations
  -t {txt,xml,csv}, --type {txt,xml,csv}
                        type fichier en entrée
  -db {bsd,dbm,dpy}, --database {bsd,dbm,dpy}
                        type de bdd
  -lf LISTFEATURE [LISTFEATURE ...], --listfeature LISTFEATURE [LISTFEATURE ...]
                        liste de traits
  -l LOG, --log LOG     fichier de log
  -d DICTS [DICTS ...], --dicts DICTS [DICTS ...]
                        dictionaries simple words
  -dc DICTC [DICTC ...], --dictc DICTC [DICTC ...]
                        dictionaries compound words
  -i INPUT [INPUT ...], --input INPUT [INPUT ...]
                        fichiers à index
  -p PREPROC, --preproc PREPROC
                        fichiers contenant des règles (substitution)
  -f, --filtre          filtre sur "level"
  -r RULES [RULES ...], --rules RULES [RULES ...]
                        fichiers de règles de transduction
```

**Faire une requête simple :**

```bash
usage: query [-h] [-v] [-l] [-i INDEX [INDEX ...]] -q QUERY [QUERY ...] [-w] [-c] [-o {txt,txtmax,cqpl,latex,chuquet}] [-r RANGE] [-f FEATURE [FEATURE ...]]
             [-pt {out,proc,procout}] [-pp POSTPARAM [POSTPARAM ...]]

interrogation d'un index

options:
  -h, --help            show this help message and exit
  -v, --verbose         active affichage informations
  -l, --large           active le mode 'grand nombre de fichiers'
  -i INDEX [INDEX ...], --index INDEX [INDEX ...]
                        fichiers index
  -q QUERY [QUERY ...], --query QUERY [QUERY ...]
                        requête(s) CQPL/nom d'un fichier
  -w, --word            recherche de la forme
  -c, --calc            uniquement calcul de la taille du résultat
  -o {txt,txtmax,cqpl,latex,chuquet}, --output {txt,txtmax,cqpl,latex,chuquet}
                        type de sortie
  -r RANGE, --range RANGE
                        taille du contexte
  -f FEATURE [FEATURE ...], --feature FEATURE [FEATURE ...]
                        nature du trait
  -pt {out,proc,procout}, --typepost {out,proc,procout}
                        nature du post traitement
  -pp POSTPARAM [POSTPARAM ...], --postparam POSTPARAM [POSTPARAM ...]
                        paramètres supplémentaires pour le post traitement

```

**Exécuter une requête étendue :**

```bash
usage: hquery [-h] [-i INDEX [INDEX ...]] [-q QUERY] [-v] [-b] [-u] [-o OUTPUT] [-M MAX] [-m MIN] [-r] [-n] [-e] [-c] [-t TRAITS] [-s SEPARATEUR]

interrogation d'un index avec gestion d'empan

options:
  -h, --help            show this help message and exit
  -i INDEX [INDEX ...], --index INDEX [INDEX ...]
                        fichiers index
  -q QUERY, --query QUERY
                        requête (non CQPL)
  -v, --verbose         active affichage informations
  -b, --bug             active affichage bugs
  -u, --unverify        active recherche sans empilement de début d'empan (genre *? de regexp)
  -o OUTPUT, --output OUTPUT
                        nom du fichier index transformé
  -M MAX, --max MAX     taille max de l'empan
  -m MIN, --min MIN     taille min de l'empan
  -r, --remplace        remplace l'index (si -o avec nouveau nom sinon le même)
  -n, --noshow          pas d'affichage du résultat à l'écran
  -e, --efface          efface l'empan
  -c, --concat          concaténation de l'empan
  -t TRAITS, --traits TRAITS
                        traits à ajouter (si 'concat') de la forma t1:v1_t2:v2
  -s SEPARATEUR, --separateur SEPARATEUR
                        separateur si concaténation

```

**Modifier un index par transduction :**

```bash
usage: modidx [-h] [-v] [-db {bsd,dbm,dpy}] [-lf {f,l,c,r,p,d,s,m,fm,o,t,k,h} [{f,l,c,r,p,d,s,m,fm,o,t,k,h} ...]] [-l LOG] -i INDEX [INDEX ...] [-o OUTPUT]
              [-p PYTHON] [-pa PARAM] -r RULES [RULES ...]

modification de l'index

options:
  -h, --help            show this help message and exit
  -v, --verbose         active affichage informations
  -db {bsd,dbm,dpy}, --database {bsd,dbm,dpy}
                        type de bdd
  -lf {f,l,c,r,p,d,s,m,fm,o,t,k,h} [{f,l,c,r,p,d,s,m,fm,o,t,k,h} ...], --listfeature {f,l,c,r,p,d,s,m,fm,o,t,k,h} [{f,l,c,r,p,d,s,m,fm,o,t,k,h} ...]
                        liste de traits
  -l LOG, --log LOG     fichier de log
  -i INDEX [INDEX ...], --index INDEX [INDEX ...]
                        fichiers à index
  -o OUTPUT, --output OUTPUT
                        nom de la copie
  -p PYTHON, --python PYTHON
                        code python
  -pa PARAM, --param PARAM
                        paramètres python
  -r RULES [RULES ...], --rules RULES [RULES ...]
                        fichiers de règles de transduction

```

**Exporter un index :**

```bash
usage: idxexport [-h] [-v] [-n] [-d] [-p] [-l] [-o {txt,xml,json,dico,sdico,brut,txtsep}] [-i INDEX [INDEX ...]] [-f FEATURE [FEATURE ...]] [-ident IDENTIFIANT]

interrogation d'un index

options:
  -h, --help            show this help message and exit
  -v, --verbose         active affichage informations
  -n, --nosep           résultat sur une seule ligne
  -d, --div             affichage des div
  -p, --pos             affichage position offset
  -l, --level           ne retient que les traits avec le level le plus élevé
  -o {txt,xml,json,dico,sdico,brut,txtsep}, --output {txt,xml,json,dico,sdico,brut,txtsep}
                        type de sortie
  -i INDEX [INDEX ...], --index INDEX [INDEX ...]
                        fichiers index
  -f FEATURE [FEATURE ...], --feature FEATURE [FEATURE ...]
                        nature des traits
  -ident IDENTIFIANT, --identifiant IDENTIFIANT
                        identifiant
```

---

## Public cible

Corpindex n’est a priori pas destiné à l’utilisateur final non-informaticien, mais à des développeurs ou 
chercheurs souhaitant créer leurs propres outils de TAL ou concordanciers. Il se situe dans la lignée 
d’outils comme **Unitex**, **Nooj** ou **Intex**, tout en étant écrit entièrement en **Python**.

---

## Licence


Ce projet est distribué sous la licence [CeCILL v2.1](https://cecill.info/licences/Licence_CeCILL_V2.1-fr.html), compatible avec la GNU GPL.

Vous pouvez utiliser, modifier et redistribuer ce logiciel selon les termes de cette licence.

Un exemplaire de la licence est fourni dans le fichier `LICENSE`.
