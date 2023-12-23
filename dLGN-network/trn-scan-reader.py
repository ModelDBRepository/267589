from numpy import *
import json, sys, os, time
import lzma as xz
import matplotlib
matplotlib.rcParams["savefig.directory"] = ""
from matplotlib.pyplot import *
from simtoolkit import tree
from simtoolkit import data as stkdata

from optparse import OptionParser
oprs = OptionParser("USAGE: %prog [flags] [variable]")
oprs.add_option("-s", "--save-json"    , dest="sjson" , default=None,    help="save into json"              , type="str")
oprs.add_option("-l", "--load-json"    , dest="ljson" , default=None,    help="load from json"              , type="str")
oprs.add_option("-q", "--recompute"    , dest="recomp", default=False,   help="Recompute correlation"       , action="store_true")
oprs.add_option("-B", "--num-of-cores" , dest="ncores", default=os.cpu_count(), \
                                                                            help="Use number of cores"      , type="int"  )
oprs.add_option("-R", "--re-normalize" , dest="renorm", default=False,   help="Renormalize g_inh by the final g_exc conductnace" \
                                                                                                            , action="store_true")
oprs.add_option("-X", "--use-max"      , dest="usemax", default=False,   help="Use max instead fo mean"     , action="store_true")
oprs.add_option("-M", "--estimate-FR"  , dest="estFR" , default=False,   help="Estimate FR"                 , action="store_true")
#-------
"""
oprs.add_option( "-o"     , dest="output"   , default=None     ,  help="output file"                        , type  ="str"        )
opts, args = oprs.parse_args() 

with stkdata(opts.output,mode='w') as wsd:
    for f in args:
        with xz.open(f) as fd:
            with stkdata(fd,dtype='stkdata',mode='ro') as sd:
                hashline = sd["/hash",-1]
                wsd["/hash"] = hashline
                wsd[f"/{hashline}/srcfile"] = f
                for n in sd:
                    if not hashline in n: continue
                    for ch in sd[n]: wsd[n] = ch
        print(f,print(hashline),'is copied')
"""
#-------


def getcor(sig2gsyn,trngsyn,trndly,t2r,ncells,spikes):
    sp = array(spikes)
    f0 = 1000. # 1ms bin = 1kHz sample rate
    rkm  = arange(-600.,601.,1)
    
    rkp  = exp(-rkm**2/20.**2)
    rkp /= sum(rkp)
    rkm  = exp(-rkm**2/80.**2)
    rkm /= sum(rkm)
    rka  = rkp-rkm
    FRdur = int(ceil(amax(sp[:,0]))+1)
    FR  = zeros( (ncells,FRdur) )
    cFR = zeros( FR.shape  )
    for t,n in sp:
        FR[int(round(n)),int(round(t))] += 1        
    FR[:,0:10] = 0.
    for n in range(ncells):
        cFR[n,:] = convolve( FR[n,:],rka,mode='same')

    xcor = corrcoef(cFR)
    xcor = array([ xcor[n1,n2] for n1 in range(ncells) for n2 in range(n1+1,ncells) ])
    xcor[~isfinite(xcor)] = 0
    meancor = mean(xcor)
    h,b = histogram(xcor, bins=201, range=(-1.,1.) )
    h,b = h/sum(h), (b[:-1]+b[1:])/2.
    cd = column_stack((b,h))#.tolist()
    maxcor = cd[argmax(cd[:,1]),0]
    #print(meancor, average(cd[:,0], weights=cd[:,1]), maxcor)
    #print(cd)
    #exit(0)
    #<<DB
    return json.dumps([sig2gsyn,trngsyn,trndly,t2r,meancor,maxcor])
    

def readFR(f):
    if not f.endswith('.stkdata.xz'):
        print(f"input file {f} doesn't seem like xz commpressed stkdata")
        return None
    fname = f[:-len('.stkdata.xz')]
    with open(fname+'-FR.json') as fd:
        ll = None
        for l in fd.readlines():
            ll = l[:]
    meanFR = mean(array(json.loads(ll)))
    with open(fname+'-blockTRN-FR.json') as fd:
        ll = None
        for l in fd.readlines():
            ll = l[:]
    meanTRNBLKFR = mean(array(json.loads(ll)))
    if meanFR == 0: return 0
    else : return meanTRNBLKFR/meanFR
    # 131->363 (1-141)


