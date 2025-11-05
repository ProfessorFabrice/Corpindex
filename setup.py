#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
	name='Corpindex',
	version='0.1',
	packages=find_packages(),
	install_requires=[
        "ply",
        "bsddb3",
        "intervaltree",  # version libre
    ],
	entry_points={
		'console_scripts': [
			'buildidx = Corpindex.cli_buildidx:main',
			'query = Corpindex.cli_query:main',
			'hquery = Corpindex.cli_hquery:main',
			'idxexport = Corpindex.cli_idxexport:main',
			'idxinfo = Corpindex.cli_idxinfo:main',
			'modidx = Corpindex.cli_modidx:main',
		],
	})
