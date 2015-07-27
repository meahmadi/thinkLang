import os
from graph import Graph

class DGraph(object):
	def __init__(self,path=None):
		self.fpath = path
		if self.fpath==None:
			self.fpath = "memory.db"
		self.initData()

	def initData(self):
		#Setting to always init data :)
		if True or self.fpath is None or not os.path.exists(self.fpath):
			self.initialGraph()
		else:
			self.G = Graph(self.fpath,keepOld=True)
			
	def writeData(self, fpath=None):
		self.G.commit()

	def initialGraph(self):
		self.G = Graph(self.fpath)
		self.G.addEdge('_',"time")
		self.G.addEdge('_',"place")
		self.G.addEdge('_',"thing")
		self.G.addEdge('_', "number")
		self.G.addEdge('_', "event")
		self.G.addEdge('_', "word")

		
	def draw(self):
		#pos=nx.spring_layout(self.G,scale=5,iterations=100)
		#plt.title("Memory Graph")
		#nx.draw(self.G,pos,node_color='#A0CBE2',width=0.2,edge_cmap=plt.cm.Blues,with_labels=True,font_size=12, node_size=30)
		
		#labels = {}
		#for u,v,d in self.G.edges_iter(data=True):
		#	if "label" in d:
		#		labels[(u,v)]=d["label"]
		#nx.draw_networkx_edge_labels(self.G,pos,labels,clip_on=False,font_size=8)
		
		# scale the axes equally
		#plt.savefig("out.png",dpi=600)
		#plt.show()
		pass

		
	def hasNodeParam(self,node,param):
		return not(self.getNodeParam == None)
	
	def getOnlyNodeParam(self,nodes,param):
		if type(nodes) is not type([]):
			nodes = [nodes]
		self.getRefNodeIDs(nodes)
		for node in nodes:
			nodeid = self.G.getNode(node)
			hasp = self.G.getRelations( inid = nodeid, label= "has_"+param )
			#has = [v for u,v,d in self.G.edges_iter(data=True) if u==node and  "label" in d and d["label"]=="has_"+param]
			if len(hasp)>0:
				hasp_names = self.G.getNodesNames(hasp)
				self.getRefNodes(hasp_names)
				return hasp_names
		
			params = self.G.getAttrib(nodeid,param)
			#params = [d[param] for n,d in self.G.nodes_iter(data=True) if n==node and param in d]
			if params is not None:
				return params
			
			defhas = list( filter((lambda x: x is not None), [self.G.getAttrib(x,"default") for x in  self.G.getRelations( inid = nodeid, label = "has" , args = {"name":param})] ) )
			#defhas = [d["default"] for u,v,d in self.G.edges_iter(data=True) if u==node and  "label" in d and d["label"]=="has" and d["name"]==param]
			if len(defhas)>0:
				defhas_names = self.G.getNodesNames(defhas)
				self.getRefNodes(defhas_names)
				return defhas_names
		return []

	def getOutLabeledNode(self,node,label,get_ref_nodes=True):
		nodeid = self.G.getNode(node)
		result = self.G.getRelations(inid=nodeid,label=label)
		result_names = self.G.getNodesNames(result)
		#result = [v for u,v,d in self.G.edges_iter(data=True) if u==node and "label" in d and d["label"]==label]
		if get_ref_nodes:
			self.getRefNodes(result_names)
		return 	result_names
	def getInLabeledNode(self,node,label,get_ref_nodes=True):
		nodeid = self.getNode(node)
		result = self.G.getRelations(outid=nodeid,label=label)
		result_names = self.G.getNodesNames(result)
		#result = [v for u,v,d in self.G.edges_iter(data=True) if v==node and "label" in d and d["label"]==label]		
		if get_ref_nodes:
			self.getRefNodes(result_names)
		return 	result_names
		
	def getRefNodeIDs(self,nodes,exclude=None,):
		if exclude == None:
			exclude = []
		x1 = self.G.getNodesNames(nodes)
		x2 = self.G.getNodesNames(exclude)
		self.getRefNodes(x1,x2)
		x1_id = self.G.getNodesIDs(x1)
		x2_id = self.G.getNodesIDs(x2)
		for x in x1_id:
			if x not in nodes:nodes.append(x)
		to_delete = []
		for x in nodes:
			if x not in x1_id:to_delete.append(x)
		for x in to_delete:
			nodes.remove(x)
	
		for x in x2_id:
			if x not in exclude:exclude.append(x)
		to_delete = []
		for x in exclude:
			if x not in x2_id:to_delete.append(x)
		for x in to_delete:
			exclude.remove(x)
	
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
	
	
	def createLink(self,o1,o2,label="",link_args={},o1_args={}):
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
				self.G.addEdge(o1,o2,label,link_args)
				if len(o1_args)>0:
					self.G.updateAttribs(self.G.getNode(o1),o1_args)
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
					t = float(value)  # @UnusedVariable
					refValue = False
				except ValueError:
					pass

			if not refValue:
				self.G.updateAttrib(self.G.getNode(node),param,value)
				#self.G.node[node][param] = value
				result.append(value)
			else:
				values = [value]
				self.getRefNodes(values)
				for v in values:
					self.G.addEdge(node,v,"has_"+param)
					#self.G.add_edge(node,v,label="has_"+param)
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
		
	
if __name__ == "__main__":
	g = DGraph()
	g.writeData()