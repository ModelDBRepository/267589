from numpy import *
import json, sys, os, time
import lzma as xz
import matplotlib
matplotlib.rcParams["savefig.directory"] = ""
from matplotlib.pyplot import *
from scipy.interpolate import griddata

from simtoolkit import tree
from simtoolkit import data as stkdata

from optparse import OptionParser
oprs = OptionParser("USAGE: %prog [flags] [variable]")
oprs.add_option("-s", "--save-json"    , dest="sjson" , default=None,    help="save into json"                              , type="str")
oprs.add_option("-l", "--load-json"    , dest="ljson" , default=None,    help="load from json"                              , type="str")
oprs.add_option("--cor-log"            , dest="corlog", default=False,   help="plot correlation map in log scale"           , action="store_true")
oprs.add_option("--trn-lin"            , dest="trnlog", default=True,    help="plot TRN block / CONTROL FR map in lin scale", action="store_false")
oprs.add_option("--ctx-lin"            , dest="ctxlog", default=True,    help="plot CTX block / CONTROL FR map in lin scale", action="store_false")
oprs.add_option("-I", "--interpolate"  , dest="interp", default=False,   help="interpolation"                               , action="store_true")
oprs.add_option("--interpolate-method" , dest="intmth", default='cubic', help="interpolation method: nearest/linear/cubic"  , type="str")
oprs.add_option("--cor-minmax"         , dest="cormim", default=None,    help="minimal/max correlation scale"               , type="float")
oprs.add_option("-B", "--num-of-cores" , dest="ncores", default=os.cpu_count()                                              , type="int"  ,\
                help="Use number of cores")

opts, args = oprs.parse_args()

def read_Stkdata(fd):
    with stkdata(fd,mode="ro",dtype='stkdata') as sd:
        try:
            hashline = sd['/hash',-1]
            ncells   = sd[f'/{hashline}/n-neurons',-1]
            model    = tree().imp(sd[f'/{hashline}/model',-1])
            sig2gsyn = model['/network/syn/sig2gsyn']
            trndly   = model['/network/trn/delay']
            trngsyn  = abs(model['/network/trn/gsyn'])
            rcwsyn0  = array(sd[f"/{hashline}/gsyn",0])
            rcwsyn1  = array(sd[f"/{hashline}/gsyn",-1])
            cxtdly   = model['/network/cx/delay']
            cxtgsyn  = abs(model['/network/cx/gsyn'])
            correl   = sd[f"/{hashline}/CorrDist/LGN",-1]
            meancor  = average(correl[:,0],weights=correl[:,1])
            maxcor   = correl[argmax(correl[:,1]),0]
            
            # if readspikes :
                # correl   = correl.tolist()
                # xspikes = None
                # for spk in sd[f"/{hashline}/spikes"]:
                    # if xspikes is None: xspikes = spk
                    # else:
                        # xspikes = append(xspikes,spk,axis=0)
                # xspikes = xspikes.tolist()
        except BaseException as e:
            sys.stderr.write(f"Cannot reaf{f} : {e}\n")
            return None
    return sig2gsyn, trngsyn, trndly, cxtgsyn, cxtdly, meancor, maxcor
        
def read_json(f):
    try:
        with open(f) as fd:
            for l in fd.readlines():
                L = json.loads(l)
        return array(L)
    except:
        return None

def read_data(f):
    print(f"READING {f}")
    fname  = os.path.basename(f)
    fname  = fname.split('-')
    _,fext = os.path.splitext(f)
    if   fext == '.xz' :
        with xz.open(f,'r') as fd:
            sig2gsyn, trngsyn, trndly, cxtgsyn, cxtdly, meancor, maxcor = read_Stkdata(fd)
        controlFD = read_json(f[:-len(".stkdata.xz")]+'-FR.json')
        trhblkFD  = read_json(f[:-len(".stkdata.xz")]+'-blockTRN-FR.json')
        ctxblkFD  = read_json(f[:-len(".stkdata.xz")]+'-blockCTX-FR.json')
    elif fext == '.stkdata' :
        sig2gsyn, trngsyn, trndly, cxtgsyn, cxtdly, meancor, maxcor = read_Stkdata(f)
        controlFD = read_json(f[:-len(".stkdata")]+'-FR.json')
        trhblkFD  = read_json(f[:-len(".stkdata")]+'-blockTRN-FR.json')
        ctxblkFD  = read_json(f[:-len(".stkdata")]+'-blockCTX-FR.json')
    else:
        print(f"Cannot read {f}")
        return None
    if controlFD is None or trhblkFD is None or ctxblkFD is None:
        print(f"Cannot read {f}: {controlFD is None} {trhblkFD is None} {ctxblkFD is None}")
        return None
    trhblkFD /= controlFD
    ctxblkFD /= controlFD
    trhblkFD  = trhblkFD[isfinite(trhblkFD)]
    ctxblkFD  = ctxblkFD[isfinite(ctxblkFD)]
    return [fname[7],sig2gsyn, trngsyn, trndly, cxtgsyn, cxtdly, meancor, maxcor, mean(trhblkFD), std(trhblkFD),mean(ctxblkFD),std(ctxblkFD)]


