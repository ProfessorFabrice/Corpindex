#!/usr/bin/env python3

import pickle
import msgpack
import json

class PickleSerializer:
	@staticmethod
	def dumps(obj):
		return pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)

	@staticmethod
	def loads(data):
		return pickle.loads(data)

	@staticmethod
	def dump(obj, file):
		pickle.dump(obj, file, protocol=pickle.HIGHEST_PROTOCOL)

	@staticmethod
	def load(file):
		return pickle.load(file)


class MsgpackSerializer:
	@staticmethod
	def dumps(obj):
		return msgpack.packb(obj, use_bin_type=True)

	@staticmethod
	def loads(data):
		return msgpack.unpackb(data, raw=False)

	@staticmethod
	def dump(obj, file):
		msgpack.pack(obj, file, use_bin_type=True)

	@staticmethod
	def load(file):
		return msgpack.unpack(file, raw=False)


class JsonSerializer:
	@staticmethod
	def dumps(obj):
		return json.dumps(obj, ensure_ascii=False).encode("utf-8")

	@staticmethod
	def loads(data):
		if isinstance(data, bytes):
			data = data.decode("utf-8")
		return json.loads(data)

	@staticmethod
	def dump(obj, file):
		json.dump(obj, file, ensure_ascii=False, indent=2)

	@staticmethod
	def load(file):
		return json.load(file)
