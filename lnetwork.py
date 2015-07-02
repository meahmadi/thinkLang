import os
import networkx as nx
import matplotlib.pyplot as plt

class DGraph(object):
	def __init__(self,path=None):
		self.fpath = path
		self.initData()


	def draw(self):
		pos=nx.spring_layout(self.G)
		plt.title("Memory Graph")
		nx.draw(self.G,pos,node_color='#A0CBE2',width=0.2,edge_cmap=plt.cm.Blues,with_labels=True,font_size=12, node_size=30)
		# scale the axes equally
		plt.savefig("out.png")
		plt.show()
		
	def initialGraph(self):
		self.G = nx.DiGraph()
		self.G.add_edge('_',"time")
		self.G.add_edge('_',"place")
		self.G.add_edge('_',"thing")
		self.G.add_edge('_', "number")
		self.G.add_edge('_', "event")
		self.G.add_edge('_', "word")
		
	def hasNodeParam(self,node,param):
		return not(self.getNodeParam == None)
	
	def getOnlyNodeParam(self,node,param):
		has = [v for u,v,d in self.G.edges_iter(data=True) if u==node and  "label" in d and d["label"]=="has_"+param]
		if len(has)>0:
			return has[0]
		
		params = [d[param] for n,d in self.G.nodes_iter(data=True) if n==node and param in d]
		if len(params)>0:
			return params[0]
		
		defhas = [d["default"] for u,v,d in self.G.edges_iter(data=True) if u==node and  "label" in d and d["label"]=="has" and d["name"]==param]
		if len(defhas)>0:
			return defhas[0]
		return None

	def getISANode(self,node):
		return self.getOutLabeledNode(node,"isa")
	def getISNode(self,node):
		return self.getOutLabeledNode(node,"is")
	def getOutLabeledNode(self,node,label):
		return [v for u,v,d in self.G.edges_iter(data=True) if u==node and "label" in d and d["label"]==label]
		
	def getNodeParam(self,node,param):
		nodes = [node]
		while len(nodes)>0:
			newNodes = []
			for x in nodes:
				result = self.getOnlyNodeParam(x,param)
				if result is not None:
					return result
				newNodes.extend( self.getISANode(x) )
				newNodes.extend( self.getISNode(x) )
			nodes = newNodes
	
	def setOnlyNodeParam(self,	node, param, value):
		if node not in self.G:
			print("ERROR, node doesn't exists:",node)
			return None
		value = value.strip()
		refValue = True
		if (value.startswith("'") and value.endswith("'")) or (value.startswith('"') and value.endswith('"')):
			refValue = False
		else:
			try:
				t = float(value)
				refValue = False
			except ValueError:
				pass

		if not refValue:
			self.G.node[node][param] = value
		else:
			self.G.add_edge(node,value,label="has_"+param)
		return value

	def getNodeForSet(self,node,param):
		nodes = [node]
		while len(nodes)>0:
			newNodes = []
			for x in nodes:
				result = self.getOnlyNodeParam(x,param)
				if result is not None:
					return result
				newNodes.extend( self.getISANode(x) )
				newNodes.extend( self.getISNode(x) )
			nodes = newNodes	
	
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