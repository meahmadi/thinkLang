import os
import networkx as nx

class DGraph(object):
	def __init__(self,path=None):
		self.fpath = path
		self.initData()
		
	def initialGraph(self):
		self.G = nx.MultiDiGraph()
		self.G.add_edge('_',"time")
		self.G.add_edge('_',"place")
		self.G.add_edge('_',"thing")
		self.G.add_edge('_', "number")
		self.G.add_edge('_', "event")
		self.G.add_edge('_', "word")
		

	def initData(self):
		if self.fpath is None or not os.path.exists(self.fpath):
			self.initialGraph()
		else:
			self.G = nx.read_gml(self.fpath)
			
	def writeData(self, fpath=None):
		if fpath==None:
			fp = self.fpath
		else:
			fp = fpath
		if fp==None:
			fp = "data.gml"
		nx.write_gml(self.G,fp)
	
	
if __name__ == "__main__":
	g = DGraph()
	g.writeData()