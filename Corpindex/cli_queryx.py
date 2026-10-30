#!/usr/bin/env python3

import argparse
import sys
import os
from typing import List, Dict, Any, Optional

from .RequeteIndex import RequeteIndex as Requete
from .Post import Post
from .Index import Index

class CIQuery:
    """
    Classe principale pour l'interrogation d'index Corpindex.
    Gère les arguments en ligne de commande et l'exécution des requêtes.
    """

    def __init__(self):
        self.verbose: bool = False
        self.large_mode: bool = False
        self.database_type: str = 'bsd'
        self.serializer_type: str = 'pickle'
        self.index_files: List[str] = []
        self.queries: List[str] = []
        self.word_search: bool = False
        self.calc_only: bool = False
        self.output_format: str = 'txt'
        self.context_size: int = 5
        self.features: List[str] = ['f']
        self.post_type: str = 'out'
        self.post_params: Optional[List[str]] = None
        self.results: List[Dict[str, Any]] = []

    def parse_arguments(self) -> None:
        """Parse les arguments en ligne de commande."""
        parser = argparse.ArgumentParser(
            description="Interrogation d'un index Corpindex",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )

        parser.add_argument(
            "-v", "--verbose",
            help="Active l'affichage des informations de débogage",
            action="store_true",
            default=False
        )
        parser.add_argument(
            "-l", "--large",
            help="Active le mode 'grand nombre de fichiers'",
            action="store_true",
            default=False
        )
        parser.add_argument(
            "-db", "--database",
            help="Type de base de données",
            default='bsd',
            choices=['bsd', 'dbm', 'dpy', "lmdb"]
        )
        parser.add_argument(
            "-s", "--serializer",
            help="Type de serializer",
            default='pickle',
            choices=['pickle', 'json', 'msgpack']
        )
        parser.add_argument(
            '-i', "--index",
            type=str,
            nargs='+',
            help='Fichiers index à interroger',
            required=True
        )
        parser.add_argument(
            "-q", "--query",
            type=str,
            nargs='+',
            help="Requête(s) CQPL ou nom d'un fichier contenant des requêtes",
            required=True
        )
        parser.add_argument(
            "-w", "--word",
            help="Recherche de la forme exacte (pour les fichiers de requêtes)",
            action="store_true",
            default=False
        )
        parser.add_argument(
            "-c", "--calc",
            help="Calcule uniquement la taille du résultat sans générer les concordances",
            action="store_true",
            default=False
        )
        parser.add_argument(
            "-o", "--output",
            help="Type de sortie pour les résultats",
            default="txt",
            choices=['txt', 'txtmax', "cqpl", "latex", "chuquet"]
        )
        parser.add_argument(
            "-r", "--range",
            help="Taille du contexte autour du pivot",
            default=5,
            type=int
        )
        parser.add_argument(
            "-f", "--feature",
            type=str,
            nargs='+',
            help="Nature des traits à afficher",
            default=['f']
        )
        parser.add_argument(
            "-pt", "--typepost",
            help="Nature du post-traitement",
            choices=['out', 'proc', 'procout'],
            default='out'
        )
        parser.add_argument(
            "-pp", "--postparam",
            help="Paramètres supplémentaires pour le post-traitement",
            type=str,
            nargs='+'
        )

        args = parser.parse_args()
        self._set_attributes_from_args(args)

    def _set_attributes_from_args(self, args: argparse.Namespace) -> None:
        """Initialise les attributs de la classe à partir des arguments."""
        self.verbose = args.verbose
        self.large_mode = args.large
        self.database_type = args.database
        self.serializer_type = args.serializer
        self.index_files = args.index
        self.context_size = args.range
        self.output_format = args.output
        self.word_search = args.word
        self.calc_only = args.calc
        self.features = args.feature
        self.post_type = args.typepost
        self.post_params = args.postparam

        # Gestion spéciale pour les requêtes
        if len(args.query) == 1 and os.path.isfile(args.query[0]):
            self._load_queries_from_file(args.query[0])
        else:
            self.queries = [q for q in args.query if q.strip() and not q.startswith('#')]

    def _load_queries_from_file(self, file_path: str) -> None:
        """Charge les requêtes depuis un fichier."""
        with open(file_path, 'r', encoding='utf-8') as f:
            if self.word_search:
                self.queries = [
                    f'[f="{line.rstrip()}"]'
                    for line in f
                    if line.strip() and not line.startswith('#')
                ]
            else:
                self.queries = [
                    line.rstrip()
                    for line in f
                    if line.strip() and not line.startswith('#')
                ]

    def execute_queries(self) -> None:
        """Exécute toutes les requêtes sur les index spécifiés."""
        req = Requete()
        total_results = 0

        try:
            for index_file in self.index_files:
                if self.verbose:
                    sys.stderr.write(f"Traitement de l'index: {index_file}\n")

                idx = Index(
                    index_file,
                    self.database_type,
                    self.serializer_type,
                    self.verbose,
                    sys.stderr
                )
                idx.lectureBase()

                if self.verbose:
                    sys.stderr.write('Index initialisé\n')

                for query_num, query in enumerate(self.queries, 1):
                    if not query.strip() or query.startswith('#'):
                        continue

                    query += " "  # Sentinelle
                    req.putIndex(idx)
                    req.putRequete(query)

                    if self.verbose:
                        actual_query = req.analyseurCqp.requete
                        sys.stderr.write(
                            f"Requête {query_num}: {query} ({actual_query})\n"
                        )

                    results = req.calculRequete()
                    total_results += len(results)

                    if self.verbose:
                        sys.stderr.write(f'Résultats: {len(results)}\n')

                    self.results.append({
                        'index': idx,
                        'results': results,
                        'query': query.rstrip(),
                        'index_name': os.path.basename(idx.getName())
                    })

                if self.large_mode:
                    idx.close()

            if self.calc_only:
                print(total_results)
            else:
                self._process_concordances()

        except OSError as err:
            if err.errno == 24:  # Too many open files
                print("Trop de fichiers ouverts, essayez l'option '-l'")
                sys.exit(1)
            else:
                raise
        except Exception as err:
            print(f"Erreur: {str(err)}")
            sys.exit(1)

    def _process_concordances(self) -> None:
        """Traite les résultats pour générer les concordances."""
        if self.verbose:
            sys.stderr.write('Calcul des concordances...\n')

        tabconc = []
        tabinfo = []

        for result in self.results:
            idx = result['index']
            res = result['results']
            ident = result['query']

            if self.large_mode:
                idx.lectureBase()

            tabinfo.append([result['index_name'], ident])
            info_index = len(tabinfo) - 1

            for concordance in idx.getTabConc(res, self.context_size, -1):
                tabconc.append([info_index, concordance])

            if self.large_mode:
                idx.close()

        if self.verbose:
            sys.stderr.write('Application des filtres...\n')

        params = {
            'att': self.features,
            'type': self.post_type,
            'id': '1',
            'value': '',
            'name': f'ci_{self.output_format}'
        }

        if self.post_params:
            for param in self.post_params:
                if ':' in param:
                    key, value = param.split(':', 1)
                    params[key] = value

        post = Post(params, tabconc, tabinfo)
        post.process()
        tabconc = post.getConc()

def main() -> None:
    """Point d'entrée principal du programme."""
    ci_query = CIQuery()
    ci_query.parse_arguments()
    ci_query.execute_queries()

if __name__ == '__main__':
    main()
