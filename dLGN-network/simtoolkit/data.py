import os, sys, types, logging, hashlib, zlib, threading, io, time, struct, platform, json
from multiprocessing import Process, Queue 
import mmap
import numpy as np
from urllib.parse import urlparse

#from simtoolkit.tree import tree
if __name__ == "__main__":
    sys.path.append(".")
    from simtoolkit import tree
else:
    from .tree import tree

logging.DEEPDEBUG = 5
logging.addLevelName(logging.DEEPDEBUG, "DEEPDEBUG")
logging.Logger.deepdebug = lambda inst, msg, *args, **kwargs: inst.log(logging.DEEPDEBUG, msg, *args, **kwargs)
logging.deepdebug = logging.Logger.deepdebug

class data:
    def __init__(self, durl, mode="r+", dtype=None, username="", password="", architecture=platform.machine(), **kwargs):
        """
        data class is an switcher, which allows to use the same interface for many different possible data 
           storage mechanisms and formats.
           general parameters:
            durl              - data URL or a file descriptor
            dtype             - type of data file: stkdata/npz/hd5/etc
                                use this if durl is a file descriptor
            mode              - mode to open data storage: r+/a+/w/wr/rw/ro
            username/password - reserved for data server
            architecture      - architecture for data structure translation
           parameters for stkdata:
            compress            - level of compression for python data (default 5)
            npcompress          - level of compression for numpy data (default None)
            maxbuffersize       - if 0        - immediately writes data into the file every time 
                                              __setitem__ is called.
                                  if positive - size of memory can be used for buffering
                                  if negative - uses 1/4 of available memory as a buffer size
            autocorrection      - automatically corrects inconsistencies in data structure and the table 
            autodefragmentation - automatically defragments data file
        """
        self.logger = logging.getLogger("simtoolkit.data.data")
        self.durl = durl
        self.mode  = mode
        if type(self.durl) is str:        
            up = urlparse(durl)
            self.dtype = "stkdata" if up.scheme == "" else up.scheme
            if up.query != "":
                upq = dist( urlparse.parse_qsl(up.query) )
                if "mode" in upq: self.mode = upq['mode']
            self.path     = dburl if up.path == "" else up.path
            self.username = up.username
            self.password = up.password

        if dtype is not None:
            self.dtype = dtype
        elif type(self.durl) is not str:
            self.dtype = 'stkdata'

        
        if type(mode) is str:
            if mode     != "": self.mode     = mode.lower()
        else:
            self.logger.error( "----------------------------------------------------")
            self.logger.error( " DATA ERROR in __init__")
            self.logger.error(f" Incorrect type of mode argument. It should be a str. {type(mode)} is given")
            self.logger.error( "----------------------------------------------------")        
            raise TypeError(f"Incorrect type of mode argument. It should be a str. {type(mode)} is given")
        if type(username) is str:
            if username != "": self.username = username
        else:
            self.logger.error("----------------------------------------------------")
            self.logger.error(" DATA ERROR in __init__")
            self.logger.error(" Incorrect type of username argument. It should be a str. {} is given".format(type(username)))
            self.logger.error("----------------------------------------------------")        
            raise TypeError("Incorrect type of username argument. It should be a str. {} is given".format(type(username)))
        if type(password) is str:
            if password != "": self.password = password
        else:
            self.logger.error("----------------------------------------------------")
            self.logger.error(" DATA ERROR in __init__")
            self.logger.error(" Incorrect type of password argument. It should be a str. {} is given".format(type(password)))
            self.logger.error("----------------------------------------------------")        
            raise TypeError("Incorrect type of password argument. It should be a str. {} is given".format(type(password)))
        
        #Default values
        if self.dtype == "" : self.dtype = "stkdata"

        if type(self.durl) is str:
            if self.dtype == "stkdata":
                if os.path.isdir(self.path):
                    self.logger.error("----------------------------------------------------")
                    self.logger.error(" DATA ERROR in __init__")
                    self.logger.error(" The {} is a directory".format(self.path))
                    self.logger.error("----------------------------------------------------")        
                    raise ValueError("The {} is a directory".format(self.path))
                cmd = {}
                # Coppy and use only relevant to data_file key parameters
                for i in 'compress','npcompress','maxbuffersize','autocorrection','autodefragmentation':
                    if i in kwargs:
                        cmd[i]=kwargs[i]
                if   self.mode == "r+" or self.mode == "a" or self.mode == "wr" or self.mode == "rw":
                    if os.path.exists(self.path) and not os.access(self.path, os.W_OK):
                        self.logger.warning("----------------------------------------------------")
                        self.logger.warning(" DATABASE ERROR in __init__")
                        self.logger.warning(" File {} is read-only - open in ro mode".format(self.path))
                        self.logger.warning("----------------------------------------------------")        
                        self.data = data_file(self.path, mode="ro", **cmd)
                    else:
                        self.data = data_file(self.path, mode="r+",**cmd)
                elif self.mode == "w":
                    if os.path.exists(self.path):
                        if not os.access(self.path, os.W_OK):
                            self.logger.error("----------------------------------------------------")
                            self.logger.error(" DATA ERROR in __init__")
                            self.logger.error(" The file {} is read-only. Cannot open it in 'w' mode".format(self.path))
                            self.logger.error("----------------------------------------------------")        
                            raise ValueError("The file {} is read-only. Cannot open it in 'w' mode".format(self.path))
                    self.data = data_file(self.path, mode="w",  **cmd)
                elif self.mode  == "ro":
                    self.data = data_file(self.path, mode="ro", **cmd)
                else:
                    self.logger.error("----------------------------------------------------")
                    self.logger.error(" DATA ERROR in __init__")
                    self.logger.error(" Unknown mode {}".format(self.mode))
                    self.logger.error(" mode should be 'r+', 'w', or 'ro'")
                    self.logger.error("----------------------------------------------------")        
                    raise ValueError("Unknown mode {}".format(self.mode))
            #elif self.dtype == "npz"
            #elif self.dtype == "hdf5"
            #elif self.dtype == "data-server"
            #elif self.dtype == "something-else-to-think-about"
            else:
                self.logger.error( "----------------------------------------------------")
                self.logger.error( " DATAE ERROR in __init__")
                self.logger.error(f" Data base connector for {self.dtype} isn't implemented yet")
                self.logger.error( "----------------------------------------------------")        
                raise ValueError(f" Data base connector for {self.dtype} isn't implemented yet")
        else:
            if self.dtype == "stkdata":
                cmd = {}
                # Coppy and use only relevant to data_file key parameters
                for i in 'compress','npcompress','maxbuffersize','autocorrection','autodefragmentation':
                    if i in kwargs:
                        cmd[i]=kwargs[i]
                self.data = data_file(self.durl, mode=self.mode, **cmd)
            #elif self.dtype == "npz"
            #elif self.dtype == "hdf5"
            #elif self.dtype == "data-server"
            #elif self.dtype == "something-else-to-think-about"
            else:
                self.logger.error( "----------------------------------------------------")
                self.logger.error( " DATAE ERROR in __init__")
                self.logger.error(f" Data base connector for {self.dtype} isn't implemented yet")
                self.logger.error( "----------------------------------------------------")        
                raise ValueError( f"Data base connector for {self.dtype} isn't implemented yet")
    #Redirection to the data class
    @property
    def __enter__(self):        return self.data.__enter__
    @property
    def __exit__(self):         return self.data.__exit__
    @property
    def sync(self):             return self.data.sync
    @property
    def __len__(self):          return self.data.__len__
    @property
    def __add__(self):          return self.data.__add__
    @property
    def __iadd__(self):
        return self.data.__iadd__
    @property
    def __setitem__(self):
        return self.data.__setitem__
    @property
    def __getitem__(self):
        return self.data.__getitem__
    @property
    def __delitem__(self):      return self.data.__delitem__
    @property
    def __call__(self):         return self.data.__call__
    @property
    def __contains__(self):     return self.data.__contains__
    @property
    def __iter__(self):         return self.data.__iter__
    @property
    def __iter__(self):         return self.data.__iter__
    @property
    def aggregate(self):        return self.data.aggregate
    @property
    def dict(self):             return self.data.dict
    @property
    def defragmentation(self):  return self.data.defragmentation
    # @property
    # def set(self):              return self.data.set

    #---   Information   ---
    # @property
    # def info(self):             return self.data.info

