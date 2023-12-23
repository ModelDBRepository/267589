import sys, zlib, os, platform, logging, hashlib, io, urllib.parse, time, random
from random import randint
import sqlite3
if __name__ == "__main__":
    sys.path.append(".")
    from simtoolkit.tree import tree
else:
    from . import tree
import numpy  as np
try:
	import pickle as pickle
except:
	import pickle

class db:
	def __init__(self, dburl, mode="", username="", password="", architecture=platform.machine() ):
		"""
		db is an aggregator for sevral possible data bases and format versions:
		
		"""
		self.logger = logging.getLogger("simtoolkit.database.db")
		self.dburl = dburl
		self.mode  = "wr"
		up = urllib.parse.urlparse(dburl)
		self.dbtype = "file" if up.scheme == "" else up.scheme
		if up.query != "":
			upq = dict( urllib.parse.parse_qsl(up.query) )
			if "mode" in upq: self.mode = upq['mode']
		self.path     = dburl if up.path == "" else up.path
		self.username = up.username
		self.password = up.password
		
		if type(mode) is str:
			if mode     != "": self.mode     = mode.lower()
		else:
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in __init__")
			self.logger.error(" Incorrect type of mode argument. It should be a str. {} is given".format(type(mode)))
			self.logger.error("----------------------------------------------------")		
			raise TypeError("Incorrect type of mode argument. It should be a str. {} is given".format(type(mode)))
		if type(username) is str:
			if username != "": self.username = username
		else:
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in __init__")
			self.logger.error(" Incorrect type of username argument. It should be a str. {} is given".format(type(username)))
			self.logger.error("----------------------------------------------------")		
			raise TypeError("Incorrect type of username argument. It should be a str. {} is given".format(type(username)))
		if type(password) is str:
			if password != "": self.password = password
		else:
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in __init__")
			self.logger.error(" Incorrect type of password argument. It should be a str. {} is given".format(type(password)))
			self.logger.error("----------------------------------------------------")		
			raise TypeError("Incorrect type of password argument. It should be a str. {} is given".format(type(password)))
		
		#Default values
		if self.dbtype == "" : self.dbtype = "file"

		if self.dbtype == "file":
			if os.path.isdir(self.path):
				self.logger.error("----------------------------------------------------")
				self.logger.error(" DATABASE ERROR in __init__")
				self.logger.error(" The {} is a directory".format(self.path))
				self.logger.error("----------------------------------------------------")		
				raise ValueError("The {} is a directory".format(self.path))
			if   self.mode == "wr" or self.mode == "rw":
				if os.path.exists(self.path) and not os.access(self.path, os.W_OK):
					self.logger.warning("----------------------------------------------------")
					self.logger.warning(" DATABASE ERROR in __init__")
					self.logger.warning(" File {} is read-only - open in ro mode".format(self.path))
					self.logger.warning("----------------------------------------------------")		
					self.db = sqlite(self.path, self.packvalue, self.unpackvalue, "ro", architecture)
				else:
					self.db = sqlite(self.path, self.packvalue, self.unpackvalue, "wr", architecture)
			elif self.mode == "w":
				if os.path.exists(self.path):
					if os.access(self.path, os.R_OK):
						self.logger.error("----------------------------------------------------")
						self.logger.error(" DATABASE ERROR in __init__")
						self.logger.error(" The file {} is read-only. Cannot open it in 'w' mode".format(self.path))
						self.logger.error("----------------------------------------------------")		
						raise ValueError("The file {} is read-only. Cannot open it in 'w' mode".format(self.path))
					else:
						os.remove(self.path)
				self.db = sqlite(self.path, self.packvalue, self.unpackvalue, "wr", architecture)
			elif self.mode == "ro":
				self.logger.warning(" > read-only mode is not supported for file database. Open {} in RW mode".format(self.path) )
				self.db = sqlite(self.path, self.packvalue, self.unpackvalue, "ro", architecture)
			else:
				self.logger.error("----------------------------------------------------")
				self.logger.error(" DATABASE ERROR in __init__")
				self.logger.error(" Unknown mode {}".format(self.mode))
				self.logger.error(" mode should be 'wr', 'w', or 'ro'")
				self.logger.error("----------------------------------------------------")		
				raise ValueError("Unknown mode {}".format(self.mode))
		#elif self.dbtype == "mysql"
		#elif self.dbtype == "postgresql"
		#elif self.dbtype == "oracle"
		else:
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in __init__")
			self.logger.error(" Data base connector for {} isn't implemented yet".format(self.dbtype))
			self.logger.error("----------------------------------------------------")		
			raise ValueError("Data base connector for {} isn't implemented yet".format(self.dbtype))
	#Redirection to the database
	#---      with      ---
	@property
	def __enter__(self):   return self.db.__enter__
	@property
	def __exit__(self):    return self.db.__exit__
	#---     Record     ---
	@property
	def record(self):	   return self.db.record
	#---set, get and del---
	@property
	def __setitem__(self): return self.db.__setitem__
	@property
	def __getitem__(self): return self.db.__getitem__
	@property
	def __delitem__(self): return self.db.__delitem__
	#---message  editing---
	@property
	def setmessage(self):  return self.db.setmessage
	@property
	def getmessage(self):  return self.db.getmessage
	#---   Iterators   ---
	@property
	def __iter__(self):	   return self.db.__iter__
	@property
	def pool(self):	       return self.db.pool
	@property
	def poolrecs(self):	   return self.db.poolrecs
	@property
	def poolnames(self):   return self.db.poolnames
	#---  RAW interface ---
	@property
	def recs(self):	       return self.db.recs
	@property
	def names(self):       return self.db.names
	@property
	def values(self):      return self.db.values
	#---      TAGS      ---
	@property
	def settag(self):      return self.db.settag
	@property
	def gettag(self):      return self.db.gettag
	@property
	def rmtag(self):       return self.db.rmtag
	@property
	def pooltags(self):	   return self.db.pooltags
	@property
	def tags(self):	       return self.db.tags
	#---    Multimedia   ---
	@property
	def setmm(self):       return self.db.setmm
	@property
	def getmm(self):       return self.db.getmm
	@property
	def rm_mm(self):       return self.db.rm_mm
	@property
	def poolmms(self):     return self.db.poolmms
	@property
	def mms(self):         return self.db.mms
	#---   Information   ---
	@property
	def info(self):        return self.db.info
		
	def packvalue(self,name,value):
		if type(value) is str :
			return 'ZIP',memoryview(zlib.compress(value.encode(),9))
		elif isinstance(value,np.ndarray):
			with io.BytesIO() as fd:
				np.save(fd,value)
				return 'ZIPNUMPY',memoryview(zlib.compress(fd.getvalue(),9))
		else:
			return 'ZIPPKL',memoryview(zlib.compress(pickle.dumps(value),9))
	def unpackvalue(self,name,valtype,value):
		if   valtype == "TEXT"    : return value
		elif valtype == "NUMPY"   : return np.load(io.BytesIO(value))
		elif valtype == "PKL"     : return pickle.loads(value)
		elif valtype == "ZIP"     : return zlib.decompress(value).decode()
		elif valtype == "ZIPNUMPY": return np.load(io.BytesIO(zlib.decompress(value)))
		elif valtype == "ZIPPKL"  : return pickle.loads(zlib.decompress(value))
		else:
			logger.error("----------------------------------------------------")
			logger.error(" DATABASE ERROR in uppackvalue")
			logger.error(" Unknown data type {} of parameter {}".format(valtype,name))
			logger.error("----------------------------------------------------")		
			raise RuntimeError("Unknown data type {} of parameter {}".format(valtype,name))
	