def readndata(f,readspikes=False):
    print(f"Reading {f}")
    with xz.open(f,'r') as fd:
        with stkdata(fd,mode="ro",dtype='stkdata') as sd:
            try:
                hashline = sd['/hash',-1]
                ncells   = sd[f'/{hashline}/n-neurons',-1]
                model    = tree().imp(sd[f'/{hashline}/model',-1])
                sig2gsyn = model['/network/syn/sig2gsyn']
                trndly   = model['/network/trn/delay']
                trngsyn  = abs(model['/network/trn/gsyn'])
                wsyn0    = array(sd[f"/{hashline}/gsyn",0])
                wsyn1    = array(sd[f"/{hashline}/gsyn",-1])
                t2r      = trngsyn/mean(wsyn1)
                correl   = sd[f"/{hashline}/CorrDist/LGN",-1]
                meancor  = average(correl[:,0],weights=correl[:,1])
                maxcor   = correl[argmax(correl[:,1]),0]
                if readspikes :
                    correl   = correl.tolist()
                    xspikes = None
                    for spk in sd[f"/{hashline}/spikes"]:
                        if xspikes is None: xspikes = spk
                        else:
                            xspikes = append(xspikes,spk,axis=0)
                    xspikes = xspikes.tolist()
            except BaseException as e:
                sys.stderr.write(f"Cannot reaf{f} : {e}\n")
                return None
    #print(meancor,maxcor)
    #print(correl)
    if opts.estFR and not readspikes:
        frp = readFR(f)
        return [sig2gsyn,trngsyn,trndly,t2r,meancor,maxcor,frp]
    elif readspikes:
        return  [sig2gsyn,trngsyn,trndly,t2r,ncells,xspikes]
    else:
        return [sig2gsyn,trngsyn,trndly,t2r,meancor,maxcor]
                

def worker(f):
    x = readndata(f,readspikes=True)
    if x is None: return None
    if opts.estFR:
        ret = json.loads(getcor(*x))
        frp = readFR(f)
        ret.append(frp)
        return json.dumps(ret)
    else:
        return getcor(*x)

opts, args = oprs.parse_args()
recs = []
if opts.ljson is not None:
    with open(opts.ljson) as fd:
        j = json.load(fd)
    recs = j['recs']
    args = j['files']
else:
    if len(args) == 0:
        print("Need input!")
        exit(1)
    if not opts.recomp:
        for f in args:
            r = readndata(f)
            if r is None: continue
            recs.append(r)

if opts.recomp:
    if opts.ncores < 2:
        recs = [ worker(f) for f in args]
    else:
        import multiprocessing as mp
        pool = mp.Pool(processes=opts.ncores)
        result = [pool.apply_async(worker,[f]) for f in args]
        pool.close()
        pool.join()
        recs = [json.loads(r.get()) for r in result]           
    
if opts.sjson is not None:
    with open(opts.sjson,'w') as fd:
        if opts.recomp:
            fd.write("{\n\t\"Recomputed\" : "+json.dumps(time.strftime("%Y-%mm-%d %H-%M-%S"))+",\n")
        else:
            fd.write("{\n\t\"Recomputed\" : "+json.dumps(None)+",\n")
        fd.write("\t\"files\" : "+json.dumps(args)+",\n")
        fd.write("\t\"recs\"  : "+json.dumps(recs)+"\n")
        fd.write("}\n")

recs = array(recs)
u_s2g = unique(recs[:,0])
u_syn = unique(recs[:,1])
u_dly = unique(recs[:,2])
u_t2r = unique(recs[:,3])
print(u_s2g)
print(u_syn)
print(u_dly)
print(u_t2r)

#cmap  = get_cmap('bwr')
cmap  = get_cmap('coolwarm')
smap  = get_cmap('rainbow')
dmap  = get_cmap('Greys')
corminmax = amax( abs(recs[:,4]) )
figure(1)
if opts.renorm:
    nr=(u_s2g.shape[0]*2) if opts.estFR else u_s2g.shape[0]
    for i,c in enumerate(u_s2g):
        idx = where(recs[:,0] == c)[0]
        subplot(1,nr,i+1)
        title(f'{c}')
        h=scatter(recs[idx,2],recs[idx,3],c=recs[idx, 5 if opts.usemax else 4],vmin=-corminmax,vmax=corminmax,cmap=cmap)
        colorbar(h)
        yscale('log')
        xscale('log')
    if opts.estFR:
        sps = u_s2g.shape[0]
        maxfrr = amax(recs[:, 6])
        for i,c in enumerate(u_s2g):
            idx = where(recs[:,0] == c)[0]
            subplot(1,nr,i+1+sps)
            title(f'{c}')
            h=scatter(recs[idx,2],recs[idx,3],c=recs[idx, 6],vmin=0,vmax=maxfrr,cmap=smap)
            colorbar(h)
            #contour(recs[idx,2],recs[idx,3],recs[idx, 6], [2.77])
            yscale('log')
            xscale('log')
