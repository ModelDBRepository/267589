gversion = '3.06'

from cell import dLGN as fitmeneuron   # importing neuron for fitting
from cell import param_nslh            # parameters list each entry is (name,scale,lowest,highest)

project   = 'dLGN-TC-fit-v'
prefix    = ''
postfix   = 'a'
simulator = 'neuron'

if __name__ == "__main__":
    import sys,os
    cmd = ""
    oldgversion = gversion
    with open(sys.argv[0],"r") as fd:
        for il,l in enumerate(fd.readlines()):
            if il == 0 or l[:len("gversion")] == "gversion": continue
            cmd += l
    gversion = [ int(m) for m in  gversion.split(".") ]
    gversion[1] += 1
    gversion =f"{gversion[0]}.{gversion[1]:02d}"
    with open(sys.argv[0],"w") as fd:
        fd.write(f"gversion = \'{gversion}\'\n\n"+cmd)
    os.system(f"git commit version.py -m \'New version {prefix}{gversion}{postfix}\'")
    os.system(f"git tag v{prefix}{gversion}{postfix}")
    os.system(f"mv {project}* {project}{prefix}{gversion}{postfix}")
    os.system(f"mkdir versions/v{prefix}{gversion}{postfix}")
    os.system(f"zip -r versions/{project}{prefix}{gversion}{postfix}.zip dLGN-TC-fit-v{prefix}{gversion}{postfix}")
    
def getversion():
    return f"{prefix}{gversion}{postfix}"