def sqlite(dburl, packvalue, unpackvalue, mode, architecture):
	"""
	Just a re-director for possible different versions of stkdb formats
	"""
	logger = logging.getLogger("simtoolkit.database.sqlite")
	try:
		db = sqlite3.connect(dburl)
	except BaseException as e:
		logger.error("----------------------------------------------------")
		logger.error(" DATABASE ERROR")
		logger.error(" Cannot open data base file {} : {}".format(dburl, e))
		logger.error("----------------------------------------------------")		
		raise RuntimeError("Cannot open data base file {} : {}".format(dburl, e))


	### Pool application id and version ###
	try:
		v = db.execute("PRAGMA application_id;").fetchone()[0]
	except BaseException as e:
		logger.error("----------------------------------------------------")
		logger.error(" DATABASE ERROR")
		logger.error(" Cannot fetch application ID from the file {} : {}".format(dburl, e))
		logger.error("----------------------------------------------------")		
		raise RuntimeError("Cannot fetch application ID attribute from data base file {} : {}".format(dburl, e))
	if v != 0x53544844 and v != 0:
		logger.error("----------------------------------------------------")
		logger.error(" DATABASE ERROR")
		logger.error(" The file \"{}\" is belong to another application! Application id : {:x}".format(dburl, v))
		logger.error("----------------------------------------------------")		
		raise RuntimeError("File {} is not STKDB : {:x}".format(dburl, v))
	if v == 0 and mode != "ro" :
		try:
			db.execute("PRAGMA application_id = 0x53544844;")
			db.commit()
		except BaseException as e:
			logger.error("----------------------------------------------------")
			logger.error(" DATABASE ERROR")
			logger.error(" Cannot set application ID from the file {} : {}".format(dburl, e))
			logger.error("----------------------------------------------------")		
			raise RuntimeError("Cannot set application ID from the file {} : {}".format(dburl, e))
	try:
		v = db.execute("PRAGMA user_version;").fetchone()[0]
	except BaseException as e:
		logger.error("----------------------------------------------------")
		logger.error(" DATABASE ERROR")
		logger.error(" Cannot fetch STKDB format version from the file {} : {}".format(dburl, e))
		logger.error("----------------------------------------------------")		
		raise RuntimeError("Cannot fetch STKDB format version from the file {} : {}".format(dburl, e))
	if v == 0 and mode != "ro" :
		try:
			db.execute("PRAGMA user_version = 1;")
			db.commit()
		except BaseException as e:
			logger.error("----------------------------------------------------")
			logger.error(" DATABASE ERROR")
			logger.error(" Cannot set format version in the file {} : {}".format(dburl, e))
			logger.error("----------------------------------------------------")		
			raise RuntimeError("Cannot set format version in the file {} : {}".format(dburl, e))
		v = 1
	if v == 1:
		return sqlite_v_0_1(dburl, packvalue, unpackvalue, mode, architecture)
	logger.error("----------------------------------------------------")
	logger.error(" DATABASE ERROR")
	logger.error(" Unknown format version {} in data base file {} ".format(v,dburl))
	logger.error("----------------------------------------------------")		
	raise ValueError("Unknown format version {} in data base file {} ".format(v,dburl))


