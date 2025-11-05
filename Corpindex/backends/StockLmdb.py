#!/usr/bin/env python3

import lmdb
import os
import sys

class StockLmdb(dict):
	def __init__(self, commit_interval=1000000):
		self.env = None
		self.dico = None
		self.txn = None
		self.path = None
		self.count = 0
		self.commit_interval = commit_interval

	def open(self, name, mode="c"):
		self.path = name + ".lmdb"
		if not os.path.exists(self.path):
			os.makedirs(self.path, exist_ok=True)
		try:
			self.env = lmdb.open(
				self.path,
				map_size=8 * 1024 * 1024 * 1024,  # 8 Go
				max_dbs=1,
				writemap=True,
				sync=False,   # pour la vitesse, on s’en remet à commit()
				metasync=False
			)
			self.dico = self.env.open_db(b"main")
			self.txn = self.env.begin(db=self.dico, write=True)
		except Exception as e:
			sys.stderr.write(f"Erreur à l’ouverture de {self.path} : {e}\n")
			raise

	def __setitem__(self, c, v):
		if isinstance(c, str):
			c = c.encode("utf8")
		if isinstance(v, str):
			v = v.encode("utf8")
		self.txn.put(c, v)
		self.count += 1
		if self.count >= self.commit_interval:
			self._commit()

	def _commit(self):
		self.txn.commit()
		self.txn = self.env.begin(db=self.dico, write=True)
		self.count = 0

	def __getitem__(self, c):
		if isinstance(c, str):
			c = c.encode("utf8")
		with self.env.begin(db=self.dico, buffers=True) as txn:
			val = txn.get(c)
			if val is None:
				raise KeyError(c)
			return bytes(val)

	def keys(self):
		with self.env.begin(db=self.dico) as txn:
			return [k.decode("utf8") for k, _ in txn.cursor()]

	def sync(self):
		self._commit()
		if self.env:
			self.env.sync(True)

	def close(self):
		if self.txn:
			self._commit()
			self.txn = None
		if self.env:
			self.env.close()
			self.env = None
			self.dico = None


if __name__ == "__main__":
	s = StockLmdb(commit_interval=500000)
	s.open("teststock")

	for i in range(2_000_000):
		s[f"mot{i}"] = f"val{i}"

	s.sync()
	print(len(s.keys()))
	s.close()

