import os, sys, types, logging,json
from collections import OrderedDict
from numpy import *

class tree(OrderedDict):
    def __init__(self, hsymbol="/"):
        """
        simtoolkil.tree ia a simple tree class
        the position in the tree defines by hierarchical symbol 
        `hsymbol = "/"` (by default)
        
        The same node cannot be a root of subtree and contains a value.
        Node names cannot have space, new-line, and tab symbols 
        as a first or last symbol, but eventually they are allowed inside.
        """
        super(tree,self).__init__()
        self.hsymbol = hsymbol
        self.logger = logging.getLogger("simtoolkit.tree[class]")
    def __clean_the_key__(self,key):
        skey = key.strip(" \n\t\r"+self.hsymbol)
        parts = skey.split(self.hsymbol, 1)
        return skey,parts
    def __setitem__(self, key, value):
        """
        sets a value for a key item
        """
        skey,parts = self.__clean_the_key__(key)
        if type(value) is dict:
            for n,v in self.__mapdict__(value):
                self[skey+self.hsymbol+n]=v
        elif isinstance(value,tree): 
            for name in value:
                self[skey+name.replace(value.hsymbol,self.hsymbol)] = value[name]
        elif len(parts) == 2:
            if not super(tree,self).__contains__( parts[0] ): 
                super(tree,self).__setitem__(parts[0], tree(hsymbol = self.hsymbol))
            elif not isinstance(self[parts[0]], tree)       : 
                super(tree,self).__setitem__(parts[0], tree(hsymbol = self.hsymbol))
            self[parts[0]].__setitem__(parts[1], value)
        else:
            super(tree, self).__setitem__(skey, value)

    def __getitem__(self, key):
        """
        returns a value for a key.
        if key in None returns an interator on top names
        """
        if key is None: return self.dict()
        skey,parts = self.__clean_the_key__(key)
        if len(parts) == 2:
            if not super(tree,self).__contains__( parts[0] ): 
                self.logger.error("__getitem__({}): Cannot find a subtree {} in the tree".format(key,parts[0]))
                raise KeyError(   "__getitem__({}): Cannot find a subtree {} in the tree".format(key,parts[0]))
            try:
                return self[parts[0]][parts[1]]
            except BaseException as e:
                self.logger.error("__getitem__({}): Cannot resolve name {} in {} : {}".format(key, parts[1],parts[0],e))
                raise KeyError(   "__getitem__({}): Cannot resolve name {} in {} : {}".format(key, parts[1],parts[0],e))
        else:
            if not super(tree,self).__contains__( skey ): 
                self.logger.error("__getitem__({}): Cannot find an item \'{}\' in the tree ".format(key, skey))
                raise KeyError(   "__getitem__({}): Cannot find an item \'{}\' in the tree ".format(key, skey))
            return super(tree, self).__getitem__(skey)
    def __contains__(self,key):
        skey,parts = self.__clean_the_key__(key)
        if len(parts) == 2:
            if not super(tree, self).__contains__(parts[0]): return False
            if not isinstance(self[parts[0]], tree) : return False
            return parts[1] in self[parts[0]]
        else:
            if not super(tree, self).__contains__(skey): return False
            return True
    def __delitem__(self, key):
        skey,parts = self.__clean_the_key__(key)
        if len(parts) == 2:
            if parts[0] not in self: 
                self.logger.error("__delitem__({}): Cannot find a subtree {} in the tree".format(key, parts[0]))
                raise KeyError(   "__delitem__({}): Cannot find a subtree {} in the tree".format(key, parts[0]))
            self[parts[0]].__delitem__(parts[1])
        else:
            if skey not in self: 
                self.logger.error("__delitem__({}): Cannot find an item {} in the tree".format(key, skey))
                raise KeyError(   "__delitem__({}): Cannot find an item {} in the tree".format(key, skey))
            super(tree,self).__delitem__(skey)        
    def keys(self): return list(iter(self))
    def __iter__(self):
        """
        generates all names in the tree and all subtrees
        """
        for name in self.dict().__iter__():
            if isinstance(self[name], tree):
                for c in self[name].__iter__():
                    yield name+c
            else:
                yield name
    def dict(self):
        """
        behaves as generator of the parent class
        """
        for name in super(tree, self).__iter__(): yield self.hsymbol+name
    def obj(self):
        """
        generates only names that are objects not a subtrees at the top level
        """
        for name in super(tree, self).__iter__():
            if not isinstance(self[name], tree):  yield self.hsymbol+name
    def dict_contains(self,key):
        """
        returns __contains__(key) of parent class
        """
        return super(tree, self).__contains__(key)
    def check(self, key):
        """
        if key is a more or less reasonable parameter returns True...
        """
        if not self.__contains__(key): return False
        xvalue= self[ key ]
        if type( xvalue ) is bool or type( xvalue ) is int: return bool( xvalue )
        elif xvalue is None :  return False
        elif type( xvalue ) is str and xvalue == '': return False
        elif (type( xvalue ) is list or type( xvalue ) is tuple) and len(xvalue) == 0: return False
        else: return True
    def __mapdict__(self,mapd,parent=""):
        for n in mapd:
            if type(mapd[n]) is dict:
                self.mapdict(mapd[n], parent = parent+self.hsymbol+n )
            else:
                yield (parent+self.hsymbol+n, mapd[n]) 
    def exp(self):
        """
        export content to a json string
        """
        names={}
        for n in self: names[n] = self[n]
        return json.dumps(names)
    def imp(self, data):
        """
        import a tree structure and values from a json string
        """
        zjson = json.loads(data,object_pairs_hook=OrderedDict)
        for name in zjson:
            self[str(name)] = zjson[name]
        return self
    def printnames(self, space = "", parent="", sort=False, maxlen = 21):
        """
        helper function for printing pretty trees
        |- > b  4
        |-v: c  
        | `- > d  12
        |-v: dic  
        | |- > z  z
        | |- > x  x
        | |- > c  c
        | |- > v  v
        | |- > b  b
        | `- > n  n
        `- > zzz  zzzzz

        """
        root = []
        #maxlen += max([ len(name) for name in self[None] ])
        if sort:
            for nidx,name in enumerate( sorted( self[None] ) ):
                if isinstance(self[name],tree):
                    lastflag = nidx==len(self)-1
                    root.append( ("%s%sv: %s "%(space, "`-" if lastflag else "|-", name[1:]), None,space) )
                    root += self[name].printnames(space=space+"  " if lastflag else space+"| ",parent=parent+name, sort=sort)
                else:
                    root.append( ("%s%s > %s "%(space,"`-" if nidx==len(self)-1 else "|-", name[1:]), parent+name,space) ) 
        else:
            for nidx,name in enumerate( self[None] ):
                if isinstance(self[name],tree):
                    lastflag = nidx==len(self)-1
                    root.append( ("%s%sv: %s "%(space, "`-" if lastflag else "|-", name[1:])+" "*(maxlen-len(name)-len(space)), None,space) )
                    root += self[name].printnames(space=space+"  " if lastflag else space+"| ",parent=parent+name)
                else:
                    root.append( ("%s%s > %s "%(space,"`-" if nidx==len(self)-1 else "|-", name[1:])+" "*(maxlen-len(name)-len(space)), parent+name,space) ) 
        return root

            
