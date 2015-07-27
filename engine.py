import sys
from lparser import LParser
from lnetwork import DGraph
import random
_debug_ = 0

class Engine(object):
	def __init__(self,data_path=None):
		global _debug_
		
		if _debug_>3 : print("> init Engine.....")
		
		self.data_path = data_path
		
		if _debug_>3 : print("> ",self.data_path)
		
		self.graph = DGraph(self.data_path)
		self.parser = LParser(self) 
	
	def drawGraph(self):
		self.graph.draw()
		
	def interpret(self,line):
		global _debug_
		
		if len(line.strip())==0:
			return
		
		if _debug_>0 : print("> ",line.strip())
		
		self.parser.parseLine(line,_debug_>4)
		

	def link(self,o1,o2,type1,link_args={},o1_args={}):
		if o1=="_":	o1 = "var_"+str(int(random.random()*100000000))
		if o2=="_":	o2 = "var_"+str(int(random.random()*100000000))
		
		return self.graph.createLink(o1,o2,type1,link_args,o1_args)

	def is_(self,sbj,obj, argdefs):
		result = self.link(sbj,obj,"is")
		self.has_(sbj,argdefs)
		return result
		
		
	def isa_(self,sbj,obj,args):
		result = self.link(sbj,obj,"isa")
		for k,v in args.items():
			self.graph.setOnlyNodeParam(sbj,k,v)
		return result

	def ref_(self,sbj,obj):
		return self.link(sbj,obj,"ref")

	def fact_(self,sbj,obj,action,args):
		result = self.link(sbj,obj,action)
		for k,v in args.items():
			self.graph.setOnlyNodeParam(sbj,k,v)
		return result
	
	def has_(self,sbj,args):
		for key in args:
			typ,default = args[key].split()
			self.link(sbj,typ,"has",{"name":key,"default":default})#,{key:args[key]})
		return sbj
	
	def set_param_(self,tok):
		# print(tok.assignmentfact)
		tokens = tok.assignmentfact[0]
		value = tok.assignmentfact[1]
		# print ("tokens",tokens)
		# print ("value",value)
		
		obj = tokens[:-1]
		last = obj[0]
		# print ("obj",obj)
		# print ("last", last)
		for arg in obj[1:]:
			last = self.graph.getNodeForSet(last,arg)
			# print ("last:",last)
			if last == None or len(last)==0:
				print ("> ERROR finding", ".".join(list(obj)))
				return []
		# print ("Setting",last,tokens[-1],value)
		return self.graph.setOnlyNodeParam(last,tokens[-1],value)
		
		
	def get_param_(self,tokens):
		tokens = tokens[0]
		last = tokens[0]
		for arg in tokens[1:]:
			last = self.graph.getNodeParam(last,arg)
			if last == None:
				print ("> ERROR finding", ".".join(list(tokens)))
				return []
		return last

	
	def rule_(self):
		if _debug_>1 : print ("> rule")

	def start_scene(self):
		if _debug_>1 : print ("> startscene")
		
	def end_scene(self):
		if _debug_>1 : print ("> endscene")
		
	def exists_(self):
		if _debug_>1 : print ("> existance")	
	
	
	def say_global_(self,tokens):
		print(tokens[1])
		return None
	def say_scene_ (self,tokens):
		return self.say_global_(tokens)
	

if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser()
	
	parser.add_argument("-v","--verbose", help="increase verbose",  type=int, choices=[0, 1, 2, 3, 4, 5], default=0)
	parser.add_argument("-i", "--inputfile", help="input file name", type=argparse.FileType('rt'),  action="store",  default=None)
	parser.add_argument("-d", "--data", help="engin data file", type=str,  action="store",  default=None)
	parser.add_argument("-q", "--quiet", help="run input file and exit", action='store_true', default=False)
	parser.add_argument("-s", "--draw", help="draw graph at execution end", action='store_true', default=False)
	args = parser.parse_args()
	
	if args.verbose:
		_debug_ = args.verbose
	
	engine = Engine(args.data)
	
	if args.inputfile is None:
		import fileinput
		for l in fileinput.input():
			engine.interpret(l)
	else:
		for l in args.inputfile:
			engine.interpret(l)
	if args.draw:
		engine.drawGraph()
	
	if not args.quiet:
		for line in sys.stdin:
			engine.interpret(line)
			if args.draw:
				engine.drawGraph()
