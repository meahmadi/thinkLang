import sys
from pyparsing import *

first = Word(alphas+"_", exact=1)
rest = Word(alphanums+"_")

LPAREN = Suppress("(")
RPAREN = Suppress(")")
DOT = Suppress(".")
SEMICOLON = Suppress(";")

types = ["time","place","thing", "number", "event", "word"]
keywords = Or(types)

identifier = Or([keywords , Combine(first+Optional(rest))])
variable = Combine(identifier+"?")
parameter = Or([Group(identifier+"."+identifier),Group(variable+"."+identifier)])

value = Forward()

argumentDef = Group(identifier + identifier + Optional( Literal("=") + value ))

argument = Group(identifier + value )


name = Or([identifier,variable,parameter, value])

operator = Or([ #ontology + is + isa
			Keyword("before"), Keyword("after"), Keyword("during"),  Keyword("starts"), Keyword("ends"),#time
			Keyword("below"), Keyword("above"), Keyword("in"),  Keyword("contains"),#place
			])

binaryMathOperations = Or([Keyword("="), Keyword("<") , Keyword(">"),  Keyword("<=") , Keyword(">=")])
tripleMathOperations = Or([Keyword("<>")])

mathOperators = Or([Keyword("+"), Keyword("*"), Keyword("/"), Keyword("-")])
mathValue = Group(Keyword("[") + name + mathOperators + name + Keyword("]"))
			
binaryMathFact = Group(
			name.setResultsName('sbj') + 
			binaryMathOperations.setResultsName('action') + 
			name.setResultsName('obj')
			).setResultsName("binaryMathfact")

tripleMathFact = Group(
			name.setResultsName('sbj') + 
			tripleMathOperations.setResultsName('action') + 
			name.setResultsName('obj1') +
			name.setResultsName('obj2')
			).setResultsName("tripleMathFact")			
			
isFact = Group(
			name.setResultsName('sbj') + 
			Keyword("is").setResultsName('action') + 
			name.setResultsName('obj') + 
			ZeroOrMore(argumentDef).setResultsName('args')
			).setResultsName("isfact")

isAFact = Group(
			name.setResultsName('sbj') + 
			Keyword("isa").setResultsName('action') + 
			name.setResultsName('obj') + 
			ZeroOrMore(argument).setResultsName('args')
			).setResultsName("isafact")			

	
refFact = Group(
			name.setResultsName('sbj') + 
			Keyword("ref").setResultsName('action') + 
			name.setResultsName('obj')
			).setResultsName("reffact")
			
otherFacts = Group(
			name.setResultsName('sbj') + 
			operator.setResultsName('action') + 
			name.setResultsName('obj')
			).setResultsName("fact")			
			
fact = Or([binaryMathFact, tripleMathFact, isFact, isAFact, refFact, otherFacts])

rule = Group(Group(LPAREN + fact + ZeroOrMore(";"+fact) + RPAREN).setResultsName("conditions") + "->" + Group(LPAREN + fact + ZeroOrMore(";"+fact) + RPAREN).setResultsName("actions")).setResultsName("rule")

startScene = Group(name + Suppress(":") + Optional(value).setResultsName("time") + Suppress(",") + Optional(value).setResultsName("place")).setResultsName("startscene")
endScene = Suppress(":") + name.setResultsName("endscene")
existance = Group(name.setResultsName('sbj') + ZeroOrMore(argument).setResultsName("args")).setResultsName("existance")

value << Or( [  Group(LPAREN + fact + RPAREN).setResultsName("factvalue")  , Combine(Optional("-")+Word(alphanums + "_")), dblQuotedString, quotedString, mathValue ] )
			
line = Optional(Or([Or([fact, rule])+DOT,Or([startScene,endScene,existance])+SEMICOLON])) + Optional( pythonStyleComment).setResultsName("comment")

def parseLine(l,debug = False):
	global line
	try:
		if debug: print(l.strip())
		result = line.parseString(l)
		if debug: print("Matches: {0}".format(result))
		if debug: print(dict(result))
		if debug: print()
		return result
	except ParseException as x:
		if debug: print ("  No match: {0}".format(str(x)))
	return None

if __name__ == "__main__":
	import fileinput
	for l in fileinput.input():
		parseLine(l,True)


