import logging, OptionParser
import random as pyrandom

if __name__ == "__main__":
	sys.path.append(".")
	from simtoolkit.tree     import tree
	from simtoolkit.database import db	
	from simtoolkit.methods  import methods	
else:
	from .tree     import tree
	from .database import db
    from .methods  import methods

class STK:
    def __init__():
        self.mth = None
