from mrth import * 
from optparse import OptionParser
oprs = OptionParser("USAGE: python3 %prog [options] stkdata stkdata .....")
oprs.add_option("-s", "--save-json" , dest="sjson" , default=False,   help="save into json"                       , type  = "str")
oprs.add_option("-l", "--load-json" , dest="ljson" , default=False,   help="load from json"                       , type  = "str")

oprs.add_option( "--no-show"        , dest="shown"  , default=True ,  help="Do not show graphs on screen"         , action="store_false")
oprs.add_option( "--png"            , dest="savepng", default=False,  help="Save png file"                        , action="store_true" )
oprs.add_option( "--svg"            , dest="savesvg", default=False,  help="Save svg file"                        , action="store_true" )
oprs.add_option( "--skip-first"     , dest="skip"   , default=-1   ,  help="skip first # hash"                    , type  ="int"        )
oprs.add_option( "--show-lines"     , dest="showlns", default=False,  help="Show individual lines along with mean", action="store_true")
oprs.add_option( '-m',"--cor-min"   , dest="cormin" , default=-0.2 ,  help="minimal correlation to show"          , type  ="float")
oprs.add_option( '-M',"--cor-max"   , dest="cormax" , default= 1.0 ,  help="maximal correlation to show"          , type  ="float")
oprs.add_option( '-Y',"--pro-max"   , dest="promax" , default= 0.25,  help="maximal of proportion"                , type  ="float")
oprs.add_option( '-Z',"--m-cor-max" , dest="meancm" , default= 0.4 ,  help="maximal of mean corelation"           , type  ="float")
oprs.add_option( '-R',"--recompute" , dest="recom"  , default=False,  help="Recompute correlation"                , action="store_true")
oprs.add_option( '-K',"--kernel"    , dest="kernel" , default=20   ,  help="Positive kernel size"                 , type="int")
oprs.add_option( '-L',"--time-lag"  , dest="tlag"   , default=False,  help="Time lag"                             , type="int")
oprs.add_option( "--use-ganglion"   , dest="rgc"    , default=False,  help="Compute metric for rGC"               , action="store_true")
oprs.add_option('--num-of-cores'    , dest="ncores" , default=os.cpu_count(), \
                                                                      help="Use number of cores"                   , type  = "int")
oprs.add_option( '-S',"--swarm"     , dest="swarm"  ,  default=False,  help="show swarm plot instead of stderr"    , action= "store_true")
oprs.add_option( '-V',"--symbol"    , dest="symbol" ,  default=None ,  help="Show a symbol and error bar"          , type  = "str")
oprs.add_option( '-v',"--sym-size"  , dest="synsize",  default=9    ,  help="symbol size"                          , type  = "float")
oprs.add_option( "--save-and-exit"  , dest="sae"    ,  default=False,  help="Save JSON file and exit"              , action= "store_true")
oprs.add_option( "-T","--title"     , dest="title"  ,  default=None,   help="Title"                                , type  = "str")
#oprs.add_option( '-0',"--hide-rGC"  , dest="hidrgc" , default=True ,  help="Hide rGC distribution"                , action="store_false")

opts, args = oprs.parse_args() 

import lzma as xz    
from simtoolkit import tree
from simtoolkit import data as stkdata

if opts.swarm:
    import pandas as pd
    from seaborn import swarmplot

def getCorDist(sp,ncells):
    rkm  = arange(-float(opts.kernel*20),float(opts.kernel*20+1),1)
    rkp  = exp(-rkm**2/float(opts.kernel  )**2)
    rkp /= sum(rkp)
    rkm  = exp(-rkm**2/float(opts.kernel*4)**2)
    rkm /= sum(rkm)
    rka = rkp-rkm
    FRdur = int( ceil(amax(sp[:,0])+10.) )
    FR = zeros( (ncells+1,FRdur) )
    for t,n in sp:
        FR[int(round(n)),int(round(t))] += 1
    FR[:,0] = 0.
    for n in range(ncells+1):
        if opts.tlag and opts.tlag != 0:
            shift = opts.tlag*n
            FR[n,  :   ] = convolve(FR[n,:],rka,mode='same')
            # print(shift, FR[n,shift:].shape, FR[n,:-shift].shape)
            if n != 0:
                FR[n,shift:] = FR[n,:-shift]
                FR[n,:shift] = zeros(shift)
        else:
            FR[n,:] = convolve(FR[n,:],rka,mode='same')
    xcor = corrcoef(FR)
    xcor = array([ xcor[n1,n2] for n1 in range(ncells) for n2 in range(n1+1,ncells) ])
    #xcor[~isfinite(xcor)] = 0
    xcor = xcor[isfinite(xcor)]

    LGNh,LGNb = histogram(xcor, bins=201, range=(-1.,1.) )
    LGNh,LGNb = LGNh/sum(LGNh), (LGNb[:-1]+LGNb[1:])/2.
    return json.dumps([column_stack((LGNb,LGNh)).tolist(),mean(xcor)])