else:
    a_syn = log10(u_syn)
    da = around(a_syn[1] - a_syn[0],2)
    a_syn = append(a_syn, a_syn[-1]+da)-da/2
    a_syn = 10**a_syn

    a_dly = log10(u_dly)
    da = around(a_dly[1] - a_dly[0],2)
    a_dly = append(a_dly, a_dly[-1]+da)-da/2
    a_dly = 10**a_dly

    cormaps=[]
    if opts.estFR:
        frmaps = []
    
    for c in u_s2g:
        cormap = zeros( (u_syn.shape[0],u_dly.shape[0],4) )
        if opts.estFR:
            frmap = zeros( (u_syn.shape[0],u_dly.shape[0],4) )
        for i,s in enumerate(u_syn):
            for j,d in enumerate(u_dly):
                idxs = where((recs[:,0] == c)*(recs[:,1] == s)*(recs[:,2] == d))[0]
                if idxs.shape[0] == 0:
                    print(f"SIGMA:{c}, Gsyn:{s}, Delay:{d} : Index size zero")
                    continue
                cors = []
                if opts.estFR:
                    frs = []
                for idx in idxs:
                    cors.append( recs[idx,  5 if opts.usemax else 4] )
                    if opts.estFR:
                        frs.append( recs[idx,6] )
                cors = array(cors)
                if opts.estFR:
                    frs  = array(frs)
                cormap[i,j,:] = array([mean(cors),std(cors),amin(cors),amax(cors) ])
                if opts.estFR:
                    frmap[i,j,:] = array([mean(frs),std(frs),amin(frs),amax(frs) ])
        cormaps.append([c,cormap])
        if opts.estFR:
            frmaps.append(frmap)

    nr=(len(cormaps)*2) if opts.estFR else len(cormaps)
    
    maxcor = max([ amax(c[:,:,0]) for _,c in cormaps ] )
    maxcst = max([ amax(c[:,:,1]) for _,c in cormaps ] )
    for i,(c, cormap) in enumerate(cormaps):
        subplot(4,nr,i+1)
        title(f'{c}')
        h=pcolormesh(a_dly,a_syn,cormap[:,:,0],shading='flat',vmin=-maxcor,vmax=maxcor,cmap=cmap)
        # h=pcolormesh(a_dly,a_syn,cormap[:,:,0],shading='flat',vmin=0,vmax=corminmax,cmap=smap)
        colorbar(h)
        yscale('log')
        xscale('log')
        
        subplot(4,nr,i+1+nr)
        h=pcolormesh(a_dly,a_syn,cormap[:,:,1],shading='flat',vmin=0,vmax=maxcst,cmap=dmap)
        colorbar(h)
        yscale('log')
        xscale('log')
        
        subplot(4,nr,i+1+nr*2)
        h=pcolormesh(a_dly,a_syn,cormap[:,:,2],shading='flat',vmin=-maxcor,vmax=maxcor,cmap=cmap)
        colorbar(h)
        yscale('log')
        xscale('log')

        subplot(4,nr,i+1+nr*3)
        h=pcolormesh(a_dly,a_syn,cormap[:,:,3],shading='flat',vmin=-maxcor,vmax=maxcor,cmap=cmap)
        colorbar(h)
        yscale('log')
        xscale('log')
    
    if opts.estFR:
        maxfrr = amax(recs[:, 6])
        maxfst = max([ amax(f[:,:,1]) for f in frmaps ] )
        sps    = len(frmaps)
        for i,frmap in enumerate(frmaps):
            subplot(4,nr,i+1+sps)
            h=pcolormesh(a_dly,a_syn,frmap[:,:,0],shading='flat',vmin=0,vmax=maxfrr,cmap=smap)
            colorbar(h)
            contour(u_dly,u_syn,frmap[:,:,0], [2.3])
            yscale('log')
            xscale('log')

            subplot(4,nr,i+1+sps+nr)
            h=pcolormesh(a_dly,a_syn,frmap[:,:,1],shading='flat',vmin=0,vmax=maxfst,cmap=dmap)
            colorbar(h)
            contour(u_dly,u_syn,frmap[:,:,0], [2.3])
            yscale('log')
            xscale('log')

            subplot(4,nr,i+1+sps+nr*2)
            h=pcolormesh(a_dly,a_syn,frmap[:,:,2],shading='flat',vmin=0,vmax=maxfrr,cmap=smap)
            colorbar(h)
            contour(u_dly,u_syn,frmap[:,:,2], [2.3])
            yscale('log')
            xscale('log')

            subplot(4,nr,i+1+sps+nr*3)
            h=pcolormesh(a_dly,a_syn,frmap[:,:,3],shading='flat',vmin=0,vmax=maxfrr,cmap=smap)
            colorbar(h)
            contour(u_dly,u_syn,frmap[:,:,3], [2.3])
            yscale('log')
            xscale('log')
    
show()
