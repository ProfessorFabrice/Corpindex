# Corpindex

L'ensemble de la bibliothèque a été concue de manière à traiter des
corpus de taille importante[^2] sur lesquels sont projetés des
ressources dictionnairiques. Il est possible de traiter des textes
bruts, uniquement composés de caractères, ou déjà étiquetés et de
proposer un langage de requête de haut niveau.

La bibliothèque est écrite en [python]{.sans-serif}[^3] et peut être
utilisée aussi bien en ligne de commande qu'au sein d'applications
graphiques. Cette bibliothèque a été écrite non pas pour
« *l'utilisateur final non spécialiste en informatique* » mais au
contraire pour permettre le développement d'outils spécifiques. Ce type
d'outils s'inscrit dans la famille des concordanciers utilisant des
dictionnaires et des grammaires locales comme
[Intex]{.sans-serif} / [Nooj]{.sans-serif} ([@MaxSil1993; @MaxSil2005])
ou [Unitex]{.sans-serif} ([@SebPau2002]).

## Architecture

La figure [1](#FIGCORP1){reference-type="ref" reference="FIGCORP1"}
présente les différents modules de la bibliothèque (Indexation, moteur
de requêtes, transduction) et la manière dont ils peuvent interagir
ainsi que les différentes ressources créées et / ou manipulées (textes,
dictionnaires, index, règles, requêtes). La bibliothèque intègre
également un mécanisme de greffons permettant de mettre en place une
chaîne de traitements.

Les ressources peuvent être de différentes natures :

-   texte brut pour des textes en entrée ;

-   format texte tabulé pour certains dictionnaires ;

-   description [proteus]{.sans-serif} pour certains dictionnaires ;

-   XML pour des textes étiquetés ;

-   langages spécifiques (cf. infra) pour les requêtes et la
    transduction ;

-   base de donnée *clé / valeur* pour l'index[^4].

## Construction de l'index

Ce module construit à partir d'un texte, étiqueté ou non, une
représentation du texte sous forme d'un index. Si le texte n'est pas
déjà étiqueté alors il est possible d'utiliser des dictionnaires de mots
simples et de mots composés qui réaliseront un étiquetage préalable sans
levée d'ambiguïté. Une prise en compte partielle des balises XML permet
d'ajouter une dimension structurelle à l'index créé.

Ce principe offre une très bonne performance en ce qui concerne le temps
de calcul puisque le nombre d'éléments, et donc de clés, à indexer croit
très rapidement 

## Requête

L'index construit, il est possible d'utiliser un langage capable de
faire des requêtes non seulement sur la forme des mots mais aussi sur
les informations attachées à ce mot. Le langage que nous avons développé
fait explicitement référence à CQP (Corpus Query Language) développé à
l'université de Stuttgart [@OliChr1994] dont il reprend une partie de la
syntaxe qui offre l'avantage d'être explicite sans être verbeuse. À
titre d'exemple la requête suivante :

    [l="un"][c~"^N"][*]?([l="vert"]|[l="jaune"])

permet d'extraire les suites de mots dont le premier mot a pour lemme
« un » suivi d'un mot dont la catégorie commence par « N » (i.e. un nom
dans le jeux d'étiquette que nous avons choisi) suivi, directement ou à
une distance de 1, d'un mot dont le lemme est soit « jaune » soit
« vert ». Le langage permet en outre de restreindre la recherche à
l'aide de l'opérateur `within` sur une partie du document. C'est dans ce
cas la valeur des identifiants que est prise en compte.

    [c~"^V"][*]?[*]?[l="human"][l="right"] within ~"H\$"

Dans l'exemple précédant la recherche porte exclusivement sur des
parties de documents encadrés par une balise avec un identifiant
finissant par « H ».

## Modification de l'index

La bibliothèque intègre la possibilité de modifier un index déjà
construit. Le langage est similaire au langage de requête à la
différence que chaque description de token peut être associée à un motif
de remplacement. Nous donnons ci après quelques exemples :

-   Recherche du lemme `pour` précédé d'un déterminant et attribution de
    l'étiquette de catégorie `N-ms` (nom masculin singulier).

        [c~"^D..s"][l="pour"/c="N-ms"]

-   Remplacement des quatre tokens `droits`, `de`, `l’`, `homme` trouvés
    consécutivement par un seul.

        [f="droits"/][f="de"/][f="l'"/][f="homme"/
                    f="droits de l'homme",l="droits de l'homme",c="N-mp"]

-   Mémorisation de valeurs (`$`) et réutilisation ultérieur (`#`).

        [l="nom"/f="$1",c="$3"][l~"^(propre|composé|locatif)$"/
                            f="$2",f2="#1 #2",l="$4",l2="nom #4",c="#3"]
        [f="pommes"/c="$1"][f="de"/][f="terre"
                         /f="pommes de terre",l="pomme de terre",c="#1"]

-   Ajout d'une balise de structure `<exp>`

        [l="prendre"/otag="exp"][f="la"][f="tête"/ctag="exp"]

-   Utilisation de fonctions [python]{.sans-serif} (possiblement écrite
    spécifiquement)

         [c~"^N"/l="$1",t="''.join(sorted([x for x in '#1']))"]
