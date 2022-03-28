#!/usr/bin/python3


class ConcError(Exception):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)
		

class TokError(Exception):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)
