import sys, os,json,gzip
import multiprocessing as mp
from numpy import *
from neuron import h
h.celsius = 35.
from cell import dLGN as themodel
from matplotlib.pyplot import *

stim = [0.025,0.05,0.075,0.10,0.125,0.15,0.175,0.20]
N    = len(stim)
View = False
def worker(prm:dict):
    # Parmaeters analyzes here>>>
    Status = True 
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    nrns = [ themodel(nid=nid) for nid,_ in enumerate(stim) ]
    for p in prm:
        for nid in range(N):
            cmd = f"nrns[{nid}].{p}=prm[\'{p}\']"
            try:
                exec(cmd)
            except BaseException as e:
                sys.stderr.write(f"cannot execute {cmd} : {e}\n")
                exit(1)
    for nid in range(N):
        nrns[nid].setcable()
    vrec= [ h.Vector()                for n in nrns ]
    mrec= [ h.Vector()                for n in nrns ]
    arec= [ h.Vector()                for n in nrns ]
    istm= [ h.IClamp(0.5, sec=n.soma) for n in nrns ]
    trec= h.Vector()
    for n,vr,mr,ar,stm,cur in zip(nrns,vrec,mrec,arec,istm,stim):
        vr.record(n.soma(0.5)._ref_v)
        mr.record(n.axon(0.5)._ref_v)
        ar.record(n.axon(0.0)._ref_v)
        stm.amp    = cur
        stm.delay  = 1000.
        stm.dur    = 1000.
    trec.record(h._ref_t)
    
    h.finitialize()
    h.fcurrent()
    h.frecord_init()
    while h.t < 3000 :h.fadvance()
    trec = array(trec)
    vrec,mrec,arec = [ array(v) for v in vrec ],[ array(v) for v in mrec ] ,[ array(v) for v in arec ] 
    nid = None
    for xnid in range(N):
        if where(vrec[xnid]>0.)[0].shape[0] == 0 : continue
        nid = xnid
        break
    if nid is None and not View:
        return False,None
    
    Status = Status and where(mrec[nid]>0.)[0].shape[0] != 0 and where(arec[nid]>0.)[0].shape[0] != 0
    if Status:
        try:
            xidx = where(vrec[nid]>0.)[0]
            splt = where(xidx[:-1] != xidx[1:]-1)[0]
            splt = array([0]+(splt+1).tolist())
            splt = splt[where(trec[xidx[splt]] > 1000.)]
            astm = splt[where(trec[xidx[splt]] > 2100.)]
            if astm.shape[0] > 0:
                Status = False
            else:
                splt = array([ [xidx[s],where(trec > trec[xidx[s]]+5.)[0][0]] for s in splt ])
                mmax = array([ amax(mrec[nid][l:r]) for l,r in splt])
                emax = array([ amax(arec[nid][l:r]) for l,r in splt])
                Status = not any(mmax-emax > 5.)
        except:
            if View:
                Status = 'Problem'
            else:
                return False,False
        
    #return True,Status
#DB>> 
    if View:
        for xnid in range(N):
            if xnid == 0: 
                ax=subplot(1,N,xnid+1)
                title(f"{Status}")
            else        : subplot(1,N,xnid+1,sharex=ax,sharey=ax)
            plot(trec,vrec[xnid],"k-" ,lw=2)
            plot(trec,mrec[xnid],"y-" ,lw=3)
            plot(trec,arec[xnid],"r--",lw=3)
            ##DB>>
            # if xnid == nid and Status:
                # for l,r in splt:
                    # plot(trec[l:r],trec[l:r]*0.,"b-")
            ##<<DB
        show()
#<<DB
    return True,Status

with open(sys.argv[1]) as fd:
    j = json.load(fd)
models = [ m['parameters'] 
    for r in 'final records unique model models'.split() if r in j
    for m in j[r] if not m is None
]
print(f"READ Total number of models : {len(models)}")
if len(sys.argv) > 2:
    mid = int(sys.argv[2])
    View = True
    worker(models[mid])
else:
    pool = mp.Pool(processes=os.cpu_count())
    result = [pool.apply_async(worker,[p]) for p in models]
    pool.close()
    pool.join()
    result = [r.get() for r in result]
    

    ProblemIDs = [ i for i,(q,p) in enumerate(result) if (not q) and (type(p) is bool) and (not p)]
    print(ProblemIDs)
    CheckQuality = all([ q for q,_ in result])
    if CheckQuality:
        failedmodels = [ i for i,(q,_) in enumerate(result) if not q ] 
        sys.stderr.write(f"Stimulation wasn't enought for this/these model(s): {failedmodels}")
    goodmodels = [ i for i,(q,t) in enumerate(result) if q and t ]
    j["models"] = [ j[r][i] for r in 'final records unique model models'.split() if r in j for i in goodmodels ]
    fname,fext = os.path.splitext(sys.argv[1])
    with open(fname+'-checked'+fext,'w') as fd:
        fd.write("{\n")
        for n in j:
            if n == "models": continue
            fd.write(f"\t\"{n}\" : "+json.dumps(j[n])+",\n")
        fd.write(f"\t\"models\" :[ \n")
        mid = -1
        for m in j["models"]:
            if m is None : continue
            mid += 1
            m["id"]=mid
            fd.write(f"\t\t{json.dumps(m)},\n")
        fd.write(f"\t\t{json.dumps(None)}\n"+"\t]\n}")
    print(f"Only {len(goodmodels)} passed the test")
##DB>>
    # with open(fname+'-tested.debug',"w") as fd:
        # for i,v in enumerate(result):
            # fd.write(f"{i:04d},{v}\n")
#<<DB