class sqlite_v_0_1:
	def __init__(self, dburl, packvalue, unpackvalue, mode, architecture):
		self.logger = logging.getLogger("simtoolkit.database.sqlite_v_0_1")
		self.db = None
		cnt     = 10
		while self.db is None:
			try:
				self.db = sqlite3.connect(dburl)
			except BaseException as e:
				self.logger.error(f"STRKDB attempt {cnt} : cannot open data base {dburl} : {e}")
				self.db = None
				cnt    -= 1
				if cnt == 0: break
				time.sleep(random(5,30))
		if self.db is None:
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in __init__")
			self.logger.error(" Cannot open data base file {} : {}".format(dburl, e))
			self.logger.error("----------------------------------------------------")		
			raise RuntimeError("Cannot open data base file {} : {}".format(dburl, e))
		self.packvalue   = packvalue
		self.unpackvalue = unpackvalue
		self.mode        = mode
		init_db =[
			'''CREATE TABLE IF NOT EXISTS stkrecords(
						   id        INTEGER PRIMARY KEY AUTOINCREMENT,
						   timestamp DATETIME,
						   hash      TEXT,
						   message   TEXT );
			''',
			'''CREATE TABLE IF NOT EXISTS stknames(
						   id        INTEGER PRIMARY KEY AUTOINCREMENT,
						   name      TEXT );
			''',
			'''CREATE TABLE IF NOT EXISTS stkvalues(
						   id        INTEGER PRIMARY KEY AUTOINCREMENT,
						   record    INTEGER,
						   name      INTEGER,
						   type      TEXT   DEFAULT 'TEXT',
						   value     BLOB );
			''',
			'''CREATE UNIQUE INDEX IF NOT EXISTS stkvalidx ON stkvalues (record,name);
			''',
			'''CREATE TABLE IF NOT EXISTS stktags(
						   id        INTEGER PRIMARY KEY AUTOINCREMENT,
						   record    INTEGER,
						   tag       TEXT );
			''',
			'''CREATE TABLE IF NOT EXISTS stkmms(
						   id        INTEGER PRIMARY KEY AUTOINCREMENT,
						   record    INTEGER,
						   mediatype TEXT,
						   name      TEXT,
						   data      BLOB );
			''',
			'''CREATE VIEW IF NOT EXISTS stkview AS SELECT
					stkrecords.id        AS id,
					stkrecords.timestamp AS timestamp,
					stkrecords.hash      AS hash,
					stkrecords.message   AS message,
					stknames.name        AS name,
					stkvalues.name       AS nameid,
					stkvalues.type       AS type,
					stkvalues.value      AS value
					FROM stkvalues INNER JOIN stkrecords, stknames
					ON stkrecords.id=stkvalues.record AND stknames.id=stkvalues.name;
			''',
			'''CREATE VIEW IF NOT EXISTS stktagview AS SELECT
					stktags.id           AS id,
					stkrecords.id        AS recid,
					stktags.tag          AS tag,
					stkrecords.timestamp AS timestamp,
					stkrecords.hash      AS hash,
					stkrecords.message   AS message
					FROM stktags INNER JOIN stkrecords
					ON stkrecords.id=stktags.record ;
			''',
			'''CREATE VIEW IF NOT EXISTS stkmmsview AS SELECT
					stkmms.id            AS id,
					stkrecords.id        AS recid,
					stkmms.name          AS name,
					stkmms.mediatype     AS mediatype,
					stkrecords.timestamp AS timestamp,
					stkrecords.hash      AS hash,
					stkrecords.message   AS message
					FROM stkmms INNER JOIN stkrecords
					ON stkrecords.id=stkmms.record ;
			''']
		if self.mode != "ro":
			with self.db:
				for cmd in init_db:
					try:
						self.db.execute(cmd)
						# self.db.commit()
					except BaseException as e :
						self.logger.error("----------------------------------------------------")
						self.logger.error(" DATABASE ERROR in __init__")
						self.logger.error(" Cannot execute initiation sequence  {} : {}".format(cmd, e))
						self.logger.error("----------------------------------------------------")		
						raise RuntimeError("Cannot execute initiation sequence  {} : {}".format(cmd, e))
		else:
			with self.db:
				self.db.execute("PRAGMA query_only = on")
			# self.db.commit()
			
	def info(self):
		info = {}
		info["application id"]= "0x{:05x}".format(self.db.execute("PRAGMA application_id;").fetchone()[0])
		info["STKDB version"] = self.db.execute("PRAGMA user_version;").fetchone()[0]
		info["py-sqlite"]     = sqlite3.version
		info["sqlite"]        = sqlite3.sqlite_version
		for i,n,v in self.db.execute("PRAGMA database_list"):
			info["files/"+n]=v
		return info
	#--- file like functions for with ---
	def __enter__(self): return self
	def __exit__(self, exc_type, exc_value, trackback):
		self.db.commit()
		self.db.close()
		
	def mkrec(self,timestamp, rechash, message):
		if self.mode == "ro":
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in mkrec")
			self.logger.error(" Cannot record in read-only data base")
			self.logger.error("----------------------------------------------------")		
			raise ValueError("Cannot record in read-only data base")

		try:
			with self.db:
				cur = self.db.execute("INSERT INTO stkrecords (timestamp, hash, message) VALUES(:timestamp,:hash,:message);",
					{'timestamp':timestamp, 'hash':rechash, 'message':message})
			# self.db.commit()
		except BaseException as e :
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in mkrec")
			self.logger.error(" Cannot add a recored : {}".format(e))
			self.logger.error("----------------------------------------------------")		
			raise RuntimeError("Cannot add a recored : {}".format(e))
		try:
			recid = self.db.execute("SELECT id FROM stkrecords WHERE timestamp=:tiemstamp AND hash=:hash AND message=:message ;",
				{'tiemstamp':timestamp, 'hash':rechash, 'message':message}).fetchone()
		except BaseException as e :
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in mkrec")
			self.logger.error(" Cannot fetch recored id : {}".format(e))
			self.logger.error("----------------------------------------------------")		
			raise RuntimeError("Cannot fetch recored id : {}".format(e))
		if len(recid) > 1:
			self.logger.warning("----------------------------------------------------")
			self.logger.warning(" DATABASE ERROR in mkrec")
			self.logger.warning(" There are more than one records with the same time stamp, hash and message")
			self.logger.warning("----------------------------------------------------")		
			#raise RuntimeError("There are more than one records with the same time stamp, hash and message")
		return cur.lastrowid
	def mkname(self,name):
		if self.mode == "ro":
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in mkname")
			self.logger.error(" Cannot record in read-only data base")
			self.logger.error("----------------------------------------------------")		
			raise ValueError("Cannot record in read-only data base")
		
		if "*" in name or "?" in name or "[" in name or "]" in name: 
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in mkname")
			self.logger.error(" name cannot contain *,?,]or[ charters: {} is given".format(name))
			self.logger.error("----------------------------------------------------")		
			raise RuntimeError("name {} is not quintic".format(name))
		try:
			nameid = self.db.execute("SELECT id FROM stknames WHERE name=:name;",{'name':name}).fetchone()
		except BaseException as e :
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in mkname")
			self.logger.error(" Cannot fetch name id : {}".format(e))
			self.logger.error("----------------------------------------------------")		
			raise RuntimeError("Cannot fetch name id : {}".format(e))
		if not nameid is None:
			if len(nameid) > 1:
				self.logger.error("----------------------------------------------------")
				self.logger.error(" DATABASE ERROR in mkname")
				self.logger.error(" name {} is not unique".format(name))
				self.logger.error("----------------------------------------------------")		
				raise RuntimeError("name {} is not unique".format(name))
			else:
				return nameid[0]
		try:
			with self.db:
				self.db.execute("INSERT OR IGNORE INTO stknames(name) VALUES(:name);",{'name':name})
			# self.db.commit()
		except BaseException as e :
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in mkname")
			self.logger.error(" Cannot add a name {} : {}".format(name,e))
			self.logger.error("----------------------------------------------------")		
			raise RuntimeError("Cannot add a name {} : {}".format(name,e))
		try:
			nameid = self.db.execute("SELECT id FROM stknames WHERE name=:name;",{'name':name}).fetchone()
		except BaseException as e :
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in mkname")
			self.logger.error(" Cannot fetch name id : {}".format(e))
			self.logger.error("----------------------------------------------------")		
			raise RuntimeError("Cannot fetch name id : {}".format(e))
		if len(nameid) > 1:
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in mkname")
			self.logger.error(" name {} is not unique".format(name))
			self.logger.error("----------------------------------------------------")		
			raise RuntimeError("name {} is not unique".format(name))
		return nameid[0]
	def recordvalue(self, n, recid, nameid, valtype, value):
		if self.mode == "ro":
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in recordvalue")
			self.logger.error(" Cannot record in read-only data base")
			self.logger.error("----------------------------------------------------")		
			raise ValueError("Cannot record in read-only data base")
		try:
			v = self.db.execute("SELECT id FROM stkvalues WHERE record=:record AND name=:name;",{'name':nameid, 'record':recid}).fetchone()
		except BaseException as e :
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in recordvalue")
			self.logger.error(" Cannot fetch value id : {}".format(e))
			self.logger.error("----------------------------------------------------")		
			raise RuntimeError("Cannot fetch value id : {}".format(e))
		if not v is None:
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in recordvalue")
			self.logger.error(" There is another parameter with the same name {} in record {} ".format(n, recid))
			self.logger.error("----------------------------------------------------")		
			raise RuntimeError("There is another parameter with the same name {} in record {} ".format(n, recid))
		try:
			with self.db:
				self.db.execute("INSERT INTO stkvalues(record,name,type,value) VALUES(?,?,?,?);",
					[recid,nameid,valtype,value])
		except BaseException as e :
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in recordvalue")
			self.logger.error(" Cannot insert parameter {} in to record  {} : {}".format(n,recid,e))
			self.logger.error("----------------------------------------------------")		
			raise RuntimeError("Cannot insert parameter {} in to record  {} : {}".format(n,recid,e))
	def record(self, tree, message, rechash=None, timestamp=None):
		if self.mode == "ro":
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in record")
			self.logger.error(" Cannot record in read-only data base")
			self.logger.error("----------------------------------------------------")		
			raise ValueError("Cannot record in read-only data base")
			
		if rechash is None or rechash == "" :
			h = hashlib.sha1()
			for n in tree:
				h.update(str(tree[n]).encode())
			rechash = h.hexdigest()
		if timestamp is None or timestamp == "" :
			timestamp = time.strftime("%Y-%m-%d %H:%M:%S")+f".{np.random.randint(999):03d}"
		recid = self.mkrec(timestamp, rechash, message)
		with self.db:
			for n in tree:
				nameid = self.mkname(n)
				try:
					self.recordvalue(n, recid, nameid, *self.packvalue(n,tree[n]) )
				except BaseException as e :
					self.logger.error("----------------------------------------------------")
					self.logger.error(" DATABASE ERROR in record")
					self.logger.error(" Cannot record value {} in to record  {} : {}".format(n,recid,e))
					self.logger.error(" Tree                           {}".format(tree))
					self.logger.error("----------------------------------------------------")		
					raise RuntimeError("Cannot record value {}  in to record  {} : {}".format(n,recid,e))
				
		# self.db.commit()
		return recid
	def __setitem__(self, key, value):
		"""
		It can support several notations
		db[record]      = tree_object            # adds the tree to the record
		db[record,name] = value                  # sets/adds the tree element `name` in the `record` into the `value for 
		db[record,name] = value_type,value_blob  # same as before with after packing the `value`
		"""
		if self.mode == "ro":
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in __setitem__")
			self.logger.error(" Cannot record in read-only data base")
			self.logger.error("----------------------------------------------------")		
			raise ValueError("Cannot record in read-only data base")

		if isinstance(value,tree):
			if type(key) is tuple or type(key) is list :
				if len(key) == 2:
					if type(key[1]) is str:
						if key[1][-1] != "/": key[1] = key[1]+"/"
						for n in value:
							self[key[0],key[1]+n] = value[n]
					else:
						self.logger.error("----------------------------------------------------")
						self.logger.error(" DATABASE ERROR in __setitem__")
						self.logger.error(" To set the parameters tree by notaton db[record,parmaeter],  parameter must be a string: {} is given".format(type(key[1])))
						self.logger.error("----------------------------------------------------")		
						raise TypeError("To set the parameters tree by notaton db[record,parmaeter],  parameter must be a string: {} is given".format(type(key[1])))
				else:
					self.logger.error("----------------------------------------------------")
					self.logger.error(" DATABASE ERROR in __setitem__")
					self.logger.error(" Incorrect notation for seting a parameters tree. Should be db[record,parameter_name], db[{}] is given".format(key))
					self.logger.error("----------------------------------------------------")		
					raise TypeError("Incorrect notation for seting a parameters tree. Should be db[record,parameter_name], db[{}] is given".format(key))
			elif type(key) is str or type(key) is str or type(key) is int:
				for n in value:
					self[key,n] = value[n]
			else:
					self.logger.error("----------------------------------------------------")
					self.logger.error(" DATABASE ERROR in __setitem__")
					self.logger.error(" Incorrect type of key. It shoudl be string, unicode or int: {} is given".format(type(key)))
					self.logger.error("----------------------------------------------------")		
					raise TypeError("Incorrect type of key. It shoudl be string, unicode or int: {} is given".format(type(key)))
		elif (type(value) is tuple or type(value) is list ) and len(value) == 2:
			namescliner = []
			if (type(key) is tuple or type(key) is list ) and len(key) == 2:
				rec,name = key
				with self.db :
					if type(rec) is int:
						reci = [ self.db.execute("SELECT id FROM stkrecords WHERE id=:rec;",{'rec':rec}).fetchone()[0] ]
					elif type(rec) is str or type(rec) is str:
						reci = [ i for i, in self.db.execute("SELECT id FROM stkrecords WHERE hash GLOB :rec OR timestamp GLOB :rec;",{'rec':rec}) ]
					if   type(name) is int:
						nami = [ self.db.execute("SELECT * FROM stknames WHERE id=:name;",{'name':name}).fetchone()[0] ]
					elif type(name) is str or type(name) is str:
						for i,n in self.db.execute("SELECT * FROM stknames WHERE name GLOB :name;",{'name':name+"/*"}):
							namescliner.append(i)
						for i,n in self.db.execute("SELECT * FROM stknames WHERE name GLOB :name;",{'name':name+"/*"}):
							namescliner.append(i)
						pname = name.split("/")
						if len(pname) > 2:
							pname = "/".join(pname[:-1])
							for i,n in self.db.execute("SELECT * FROM stknames WHERE name GLOB :name;",{'name':pname}):
								namescliner.append(i)
						nrec = self.db.execute("SELECT * FROM stknames WHERE name GLOB :name;",{'name':name}).fetchall()
						if nrec is None or len(nrec) == 0:
							nami = [self.mkname(name)]#yield self.mkname(name)
						else:
							nami = [ i for i,n in nrec ]
					
					vfl = [ {'rec':r,'name':n,'type':value[0],'value':value[1]} for r in reci for n in nami ]
					if len(vfl) == 0 :
						self.logger.error("----------------------------------------------------")
						self.logger.error(" DATABASE ERROR in __setitem__")
						self.logger.error(" Couldn't find record or name reci={}, namei={}".format(reci,nami))
						self.logger.error("----------------------------------------------------")		
						raise RuntimeError("Couldn't find record or name reci={}, namei={}".format(reci,nami))
					self.db.executemany("REPLACE INTO stkvalues (id,record,name,type, value) VALUES ((SELECT id FROM stkvalues WHERE record = :rec AND name = :name),:rec,:name,:type,:value);",tuple(vfl))	
				# self.db.commit()
				# Deleting all values in this record which are lower in the name tree
				#  or parent if it has a value
				with self.db:
					for r,n in [ (r,n) for r in reci for n in namescliner ]:
						self.db.execute("DELETE FROM stkvalues WHERE record = :rec AND name = :name;",{'name':n,'rec':r})
				# self.db.commit()
			else:
				self.logger.error("----------------------------------------------------")
				self.logger.error(" DATABASE ERROR in __setitem__")
				self.logger.error(" key should be tuple and should have 2 entries, no more no less, {}:{} is given".format(key,len(key)))
				self.logger.error("----------------------------------------------------")		
				raise TypeError("key should have 2 entries, {} is given".format(len(key)))
		else:
			try:
				value =  self.packvalue(key,value)
			except BaseException as e :	
				self.logger.error("----------------------------------------------------")
				self.logger.error(" DATABASE ERROR in __setitem__")
				self.logger.error(" Cannot pack a vlaue for key {}: {}".format(key,e))
				self.logger.error("----------------------------------------------------")		
				raise TypeError("Cannot pack a vlaue for key {}: {}".format(key,e))
			if not (type(value) is tuple or type(value) is list ) or len(value) != 2:
				self.logger.error("----------------------------------------------------")
				self.logger.error(" DATABASE ERROR in __setitem__")
				self.logger.error(" Packvalue returns error type or length for key {}: {} {}".format(key,type(value),len(value)) )
				self.logger.error("----------------------------------------------------")		
				raise RuntimeError("Packvalue returns error type or length for key {}: {} {}".format(key,type(value),len(value)) )
			self[ key ] = value
	def __getitem__(self, key):
		def keyswitcher(key):
			if type(key) is int:
				return " id=:key",None,key
			elif type(key) is str:
				if key[-1]  == "/" : key  = key+"*"
				if "*" in key or "?" in key or "[" in key or "]" in key:
					SQL = " timestamp GLOB :key OR hash GLOB :key"
				else:
					SQL = " timestamp=:key OR hash=:key"
				return SQL,None,key
			elif ( type(key) is tuple or type(key) is list ) and len(key) == 2:
				key,name = key
				SQL,_,key = keyswitcher(key)
				return SQL,name,key
			else:
				self.logger.error("----------------------------------------------------")
				self.logger.error(" DATABASE ERROR in __getitem__")
				self.logger.error(f" Incorrect name type. It should be int or string or tuple of two, but {name}:{type(name)} is given")
				self.logger.error("----------------------------------------------------")		
				raise TypeError(f" Incorrect name type. It should be int or string or tuple of two, but {name}:{type(name)} is given")
				
		SQL = "SELECT name,type, value FROM stkview WHERE "
		pSQL,name,key = keyswitcher(key)
		SQL += pSQL
		if type(name) is int: SQL += " AND nameid=:name"
		elif type(name) is str or type(name) is str:
			if name[-1]  == "/" : name  = name+"*"
			if "*" in name or "?" in name or "[" in name or "]" in name: 
				SQL += " AND name GLOB :name"
			else :
				SQL += " AND name=:name"
		SQL += " ;"
		try:
			Atree = tree()
			for name,tpy,val in self.db.execute(SQL,{'key':key,'name':name}):
				Atree[name]= self.unpackvalue(name,tpy,val)
			return Atree
		except BaseException as e:
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in __getitem__")
			self.logger.error(" Cannot fetch items for key: {} : {}".format(key, e))
			self.logger.error("----------------------------------------------------")		
			raise RuntimeError("Cannot fetch items for key: {} : {}".format(key, e))