def readafile(f):
    #DB>>
    # print(f,type(f))
    #<<DB
    if type(f) is str:
        _, fext = os.path.splitext(f)
        if   fext == '.stkdata':
            return readafile((f,f))
        elif fext == '.xz':
            with xz.open(f,'r') as fd:
                return readafile((f,fd))
    elif type(f) is tuple:
        f,fd = f
        with stkdata(fd,'ro') as sd:
            try:
                hashline = sd["/hash", -1]
                model    = tree().imp(sd["/"+hashline+"/model",-1])
                if model.check("/network/syn/sig2gsyn"):
                    s2s  = model["/network/syn/sig2gsyn"]
                elif model.check("/network/syn/geom/o2o"):
                    s2s  = 0
                else:
                    print(f"File {f}: there is no sig2syn and o2o isn't true (-.-)")
                    return json.dumps(None)
                ncells = sd['/'+hashline+'/n-neurons',-1]
                NMADp  = model['/network/syn/NMDA/p']
                AMPAp  = model['/network/syn/AMPA/p']
            except BaseException as e:
                print(f"Cannot read {f} file: {e}")
                return json.dumps(None)
            
            #for hashid,hashline in enumerate(sd["/hash"]):
                #if hashid < opts.skip : continue            
            if opts.rgc :
                hashline = sd["/hash",0]
                if not "/"+hashline+"/CorrDist/rGC" in sd or opts.recom:
                    xspikes = sd["/"+hashline+"/rGC/spikes",-1]
                    ncells  = int(amax(xspikes[:,1])+1)
                    #DB>>
                    print(f"Using {ncells} rGC from {f}")
                    #<<DB
                    return json.dumps(json.loads(getCorDist(xspikes,ncells )) + [s2s,NMADp,AMPAp])
                else:
                    corr = sd[f"/{hashline}/CorrDist/rGC", -1]
                    return json.dumps([corr.tolist(),average(corr[:,0], weights=corr[:,1]),s2s,NMADp,AMPAp] )
            else:
                for hashid,hashline in enumerate(sd["/hash",None][opts.skip:]):
                    if not "/"+hashline+"/CorrDist/LGN" in sd or opts.recom:
                        xspikes = None
                        for spk in sd["/"+hashline+"/spikes"]:
                            if xspikes is None: xspikes = spk
                            else:
                                xspikes = append(xspikes,spk,axis=0)
                        if xspikes is None: return json.dumps(None)
                        return json.dumps(json.loads(getCorDist(xspikes,ncells )) + [s2s,NMADp,AMPAp])
                    else:
                        corr = sd[f"/{hashline}/CorrDist/LGN", -1]
                        return json.dumps([corr.tolist(),average(corr[:,0], weights=corr[:,1]),s2s,NMADp,AMPAp] )
                # labels.append([s2s,len(corrdist)-1])
            # if "/"+hashline+"/CorrDist/rGC" in sd and rgdist is None:
                # rgdist = sd["/"+hashline+"/CorrDist/rGC",-1]
    else:
        print(f"Unknow type {f}: {type(f)}")
        return json.dumps(None)
            
        

if opts.ljson:
    with open(opts.ljson) as fd:
        j = json.load(fd)
    args        = j['files']
    corrdist    = [ array(json.loads(xcorr)) for xcorr in j['cordist'] ]
    meancordist = array(j['meancordist'])
    labels      = array([ json.loads(l) for l in j['labels'] ])
else:
    if len(args) == 0:
        print(f"Need at least one data file")
        print(f"python3 {sys.argv[0]} -h for more information")
        exit(1)

    if opts.ncores < 2:
        result      = [ [array(corr), xmean, s2s, NMDAp, AMPAp] for corr, xmean, s2s, NMDAp, AMPAp in [ json.loads(readafile(f)) for f in args ] ]
        meancordist = array([   xmean             for _, xmean, s2s, NMDAp, AMPAp in result ])
        labels      = array([ [s2s, NMDAp, AMPAp] for _,     _, s2s, NMDAp, AMPAp in result ])
        corrdist    = [ array(corr) for corr, _, _, _, _ in result ]
    else:
        import multiprocessing as mp
        print(f"TOTAL TASKS : {len(args)} / KERNEL : {opts.kernel} / TIMELAG : {opts.tlag}")
        pool = mp.Pool(processes=opts.ncores)
        result = [ pool.apply_async(readafile,[tsk]) for tsk in args ]
        pool.close()
        pool.join()
        result      = [json.loads(r.get()) for r in result]
        result    = [ r for r in result if not r is None ]
        meancordist = array([   xmean             for _, xmean, s2s, NMDAp, AMPAp in result ])
        labels      = array([ [s2s, NMDAp, AMPAp] for _,     _, s2s, NMDAp, AMPAp in result ])
        corrdist    = [ array(corr) for corr, _, _, _, _ in result ]
    if opts.sjson:
        with open(opts.sjson, 'w') as fd:
            json.dump({
                'rGC'         : opts.rgc,
                'timelag'     : opts.tlag,
                'recompute'   : opts.recom,
                'kernel'      : opts.kernel,
                'files'       : args,
                'cordist'     : [ json.dumps(xcorr.tolist())  for xcorr in corrdist],
                'meancordist' : meancordist.tolist(),
                'labels'      : [ json.dumps(l.tolist()) for l in labels ]
            },fd, sort_keys=True, indent=4)
    if opts.sae:
        exit(0)

