import sys
import functools
import inspect
from pyparsing import *  # @UnusedWildImport


def parse_action(f):
	"""
	Decorator for pyparsing parse actions to ease debugging.

	pyparsing uses trial & error to deduce the number of arguments a parse
	action accepts. Unfortunately any ``TypeError`` raised by a parse action
	confuses that mechanism.

	This decorator replaces the trial & error mechanism with one based on
	reflection. If the decorated function itself raises a ``TypeError`` then
	that exception is re-raised if the wrapper is called with less arguments
	than required. This makes sure that the actual ``TypeError`` bubbles up
	from the call to the parse action (instead of the one caused by pyparsing's
	trial & error).
	"""
	num_args = len(inspect.getargspec(f).args)
	if num_args > 4:
		raise ValueError('Input function must take at most 3 parameters.')

	@functools.wraps(f)
	def action(*args):
		if len(args) < num_args:
			if action.exc_info:
				print( action.exc_info[0], action.exc_info[1], action.exc_info[2], action.exc_info[3])
		action.exc_info = None
		try:
			x = args[:-(num_args + 1):-1]
			x = x[::-1]
			return f(*x)
		except TypeError as e:
			action.exc_info = sys.exc_info()
			print(e)
			raise

	action.exc_info = None
	return action

class LParser(object):
	def __init__(self,engine1):
		self.engine = engine1
		
		self.first = Word(alphas+"_", exact=1)
		self.rest = Word(alphanums+"_")

		self.LPAREN = Suppress("(")
		self.RPAREN = Suppress(")")
		self.DOT = Suppress(".")
		self.SEMICOLON = Suppress(";")

		self.types = ["time","place","thing", "number", "event", "word"]
		self.keywords = Or(self.types)

		self.identifier = Or([self.keywords , Combine(self.first+Optional(self.rest))])
		self.variable = Combine(self.identifier+"?")
		
		self.gparameter = Group(Or([self.identifier,self.variable])+self.DOT+self.identifier+ZeroOrMore(self.DOT+self.identifier))
		self.sparameter = Group(Or([self.identifier,self.variable])+self.DOT+self.identifier+ZeroOrMore(self.DOT+self.identifier))

		self.value = Forward()

		self.argumentDef = Group(self.identifier + self.identifier +  Suppress("=") + self.value )

		self.argument = Group(self.identifier + self.value )


		self.name = Or([self.identifier, self.variable, self.sparameter, self.value])

		self.operator = Or([ #ontology + is + isa
					Keyword("before"), Keyword("after"), Keyword("during"),  Keyword("starts"), Keyword("ends"),#time
					Keyword("below"), Keyword("above"), Keyword("in"),  Keyword("contains"),#place
					])

		self.binaryMathOperations = Or([Keyword("=="), Keyword("<") , Keyword(">"),  Keyword("<=") , Keyword(">=")])
		self.tripleMathOperations = Or([Keyword("<>")])
		

		self.mathOperators = Or([Keyword("+"), Keyword("*"), Keyword("/"), Keyword("-")])
		self.mathValue = Group(Keyword("[") + self.name + self.mathOperators + self.name + Keyword("]"))
		
		self.assignment = Group(
					self.sparameter +
					Suppress("=") +
					Or([self.identifier, self.value, self.gparameter.setParseAction(self.fn_getparameter)])
					).setResultsName("assignmentfact").setParseAction(self.fn_setparameter)
		
		self.binaryMathFact = Group(
					self.name.setResultsName('sbj') + 
					self.binaryMathOperations.setResultsName('action') + 
					self.name.setResultsName('obj')
					).setResultsName("binaryMathfact")

		self.tripleMathFact = Group(
					self.name.setResultsName('sbj') + 
					self.tripleMathOperations.setResultsName('action') + 
					self.name.setResultsName('obj1') +
					self.name.setResultsName('obj2')
					).setResultsName("tripleMathFact")			
					
		self.isFact = Group(
					self.name.setResultsName('sbj') + 
					Keyword("is").setResultsName('action') + 
					self.name.setResultsName('obj') + 
					ZeroOrMore(self.argumentDef).setResultsName('args')
					).setResultsName("isfact").setParseAction( self.fn_is)

		self.isAFact = Group(
					self.name.setResultsName('sbj') + 
					Keyword("isa").setResultsName('action') + 
					self.name.setResultsName('obj') + 
					ZeroOrMore(self.argument).setResultsName('args')
					).setResultsName("isafact").setParseAction( self.fn_isa)

			
		self.refFact = Group(
					self.name.setResultsName('sbj') + 
					Keyword("ref").setResultsName('action') + 
					self.name.setResultsName('obj')
					).setResultsName("reffact").setParseAction( self.fn_ref)
					
		self.otherFacts = Group(
					self.name.setResultsName('sbj') + 
					self.operator.setResultsName('action') + 
					self.name.setResultsName('obj')
					).setResultsName("fact").setParseAction( self.fn_fact)
		
		self.hasFact = Group(
					self.name.setResultsName('sbj') +
					Keyword("has").setResultsName('action') +
					OneOrMore(self.argumentDef).setResultsName('args')
					).setResultsName("hasfact").setParseAction( self.fn_has )
					
		self.fact = Or([self.assignment, self.binaryMathFact, self.tripleMathFact, self.isFact, self.isAFact, self.refFact, self.otherFacts, self.hasFact])

		self.rule = Group(Group(self.LPAREN + self.fact + ZeroOrMore(";"+self.fact) + self.RPAREN).setResultsName("conditions") + "->" + Group(self.LPAREN + self.fact + ZeroOrMore(";"+self.fact) + self.RPAREN).setResultsName("actions")).setResultsName("rule")

		self.startScene = Group(self.name + Suppress(":") + Optional(self.value).setResultsName("time") + Suppress(",") + Optional(self.value).setResultsName("place")).setResultsName("startscene")
		self.endScene = Suppress(":") + self.name.setResultsName("endscene")
		self.existance = Group(self.name.setResultsName('sbj') + ZeroOrMore(self.argument).setResultsName("args")).setResultsName("existance")

		self.value << Or( [  (self.LPAREN + self.fact + self.RPAREN).setResultsName("factvalue")  ,
							Combine(Optional("-")+Word(alphanums + "_")),
							dblQuotedString, 
							quotedString, 
							#self.mathValue 
							] )
					
		self.say = Literal("say") + Or([self.identifier, self.value, self.gparameter.setParseAction(self.fn_getparameter)])
					
		self.line = Optional(Or([	Or([self.fact, self.rule, self.say.setParseAction(self.fn_say_global)])	+self.DOT,	Or([ self.startScene, self.endScene, self.existance, self.say.setParseAction(self.fn_say_scene)]) +self.SEMICOLON])) + Optional( pythonStyleComment).setResultsName("comment")
		
	@parse_action
	def fn_is(self, s, loc, toks ):
		args = dict([ [x[0],' '.join(x[1:])] for x in list(toks.isfact.args)])
		result = self.engine.is_(toks.isfact.sbj, toks.isfact.obj, args)
		return result
	
	@parse_action
	def fn_isa(self, s, loc, toks ):
		result = self.engine.isa_(toks.isafact.sbj, toks.isafact.obj, dict(list(toks.isafact.args)))
		return result

	@parse_action
	def fn_ref(self, s, loc, toks ):
		result = self.engine.ref_(toks.reffact.sbj, toks.reffact.obj)
		return result
	
	@parse_action
	def fn_fact(self, s, loc, toks ):
		result = self.engine.fact_(toks.fact.sbj, toks.fact.obj, toks.fact.action, dict(list(toks.fact.args)))
		return result
	
	@parse_action
	def fn_has(self, s, loc, toks ):
		args = dict([ [x[0],' '.join(x[1:])] for x in list(toks.hasfact.args)])
		result = self.engine.has_(toks.hasfact.sbj, args)
		return result
	
	@parse_action
	def fn_setparameter(self, s, loc, toks ):
		return self.engine.set_param_(toks)
	@parse_action
	def fn_getparameter(self, s, loc, toks ):
		return self.engine.get_param_(toks)
	
	@parse_action
	def fn_say_global(self,s,loc,toks):
		return self.engine.say_global_(toks)
	@parse_action
	def fn_say_scene(self,s,loc,toks):
		return self.engine.say_scene_(toks)
	
	def parseLine(self,l,debug = False):
		try:
			if debug: print(l.strip())
			result = self.line.parseString(l)
			if debug: print("Matches: {0}".format(result))
			if debug: print(dict(result))
			return result
		except ParseException as x:
			if debug: print ("  No match: {0}".format(str(x)))
		return None

if __name__ == "__main__":
	import fileinput
	parser = LParser(None)
	for l in fileinput.input():
		parser.parseLine(l,True)