#-------- NEED TO THINK ABOUT IT -----------------#
	def __delitem__(self,key): pass #!!!!!
#-------- NEED TO THINK ABOUT IT -----------------#

	def getmessage(self, key):
		if type(key) is int:
			return [ (i,h,m) for i,h,m in self.db.execute("SELECT id,hash,message FROM stkrecords WHERE id = :key ;",{'key':key}) ]
		elif type(key) is str:
			return [ (i,h,m) for i,h,m in self.db.execute("SELECT id,hash,message FROM stkrecords WHERE hash GLOB :key OR timestamp GLOB :key;",{'key':key}) ]
		else:
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in getmessage")
			self.logger.error(" Incorrect key type. It should be string or int. {} is given".format(type(key)))
			self.logger.error("----------------------------------------------------")		
			raise TypeError("Incorrect key type. It should be string or int. {} is given".format(type(key)))
	def setmessage(self, key, message):
		if type(key) is int:
			with self.db:
				self.db.execute("REPLACE INTO stkrecords (id,timestamp,hash,message)"+\
				 "VALUES (?,(SELECT timestamp FROM stkrecords WHERE id=:key),(SELECT hash FROM stkrecords WHERE id=:key),:message);"
				 ,{'key':key,message:'message'}).fetchone()
			# self.db.commit()
		elif type(key) is str :
			with self.db:
				self.db.execute("REPLACE INTO stkrecords (id,timestamp,hash,message)"+\
				 " VALUES ((SELECT id        FROM stkrecords WHERE hash = ? OR name = ?),"+\
						  "(SELECT timestamp FROM stkrecords WHERE hash = ? OR name = ?),"+\
						  "(SELECT hash      FROM stkrecords WHERE hash = ? OR name = ?),?);",(key,key,key,key,key,key,message)).fetchall()
			# self.db.commit()
		else:
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in setmessage")
			self.logger.error(" Incorrect key type. It should be string or int. {} is given".format(type(key)))
			self.logger.error("----------------------------------------------------")		
			raise TypeError("Incorrect key type. It should be string or int. {} is given".format(type(key)))
			
