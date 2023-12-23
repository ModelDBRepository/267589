#!/usr/bin/env python
# coding: utf-8

import logging,io
from numpy import *
import matplotlib
matplotlib.rcParams["savefig.directory"] = ""
from matplotlib.pyplot import *
from simtoolkit import tree
from simtoolkit import data as stkdata

from dLGNanalysis import getXname

def mkgraphs(mdata=None, mth=None, hashline=None, amth=None):
    if mdata is None and mth is None:
        logging.error("mkgraphs() needs at least mdata or mth variables")
        exit(1)
    elif not mdata is None:
        if hashline is None:
            with stkdata(mdata) as sd:
                hashline = sd["/hash",-1]
        if mth is None:
            with stkdata(mdata) as sd:
                mth = tree().imp(sd['/'+hashline+'/model',-1])
    elif not mth is None:
        mdata = getXname(mth,"")
    
        
    with stkdata(mdata) as sd:
        ncells       = sd['/'+hashline+'/n-neurons',-1]
        cellids      = sd["/"+hashline+'/nprms',-1]
        epos         = sd["/"+hashline+"/epos",-1]
        posxy        = sd["/"+hashline+"/posxy",-1]
        xgapjlst     = sd["/"+hashline+'/gjcon',-1]
        xsynconlst   = sd["/"+hashline+'/syncon',-1]
        xgsyncondlst = sd["/"+hashline+'/gsyncond',-1]

    if not amth is None:
        #alternative parameters from cmd
        for name in amth:
            mth[name] = amth[name]
            logging.info( " >  Set          : {} = {}".format(name,amth[name]) )
    
                
    if not mth.check("/Figures/disable/connectivity"):
        logging.debug("=DRAW  CONNECTIONS=")
        
        if mth.check("/Figures/connectivity/flat"):
            f1=figure(1, figsize=mth["/Figures/FigSize"])
            f1ax = subplot(111)
            xticks(fontsize=6)
            f1ax.set_aspect('equal')

            if not xsynconlst is None:
                for rgcid,nid in xsynconlst:
                    (rgx,rgy),(posx,posy) = epos[rgcid,:],posxy[nid,:]
                    clr = get_cmap('jet')(rgcid/9)
                    f1ax.plot([rgx,posx], [rgy,posy],"-",lw=0.5,c=clr)

            plot(posxy[:,0],posxy[:,1],'o')
            for cid,(x,y) in enumerate(posxy):
                f1.text(x,y,"{:d}".format(cid), fontsize=9)

            for i,grp in enumerate(mth["/stim/rGC/groups"]):
                x,y = epos[i,0],epos[i,1]
                plot(x,y,"o",mfc=get_cmap('jet')(i/9),mec=get_cmap('jet')(i/9))
                text(x,y,"{:d}".format(i),fontsize=16)
            if not xgapjlst is None:
                for i,j in xgapjlst:
                    f1ax.plot([posxy[i,0],posxy[j,0]], [posxy[i,1],posxy[j,1]],"k-",lw=1.5)
        else:
            from mpl_toolkits.mplot3d import Axes3D
            f1   = figure(1, figsize=mth["/Figures/FigSize"])
            f1ax = f1.add_subplot(111, projection='3d')
            cmap = get_cmap('tab10')
            col = [ cmap((i%10)/10+0.05) for i,grp in enumerate(mth["/stim/rGC/groups"])]
            scatter(epos[:,0],epos[:,1], zs=0, zdir='z', s=60, c=col, marker='o')
            for i,(x,y) in enumerate(zip(epos[:,0],epos[:,1])):
                cmap((i%10)/10+0.05)
            if not xsynconlst is None:
                for rgcid,nid in xsynconlst:
                    (rgx,rgy),(posx,posy) = epos[rgcid,:],posxy[nid,:]
                    clr = cmap((rgcid%10)/10+0.05)
                    plot([rgx,posx], [rgy,posy], [0.,1.], "-",lw=0.5,c=clr)
            if not xgapjlst is None:
                for i,j in xgapjlst:
                    plot([posxy[i,0],posxy[j,0]], [posxy[i,1],posxy[j,1]],[1,1],"k-",lw=3.)
            scatter(posxy[:,0],posxy[:,1], zs=1, zdir='z', s=160, c='k', marker='s')
            # show()
            # exit(0)
    else:
        f1 = None

    if    mth.check("/Figures/timerange") and type(mth["/Figures/timerange"]) is tuple and len(mth["/Figures/timerange"]) == 2:
        lt,rt = mth["/Figures/timerange"]
    elif mth.check("/Figures/timerange") and (type(mth["/Figures/timerange"]) is int   or  type(mth["/Figures/timerange"]) is float):
        lt,rt = 0.,float(mth["/Figures/timerange"])
    else:
        lt,rt = None, None
    
    
    logging.debug("=DRAW  SPIKES=")
    f2=figure(2,figsize=mth["/Figures/FigSize"])
    if    mth.check("/sim/record/cont/meancur") and mth.check("/network/cx/enable"): upsubplot = 5
    elif  mth.check("/sim/record/cont/meancur") or  mth.check("/network/cx/enable"): upsubplot = 4
    else:  upsubplot = 3
    axI = subplot(upsubplot,1,1) #rGC raster
    if mth.check("/network/gj/dir"):
        axI.set_title("GJ Direction {}".format(mth["/network/gj/dir"]) ) 
    axP = subplot(upsubplot,1,2,sharex=axI) # dLGN raster
    axR = subplot(upsubplot,1,3,sharex=axI) # Firing rates
    if   mth.check("/sim/record/cont/meancur") and mth.check("/network/cx/enable"):
        axG  = subplot(upsubplot,1,4,sharex=axI) #rGC -> dLGN syn currents
        axCX = subplot(upsubplot,1,5,sharex=axI) #virtual Cx -> dLGN syn currents 
    elif mth.check("/sim/record/cont/meancur"):
        axG  = subplot(upsubplot,1,4,sharex=axI)
    elif mth.check("/network/cx/enable"):
        axCX = subplot(upsubplot,1,4,sharex=axI)
    totspikes = array([])
    with stkdata(getXname(mth,"/sim/record/spike")) as sd:
        us = sd["/"+hashline+"/rGC/spikes",-1]
        if lt is None:
            axI.plot(us[:,0],us[:,1],'k.')
        else:
            us = us[where(logical_and(us[:,0]>lt,us[:,0]<rt) )]
            axI.plot(us[:,0],us[:,1],'k.')
        for sp in sd["/"+hashline+"/spikes"]:
            totspikes = append(totspikes,sp[:,0])
            if lt is None:
                axP.plot(sp[:,0],sp[:,1],'k.')
            else:
                xsp = sp[where( logical_and(sp[:,0]>lt,sp[:,0]<rt) )]
                if xsp.shape[0] == 0: continue
                axP.plot(xsp[:,0],xsp[:,1],'k.')
    if not mth.check("/Figures/disable/2dspiking"):
        ltimepoint, = axP.plot([0.,0.],[0.,ncells],"--",lw=4)
    if mth.check("/FR/kernel") and mth.check("/FR/kernelwidth"):
        if lt is None:
            h,b = histogram(totspikes,bins=int(ceil(mth["/sim/Tmax"])), range=(0,mth["/sim/Tmax"]))
        else:
            h,b = histogram(totspikes,bins=int(ceil(rt-lt)), range=(lt,rt))
        h[0] = 0
        xkernel  = arange(-mth["/FR/kernelwidth"],mth["/FR/kernelwidth"],1.)
        xkernel  = exp(-(xkernel)**2/mth["/FR/kernel"]**2)
        xkernel /= sum(xkernel)
        h        = convolve(h,xkernel,mode='same')
        axR.plot((b[:-1]+b[1:])/2,h,"k-")
    elif mth.check("/FR/window"):
        if lt is None:
            h,b = histogram(totspikes,bins=int(round(mth["/sim/Tmax"]/mth["/FR/window"])), range=(0,mth["/sim/Tmax"]))
        else:
            h,b = histogram(totspikes,bins=int(ceil(rt-lt)), range=(lt,rt))
        h[0] = 0
        axR.plot((b[:-1]+b[1:])/2,h,"k-")
    
    def plotpart(trec,vrec,ax,pat,lt,rt):
        if vrec is not None:
            if lt is None:
                ax.plot(trec,vrec,pat)
            else:
                xidx = where((trec>=lt)*(trec<=rt))[0]
                if xidx.shape[0] != 0:
                    ax.plot(trec[xidx],vrec[xidx],pat)
    
    if   mth.check("/sim/record/cont/meancur"):
        with stkdata(getXname(mth,"/sim/record/cont/meancur")) as sd:
            if not mth.check("/block/gjcon"):
                logging.debug("= MEAN GJ  =")
                for trec,meangj in zip (sd['/'+hashline+"/cont/time"],sd['/'+hashline+"/cont/cur/gj/mean" ]):
                    plotpart(trec,meangj,axG,"k-",lt,rt)
                        
            if not mth.check("/block/syncon"):
                logging.debug("= MEAN SYN  =")
                for trec,meanampa in zip (sd['/'+hashline+"/cont/time"],sd['/'+hashline+"/cont/cur/syn/mean/ampa" ]):
                    plotpart(trec,meanampa,axG,"r-",lt,rt)
                for trec,meannmda in zip (sd['/'+hashline+"/cont/time"],sd['/'+hashline+"/cont/cur/syn/mean/nmda" ]):
                    plotpart(trec,meannmda,axG,"g-",lt,rt)
                    
            if mth.check("/network/cx/enable"):
                logging.debug("= MEAN CORTICAL SYN  =")
                for trec,meanampa in zip (sd['/'+hashline+"/cont/time"],sd['/'+hashline+"/cont/cur/cxsyn/mean/ampa" ]):
                    plotpart(trec,meanampa,axCX,"m-",lt,rt)
                for trec,meannmda in zip (sd['/'+hashline+"/cont/time"],sd['/'+hashline+"/cont/cur/cxsyn/mean/nmda" ]):
                    plotpart(trec,meannmda,axCX,"y-",lt,rt)
            if mth.check("/network/trn/enable"):
                logging.debug("= MEAN TRN SYN  =")
                for trec,meangaba in zip (sd['/'+hashline+"/cont/time"],sd['/'+hashline+"/cont/cur/trnsyn/mean/gaba" ]):
                    plotpart(trec,meangaba,axCX,"b-",lt,rt)


    if not mth.check("/Figures/disable/volt") and mth.check("/sim/record/cont/volt"):
        logging.debug("=DRAW VOLTAGE=")
        f3=figure(3,figsize=mth["/Figures/FigSize"])
        if mth.check("/Figures/FigLimit"):
            Nplot = int(ceil(ncells/mth["/Figures/FigLimit"])+1)
            fnx    = int(floor(sqrt(Nplot)))
            fny    = int(Nplot//fnx+(1 if Nplot%fnx else 0))
            with stkdata(getXname(mth,"/sim/record/cont/volt"), 'ro') as sd:
                for i,n in enumerate( range(0,ncells,mth["/Figures/FigLimit"]) ):
                    if i == 0: ax = subplot(fnx,fny,i+1,sharex=axI)
                    else:      ax = subplot(fnx,fny,i+1,sharex=ax, sharey=ax)
                    xticks(fontsize=6)
                    #title("x={} y={}".format(posxy[n,0],posxy[n,1]),fontsize=6)
                    if type(cellids[n]) is list or type(cellids[n]) is tuple:
                        title(f"DBID = {cellids[n][-1]:d}",fontsize=6)
                    else:
                        title(f"# {cellids[n]:d}",fontsize=6)
                    for trec,volt in zip(sd['/'+hashline+"/cont/time"],sd['/'+hashline+"/cont/volt/{:03d}".format(n) ]):
                        plotpart(trec,volt,ax,"k-",lt,rt)
                        
        else:
            for i in range(ncells):
                if i == 0: ax = subplot(mth["/network/geom/x"],mth["/network/geom/y"],i+1,sharex=axI)
                else:      ax = subplot(mth["/network/geom/x"],mth["/network/geom/y"],i+1,sharex=ax, sharey=ax)
                xticks(fontsize=6)
                #title("x={} y={}".format(posxy[i,0],posxy[i,1]),fontsize=6)
                if type(cellids[i]) is list or type(cellids[n]) is tuple:
                    title(f"DBID = {cellids[i][-1]:d}",fontsize=6)
                else:
                    title(f"# {cellids[i]:d}",fontsize=6)
                for trec,volt in zip(sd['/'+hashline+"/cont/time"],sd['/'+hashline+"/cont/volt/{:03d}".format(i) ]):
                    plotpart(trec,volt,ax,"k-",lt,rt)
        logging.debug("=== DONE ===")
    else:
        f3 = None

    if not mth.check("/Figures/disable/cur") and mth.check("/sim/record/cont/cur"):
        logging.debug("=DRAW CURRENT=")
        f4=figure(4,figsize=mth["/Figures/FigSize"])
        if mth.check("/Figures/FigLimit"):
            Nplot = int(ceil(ncells/mth["/Figures/FigLimit"])+1)
            fnx    = int(floor(sqrt(Nplot)))
            fny    = int(Nplot//fnx+(1 if Nplot%fnx else 0))
            with stkdata(getXname(mth,"/sim/record/cont/cur"), 'ro') as sd:
                for i,n in enumerate( range(0,ncells,mth["/Figures/FigLimit"]) ):
                    if i == 0: ax = subplot(fnx,fny,i+1,sharex=axI)
                    else:      ax = subplot(fnx,fny,i+1,sharex=ax, sharey=ax)
                    xticks(fontsize=6)
                    title("x={} y={}".format(posxy[n,0],posxy[n,1]),fontsize=6)
                    if not mth.check("/block/syncon"):
                        for trec,ampa in zip(sd['/'+hashline+"/cont/time"],sd['/'+hashline+"/cont/cur/syn/ampa/{:03d}".format(n) ]):
                            plot(trec,ampa,"r-")
                        for trec,nmda in zip(sd['/'+hashline+"/cont/time"],sd['/'+hashline+"/cont/cur/syn/nmda/{:03d}".format(n) ]):
                            if not nmda is None: plot(trec,nmda,"g-")
                    if not mth.check("/block/gjcon"):
                        gjtr,gjcr,gjcn = None,None,0
                        for gj0,gj1 in xgapjlst:
                            if gj0 == n :
                                trec,gjcur = sd['/'+hashline+"/cont/time",None],sd['/'+hashline+"/cont/cur/gj/{:03d}x{:03d}".format(gj0,gj1),None ]
                                if gjtr is None: gjtr = trec[:]
                                if gjcr is None: gjcr = gjcur[:]
                                else:
                                    for recid,gji in enumerate(gjcur):
                                        gjcr[recid] += gji
                                gjcn += 1
                            if gj1 == n :
                                trec,gjcur = sd['/'+hashline+"/cont/time",None],sd['/'+hashline+"/cont/cur/gj/{:03d}x{:03d}".format(gj0,gj1),None ]
                                if gjtr is None: gjtr = trec[:]
                                if gjcr is None: gjcr = [ -gji  for gji in gjcur ]
                                else:
                                    for recid,gji in enumerate(gjcur):
                                        gjcr[recid] -= gji
                                gjcn += 1
                        if not gjtr is None:
                            for trec,gji in zip(gjtr,gjcr):
                                plot(trec,gji/gjcn,"k-")
                    if mth.check("/network/cx/enable"):
                        for trec,ampa in zip(sd['/'+hashline+"/cont/time"],sd['/'+hashline+"/cont/cur/cxsyn/ampa/{:03d}".format(n) ]):
                            plot(trec,ampa,"-",c="#b15928")
                        for trec,nmda in zip(sd['/'+hashline+"/cont/time"],sd['/'+hashline+"/cont/cur/cxsyn/nmda/{:03d}".format(n) ]):
                            if not nmda is None:
                                plot(trec,nmda,"-",c="#6a3d9a")
        else:                
            with stkdata(getXname(mth,"/sim/record/cont/cur"), 'ro') as sd:
                for i in range(ncells):
                    if i == 0: ax = subplot(mth["/network/geom/x"],mth["/network/geom/y"],i+1,sharex=axI)
                    else:      ax = subplot(mth["/network/geom/x"],mth["/network/geom/y"],i+1,sharex=ax, sharey=ax)
                    xticks(fontsize=6)
                    title("x={} y={}".format(posxy[i,0],posxy[i,1]),fontsize=6)
                    if not mth.check("/block/syncon"):
                        for trec,ampa in zip(sd['/'+hashline+"/cont/time"],sd['/'+hashline+"/cont/cur/syn/ampa/{:03d}".format(i) ]):
                            plot(trec,ampa,"r-")
                        for trec,nmda in zip(sd['/'+hashline+"/cont/time"],sd['/'+hashline+"/cont/cur/syn/nmda/{:03d}".format(i) ]):
                            if not nmda is None: plot(trec,nmda,"g-")
                    if not mth.check("/block/gjcon"):
                        gjtr,gjcr,gjcn = None,None,0
                        for gj0,gj1 in xgapjlst:
                            if gj0 == i :
                                trec,gjcur = sd['/'+hashline+"/cont/time",None],sd['/'+hashline+"/cont/cur/gj/{:03d}x{:03d}".format(gj0,gj1),None ]
                                if gjtr is None: gjtr = trec[:]
                                if gjcr is None: gjcr = gjcur[:]
                                else:
                                    for recid,gji in enumerate(gjcur):
                                        gjcr[recid] += gji
                                gjcn += 1
                            if gj1 == i :
                                trec,gjcur = sd['/'+hashline+"/cont/time",None],sd['/'+hashline+"/cont/cur/gj/{:03d}x{:03d}".format(gj0,gj1),None ]
                                if gjtr is None: gjtr = trec[:]
                                if gjcr is None: gjcr = [ -gji  for gji in gjcur ]
                                else:
                                    for recid,gji in enumerate(gjcur):
                                        gjcr[recid] -= gji
                                gjcn += 1
                        if not gjtr is None:
                            for trec,gji in zip(gjtr,gjcr):
                                plot(trec,gji/gjcn,"k-")
                    if mth.check("/network/cx/enable"):
                        for trec,ampa in zip(sd['/'+hashline+"/cont/time"],sd['/'+hashline+"/cont/cur/cxsyn/ampa/{:03d}".format(i) ]):
                            plot(trec,ampa,"-",c="#b15928")
                        for trec,nmda in zip(sd['/'+hashline+"/cont/time"],sd['/'+hashline+"/cont/cur/cxsyn/nmda/{:03d}".format(i) ]):
                            if not nmda is None: plot(trec,nmda,"-",c="#6a3d9a")
        logging.debug("=== DONE ===")
    else:
        f4 = None
    
    if mth.check("/FR/CorrDist/window") and mth.check("/FR/CorrDist/negative") and\
       mth.check("/FR/CorrDist/positive") and not mth.check("/Figures/disable/cordist"):
        logging.debug("===DRAW CORRELATION DISTRIBUTION===")
        with stkdata(getXname(mth,"/FR/CorrDist/file"),"ro") as sd:
            RGCbh = sd["/"+hashline+"/CorrDist/rGC",-1]
            LGNbh = sd["/"+hashline+"/CorrDist/LGN",-1]
        if RGCbh is None or LGNbh is None:
            logging.error("Cannot read /CorrDist/rGC or /CorrDist/LGN - skipping Figure 5")
            f5 = None
        else:
            f5=figure(5,figsize=mth["/Figures/FigSize"])
            plot(RGCbh[:,0],RGCbh[:,1],"k-",lw=3,label="RGC")
            plot(LGNbh[:,0],LGNbh[:,1],"-",lw=3,label="LGN")
            legend(loc=1)
            logging.debug("=== DONE ===")
    else:
        f5 = None
        
    if mth.check("/FR/Spectrum/Fmax") and mth.check("/FR/Spectrum/dt") and\
       mth.check("/FR/Spectrum/kernel") and mth.check("/FR/Spectrum/width") and\
       not mth.check("/Figures/disable/spectrum"):        
        logging.debug("===DRAW SPECTRUM DENSITY===")
        with stkdata(getXname(mth,"/FR/Spectrum/file"), 'ro') as sd:
            rgcFP = sd["/"+hashline+"/Spectrum/rGC",-1]
            lgnFP = sd["/"+hashline+"/Spectrum/LGN",-1]
        if rgcFP is None or lgnFP is None:
            logging.error("Cannot read /Spectrum/rGC or /Spectrum/LGN - skipping Figure 6")
            f6 = None
        else:
            f6=figure(6,figsize=mth["/Figures/FigSize"])
            loglog(rgcFP[:,0],rgcFP[:,0]*rgcFP[:,1],"k-",label="RGC",lw=3)
            loglog(lgnFP[:,0],lgnFP[:,0]*lgnFP[:,1],"-" ,label="LGN",lw=3)
            legend(loc=1)
            logging.debug("=== DONE ===")
    else:
        f6 = None
        
    if not mth.check("/Figures/disable/2dspiking"):
        logging.debug("===ITERATIVE GRAPH IS ON===")
        f7cvlt = get_cmap('viridis')
        # f7cspk = get_cmap('tab10')
        f7     = figure(7,figsize=mth["/Figures/FigSize"])
        rgbax  = subplot(121)
        rgbax.get_xaxis().set_visible(False)
        rgbax.get_yaxis().set_visible(False)
        rgbcl  = rgbax.scatter(epos[:,0],epos[:,1], s=80)
        lgnax  = subplot(122)
        lgnax.get_xaxis().set_visible(False)
        lgnax.get_yaxis().set_visible(False)
        lgncl  = lgnax.scatter(posxy[:,0],posxy[:,1], s=80)
        
        with stkdata(getXname(mth,"/sim/record/spike")) as sd:
            rgbrst = sd["/"+hashline+"/rGC/spikes",-1]
            lgnrst = None
            for sp in sd["/"+hashline+"/spikes"]:
                lgnrst = sp if lgnrst is None else vstack((lgnrst,sp))
        with stkdata(getXname(mth,"/sim/record/cont/volt")) as sd:
            timept = []
            for tp in sd["/"+hashline+"/cont/time"]:
                timept.append(tp)
                # totspikes = append(totspikes,sp[:,0])
            # if lt is None:
                # axP.plot(sp[:,0],sp[:,1],'k.')
            # else:
                # xsp = sp[where( logical_and(sp[:,0]>lt,sp[:,0]<rt) )]
                # if xsp.shape[0] == 0: continue
                # axP.plot(xsp[:,0],xsp[:,1],'k.')
        #DB>> 
        # print(rgbrst.shape,lgnrst.shape)
        #<<DB
        for x1,x2 in xgapjlst:
            lgnax.plot(posxy[[x1,x2],0],posxy[[x1,x2],1],"k-",lw=5)
        if mth.check("/Figures/2Dspiking/showtypes"):
            for i in range(ncells):

                lgnax.text(posxy[i,0]+(random.rand()-0.5)/2,posxy[i,1]+(random.rand()-0.5)/2,f"{cellids[i][-1]:d}",fontsize=6)
        if mth.check("/Figures/2Dspiking/projections"):
            outgoinglines = [ [] for x in epos ]
            tab10 = get_cmap("tab10")
            for f,t in xsynconlst:
                l, = rgbax.plot([epos[f,0],posxy[t,0]],[epos[f,1],posxy[t,1]],"-",c=tab10((f%10)/10+0.5) )
                l.set_visible(False)
                outgoinglines[f].append(l)
        def updater():
            rgdc0l,lgnc0l = [ f7cvlt(0) for i in epos ], [ f7cvlt(0) for i in posxy ]
            rgbsz0,lgnsz0 = [ 80        for i in epos ], [ 80        for i in posxy ]
            changedlines=[]
            if mth.check("/Figures/2Dspiking/projections"):
                for l in outgoinglines:
                    if len(l) == 0: continue
                    if not l[0].get_visible(): continue
                    for x in l:x.set_visible(False)
                    changedlines += l
            for tx,rgbx in rgbrst[where((rgbrst[:,0] >= f7keyevent.tp)*(rgbrst[:,0] < f7keyevent.tp+f7keyevent.sz))]:
                rgdc0l[int(rgbx)] = f7cvlt(1)
                rgbsz0[int(rgbx)] = 800
                if mth.check("/Figures/2Dspiking/projections"):
                    for l in outgoinglines[int(rgbx)]:
                        l.set_visible(True)
                        if not l in changedlines:
                            changedlines.append(l)
            idx0 = 0
            while timept[idx0][-1] <  f7keyevent.tp             : idx0 += 1
            idx1 = copy(idx0)
            while timept[idx1][ 0] < f7keyevent.tp+f7keyevent.sz: idx1 += 1
            #if idx0 == idx1: idx +=1
            #DB>>
            #for x in timept: print(x)
            #print(f"UPDATER: idx0={idx0:d}, idx1={idx1:d}, t=[{f7keyevent.tp}, {f7keyevent.tp+f7keyevent.sz}], {timept[idx0][-1]},{timept[idx1][ 0]},{timept[idx0][-1] <  f7keyevent.tp},{timept[idx1][ 0] < f7keyevent.tp+f7keyevent.sz}")
            #<<DB
            with stkdata(getXname(mth,"/sim/record/cont/volt")) as sd:
                xtime = vstack(sd["/"+hashline+"/cont/time",(idx0,idx1)])
                for n in range(ncells):
                    volt = vstack(sd["/"+hashline+f"/cont/volt/{n:03d}",(idx0,idx1)])
                    volt = volt[where((xtime >= f7keyevent.tp)*(xtime < f7keyevent.tp+f7keyevent.sz))]
                    if f7keyevent.md == 0: mvolt = amax(volt)
                    if f7keyevent.md == 1: mvolt = amin(volt)
                    if f7keyevent.md == 2: mvolt = mean(volt)
                    if f7keyevent.md == 3: mvolt = median(volt)
                    xvolt = (mvolt+90)/150.
                    if xvolt < 0. : xvolt = 0.
                    if xvolt > 1. : xvolt = 1.
                    lgnc0l[n] = f7cvlt(xvolt)
                    lgnsz0[n] = xvolt*800
                    
                    #DB>>
                    # print(n,mvolt,xvolt)
                    #<<DB
            rgbcl.set_color(rgdc0l)
            rgbcl.set_sizes(rgbsz0)
            lgncl.set_color(lgnc0l)
            lgncl.set_sizes(lgnsz0)
            ltimepoint.set_xdata([f7keyevent.tp,f7keyevent.tp])
            tmark.set_text(f"t={f7keyevent.tp:0.1f}\ndt={f7keyevent.sz:0.1f} ms\nmd={f7keyevent.md}")
            
                
            return [rgbcl,lgncl,ltimepoint,tmark]+changedlines

            
            
        def f7keyevent(event):
            if   event.key == "down"    :  f7keyevent.tp -= f7keyevent.sz
            elif event.key == "up"      :  f7keyevent.tp += f7keyevent.sz
            elif event.key == "left"    :  f7keyevent.tp  = max(rgbrst[where(rgbrst[:,0]<f7keyevent.tp),0][0][-1],lgnrst[where(lgnrst[:,0]<f7keyevent.tp),0][0][-1])
            elif event.key == "right"   :  f7keyevent.tp  = min(rgbrst[where(rgbrst[:,0]>f7keyevent.tp),0][0][ 0],lgnrst[where(lgnrst[:,0]>f7keyevent.tp),0][0][ 0])
            elif event.key == "+"       :  f7keyevent.sz  = 0.8*f7keyevent.sz
            elif event.key == "-"       :  f7keyevent.sz  = 1.3*f7keyevent.sz
            elif event.key == "m"       :  f7keyevent.md  = (f7keyevent.md + 1 )%4
            
            # elif event.key == "pageup":    idx -= 20
            # elif event.key == "pagedown":  idx += 20
            # elif event.key == "home":      idx  = where(thv.t/ms < 100.)[0][-1]+1
            # elif event.key == "end":       idx  = where(thv.t/ms < 200.)[0][-1]+1
            if f7keyevent.sz < 0.5              : f7keyevent.sz = 0.5
            if f7keyevent.sz > mth["/sim/Tmax"] : f7keyevent.sz = mth["/sim/Tmax"]
            if f7keyevent.tp < 0                : f7keyevent.tp = 0
            if f7keyevent.tp > mth["/sim/Tmax"] : f7keyevent.tp = mth["/sim/Tmax"]
            updater()
            f7.canvas.draw()
            f2.canvas.draw()
            print( f"t={f7keyevent.tp} dt={f7keyevent.sz} ms" )
        
        # for trec,volt in zip(sd['/'+hashline+"/cont/time"],sd['/'+hashline+"/cont/volt/{:03d}".format(n) ]):
        
        # excc0l,inhc0l = [ f3cmap(0) for i in range(mth["/nrn/exc/num"]) ], [f3cmap(0) for i in range(mth["/nrn/inh/num"]) ]
        # for exci in excspk.i[where((excspk.t >= keyevent.tp)*(excspk.t < keyevent.tp+keyevent.sz))[0]]:
            # excc0l[exci] = f3cmap(0.45)
        # for inhi in inhspk.i[where((inhspk.t >= keyevent.tp)*(inhspk.t < keyevent.tp+keyevent.sz))[0]]:
            # inhc0l[inhi] = f3cmap(0.09)
        # esctr.set_color(excc0l)
        # isctr.set_color(inhc0l)
        # f6.canvas.draw()
        # print( "t={} ms".format(keyevent.tp/ms) )
        
   
        f7keyevent.tp = 0.
        f7keyevent.sz = mth["/Figures/2Dspiking/timestep"] if mth.check("/Figures/2Dspiking/timestep") else 2.
        f7keyevent.md = 0
        tmark = rgbax.text(4.5,2.0,f"t={f7keyevent.tp:0.1f}\ndt={f7keyevent.sz:0.1f} ms\nmd={f7keyevent.md}",fontsize=24)
        f7.canvas.mpl_connect('key_press_event', f7keyevent)
        

        
    if mth.check("/Figures/STKDB-Record"):
        if f1 is None:
            f1data = None
        else:
            f1data = io.BytesIO()
            f1.savefig(f1data, format="png", dpi=f1.dpi)
            f1data = f1data.getvalue()

        f2data = io.BytesIO()
        f2.savefig(f2data, format="png", dpi=f2.dpi)
        f2data = f2data.getvalue()
        
        if f3 is None:
            f3data = None
        else:
            f3data = io.BytesIO()
            f3.savefig(f3data, format="png", dpi=f3.dpi)
            f3data = f3data.getvalue()

        if f4 is None:
            f4data = None
        else:
            f4data = io.BytesIO()
            f4.savefig(f4data, format="png", dpi=f4.dpi)
            f4data = f4data.getvalue()

        if f5 is None:
            f5data = None
        else:
            f5data = io.BytesIO()
            f5.savefig(f5data, format="png", dpi=f5.dpi)
            f5data = f5data.getvalue()

        if f6 is None:
            f6data = None
        else:
            f6data = io.BytesIO()
            f6.savefig(f6data, format="png", dpi=f6.dpi)
            f6data = f6data.getvalue()

        return (f1,f2,f3,f4,f5,f6),(f1data,f2data,f3data,f4data,f5data,f6data)
    else:
        return (f1,f2,f3,f4,f5,f6),(None,None,None,None,None,None)

def savegraphs(mth,*figures):
    if not mth.check("/Figures/formats"):
        mth["/Figures/formats"] = ['png']
        logging.info(" < /Figures/formats isn't set, will safe only png")
    if not (type(mth["/Figures/formats"]) is list or type(mth["/Figures/formats"]) is tuple):
        if type(mth["/Figures/formats"]) is str:
            mth["/Figures/formats"] = mth["/Figures/formats"].split(",")
        else:
            logging.error(" > /Figures/formats must be a list o string separated by comas, but got {} - skipping saving figures".fotmat(type(mth["/Figures/formats"])))
            return
    if not (type(mth["/Figures/formats"]) is list or type(mth["/Figures/formats"]) is tuple):
        logging.error(" > Cannot figure out /Figures/formats. Skipping saving figures")
        return
    for figfrm in mth["/Figures/formats"]:
        if type(figfrm) is not str:
            logging.error(f" > Bad format type {figfrm} ({type(figfrm)}) but should be string. Skipping!")
            continue
        for fi,f in enumerate(figures):
            if not f is None: f.savefig(mth["/Figures/X-term"]+f"-F{fi+1:d}."+figfrm)
        logging.info(f" >  Saved {figfrm:<7s} : "+" ".join([ f"F{fi+1:d}={not f is None}" for fi,f in enumerate(figures)]) )

if __name__ == "__main__":
    from optparse import OptionParser
    oprs = OptionParser("USAGE: %prog [flags] stkdata-file [variables]",add_help_option=False)
    oprs.add_option("-p", "--print-hash"  ,  dest="ph", default=False,  help="prints list of hashes in the file and exit",action="store_true")
    oprs.add_option("-P", "--print-model" ,  dest="pm", default=False,  help="prints model parameters for each recording",action="store_true")
    oprs.add_option("-H", "--hash"        ,  dest="hl", default=None,   help="reads recording with specified hash the file (default latest)")
    oprs.add_option("-A", "--analyze"     ,  dest="al", default=False,  help="Analyze recordings",action="store_true")
    oprs.add_option("-L", "--log"         ,  dest="lg", default=None,   help="Output log to the file (default on the screen)")
    oprs.add_option("-l", "--log-level"   ,  dest="ll", default="INFO", help="Level of logging may be CRITICAL, ERROR, WARNING, INFO, or DEBUG (default INFO)") 
    oprs.add_option("-h", "--help"        ,  dest="hp", default=False,  help="Print this help", action="store_true")
    options, args = oprs.parse_args()

    if options.hp:
        #print("\n\n"+mth.mainmessage)
        oprs.set_usage("""USAGE: %prog [flags] stkdata-file [variable]\n
    Any model parameter can be altered by /parameter_name=parameter_value in command line""")
        oprs.print_help()
        #print(mth.printhelp())
        exit(0)
    
    if len(args) == 0:
        sys.stderr.write("Specify input stkdata file. -h for list of options \n")
        exit(1)

    if options.ph:
        with stkdata(args[0],'ro') as sd:
            print(args[0])
            for xhash,xtimesamp in zip(sd["/hash"],sd["/timestamp"]):
                print(" > ",xhash," : ",xtimesamp)
            print()
        exit(0)

    if options.pm:
        with stkdata(args[0],'ro') as sd:
            print(args[0])
            for xhash,xtimesamp in zip(sd["/hash"],sd["/timestamp"]):
                print(" > ",xhash," : ",xtimesamp)
                model = tree().imp(sd['/'+xhash+'/model',-1])
                for name in model:
                    print(" > {: <24s} = {}".format(name,model[name]) )
            print()
        exit(0)
        
    if options.lg is None:
        logging.basicConfig(format='%(asctime)s:%(lineno)-6d%(levelname)-8s:%(message)s', level=eval("logging."+options.ll) )
    else:
        logging.basicConfig(filename=options.lg, format='%(asctime)s:%(name)-33s%(lineno)-6d%(levelname)-8s:%(message)s', level=eval("logging."+options.ll) )

    logging.info("======================================")
    logging.info("===       Plotting Figures         ===")
    logging.info(f" >  Recording    : {args[0]}")
    logging.info(f" >  HASH         : {options.hl}" )
    
    # vvv This is fast and dirty way to provide changes to methods in the file.
    #     It repeats the same code fro simtoolkit/method class, and should be removed
    amth = tree()
    for kv in args[1:]:
        k_and_v = kv.split("=",1)
        if len(k_and_v) != 2:
            logging.error("Cannot get parameter : {}".format(kv) )
            continue
        key,value = k_and_v
        try:
            value = eval(value)
        except BaseException as e:
            logging.error("Cannot evaluate value {} : error {}".format(value,e) )
            continue
        amth[key]=value
        logging.info( " >  Accept       : {}={}".format(key,value))

    # ^^^
    amth["/Figures/STKDB-Record"]=False
    amth["/sim/record/file"]=args[0]
    
    if options.al:
        from dLGNanalysis import mkanalysis
        mth = mkanalysis(mdata=args[0],hashline=options.hl,amth=amth)
    else:
        mth = None
    
    

    if amth.check("/Figures/X-term"):
        import matplotlib
        matplotlib.use('Agg')

    (f1,f2,f3,f4,f5,f6),_ =mkgraphs(mdata=args[0], mth=mth, hashline=options.hl, amth=amth)
    if amth.check("/Figures/X-term"):
        logging.info(" >  Saving Fig   : {}".format(amth["/Figures/X-term"]) )
        savegraphs(amth,f1,f2,f3,f4,f5,f6)
    else:
        show()
    logging.info("===               DONE             ===")
    logging.info("======================================")

    # mth = methods("", 'mth', locals(), argvs = args )

    # mth.generate()

    

