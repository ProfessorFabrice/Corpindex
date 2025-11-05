#!/usr/bin/env python3

# classe pour les divs
class Node:
	def __init__(self, data):
		self.fils = None
		self.frere = None
		self.data = data

	def insert(self, data,pos=1):
		print("INSERT",data)
		self.insert2(data,pos)

	def insert2(self, data,pos=1,n=0):
		print(n*" ","n.insert("+str(data)+")",self.data)
		if data[1] < self.data[2]:
			print("\t1",data,self.data)
			if data[2] <= self.data[1]:
				print("\t\t",data,self.data)
				ntmp = Node(self.data)
				ntmp.fils = None
				ntmp.frere = self.frere
				tmp = self.data
				self.data = data
				ntmp.data = tmp
			else:
				print("\t3",data,self.data)
				if self.fils is None:
					self.fils = Node(data)
				else:
					self.fils.insert2(data,pos+1,n+1)
		else:
			print("\t2",data,self.data)			
			if self.frere is None:
				self.frere = Node(data)
			else:
				self.frere.insert2(data,pos,n+1)
			
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

	def getDivPosSave(self,pos):
		print(pos,self.data)
		if pos>=self.data[1] and pos<=self.data[2]:
			if self.fils != None:
				return [self.data]+self.fils.getDivPosSave(pos)
			else:
				return [self.data]
		else:
			while not (pos>=self.data[1] and pos<=self.data[2]) and self.frere != None:
				self.frere = self.frere.frere
			if self.frere!= None:
				return self.frere.getDivPosSave(pos)
			else:
				return []

					
	def affiche(self,dec,prov):
		print(dec*" ",prov,self.data)
		if self.fils != None:
			self.fils.affiche(dec+1,"fils")
		if self.frere != None:
			self.frere.affiche(dec,"frere")


if __name__ == '__main__':
	n = Node(['_top',1,100000])
	n.insert(['chanson1', 1, 33])
	n.insert(['strophe_1_1', 4, 15])
	n.insert(['strophe_1_2', 16, 26])
	n.insert(['title1', 1, 3])
	n.insert(['strophe_1_3', 27, 32])
	n.affiche(0,"root")
	#print(n.getDivPosSave(2))