#### Debug interfaces >>>
	def recs(self,flt=None,column=None):
		SQL = "SELECT id,hash,timestamp,message FROM stkrecords"
		if flt is None:			SQL += ";"
		elif type(flt) is int:	SQL += " WHERE id=:flt;"
		elif type(flt) is str or type(flt) is str:
			if column is None:
				SQL += " WHERE timestamp GLOB :flt OR hash GLOB :flt OR message GLOB :flt;"
			elif column == "timestamp":
				SQL += " WHERE timestamp GLOB :flt;"
			elif column == "hash":
				SQL += " WHERE  hash GLOB :flt ;"
			elif column == "message":
				SQL += " WHERE  message GLOB :flt;"
			else:
				self.logger.error("----------------------------------------------------")
				self.logger.error(" DATABASE ERROR in recs")
				self.logger.error(" Incorrect column for filter. It should be timestamp or hash or message: {} is given".format(column))
				self.logger.error("----------------------------------------------------")		
				raise ValueError("Incorrect column for filter. It should be timestamp or hash or message: {} is given".format(column))
		else:
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in recs")
			self.logger.error(" Incorrect filter type. It should be string. {} is given".format(type(flt)))
			self.logger.error("----------------------------------------------------")		
			raise TypeError("Incorrect filter type. It should be string. {} is given".format(type(flt)))
		for recid,rechash,timestemp,message in self.db.execute(SQL,{'flt':flt}): yield recid,rechash,timestemp,message
	def names(self,flt=None):
		if flt is None:
			SQL = "SELECT id,name FROM stknames;"
		elif type(flt) is str or type(flt) is str:
			SQL = "SELECT id,name FROM stknames WHERE name GLOB :flt;"
		else:
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in nanes")
			self.logger.error(" Incorrect filter type. It should be a string: {} is given".format(type(flt)))
			self.logger.error("----------------------------------------------------")		
			raise TypeError("Incorrect filter type. It should be a string: {} is given".format(type(flt)))
		for nameid,name in self.db.execute(SQL,{'flt':flt}): yield nameid,name
	def values(self,flt=None,column=None):
		if flt is None:
			SQL = "SELECT id,record,name,type,value FROM stkvalues;"
		elif type(flt) is int:
			if column is None:
				SQL = "SELECT id,record,name,type,value FROM stkvalues WHERE record = :flt OR name = :flt;"
			elif column == "record":
				SQL = "SELECT id,record,name,type,value FROM stkvalues WHERE record = :flt;"
			elif column == "name":
				SQL = "SELECT id,record,name,type,value FROM stkvalues WHERE  name = :flt;"
			else:
				self.logger.error("----------------------------------------------------")
				self.logger.error(" DATABASE ERROR in values")
				self.logger.error(" Incorrect column for filter. It should be record or name : {} is given".format(column))
				self.logger.error("----------------------------------------------------")		
				raise ValueError("Incorrect column for filter. It should be record or name : {} is given".format(column))
		else:
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in values")
			self.logger.error(" Incorrect filter type. It should be int: {} is given".format(type(flt)))
			self.logger.error("----------------------------------------------------")		
			raise TypeError("Incorrect filter type. It should be int: {} is given".format(type(flt)))
		for valid,record,name,valtype,value in self.db.execute(SQL,{'flt':flt}): 
			yield valid,record,name,self.unpackvalue("RAW"+valtype,valtype,value)
