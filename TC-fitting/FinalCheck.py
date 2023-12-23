import sys, os, json
from numpy import *
if len(sys.argv) > 3 :
    import matplotlib
    matplotlib.use('Agg')
from matplotlib.pyplot import *
from pyneuronautofit import Evaluator, RunAndTest
from project import fitmeneuron as dLGN

with open(sys.argv[1]) as fd:
    j = json.load(fd)
lst_model = j["models"] if "models" in j else j["model"]
lst_model = [ p for p in lst_model if p is not None ]
    # (
        # p["parameters"],p["target"], p["evaluation"],
        # (p['id'] if 'id' in p else None), (p['src'] if 'src' in p else None), (p['src'] if 'src' in p else None)
    # for p in lst_model if p is not None
# ]
print(f"Total number model {len(lst_model)}")
targets  = j["targets"]
ntargets = len(targets)
print(f"Total number of targets {ntargets}")
evaluations = [ n for n in j["evaluations"] ]
if "sources" in j:
    sources  = j["sources"]
    nsources = len(sources)
    print(f"Total number of sources {nsources}")
else:
    sources = None


def worker(nid):
    prms = lst_model[nid]["parameters"]
    init = lst_model[nid]["init"] if "init" in lst_model[nid] else None
    evaluator = Evaluator(targets[lst_model[nid]['target']], savetruedata=True, **j["evaluations"][lst_model[nid]["evaluation"]])
    trec,vrec = RunAndTest(evaluator,celsius=35.,dt=None, params=prms, init=init).__run__(view=True)
    sp = None
    nh = len(vrec)//8 + (1 if len(vrec)%8  else 0)
    f  = figure(nid, figsize=(24,16) )
    for ir,(mrec,nrec) in enumerate( zip(vrec,evaluator.TrueData) ):
        if ir == 0:
            sp = subplot(nh, 8, ir+1)
            title(f"Mode #{nid:4d}")
        else: subplot(nh, 8, ir+1, sharex=sp, sharey=sp)
        if ir == 1: title(f"Targert: {targets[lst_model[nid]['target']]}")
        if sources is not None:
            if ir == 5: title(f"Source : {sources[lst_model[nid]['src'   ]]}")
            if ir == 7: title(f"#{lst_model[nid]['selection']}")
        plot(arange(nrec.shape[0])*evaluator.expdt,nrec)
        plot(trec, mrec)
    if len(sys.argv) > 3 :
        for x in sys.argv[3:]:
            f.savefig(x.format(nid))
    else:
        show()
    f.clear()
    # clear(f)
    del f
    return nid


nid = eval(sys.argv[2])
if   type(nid) is int: 
    print(f"Testing {nid:4d} neuron")
    worker(nid)
elif nid is None:

    import multiprocessing as mp
    pool = mp.Pool(processes=os.cpu_count())
    result = [pool.apply_async(worker,[nid]) for nid in range(len(lst_model))]
    pool.close()
    pool.join()
    for r in result:
        print(f"Neuron #{r.get()} is tested")