fname,_ = os.path.splitext(args[0])
comname = list(fname)
for f in  args[1:]:
    fname,_ = os.path.splitext(f)
    comname = [ x if x == y else 'X' for x,y in zip(comname,list(fname)) ]

comname = "".join(comname)


s2sunic = unique(labels[:,0])


def catrange(x,y):
    y  = y[where(logical_and(x>=opts.cormin,x<=opts.cormax))]
    x  = x[where(logical_and(x>=opts.cormin,x<=opts.cormax))]
    return x,y

f1 = figure(1, figsize=(16,8))
if opts.title is not None:
    suptitle(opts.title,fontsize=23)
cmap = get_cmap("rainbow")
#cmap = get_cmap("tab10")
subplot(121)
# if rgdist is not None and opts.hidrgc:
    # x,y = rgdist[:,0],rgdist[:,1]
    # x,y = catrange(x,y)
    # plot(x,y,"k-",label="rGC",lw=5 if opts.showlns else 3)


for s in s2sunic:
    si   = int(round(s-1))
    idx, =  where(labels[:,0] == s)
    c = cmap(1-si/9. )
    meancor = None
    for ki,k in  enumerate(idx):
        cd = corrdist[k]
        meancor = cd if meancor is None else column_stack((meancor,cd[:,1]))
        if opts.showlns:                    
            x,y = cd[:,0], cd[:,1]
            x,y = catrange(x,y)
            plot(x,y,"-",c=c,lw=0.75)
                
    if meancor is not None:
        x, y = meancor[:,0],mean(meancor[:,1:],axis=1)
        x,y = catrange(x,y)
        plot(x,y,"-",c=c,lw=3,label=r"$\sigma^2$="+f"{s}")
        #DB>>
        # print(si,s,idx)
        # print(meancor)
        # print(x)
        # print(y)
        #<<DB
            
# if igsyn==0 and idly == 0:
legend(loc='best',fontsize=10)
if type(opts.promax) is float:
    ylim(bottom=0,top=opts.promax)

meanmap = {}
ax2= subplot(122)

if opts.swarm:
    df = pd.DataFrame()
    c  ={}
    for s in s2sunic:
        si   = int(round(s-1))
        idx, =  where(labels[:,0] == s)
        df[s] = [meancordist[k] for k in idx]
        c[s]  = cmap(1-si/9. )
    bar(arange(s2sunic.shape[0]),df.mean(),0.25,fc='None',ec='k')
    _, caplines, _ = errorbar(arange(s2sunic.shape[0]),df.mean(),yerr=df.std(),color='k',linestyle='None',lw=1,lolims=True)
    caplines[0].set_marker('_')
    swarmplot(data = df,palette=c,size=10)
    # ylim(bottom=0)
    # #plot(ALLM[:,0],ALLM[:,i+1],'ko')
    # ylim(bottom=0)
elif opts.symbol is not None:
    print(opts.symbol)
    for s in s2sunic:
        si   = int(round(s-1))
        idx, =  where(labels[:,0] == s)
        c = cmap(1-si/9. )
        meancor = [meancordist[k] for k in idx]
        if len(meancor) > 2:
            y = mean(meancor)
            z = std(meancor)
            plot([si],[y],opts.symbol,c=c,ms=opts.synsize)
            errorbar([si],[y],yerr=[z],color='k')
            
else:
    for s in s2sunic:
        si   = int(round(s-1))
        idx, =  where(labels[:,0] == s)
        c = cmap(1-si/9. )
        meancor = [meancordist[k] for k in idx]
        if len(meancor) > 2:
            y = mean(meancor)
            z = std(meancor)
            bar([si],[y],color=c)
            errorbar([si],[y],yerr=[z],color='k')
if type(opts.meancm) is float:
    ylim(bottom=0,top=opts.meancm)
        
        



if opts.savepng:
    f1.savefig(comname+"-distribution-and-meancorrelation.png")
if opts.savesvg:
    f1.savefig(comname+"-distribution-and-meancorrelation.svg")
if opts.shown  : show()