#<<< Debug interfaces ###

#### Iterators        >>>
	def __iter__(self):
		for recid,rechash,timestemp,message in self.db.execute("SELECT id,hash,timestamp,message FROM stkrecords;"):
			yield recid,rechash,timestemp,message
	
	def pool(self, key, name):
		if name[-1] == "/" :name += "*"
		SQL = "SELECT id,hash,timestamp,message,name,type,value FROM stkview "
		if type(key) is int:
			SQL += "WHERE id=:key AND name GLOB :name;"
		elif type(key) is str or type(key) is str:
			SQL += "WHERE (timestamp GLOB :key OR hash GLOB :key) AND name GLOB :name;"
		else:
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in pool")
			self.logger.error(" Incorrect key type. It should be int or string. {} is given".format(type(key)))
			self.logger.error("----------------------------------------------------")		
			raise TypeError("Incorrect key type. It should be int or string. {} is given".format(type(key)))
		try:
			for recid,rechash,timestamp,message,name,valtype,value in self.db.execute(SQL,{'key':key,'name':name}):
				yield recid,rechash,timestamp,message,name,self.unpackvalue(name,valtype,value)
		except BaseException as e:
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in pool")
			self.logger.error(" Cannot fetch value for key: {} and name {}: {}".format(key,name, e))
			self.logger.error("----------------------------------------------------")		
			raise RuntimeError("Cannot fetch value for key: {} and name {}: {}".format(key,name, e))
	
	def poolrecs(self,key):
		SQL = "SELECT id,hash,timestamp,message FROM stkrecords "
		if type(key) is int:
			SQL += "WHERE id=:key ;"
		elif type(key) is str or type(key) is str:
			SQL += "WHERE timestamp GLOB :key OR hash GLOB :key;"
		else:
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in poolrecs")
			self.logger.error(" Incorrect key type. It should be int or string. {} is given".format(type(key)))
			self.logger.error("----------------------------------------------------")		
			raise TypeError("Incorrect key type. It should be int or string. {} is given".format(type(key)))
		try:
			for recid,rechash,timestamp,message in self.db.execute(SQL,{'key':key}):
				yield recid,rechash,timestamp,message
		except BaseException as e:
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in poolrecs")
			self.logger.error(" Cannot fetch value for key: {} : {}".format(key, e))
			self.logger.error("----------------------------------------------------")		
			raise RuntimeError("Cannot fetch value for key: {} : {}".format(key, e))
			
	def poolnames(self,key=None):
		if key is None:
			SQL = "SELECT name FROM stknames;"
		elif type(key) is int:
			SQL = "SELECT name FROM stknames WHERE id = :key;"
		elif type(key) is str or type(key) is str:
			
			SQL = "SELECT name FROM stknames WHERE name GLOB :key;"
		else:
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in poolnames")
			self.logger.error(" Incorrect key type. It should be int or string. {} is given".format(type(key)))
			self.logger.error("----------------------------------------------------")		
			raise TypeError("Incorrect key type. It should be int or string. {} is given".format(type(key)))	
		try:
			for name in self.db.execute(SQL,{'key':key}):yield name
		except BaseException as e:
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in poolnames")
			self.logger.error(" Cannot fetch names for any key {} : {}".format(key,e))
			self.logger.error("----------------------------------------------------")		
			raise RuntimeError("Cannot fetch names for any key {} : {}".format(key,e))
#<<< Iterators        ###

