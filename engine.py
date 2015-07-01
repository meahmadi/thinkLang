from lparser import parseLine
import lnetwork
_debug_ = 0

class Engine(object):
	def __init__(self,data_path=None):
		global _debug_
		
		if _debug_>3 : print("init Engine.....")
		
		self.data_path = data_path
		
		if _debug_>3 : print(self.data_path)
		
		self.graph = lnetwork.DGraph(self.data_path)
		
	def interpret(self,line):
		global _debug_
		
		if len(line.strip())==0:
			return
		
		if _debug_>0 : print(line)
		
		parse = parseLine(line,_debug_>4)
		
		if parse is None:
			self.syntaxError(line,parse)
			return
		
		if _debug_>3 : print (type(parse),"\n", dir(parse),"\n", parse,"\n", dict(parse))
		
		if parse.isfact: self.interpret_isfact(parse)
		elif parse.isafact: self.interpret_isafact(parse)
		elif parse.reffact: self.interpret_reffact(parse)
		elif parse.fact: self.interpret_otherfact(parse)
		elif parse.rule: self.interpret_rule(parse)
		elif parse.startscene: self.interpret_startscene(parse)
		elif parse.endscene: self.interpret_endscene(parse)
		elif parse.existance: self.interpret_existance(parse)
		elif parse.comment: pass
		elif _debug_>0 : print ("not supported")	#syntaxError(line,parse)

	def interpret_isfact(self,parse):
		if _debug_>1 : print ("isfact")
		self.graph.G.add_edge(parse.isfact.sbj,parse.isfact.obj,type="is")
		
	def interpret_isafact(self,parse):
		if _debug_>1 : print ("isafact")
		self.graph.G.add_edge(parse.isafact.sbj,parse.isafact.obj,type="isa")
#		if parse.isafact.args:
#			for arg in parse.isafact.args:
#				self.graph.G.node[parse.isafact.sbj][arg[0]] = arg[1]
		
	def interpret_reffact(self,parse):
		if _debug_>1 : print ("reffact")
		self.graph.G.add_edge(parse.reffact.sbj,parse.reffact.obj,type="ref")
		
	def interpret_otherfact(self,parse):
		if _debug_>1 : print ("otherfact")
		self.graph.G.add_edge(parse.fact.sbj,parse.fact.obj,type=parse.fact.action)
		
	def interpret_rule(self,parse):
		if _debug_>1 : print ("rule")

	def interpret_startscene(self,parse):
		if _debug_>1 : print ("startscene")
		
	def interpret_endscene(self,parse):
		if _debug_>1 : print ("endscene")
		
	def interpret_existance(self,parse):
		if _debug_>1 : print ("existance")	
		
	def syntaxError(self,line,parse):
		print("Syntax Error:%s"%line)
		exit(1)
	


if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser()
	
	parser.add_argument("-v","--verbose", help="increase verbose",  type=int, choices=[0, 1, 2, 3, 4, 5], default=0)
	parser.add_argument("-i", "--inputfile", help="input file name", type=argparse.FileType('rt'),  action="store",  default=None)
	parser.add_argument("-d", "--data", help="engin data file", type=str,  action="store",  default=None)
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
	engine.graph.writeData()