if opts.ljson != None:
    with open(opts.ljson) as fd:
        j = json.load(fd)
    args = j['files']
    results = j['results']
else:
    if opts.ncores < 1:
        cordisdiff = [read_data(f) for f in args]
    else:
        import multiprocessing as mp
        pool = mp.Pool(processes=opts.ncores)
        result = [pool.apply_async(read_data,[f]) for f in args]
        pool.close()
        pool.join()
        results = [r.get() for r in result]
    results = [ r for r in results if r is not None]
    if opts.sjson != None:
        with open(opts.sjson,'w') as fd:
            json.dump({
            'files'   : args,
            'results' : results
            },fd)

marks = {}
for i,(x,_,_,_,_,_,_,_,_,_,_,_) in enumerate(results):
    if not x in marks: marks[x] = []
    marks[x].append(i)
print(marks)
marklist  = sorted([x for x in marks])
    
results   = array([ [s,tg,td,cg,cd,m,M,mTRN,mCTX] for _,s,tg,td,cg,cd,m,M,mTRN,sTRN,mCTX,sCTX in results ])

resultset = []
for m in marklist:
    idx =  marks[m]
    print(m,len(idx))
    resultset.append(results[idx[0],:5].tolist()+[\
        mean(results[idx,5]),std(results[idx,5]),\
        mean(results[idx,6]),std(results[idx,6]),\
        mean(results[idx,7]),std(results[idx,7]),\
        mean(results[idx,8]),std(results[idx,8]) \
        ])
resultset = array(resultset)
print(resultset.shape)
# exit(0)
sig2gsyn = unique(results[:,0])
trngsyn  = unique(results[:,1])
trndly   = unique(results[:,2])
cxtgsyn  = unique(results[:,3])
cxtdly   = unique(results[:,4])
print(sig2gsyn)

bwr = get_cmap('bwr')

for i,s in enumerate(sig2gsyn):
    r = resultset[where(resultset[:,0] == s)]
    figure(i+1)
    suptitle(r"$\sigma$ = "+f"{s}")
    X = [[2,3,4],[3,4],[4]]
    Y = [   1,    2,    3  ]
    C = [ log10(r[:,5])  if opts.corlog else r[:,5], # CORR
          log10(r[:,9])  if opts.trnlog else r[:,9], # TRNBLK
          log10(r[:,11]) if opts.ctxlog else r[:,11] # CTXBLK
        ]
    XL = [ r"TRN delay", r"CTX $g_{syn}$" , r"CTX delay" ]
    YL = [ r"TRN $g_{syn}$",r"TRN delay", r"CTX $g_{syn}$"]
    cnt = 1
    for yi,y in enumerate(Y):
        for ci,c in enumerate(C):
            cnt += yi
            for xi, x in enumerate(X[yi]):
                subplot(3,9,cnt); cnt += 1
                if xi == 0:
                    ylabel(YL[yi])
                    xlabel(XL[yi])
                if opts.interp:
                    points = column_stack((log10(r[:,x]),log10(r[:,y])))
                    xmin,xmax = amin(points[:,0]),amax(points[:,0])
                    ymin,ymax = amin(points[:,1]),amax(points[:,1])
                    grid_x, grid_y = mgrid[xmin:xmax:100j, ymin:ymax:100j]
                    grid_z = griddata(points, c, (grid_x, grid_y), method=opts.intmth)
                    if opts.cormim is not None and ci == 0:
                        h = pcolormesh(10**grid_x, 10**grid_y, grid_z,\
                        vmin = -(log10(opts.cormim) if opts.corlog else opts.cormim),\
                        vmax =   log10(opts.cormim) if opts.corlog else opts.cormim ,\
                        cmap=get_cmap('coolwarm'))
                    else:
                         h = pcolormesh(10**grid_x, 10**grid_y, grid_z)
            
                    if   ci == 1:
                        contour(10**grid_x,10**grid_y,grid_z,[log10(2.3) if opts.trnlog else 2.3],colors=['w'])
                    elif ci == 2:
                        contour(10**grid_x,10**grid_y,grid_z,[log10(0.7842105263157895) if opts.trnlog else 0.7842105263157895],colors=['w'])
                    
                else:
                    h=scatter(r[:,x],r[:,y],c=c)
                colorbar(h)
                yscale('log')
                xscale('log')
            


show()