#### TAGS             >>>
	def settag(self,key,tag):
		if self.mode == "ro":
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in settag")
			self.logger.error(" Cannot set a tag in the read-only data base")
			self.logger.error("----------------------------------------------------")		
			raise ValueError("Cannot set a tag in the read-only data base")
		if "%" in tag or "*" in tag:
				self.logger.error("----------------------------------------------------")
				self.logger.error(" DATABASE ERROR in settag")
				self.logger.error(" Tag cannot contains * or % characters. Given {}".format(tag))
				self.logger.error("----------------------------------------------------")		
				raise RuntimeError("Tag cannot contains * or % characters. Given {}".format(tag))
		if type(key) is int:
			SQL = "SELECT id FROM stkrecords WHERE id=:key"
		elif type(key) is str or type(key) is str:
			if "%" in key:
				self.logger.error("----------------------------------------------------")
				self.logger.error(" DATABASE ERROR in settag")
				self.logger.error(" key cannot contains % character. Given {}".format(key))
				self.logger.error("----------------------------------------------------")		
				raise ValueError("key cannot contains % character. Given {}".format(key))
			SQL = "SELECT id FROM stkrecords WHERE timestamp=:key OR hash=:key"
		else:
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in settag")
			self.logger.error(" Incorrect key type. It should be int or string. {} is given".format(type(key)))
			self.logger.error("----------------------------------------------------")		
			raise TypeError("Incorrect key type. It should be int or string. {} is given".format(type(key)))
		try:
			with self.db:
				self.db.execute("INSERT INTO stktags(record,tag) VALUES(("+SQL+"),:tag);",{'key':key,'tag':str(tag)})
			# self.db.commit()
		except BaseException as e:
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in settag")
			self.logger.error(" Cannot set tag: {} for key {}: {}".format(tag,key,e))
			self.logger.error("----------------------------------------------------")		
			raise RuntimeError("Cannot set tag: {} for key ;{}: {}".format(tag,key,e))
	def gettag(self,key):
		if key is None:
			SQL = "SELECT tag FROM stktagview ;"
		if type(key) is int:
			SQL = "SELECT tag FROM stktagview WHERE id=:key;"
		elif type(key) is str:
			SQL = "SELECT tag FROM stktagview WHERE timestamp=:key OR hash=:key ;"
		for tag, in self.db.execute(SQL,{'key':key}):
			yield tag
	def rmtag(self,key):
		if self.mode == "ro":
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in rmtag")
			self.logger.error(" Cannot remove a tag from the read-only data base")
			self.logger.error("----------------------------------------------------")		
			raise ValueError("Cannot remove a tag from the read-only data base")
		try:
			with self.db:
				self.db.execute("DELETE FROM stktags WHERE tag GLOB :key;",{'key':key})
			# self.db.commit()
		except BaseException as e:
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in rmtag")
			self.logger.error(" Cannot remove tag {} : {}".format(tag,e))
			self.logger.error("----------------------------------------------------")		
			raise RuntimeError("Cannot remove tag {} : {}".format(tag,e))
	def pooltags(self, key=None):
		SQL ="SELECT id,tag, recid,timestamp,hash,message "
		if key is None:
			SQL += "FROM stktagview ;"
		if type(key) is int:
			SQL += "FROM stktagview WHERE id=:key;"
		elif type(key) is str:
			SQL += "FROM stktagview WHERE tag GLOB :key;"
		for tagid,tag,recid,timestamp,rechash,message in self.db.execute(SQL,{'key':key}):
			yield tagid,tag,recid,timestamp,rechash,message
	def tags(self):
		for tag,recid in self.db.execute("SELECT tag,recid FROM stktagview"):
			yield tag,recid
#<<< TAGS             ###

