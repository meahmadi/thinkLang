import os
import networkx as nx
import matplotlib.pyplot as plt

class DGraph(object):
	def __init__(self,path=None):
		self.fpath = path
		self.initData()


	def draw(self):
		pos=nx.spring_layout(self.G,scale=5,iterations=100)
		plt.title("Memory Graph")
		nx.draw(self.G,pos,node_color='#A0CBE2',width=0.2,edge_cmap=plt.cm.Blues,with_labels=True,font_size=12, node_size=30)
		
		labels = {}
		for u,v,d in self.G.edges_iter(data=True):
			if "label" in d:
				labels[(u,v)]=d["label"]
		nx.draw_networkx_edge_labels(self.G,pos,labels,clip_on=False,font_size=8)
		
		# scale the axes equally
		plt.savefig("out.png",dpi=600)
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
	
	def getOnlyNodeParam(self,nodes,param):
		if type(nodes) is not type([]):
			nodes = [nodes]
		self.getRefNodes(nodes)
		for node in nodes:
			has = [v for u,v,d in self.G.edges_iter(data=True) if u==node and  "label" in d and d["label"]=="has_"+param]
			if len(has)>0:
				self.getRefNodes(has)
				return has
		
			params = [d[param] for n,d in self.G.nodes_iter(data=True) if n==node and param in d]
			if len(params)>0:
				self.getRefNodes(params)
				return params
			
			defhas = [d["default"] for u,v,d in self.G.edges_iter(data=True) if u==node and  "label" in d and d["label"]=="has" and d["name"]==param]
			if len(defhas)>0:
				self.getRefNodes(defhas)
				return defhas
		return []

	def getOutLabeledNode(self,node,label,get_ref_nodes=True):
		result = [v for u,v,d in self.G.edges_iter(data=True) if u==node and "label" in d and d["label"]==label]
		if get_ref_nodes:
			self.getRefNodes(result)
		#print("outlabels:",node,label,result)
		return 	result
	def getInLabeledNode(self,node,label,get_ref_nodes=True):
		result = [v for u,v,d in self.G.edges_iter(data=True) if v==node and "label" in d and d["label"]==label]		
		if get_ref_nodes:
			self.getRefNodes(result)
		#print("inlabels:",node,label,result)
		return 	result
		
	def getRefNodes(self,nodes,exclude=None,):
		if exclude == None:
			exclude = []
		while True:
			toDel = []
			toAdd = []
			for node in nodes:
				exclude.append(node)
				adj = self.getOutLabeledNode(node,"ref",get_ref_nodes=False)
				#print("exclude:",exclude)
				#print("adj:",adj)
				adj = [ x for x in adj if x not in exclude]
				#print("adj1:",adj)
				if len(adj)>0:
					toDel.append(node)
					toAdd.extend(adj)
					#print(node,"->",adj)
			if len(toDel)==0:
				break;
			for node in toDel:
				nodes.remove(node)
			nodes.extend(toAdd)
		
	def getISANode(self,node):
		return self.getOutLabeledNode(node,"isa")
	def getISNode(self,node):
		return self.getOutLabeledNode(node,"is")
	
	
	def createLink(self,o1,o2,link_args={},o1_args={}):
		if type(o1) is not type([]):
			o1s = [o1]
		else:
			o1s = o1
		if type(o2) is not type([]):
			o2s = [o2]
		else:
			o2s = o2
		
		self.getRefNodes(o1s)
		self.getRefNodes(o2s)
		#print(o1s,o2s)
		for o1 in o1s:
			for o2 in o2s:
				self.G.add_edge(o1,o2,**link_args)
				for key in o1_args:
					self.G.node[o1][key] = o1_args[key]
		return o1s
	
	
	def getNodeParam(self,node,param):
		nodes = [node]
		while len(nodes)>0:
			newNodes = []
			for x in nodes:
				result = self.getOnlyNodeParam(x,param)
				if result is not None and len(result)>0:
					return result
				newNodes.extend( self.getISANode(x) )
				newNodes.extend( self.getISNode(x) )
			nodes = newNodes
	
	def setOnlyNodeParam(self,	node, param, value):
		if type(node) is not type([]):
			nodes = [node]
		else:
			nodes = node
		result = []
		for node in nodes:
			if node not in self.G:
				print("ERROR, node doesn't exists:",node)
				continue
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
				result.append(value)
			else:
				values = [value]
				self.getRefNodes(values)
				for v in values:
					self.G.add_edge(node,v,label="has_"+param)
				result.extend(values)
		return result

	def getNodeForSet(self,node,param):
		nodes = [node]
		while len(nodes)>0:
			newNodes = []
			for x in nodes:
				result = self.getOnlyNodeParam(x,param)
				if result is not None and len(result)>0:
					return result
				newNodes.extend( self.getISANode(x) )
				newNodes.extend( self.getISNode(x) )
			nodes = newNodes	
	
	def initData(self):
		#Setting to always init data :)
		if True or self.fpath is None or not os.path.exists(self.fpath):
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
		if os.path.exists(fp):
			os.remove(fp)
		nx.write_gml(self.G,fp)
	
	
if __name__ == "__main__":
	g = DGraph()
	g.writeData()