# classe pour les divs
class Node:
	def __init__(self, data):
		self.fils = None
		self.frere = None
		self.data = data

	def insert(self, data,pos=1):
		if data[1] < self.data[2]:
			if data[2] < self.data[1]:
				ntmp = Node(self.data)
				ntmp.fils = self.fils
				ntmp.frere = self.frere
				ntmp.data = data
				self.fils = None
				self.frere = ntmp
			else:
				if self.fils is None:
					self.fils = Node(data)
				else:
					self.fils.insert(data,pos+1)
		else:
			if self.frere is None:
				self.frere = Node(data)
			else:
				self.frere.insert(data,pos)
			
	def getDivPos(self,pos):
		if pos>=self.data[1] and pos<=self.data[2]:
			if self.fils != None:
				return [self.data]+self.fils.getDivPos(pos)
			else:
				return [self.data]
		else:
			if self.frere != None:
				return self.frere.getDivPos(pos)
			else:
				return []