#### MMS              >>>
	def setmm  (self, key, name, data, mediatype=None):
		if self.mode == "ro":
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in setmm")
			self.logger.error(" Cannot set a tag in the read-only data base")
			self.logger.error("----------------------------------------------------")		
			raise ValueError("Cannot set a tag in the read-only data base")
		if "%" in name or "*" in name:
				self.logger.error("----------------------------------------------------")
				self.logger.error(" DATABASE ERROR in setmm")
				self.logger.error(" name cannot contains * or % characters. Given {}".format(name))
				self.logger.error("----------------------------------------------------")		
				raise RuntimeError("name cannot contains * or % characters. Given {}".format(name))
		if mediatype is None:
			import magic
			mime = magic.Magic(mime=True)
			try:
				mediatype = mime.from_buffer(data)
			except BaseException as e:
				self.logger.error("----------------------------------------------------")
				self.logger.error(" DATABASE ERROR in setmm")
				self.logger.error(" Cannot identify media type for data: {}".format(e) )
				self.logger.error("----------------------------------------------------")
				raise ValueError("Cannot identify media type for data: {}".format(e) )
		SQLDIC = {'key':key,'mediatype':mediatype,'name':name,'data':data}
		if type(key) is int:
			SQL = "SELECT id FROM stkrecords WHERE id=:key"
		elif type(key) is str:
			if "%" in key:
				self.logger.error("----------------------------------------------------")
				self.logger.error(" DATABASE ERROR in setmm")
				self.logger.error(" key cannot contains % character. Given {}".format(key))
				self.logger.error("----------------------------------------------------")		
				raise ValueError("key cannot contains % character. Given {}".format(key))
			SQL = "SELECT id FROM stkrecords WHERE timestamp=:key OR hash=:key"
		elif type(key) is tuple or type(key) is list:
			if len(key) != 2 :
				self.logger.error("----------------------------------------------------")
				self.logger.error(" DATABASE ERROR in setmm")
				self.logger.error(" Incorrect length of key tuple. It should be 2, but {} is given".format(len(key)))
				self.logger.error("----------------------------------------------------")		
				raise TypeError("Incorrect length of key tuple. It should be 2, but {} is given".format(len(key)))
			if   type(key[0]) is str and type(key[1]) is str:
				if "%" in key[0] or "%" in key[0]:
					self.logger.error("----------------------------------------------------")
					self.logger.error(" DATABASE ERROR in setmm")
					self.logger.error(" key cannot contains % character. Given {}".format(key))
					self.logger.error("----------------------------------------------------")		
					raise ValueError("key cannot contains % character. Given {}".format(key))
				SQL = "SELECT id FROM stkrecords WHERE timestamp=:key0 AND hash=:key1"
				SQLDIC["key0"],SQLDIC["key1"] = key[0], key[1]
			else:
				self.logger.error("----------------------------------------------------")
				self.logger.error(" DATABASE ERROR in setmm")
				self.logger.error(" Incorrect key type. It should be int or string or tuple of 2 strings. {} is given".format(key))
				self.logger.error("----------------------------------------------------")		
				raise TypeError("Incorrect key type. It should be int or string or tuple of 2 strings. {} is given".format(key))
		else:
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in setmm")
			self.logger.error(" Incorrect key type. It should be int or string or tuple of length 2. {} is given".format(type(key)))
			self.logger.error("----------------------------------------------------")		
			raise TypeError("Incorrect key type. It should be int or string or tuple of length 2. {} is given".format(type(key)))
		try:
			with self.db:
				self.db.execute("INSERT INTO stkmms(record,mediatype,name,data) VALUES(("+SQL+"),:mediatype,:name,:data);",SQLDIC)
			# self.db.commit()
		except BaseException as e:
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in setmm")
			self.logger.error(" Cannot set multimedia {} mediatype({}) : for key {}: {}".format(name, mediatype, key,e))
			self.logger.error("----------------------------------------------------")		
			raise RuntimeError("Cannot set multimedia {} mediatype({}) : for key {}: {}".format(name, mediatype, key,e))

	def getmm  (self, mmid):
		"""
		returns binary data of mm content, recorded under mmid ID
		for searching mmid for needed mm, use poolmms() function
		"""
		if mmid is None:
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in getmm")
			self.logger.error(" A mmid (key) cannot be None")
			self.logger.error("----------------------------------------------------")		
			raise RuntimeError("A mmid (key) cannot be None")
		if type(mmid) is not int:
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in getmm")
			self.logger.error(" A mmid must be integer. {} is given".format(type(mmid)) )
			self.logger.error("----------------------------------------------------")		
			raise RuntimeError("A mmid must be integer. {} is given".format(type(mmid)) )
		try:
			with self.db:
				data = self.db.execute("SELECT data FROM stkmms WHERE id=:key;",{'key':mmid}).fetchone()[0]
			# self.db.commit()
		except BaseException as e:
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in getmm")
			self.logger.error(" Cannot get mm {} : {}".format(mmid,e))
			self.logger.error("----------------------------------------------------")		
			raise RuntimeError("Cannot get mm {} : {}".format(mmid,e))
		return data

	def rm_mm  (self, mmid):
		"""
		deletes mm record with given mmid
		"""
		if self.mode == "ro":
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in rm_mm")
			self.logger.error(" Cannot remove a mm from the read-only data base")
			self.logger.error("----------------------------------------------------")		
			raise ValueError("Cannot remove a mm from the read-only data base")
		try:
			with self.db:
				self.db.execute("DELETE FROM stkmms WHERE id=:key;",{'key':key})
			# self.db.commit()
		except BaseException as e:
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in rm_mm")
			self.logger.error(" Cannot remove mm {} : {}".format(mmid,e))
			self.logger.error("----------------------------------------------------")		
			raise RuntimeError("Cannot remove mm {} : {}".format(mmid,e))
	def poolmms(self, key=None, name=None):
		SQL ="SELECT id, name, mediatype, recid,timestamp,hash,message "
		if   key is None and name is None :
			SQL += "FROM stkmmsview ;"
		elif type(key) is int and name is None:
			SQL += "FROM stkmmsview WHERE recid=:key;"
		elif type(key) is int and type(name) is str:
			SQL += "FROM stkmmsview WHERE recid=:key AND name GLOB :name;"
		elif type(key) is str and name is None:
			SQL += "FROM stkmmsview WHERE timestamp GLOB :key OR hash GLOB :key;"
		elif type(key) is str and type(name) is str:
			SQL += "FROM stkmmsview WHERE ( timestamp GLOB :key OR hash GLOB :key ) AND name GLOB :name;"
		elif key is None and type(name) is str:
			SQL += "FROM stkmmsview WHERE  name GLOB :name;"
		else:
			self.logger.error("----------------------------------------------------")
			self.logger.error(" DATABASE ERROR in poolmms")
			self.logger.error(" incorrect parameters of request key maybe None, int or string; name may be only None or string: key={} and name={} are given. If key is None,".format(type(key),type(name)))
			self.logger.error("----------------------------------------------------")		
			raise RuntimeError("incorrect parameters of request key maybe None, int or string; name may be only None or string: key={} and name={} are given. If key is None,".format(type(key),type(name)))
		for mmid,name,mediatype,recid,timestamp,rechash,message in self.db.execute(SQL,{'key':key,'name':name}):
			yield mmid,name,mediatype,recid,timestamp,rechash,message

	def mms(self): pass
#<<< MMS              ###

# class recorder:
	# def __init__(self, dbfile, tree):
		

if __name__ == "__main__":		
	if len(sys.argv) < 2:
		print("USEAGE: python simtoolkit/database model-fileformats/example.stkdb")
		exit(1)
	testdb = db(sys.argv[1])
	#DB>>
	#for row in testdb.db.db.execute("SELECT * FROM stkview;"):
		#print row
	#for row in testdb.db.db.execute("SELECT * FROM stkvalues;"):
		#print row
	#<<DB
	#DB>>
	x=tree()
	x["/a/b/s"]='2'
	x["/a/b/k"]='5'
	x["/list" ]=[1,2,3,4,5]
	x["/array"]=np.random.rand(10)
	recid = testdb.record(x,"Blash-blash-blash")
	for r,h,t,m in testdb:
		print(r,h,t,m)
		At = testdb[h]
		for p,k,s in At.printnames():
			print(p, "" if k is None else At[k] ) 
		print() 

	print("\n/list  :")
	for l in testdb.pool("d0a25351ff6fe352b55ca29d10d6cc09d10890e8","/list"):
		print(l)
	print("\n/li    :")
	for l in testdb.pool("d0a25351ff6fe352b55ca29d10d6cc09d10890e8","/li"):
		print(l)
	print("\n/li*   :")
	for l in testdb.pool("d0a25351ff6fe352b55ca29d10d6cc09d10890e8","/li*"):
		print(l)
	print("\n/a/   :")
	for l in testdb.pool("d0a25351ff6fe352b55ca29d10d6cc09d10890e8","/a/"):
		print(l)
	print("\n/a    :")
	for l in testdb.pool("d0a25351ff6fe352b55ca29d10d6cc09d10890e8","/a"):
		print(l)
	print("\n/a*   :")
	for l in testdb.pool("d0a25351ff6fe352b55ca29d10d6cc09d10890e8","/a*"):
		print(l)
	print("\n/     :")
	for l in testdb.pool("d0a25351ff6fe352b55ca29d10d6cc09d10890e8","*"):
		print(l)
	print("\nkey* /* :")
	for l in testdb.pool("d*","/*"):
		print(l)
	print()
	#print "=== TAGS ==="
	#print " > SET TAG"
	#tag = "%04d"%(np.random.randint(9999))
	#testdb.settag(recid,tag)
	#for tag,recid,timestamp,rechash,message in testdb.pooltags():
		#print "TAG        = ", tag
		#print "RECID      = ", recid
		#print "TIME STAMP = ", timestamp
		#print "HASH       = ", rechash
		#print "MESSAGE    = ", message
		#print "=============="
		#print
	#for tag,recid in testdb.tags():
		#print tag,recid
	