if __name__ == "__main__":
    x=tree()
    x['/w']=1024
    x["/a"]=2
    x["/b"]=4
    x["/c"]=8
    print( "x=", x,"\n 1------------")
    x["/a/w"]=11
    x["/a/b"]=10
    x["/c/d"]=12
    print( "x=", x )
    print( "x['c']['d']=",x['c']['d'])
    print( "x.check(\"/a\")=",x.check("/a") )
    print( "x.check(\"/z\")=",x.check("/z"),"\n 2------------")
    
    for n in x:
        print( "n=% 6s"%n,", x[n]=",x[n])
    print( " 3------------")
    for n in x.obj():
        print( "n=% 6s"%n,", x[n]=",x[n])
    print( " 4------------" )
    for n in x[None]:
        print( "n=% 6s"%n,", x[n]=",x[n])
    print( " 5------------" )
    x["/dic"] = {'a':1,'b':2.5,'c':3}
    x["/a/w"]=22
    for n in x:
        print( "n=% 6s"%n,", x[n]=",x[n])
    print( " 6------------")
    rep = x.exp()
    print( "export:", rep )
    print( "import:", tree().imp(rep) )
    print( " 7------------" )
    print( "names", x.printnames() )
    print( " 8------------\n  PRINT NAMES" )
    print( x.printnames(sort=True) )
    for p,k,s in x.printnames(sort=True):
        if k is None:
            print( "p=% 6s"%p )
        else:
            print( "p=% 6s"%p,", k=% 6s"%k,", x[k]=",x[k] )
    print( " 9------------")
    for p,k,s in x.printnames():
        print( p, "" if k is None else x[k])
    print( " A------------")
    del x["/a"]
    for p,k,s in x.printnames():
        print( p, "" if k is None else x[k])
    print( " B------------" )
    del x["/w"]
    for p,k,s in x.printnames():
        print( p, "" if k is None else x[k])
    print( " C------------")
    del x["/dic/a"]
    for p,k,s in x.printnames():
        print( p, "" if k is None else x[k])
    print( " D------------" )
    del x["/dic/b"]
    del x["/dic/c"]
    print( x.exp() )
    for p,k,s in x.printnames():
        print( p, "" if k is None else x[k])
    print( " E------------" )
    print( " vvv ???? vvv" )
    print( x.check("/dic") )
    print( x["/dic"] )
    print( " ^^^ ???? ^^^" )
    print( " F------------" )
    y=tree()
    for n in 'z','x','c','v','b','n': y[n]=n
    x["/dic"] = y
    x["/zzz"] = "zzzzz"
    for p,k,s in x.printnames():
        print( p, "" if k is None else x[k])
    