class data_file:
    """
    SimToolKit Data File
    """
    def __init__(self, filend, mode="r+", compress = 5, npcompress=False, maxbuffersize=0, autocorrection=False, autodefragmentation=False):
        """
        maxbuffersize - if 0        - immediately writes data into file every time __setitem__ is called.
                        if positive - size of memory can be used for buffering
                        if negative - uses 1/4 of available memory as a buffer size
        """
        self.logger = logging.getLogger("simtoolkit.data.data_file")
        if type(filend) is str:
            self.filename = filend
            self.logger.deepdebug(f" > Open simdata: file={self.filename}, modw={mode}, compress={compress}, npcompress={npcompress}, maxbuffersize={maxbuffersize}")
            self.fd       = None
        else:
            self.fd       = filend
            self.logger.deepdebug(f" > Open simdata descriptor {self.fd}, modw={mode}, compress={compress}, npcompress={npcompress}, maxbuffersize={maxbuffersize}")
            self.filename = None
            
        self.autocorrection = autocorrection
        self.autodefragmentation = autodefragmentation
        self.mode = mode
        if mode != "w":
            self.readfooter()                
        else:
            self.initfooter()

        self.bufdata = []
        self.bufsize = 0
        self.compres = compress
        self.npcompress = npcompress
        self.maxbufsize = maxbuffersize
        if self.maxbufsize < 0:
            self.maxbufsize = self.memory_available()//4
            self.logger.deepdebug("init : maxbuffersize={}".format(self.maxbufsize))             

    
    ##=== Standard Python interface ===##
    def __enter__(self) :
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        if self.filename is None or self.mode == "ro": return
        self.logger.deepdebug("__exit__: writefotter()")
        if self.maxbufsize != 0 : self.__flushbuf__()
        self.writefooter()

    def __len__(self) :
        cnt=0
        for n in self: cnt += 1
        return cnt
    def __add__(self,xdata):
        "Creating a new object add aggregate all data there"
        newdata = data(None)
        newdata.aggregate(self, xdata)
        return newdata
    def __iadd__(self,xdata):
        "Aggregating all data in this object += operator"
        if type(xdata) is list or type(xdata) is tuple:
            self.aggregate(*xdata)
        else:
            self.aggregate(xdata)
        return self
             
    def sync(self)                                    :    self.writefooter()
    
    def __setitem__(self,name,data)                   :
        if self.maxbufsize == 0 :
            return self.__save_chunk__( *self.zipper( name, data ) )
        else:
            self.bufdata.append( self.zipper( name, data ) )
            self.bufsize += len(self.bufdata[-1][1])
            return self.__flushbuf__() if self.bufsize >= self.maxbufsize*3//4 else self
            
                
        #<>
    def __getitem__(self,key)                         :
        """
        Possible syntaxes:
        for n in data         -> generator for all names in data file
        data[None]            -> returns a generator of name,chunk_number,chunk_data for all data in the file
        data[None,None]       -> returns a generator for raw data strim:
                                  name,chunk_number,data_size,data_type,data for all data in the file.
                                  it can be used for transferring data to a server or so on. 
        data['/name']         -> returns a generator for all chunks of data under /name
        data['/name',2]       -> returns 3rd chunk of the /name's data
        data['/name',2,5,7]   -> returns list of chunks of the /name's data
        data['/name',None]    -> returns a list with all chunks of /name's data
        data['/name',]        -> returns total number of chunks for a /name
        data['/name',(3,7,2)] -> returns a list of data within a slice (3,7,2)
        """
        #if (not self.filename is None) and self.mtime != os.stat(self.filename).st_mtime: self.readfooter()
        if   key is None                              : return self.__stream__()
        elif type(key) is str  : return self.__gen__(key)
        elif type(key) is tuple:
            name = key[0]
            if not name in self.datamap:
                self.logger.error("----------------------------------------------------")
                self.logger.error(" DATA ERROR in get")
                self.logger.error(" Cannot find  record {}".format(name))
                self.logger.error("----------------------------------------------------")
                raise RuntimeError("Cannot find  record {}".format(name))
            if   len(key) == 1 : return len(self.datamap[name])
            elif len(key) >= 2 :
                ret = []
                for chunk in key[1:]:
                    if key is None and chunk is None   : return self.__raw_stream__()
                    if chunk is None                   : 
                        for fl, st, sz, tp in self.datamap[name]:
                            ret.append( self.__read_chunk__(fl,st,sz,tp) )
                    elif type(chunk) is int            :
                        if chunk > 0 and chunk >= len(self.datamap[name]):
                            self.logger.error("----------------------------------------------------")
                            self.logger.error(" DATA ERROR in get")
                            self.logger.error(" Chunk {} greater than record {} size {}".format(chunk, name, len(self.datamap[name])))
                            self.logger.error("----------------------------------------------------")
                            raise RuntimeError("Chunk {} greater than record {} size {}".format(chunk, name, len(self.datamap[name])))
                        if chunk < 0 and abs(chunk) > len(self.datamap[name]):
                            self.logger.error("----------------------------------------------------")
                            self.logger.error(" DATA ERROR in get")
                            self.logger.error(" Chunk {} greater than record {} size {}".format(chunk, name, len(self.datamap[name])))
                            self.logger.error("----------------------------------------------------")
                            raise RuntimeError("Chunk {} greater than record {} size {}".format(chunk, name, len(self.datamap[name])))
                        if len(key) == 2:
                            return self.__read_chunk__( *self.datamap[name][chunk] )
                        else:
                            ret.append( self.__read_chunk__(fl,st,sz,tp) )
                    elif type(chunk) is tuple          :
                        sl = slice(*chunk)
                        for fl, st, sz, tp in self.datamap[name][sl]:
                            ret.append( self.__read_chunk__(fl,st,sz,tp) )
                    else:
                        self.logger.error("----------------------------------------------------")
                        self.logger.error(" DATA ERROR in get")
                        self.logger.error(" Incorrect chunk type for name {}. It should int or tuple, {} given".format(name, type(chunk)))
                        self.logger.error("----------------------------------------------------")
                        raise RuntimeError("Incorrect chunk type for name {}. It should int or tuple, {} given".format(name, type(chunk)))
                for dkey,ddata in self.bufdata:
                    if dkey == key: ret.append(ddata)
                return ret
            else:
                self.logger.error("----------------------------------------------------")
                self.logger.error(" DATA ERROR in get")
                self.logger.error(" Unexpected error with key{}".format(key))
                self.logger.error("----------------------------------------------------")
                raise RuntimeError("Unexpected error with key{}".format(key))
        else:
            self.logger.error("----------------------------------------------------")
            self.logger.error(" DATA ERROR in get")
            self.logger.error(" Incorrect type of key {}.".format(key))
            self.logger.error("----------------------------------------------------")
            raise RuntimeError("Incorrect type of key {}.".format(key))

    def __raw_stream__(self):
        for name in self:
            for chunkid,(fl,st,sz,tp)in enumerate(self.datamap[name]):
                with open(self.filename if fl is None else fl,"rb") as fd:
                    fd.seek(st)
                    data = fd.read(sz)
                yield name,chunkid,sz,tp,data

    def __stream__(self):
        for name in self:
            for chunkid,chunk in enumerate(self.datamap[name]):
                yield name,chunkid,self.__read_chunk__(*chunk)

    def __gen__(self,name):
        if not name in self.datamap:
            self.logger.error( "----------------------------------------------------")
            self.logger.error( " DATA ERROR in __gen__")
            self.logger.error(f" Cannot find  record {name}")
            self.logger.error( "----------------------------------------------------")
            raise RuntimeError(f"Cannot find  record {name}")
        if isinstance(self.datamap[name],tree):
            for n in self.datamap[name]:
                for fl, st, sz, tp in self.datamap[name+n]:
                    yield self.__read_chunk__(fl,st,sz,tp)
        else:
            for fl, st, sz, tp in self.datamap[name]:
                yield self.__read_chunk__(fl,st,sz,tp)
        if len(self.bufdata) > 0:
            for n,d,t in self.bufdata:
                if n == name: yield d

    def __contains__(self,key): return key in self.datamap

    def __iter__(self):
        self.logger.deepdebug(" > iter: self.datamap = {}".format(self.datamap) )
        for name in self.datamap       :# yield name
            self.logger.deepdebug(" > iter: yield {} of {}".format(name,self.datamap) )
            yield name
            

    def dict(self):
        for name in self.datamap.dict(): yield name

    def __delitem__(self,key):
        """
        del data["/name"]       - deletes just a record /name in footer 
                                  (file needs defragmentation to delete actual data)
        del data["/name",3]     - removes only chunk 3 in footer
        del data["/name",(3,5)] - deletes chunks 3 and 4 under name /name
        """
        if type(key) is str:
            del self.datamap[key]
        elif type(key) is tuple:
            name = key[0]
            if not name in self.datamap:
                self.logger.error( "----------------------------------------------------")
                self.logger.error( " DATA ERROR in __delitem__")
                self.logger.error(f" Cannot find  record {name}")
                self.logger.error( "----------------------------------------------------")
                raise RuntimeError(f"Cannot find  record {name}")
            if   len(key) == 1 : return self.__delitem__(name)
            elif len(key) == 2 :
                chunk = key[1]
                if type(chunk) is int:
                    self.datamap[name] = self.datamap[name][:chunk]+self.datamap[name][chunk+1:]
                elif type(chunk) is tuple:
                    sl = slice(*chunk)
                    del self.datamap[name][sl]
            else :
                self.logger.error( "----------------------------------------------------")
                self.logger.error( " DATA ERROR in __delitem__")
                self.logger.error(f" Too many chunks to delete in {name}, use one chunk at the time or slice notation")
                self.logger.error( "----------------------------------------------------")
                raise RuntimeError(f"Too many chunks to delete in {name}, use one chunk at the time or slice notation")
        if self.autodefragmentation: self.defragmentation()

        
    #--- TODO ---#        
    def __call__(self,name,*key):
        """
        Possible syntaxes:
        data(None)            -> 
        data(None,None)       -> 
        data('/name')         -> returns a concatenation of all data under /name 
        data('/name',2)       -> 
        data('/name',2,5,7)   -> returns a concatenation of chunks 2, 5 and 7 of /name 
        data('/name',None)    -> 
        data('/name',)        -> 
        data('/name',(3,7,2)) -> returns a concatenation of data in slice (3,7,2) for /name's chunks 
        """
        if (not self.filename is None) and self.mtime != os.stat(self.filename).st_mtime: self.readfooter()
        pass
    #-------------#




    ##=== Footer operations ===##
    def initfooter(self):
        self.datamap = tree()
        self.mtime   = time.time()
        self.tail    = 0
        self.fsize   = 0
        if self.filename is None or self.mode == "ro": return
        try:
            with open(self.filename,"wb") as fd: pass
        except BaseException as e:
            self.logger.error("----------------------------------------------------")
            self.logger.error(" DATA ERROR in initfooter")
            self.logger.error(" File \'{}\' cannot be written: {}".format(self.filename,e))
            self.logger.error("----------------------------------------------------")        
            raise ValueError("File \'{}\' cannot be written: {}".format(self.filename,e))

    def __readfooterfromfd__(self,fd):
        try:
            self.fsize   = fd.seek(-8,2)+8 #everything from the tail
            self.logger.deepdebug(" > rdft: shits to -8,2")
            idx =  struct.unpack(">Q",fd.read(8))[0] #Tree size
            self.logger.deepdebug(" > rdft: idx(treesize)={}".format(idx))
            fd.seek(-idx-8,2)
            self.logger.deepdebug(" > rdft: shits to -{}-8,2={}".format(idx,(-idx-8,2)))
            #importing back to the tree
            self.datamap = tree().imp( zlib.decompress(fd.read(idx)).decode() ) 
            self.logger.deepdebug(" > rdft: the tree={}".format(self.datamap))
        except BaseException as e:
            self.logger.warning( "----------------------------------------------------")
            self.logger.warning( " DATA ERROR in _readfooterfromfd_")
            self.logger.warning(f" Cannot read footer: {e} ")
            self.logger.warning( "----------------------------------------------------")
            raise RuntimeError(f" Cannot read footer: {e} ")
    
    def readfooter(self):
        if   self.fd is not None:
            self.__readfooterfromfd__(self.fd)
        elif self.filename is not None:        
            try:
                self.fsize = os.path.getsize(self.filename)
            except:
                return self.initfooter()
            if self.fsize < 9:
                return self.initfooter()
            try:
                with open(self.filename,"rb") as fd:
                    self.__readfooterfromfd__(fd)
            except BaseException as e:
                self.logger.warning("----------------------------------------------------")
                self.logger.warning(" DATA ERROR in readfooter")
                self.logger.warning(" Cannot open file \'{}\': {}".format(self.filename,e))
                self.logger.warning("----------------------------------------------------")        
                if not self.autocorrection:
                    raise RuntimeError("Cannot open file \'{}\': {}".format(self.filename,e))
                else:
                    self.rescan_file()
                
            self.mtime = os.stat(self.filename).st_mtime
        else:
            return self.initfooter()

        self.tail  = 0
        for n in self.datamap:
            for fl,st,sz,tp in self.datamap[n]:
                if not fl is None: continue
                if self.tail <= st+sz: self.tail = st+sz
        self.logger.deepdebug(" > rdtf: self.tail={}".format(self.tail))

    def rescan_file(self):
        #TODO : doesn't work in python 3
        # self.datamap = tree()
        # self.tail    = 0
        # self.fsize = os.path.getsize(self.filename)
        # with open(self.filename,"rw+b") as fd:
            # mm = mmap.mmap(fd.fileno(), 0)
            # start = mm.find('#STKDATA')
            # while start >= 0:
                # if start+10 >= self.fsize: break
                # chheadersize, = struct.unpack(">H",mm[start+8:start+10])
                # if start+10+chheadersize >= self.fsize: break
                # sz,ch,ty,name = eval(mm[start+10:start+10+chheadersize])
                # st = start+10+chheadersize
                # Xch = 0 if not name in self.datamap else len(self.datamap[name])
                # if Xch != ch:
                    # self.logger.error("----------------------------------------------------")
                    # self.logger.error(" DATA ERROR in repare_file")
                    # self.logger.error(" Chunk number {} of variable {} is not correct - should be".format(ch,name,Xch))
                    # self.logger.error("----------------------------------------------------")
                # #checking chunk size
                # if start+10+chheadersize+sz >= self.fsize: break
                # self.tail = start+10+chheadersize+sz
                # if self.tail+8 >= self.fsize: break
                # if mm[self.tail:self.tail+8] == '#STKDATA':
                    # start = self.tail
                # else:
                    # start = mm.find('#STKDATA',start+1)
                    # #TODO: recalculate actual data
                    # if start > 0:
                        # self.logger.error("----------------------------------------------------")
                        # self.logger.error(" DATA ERROR in repare_file")
                        # self.logger.error(" Chunk {} of variable {} has a wrong size : {} - skip it".format(Xch,name,sz))
                        # self.logger.error("----------------------------------------------------")
                        # continue
                    
                # if name in self.datamap:
                    # self.datamap[name].append( [None,st,sz,ty] )
                # else:
                    # self.datamap[name] = [ [None,st,sz,ty] ]         
            # #TODO: sort every name
            # #TODO: 
            # self.writefooter()
        pass

    def __writefottertofd__(self,fd):
        try:
            self.logger.deepdebug(" > wrft: self.tail={}".format(self.tail))
            fd.seek( self.tail )
            footer = zlib.compress(str(self.datamap.exp()).encode(),9)
            self.logger.deepdebug(" > wrft: str(self.datamap.exp()={}".format(str(self.datamap.exp())) )
            fd.write(footer)
            self.logger.deepdebug(" > wrft: len(footer)={}".format(len(footer)))
            fd.write(struct.pack(">Q",len(footer)) )
            fd.truncate()
            fd.flush()
        except BaseException as e:
            self.logger.warning( "----------------------------------------------------")
            self.logger.warning( " DATA ERROR in _writefottertofd_")
            self.logger.warning(f" Cannot write footer: {e} ")
            self.logger.warning( "----------------------------------------------------")
            raise RuntimeError(f" Cannot write footer: {e} ")

    def writefooter(self):
        if self.mode == "ro":
            self.logger.warning("----------------------------------------------------")
            self.logger.warning(" DATA ERROR in writefooter")
            self.logger.warning(" Cannot write footer into read only 'ro' file/descriptor")
            self.logger.warning("----------------------------------------------------")
            return
        elif self.fd is not None :
            self.__writefottertofd__(self.fd)
        elif self.filename is not None:
            try:
                with open(self.filename,"rb+") as fd:
                    self.__writefottertofd__(fd)
            except BaseException as e:
                self.logger.warning("----------------------------------------------------")
                self.logger.warning(" DATA ERROR in writefooter")
                self.logger.warning(" Cannot open or write file \'{}\': {}".format(self.filename,e))
                self.logger.warning("----------------------------------------------------")        
                if not self.autocorrection:
                    raise RuntimeError("Cannot open or write  file \'{}\': {}".format(self.filename,e))
                else:
                    self.rescan_file()
            self.mtime = os.stat(self.filename).st_mtime    
        else:
            self.logger.warning("----------------------------------------------------")
            self.logger.warning(" DATA ERROR in writefooter")
            self.logger.warning(" Cannot write footer into virtual file")
            self.logger.warning("----------------------------------------------------")
            return
            
            
        
    
    ##=== Chunk functions ===##
    def zipper(self, name, data):
        def recpyobj(data):
            if   type(data) is int  or type(data) is float   or\
                 type(data) is bool or type(data) is complex or\
                 type(data) is str  or data is None :
                return data
            elif type(data) is list or type(data) is tuple:
                return [ recpyobj(x) for x in data ]
            elif type(data) is dict:
                recd = {}
                for n in data: recd[n] = recpyobj(data[n])
                return recd
            elif isinstance(data,np.ndarray):
                return data.tolist()
            else:
                #TODO: here should be tests for other types and
                #      better type detection must be done
                return data.tolist()
        if type(data) is str:
            if self.compres:
                return name, zlib.compress(data.encode(),self.compres),"ZSTRING"
            else:
                return name, data.encode(),"STRING"
        elif not isinstance(data,np.ndarray):
            data = recpyobj(data)
            if self.compres:
                return name, zlib.compress(json.dumps(data).encode(),self.compres),"ZPYTHON"
            else:
                return name, json.dumps(data).encode(),"PYTHON"
        else:
            with io.BytesIO() as fd:
                np.save(fd, data)
                if self.npcompress:
                    return name, zlib.compress(fd.getvalue(),self.npcompress) ,"ZNUMPY"
                else:
                    return name, fd.getvalue() ,"NUMPY"

    def __save_chunk_tofd__(self,fd,name,data,datatype):
        try:
            datasize = len(data)
            chn = len(self.datamap[name]) if name in self.datamap else 0
            fd.seek(self.tail)
            chheader = str([ datasize,chn,datatype,    name ])
            chheadersize = struct.pack(">H",len(chheader))
            fd.write("#STKDATA".encode())
            fd.write(chheadersize)
            fd.write(chheader.encode())
            fd.write(data)
            chrec = ( None, self.tail+10+len(chheader), datasize, datatype )
            if name in self.datamap:
                if isinstance(self.datamap[name],tree):
                    subnames = ""
                    for n in self.datamap[name]:
                        subnames += f"{name}/{n} " 
                    self.logger.error( "----------------------------------------------------")
                    self.logger.error( " DATA ERROR in __save_chunk_tofd__")
                    self.logger.error(f" Attempt to write data into a name which has at least one subtree: {subnames} ")
                    self.logger.error( "----------------------------------------------------")
                    raise RuntimeError(f" Attempt to write data into a name which has at least one subtree: {subnames} ")
                self.datamap[name].append(chrec)
            else:
                self.datamap[name] = [chrec]
            self.tail += 10 + len(chheader) + datasize #+1
        except BaseException as e:
            self.logger.warning( "----------------------------------------------------")
            self.logger.warning( " DATA ERROR in __save_chunk_tofd__")
            self.logger.warning(f" Cannot write chunk: {e} ")
            self.logger.warning( "----------------------------------------------------")
            raise RuntimeError(f" Cannot write chunk: {e} ")
    def __save_chunk__(self,name,data,datatype):
        if self.mode == 'ro':
            self.logger.warning("----------------------------------------------------")
            self.logger.warning(" DATA ERROR in __save_chunk__")
            self.logger.warning(" Cannot save data into read only 'ro' file/descriptor")
            self.logger.warning("----------------------------------------------------")
            return
        elif self.fd is not None:
            self.__save_chunk_tofd__(self.fd,name,data,datatype)
        elif self.filename is not None:
            try:
                with open(self.filename,"rb+") as fd:
                    self.__save_chunk_tofd__(fd,name,data,datatype)
            except BaseException as e:
                self.logger.warning( "----------------------------------------------------")
                self.logger.warning( " DATA ERROR in __save_chunk__")
                self.logger.warning(f" Cannot save chunk into {self.filename}: {e} ")
                self.logger.warning( "----------------------------------------------------")
                raise RuntimeError(f" Cannot save chunk into {self.filename}: {e} ")
        else:
            self.logger.warning("----------------------------------------------------")
            self.logger.warning(" DATA ERROR in __save_chunk__")
            self.logger.warning(" Cannot save data into virtual file")
            self.logger.warning("----------------------------------------------------")
            return
        #if self.mtime != os.stat(self.filename).st_mtime: self.readfooter()
        return self

    def __read_chunk_fromfd__(self,fd,fl,st,sz,tp):
        fd.seek(st)
        if   tp == "ZNUMPY":
            return np.load(io.BytesIO(zlib.decompress(fd.read(sz)))) 
        elif tp == "NUMPY":
            return  np.load(io.BytesIO(fd.read(sz)))
        elif tp == "ZPYTHON":
            return  json.loads(zlib.decompress(fd.read(sz)))
            #return  eval(zlib.decompress(fd.read(sz)))
        elif tp == "PYTHON":
            return  json.loads(fd.read(sz))
            #return  eval(fd.read(sz))
        elif tp == "ZSTRING":
            return  zlib.decompress(fd.read(sz)).decode()
        elif tp == "STRING":
            return  fd.read(sz).decode()
        else: 
            self.logger.error( "----------------------------------------------------")
            self.logger.error( " DATA ERROR in __read_chunk_fromfd__")
            self.logger.error(f" Unsupported data format : {tp}")
            self.logger.error( "----------------------------------------------------")
            raise RuntimeError(f"Unsupported data format : {tp}")

    def __read_chunk__(self,fl,st,sz,tp):
        self.logger.deepdebug(" > reading chunk: file={}, start={}, size={},type={}".format(fl,st,sz,tp) )
        self.logger.deepdebug(" > reading chunk: open file={}".format(self.filename if fl is None else fl))
        if fl is not None:
            with open(fl,'rb') as fd:
                return self.__read_chunk_fromfd__(fd,fl,st,sz,tp)
        elif self.fd is not None:
            return self.__read_chunk_fromfd__(self.fd,fl,st,sz,tp)
        elif self.filename is not None:
            with open(self.filename,"rb") as fd:
                return self.__read_chunk_fromfd__(fd,fl,st,sz,tp)
        else:
            self.logger.error("----------------------------------------------------")
            self.logger.error(" DATA ERROR in __read_chunk__")
            self.logger.error(" Cannot read from a virtual file" )
            self.logger.error("----------------------------------------------------")
            raise RuntimeError(" Cannot read from a virtual file" )
        self.logger.deepdebug(" > reading chunk: DONE" )
    def __flushbuf__(self):
        self.logger.deepdebug(" __flushbuf__ : maxsize={} cursize={}".format(self.maxbufsize,self.bufsize))
        for n,d,t in self.bufdata:
            if self != self.__save_chunk__(n,d,t): return
        self.writefooter()
        del self.bufdata
        self.bufdata = []
        self.bufsize = 0
        return self
    def aggregate(self,*stkdatafiles):
        for f in stkdatafiles:
            if isinstance(f,data):
                if f.filename == self.filename and self.filename is not None: continue
                for name in f:
                    if not name in self.datamap: self.datamap[name]=[]
                    self.datamap[name] += [ (f.filename if fl is None else fl,st,sz,tp) for fl,st,sz,tp in f.datamap[name] if fl != self.filename or fl is None ]
            elif type(f) is str or type(f) is str:
                with data(f) as tsd:
                    for name in tsd:
                        if not name in self.datamap: self.datamap[name]=[]
                        self.datamap[name] += [ (tsd.filename if fl is None else fl,st,sz,tp) for fl,st,sz,tp in tsd.datamap[name] if fl != self.filename or fl is None ]
            else:
                self.logger.error("----------------------------------------------------")
                self.logger.error(" DATA ERROR in aggregate")
                self.logger.error(" Incorrect type of file {}.".format(f))
                self.logger.error("----------------------------------------------------")
                raise RuntimeError("Incorrect type of file {}.".format(f))
        self.writefooter()

    def defragmentation(self): 
        """
        it goes over all names and check to find gaps in data positions
        after deletion. If there are gaps, it should move data and reset 
        file size.
        """

        reclist  = [ st for nm in self for fl,st,sz,tp in self.datamap[nm] ]
        reclist.sort()
        
        with open(self.filename,"rw+b") as fd:
            mm = mmap.mmap(fd.fileno(), 0)
            l = len(mm)
            p,r,c = 0,0,0
            while p < l:
                while mm[p:p+8] !='#STKDATA' and p < l: p += 1
                if p >= l: continue
                if p != r:
                    mm[r:-p+r] = mm[p:]
                    c += p-r
                    p = r
                chheadersize, = struct.unpack(">H",mm[p+8:p+10])
                sz,ch,ty,name = eval(mm[p+10:p+10+chheadersize])
                df = p+10+chheadersize
                if df+c in reclist:
                    if p != r:
                        mm[r:-p+r] = mm[p:]
                        c += p-r
                        p = r
                    r = p = p+10+chheadersize+sz
                    continue
                else:
                    p = df+sz                    
        self.datamap = {}    
        self.rescan_file()
                

    def memory_available(self):
        with open("/proc/meminfo") as fd:
            stats = fd.read().split("\n")
        #self.logger.deepdebug("stats[1] > {}".format(stats[1]))
        _,avl,unt = stats[1].split()
        avl = eval(avl)
        self.logger.deepdebug("avl,unt = {}{}".format(avl,unt))
        if   unt == "kB" or unt == "KB": return avl*1024
        elif unt == "mB" or unt == "MB": return avl*1024*1024
        elif unt == "gB" or unt == "GB": return avl*1024*1024*1024
        elif unt == "tB" or unt == "TB": return avl*1024*1024*1024*1024
        else                           : return avl

            
    

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s:%(name)-33s%(lineno)-6d%(levelname)-8s:%(message)s', level=logging.DEEPDEBUG)
    if len(sys.argv) < 2:
        print("USAGE: python simtoolkit/data.py data-file-name [second-data-file-name]")
        exit(1)
    if len(sys.argv) == 3:
        with data(sys.argv[1]) as sd1,data(sys.argv[2]) as sd2:
            print("BEFORE ADDING")
            print(" FILE 1:")
            print(" Data length", len(sd1))
            for name in sd1:
                print(" number of chunks in name",name,"=",sd1[name,])
            print()
            print(" FILE 2:")
            print(" Data length", len(sd2))
            for name in sd2:
                print(" number of chunks in name",name,"=",sd2[name,])
            print()
            print("=====================================================\n")
            print("SUMMING File 1 and File 2")
            nsd = sd1 + sd2
            print(" FILE",nsd.filename)                
            print(" Data length", len(nsd))
            for name in nsd:
                print(" number of chunks in name",name,"=",nsd[name,])
            print()
            print(" FILE 1:")
            print(" Data length", len(sd1))
            for name in sd1:
                print(" number of chunks in name",name,"=",sd1[name,])
            print()
            print(" FILE 2:")
            print(" Data length", len(sd2))
            for name in sd2:
                print(" number of chunks in name",name,"=",sd2[name,])
            print()
            print("=====================================================\n")
            print("AGGREGATING File 2 into File 1:")
            #>>aggregate another file.....
            sd1 += sd2
            print("AFTER IN-PLACE ADDITION ANOTHER FILE")
            print(" FILE 1:")
            print("Data length", len(sd1))
            for name in sd1:
                print("number of chunks in name",name,"=",sd1[name,])
            print()
            print(" FILE 2:")
            print(" Data length", len(sd2))
            for name in sd2:
                print(" number of chunks in name",name,"=",sd2[name,])
            print()
            print("=====================================================\n")
            print("#DB>>")
            print("#DB>> TREE:")
            for n in sd1.datamap    :
                for i,p in enumerate(sd1.datamap[n]):
                    print("#DB>>   ",n,"[%02d]="%i,p)
        print() 
        print("CHECK one more time")
        with data(sys.argv[1]) as sd:
            print("Data length", len(sd))
            for name in sd:
                print("number of chunks in name",name,"=",sd[name,])
        for n,i,d in data(sys.argv[1])[None]:
            print("DATACHECK> ",n,"[%03d]="%i,d)
    elif len(sys.argv) == 2:
        print("#DB>> st")
        with data(sys.argv[1],autocorrection=True,maxbuffersize=4096) as sd:
            print("#DB>> in")
            sd["/np/array"]=np.random.rand(50) 
            sd["/x/np/array"]=np.random.rand(70)
            sd["/x/np/long/array"]=np.random.rand(256)
            print("#DB>> TREE:")
            for n in sd.datamap    :
                for i,p in enumerate(sd.datamap[n]):
                    print(" ",n,"[%02d]="%i,p)
            print("Data length", len(sd))
            for name in sd:
                print("number of chunks in name",name,"=",sd[name,])
        print("#DB>> out")
        #exit(0)
        with data(sys.argv[1],compress=False) as sd:
            sd["/prime"]="number"
            sd["/simple"]="words"

        print("data[\"/prime\"]       =",data(sys.argv[1])["/prime"])
        print("data[\"/simple\"]      =",data(sys.argv[1])["/simple"])
        print("data[\"/prime\",None]  =",data(sys.argv[1])["/prime",None])
        print("data[\"/simple\",None] =",data(sys.argv[1])["/simple",None])
        
        with data(sys.argv[1]) as sd:
            sd["/prime"]=(1,2,3,5)


        print("print      data[\"/np/array\"]      =",     data(sys.argv[1])["/np/array"])
        print("print type(data[\"/np/array\"]     )=",type(data(sys.argv[1])["/np/array"]))
        print("print      data[\"/np/array\",None] =",     data(sys.argv[1])["/np/array",None])
        print("print type(data[\"/np/array\",None])=",type(data(sys.argv[1])["/np/array",None]))
        print("print type(data[\"/np/array\",0]   )=",type(data(sys.argv[1])["/np/array",0]))
        print("print data[\"/np/array\",0].shape   =",     data(sys.argv[1])["/np/array",0].shape)
        
        
        for n,i,d in data(sys.argv[1])[None]:
            print("DATACHECK> ",n,"[%03d]="%i,d)

        print("negative chunk"        , data(sys.argv[1])["/x/np/array",-1])
        print("another negative chunk", data(sys.argv[1])["/x/np/long/array",-1])
        print("multiple names ", data(sys.argv[1])["/x/np/"] )
        print("multiple names ", [ n for n in data(sys.argv[1])["/x/np/"]] )
        
        #print "positive oversize", data(sys.argv[1])["/x/np/array", 1000]
        #print "negative oversize", data(sys.argv[1])["/x/np/array",-1000]
