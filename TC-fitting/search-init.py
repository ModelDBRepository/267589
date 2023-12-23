import sys, os, json
from numpy import *
from cell import dLGN
from neuron import h

    
def worker(nid):
    # print(nid)
    parameters = models[nid]["parameters"]

    nrn = dLGN(nid=nid)
    for p in parameters:
        try:
            exec("nrn."+p+f"= {parameters[p]}")
        except BaseException as e:
            sys.stderr.write(f"Cannot set parameter {p} to {parameters[p]}:\n\t{e}\n")
            exit(1)
    nrn.setcable()

    for x in nrn.soma : x.v = -76.
    for x in nrn.axon : x.v = -76.
    
    if 'init' in models[nid]:
        for var in models[nid]['init']:
            varinit = models[nid]['init'][var]
            try:
                exec(f"nrn."+var+"= varinit")
            except BaseException as e:
                sys.stderr.write(f"Cannot set dynamic variable{var} into initical condition {varinit}:\n\t{e}\n")
                exit(1)
    h.finitialize()
    h.fcurrent()
    h.frecord_init()
    h.t = 0.
    while h.t < 60000 :h.fadvance()
    return { 'soma.v': nrn.soma.v, 'axon.v': nrn.axon.v }

if len(sys.argv) < 2:
    sys.stderr.write("USAGE: json-file \n")
    exit(1)
try:
    with open(sys.argv[1]) as fd:
        j = json.load(fd)
except BaseException as e:
    sys.stderr.write(f"Cannot read parameter database {src}:\n\t{e}\n")
    exit(1)

if not "models" in j:
    sys.stderr.write(f"Cannot convert find \"models\" list in {sys.argv[1]}\n")
    exit(1)
models = [ m for m in j["models"] if m is not None ]
print("Searching steady-state")
import multiprocessing as mp
pool = mp.Pool(processes=os.cpu_count())
result = [pool.apply_async(worker,[nid]) for nid in range(len(models))]
pool.close()
pool.join()
result = [r.get() for r in result]

for nid,init in enumerate(result):
    j["models"][nid]['init'] = init
    j["models"][nid]['id'  ] = nid
src = sys.argv[2] if len(sys.argv) > 2 else sys.argv[1]
with open(src,'w') as fd:
    fd.write("{\n")
    for n in j:
        if n == "models": continue
        fd.write(f"\t\"{n}\" : "+json.dumps(j[n])+",\n")
    fd.write(f"\t\"models\" :[ \n")
    for m in j["models"]:
        if m is None : continue
        fd.write(f"\t\t{json.dumps(m)},\n")
    fd.write(f"\t\t{json.dumps(None)}\n"+"\t]\n}")
