import sqlite3
import random

class Graph(object):
	def __init__(self,fpath='memory',keepOld=False):
		self.conn = sqlite3.connect(fpath)
		self.cur  = self.conn.cursor()
		
		self.createScheme()
		if not keepOld:
			self.emptyData()
		
	def createScheme(self):
		self.executeAndCommitMany([
		'create table if not exists nodes (id text, name text);',
		'create table if not exists attrib (id text, name text, value text, type text);',
		'create table if not exists relation (id text, inid text, outid text, label text);'
		])
	def emptyData(self):
		self.executeAndCommitMany([
		'delete from nodes;',
		'delete from attrib;',
		'delete from relation;'
		])
	
	def getNodesNames(self, ids):
		result = []
		for _id in ids:
			self.execute("select name from nodes where _id=?",(_id,))
			r = self._first_()
			if r is None:
				result.append(None)
			else:
				result.append(r[0])
		return result
	def getNodesIDs(self, names):
		result = []
		for name in names:
			self.execute("select id from nodes where name=?",(name,))
			r = self._first_()
			if r is None:
				result.append(None)
			else:
				result.append(r[0])
		return result		
	def getNode(self,name=None,args=None,one=True,create=True):
		tables = ""
		wheres = []
		vals = []
		if name is not None:
			wheres.append("name=?")
			vals.append(name)
		if args is not None:
			cnt = 0
			for k,v in args.items():
				cnt = cnt + 1
				tbname = "attrib"+str(cnt)
				tables = tables + ", attrib as %s "%tbname
				wheres.append("%s.id = nodes.id"%tbname)
				wheres.append("%s.name = ?"%tbname)
				vals.append(k)
				wheres.append("%s.value = ?"%tbname)
				vals.append(v)
				wheres.append("%s.type = ?"%tbname)
				vals.append(str(type(v)))
		where = ""
		if len(wheres)>0:
			where = tables + "where " + " and ".join(wheres) 
		self.execute("select nodes.id from nodes " + where,vals)
		result = [ x[0] for x in self._all_()]
		if len(result)==0:
			if create:
				newid = "N%d_%s"%(random.randint(1000,9999),name)
				self.executeAndCommit("insert into nodes (id,name) values (?,?)",(newid,name))
				if args is not None:
					self.updateAttribs(newid,args)
				if one:
					return newid
				else:
					return [newid]
			else:
				return []
		if one:
			return result[0]
		else:
			return result
		
	def relate(self,inid,outid,label):
		self.executeAndCommit("delete from relation where inid=? and outid=? and label=?",(inid,outid,label))
		relid = "R%d_%s_%s"%(random.randint(1000,9999),inid,outid)
		self.executeAndCommit("insert into relation (id,inid,outid,label) values (?,?,?,?)",(relid,inid,outid,label))
		return relid
		
	#return id, in_node_name, out_node_name, label
	def edgesIter(self):
		result = []
		self.execute("select relation.id,node1.name,node2.name,relation.label from nodes as node1 , nodes as node2 , relation where relation.inid=node1.id and relation.outid=node2.id")
		for r in self._all_():
			result.append(r)
		return result
		
	def getRelations(self,inid=None,outid=None,label=None,args=None):
		tables = ""
		wheres = []
		vals = []
		if label is not None:
			wheres.append("label=?")
			vals.append(label)
		if outid is not None:
			wheres.append("outid=?")
			vals.append(outid)
		if inid is not None:
			wheres.append("inid=?")
			vals.append(inid)
		if args is not None:
			cnt = 0
			for k,v in args.items():
				cnt = cnt + 1
				tbname = "attrib"+str(cnt)
				tables = tables + ", attrib as %s " % tbname
				wheres.append("%s.id = relation.id"%tbname)
				wheres.append("%s.name = ?"%tbname)
				vals.append(k)
				wheres.append("%s.value = ?"%tbname)
				vals.append(v)
				wheres.append("%s.type = ?"%tbname)
				vals.append(str(type(v)))
		
		where = ""
		if len(wheres)>0:
			where = tables + "where " + " and ".join(wheres)
		self.execute("select relation.id from relation " + where,vals)
		result = self._all_()
		return [ x[0] for x in result ]
		
	def updateAttrib(self,_id,name,value):
		print("update att:",_id,name,value)
		self.executeAndCommit("insert or replace into attrib (id, name, value, type) values (?, ?, ?, ?)",(id,name,value,type(value)))
	def updateAttribs(self,_id,args={}):
		print("update atts:",_id,args)
		for k,v in args.items():
			self.updateAttrib(_id,k,v)
	def delAttribs(self,_id):
		self.executeAndCommit("delete from attrib where id=?",(_id,))
	
	def _convertVal_(self,val,ty):
		if ty == str(type(10)):
			return int(val)
		if ty == str(type(10.1)):
			return float(val)
		return val
	
	def getAttribs(self,_id):
		self.execute("select name,value,type from attrib where id=?",(_id,))
		result = {}
		for r in self._all_():
			result[r[0]] = self._convertVal_(r[1],r[2])
		return result
		
	def getAttrib(self,_id,name):
		self.execute("select value,type from attrib where id=? and name=?",(_id,name))
		r = self._first_()
		if r is not None:
			return self._convertVal_(r[0],r[1])
		return None
	
	def addEdge(self,inname, outname, label="", args={}):
		inid = self.getNode(inname)
		outid = self.getNode(outname)
		relid = self.relate(inid,outid,label);
		self.updateAttribs(relid,args);
		
				
	def _first_(self):
		return self.cur.fetchone()
	def _all_(self):
		return self.cur.fetchall()
	def execute(self, query,vals=()):
		try:
			return self.cur.execute(query,tuple([str(x) for x in vals]))
		except sqlite3.Error as e:
			print("An SQL error occurred:", e.args[0], query, "\n\t\t".join([str(x)+":"+str(type(x)) for x in vals]))
			exit(0)
	def executeAndCommitMany(self,queries):
		for query in queries:
			self.executeAndCommit(query)
	def executeAndCommit(self,query,vals=()):
		try:
			r = self.cur.execute(query,tuple([str(x) for x in vals]))
			return r
		except sqlite3.Error as e:
			print("An SQL error occurred:", e.args[0], query, "\n\t\t".join([str(x)+":"+str(type(x)) for x in vals]))
			exit(0)
	def commit(self):
		return self.conn.commit()
	def __del__(self):
		self.conn.commit()
		self.conn.close()