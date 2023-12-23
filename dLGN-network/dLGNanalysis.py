#!/usr/bin/env python
# coding: utf-8
import logging,io
from numpy import *
from neurodsp.spectral import compute_spectrum
from simtoolkit import tree
from simtoolkit import data as stkdata

def getXname(mth,name):
    if mth.check(name):
        if type(mth[name]) is str: return mth[name]
    if mth.check("/sim/record/save"):
        if type(mth["/sim/record/save"]) is str: return mth["/sim/record/save"]
    if mth.check("/sim/record/file"):
        if type(mth["/sim/record/file"]) is str: return mth["/sim/record/file"]
    logging.error("Cannot determent reading file for {} recordings".format(name) )
    exit(1)


def mkanalysis(mdata=None, mth=None, hashline=None, amth=None):
    if mdata is None and mth is None:
        logging.error("mkanalysis() needs at least mdata or mth variables")
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
        epos         = sd["/"+hashline+"/epos",-1]
        # posxy        = sd["/"+hashline+"/posxy",-1]
        # xgapjlst     = sd["/"+hashline+'/gjcon',-1]
        # xsynconlst   = sd["/"+hashline+'/syncon',-1]
        # xgsyncondlst = sd["/"+hashline+'/gsyncond',-1]
    
    if not amth is None:
        #alternative parameters from cmd
        for name in amth:
            mth[name] = amth[name]
            logging.info( " >  Set          : {} = {}".format(name,amth[name]) )
    
    if mth.check("/FR/CorrDist/window") and mth.check("/FR/CorrDist/negative") and\
       mth.check("/FR/CorrDist/positive"):
        logging.info(" > COMPUTE CORRELATION DISTRIBUTION")
        xwindow  = arange(-mth["/FR/CorrDist/window"],mth["/FR/CorrDist/window"],1.)
        nwindow  = exp(-xwindow**2/mth["/FR/CorrDist/negative"]**2)
        xwindow  = exp(-xwindow**2/mth["/FR/CorrDist/positive"]**2)
        xwindow  = xwindow/sum(xwindow)
        xwindow  = xwindow - nwindow/sum(nwindow)
        RGCFR    = zeros( (epos.shape[0],int(ceil(mth["/sim/Tmax"])+1) ) )
        LGNFR    = zeros( (ncells       ,int(ceil(mth["/sim/Tmax"])+1) ) )
        with stkdata(getXname(mth,"/sim/record/spike"), 'ro') as sd:
            us = sd["/"+hashline+"/rGC/spikes",-1]
            for spt,spc in us:
                RGCFR[int(round(spc)),int(round(spt))] += 1
            for sp in sd["/"+hashline+"/spikes"]:
                for spt,spc in sp:
                    if spt > mth["/sim/Tmax"]: continue
                    LGNFR[int(round(spc)),int(round(spt))] += 1
        RGCFR[:,0:10] = 0
        LGNFR[:,0:10] = 0
        CMFR = sum(LGNFR,axis=1)*1000./mth["/sim/Tmax"]
        PMFR = mean(CMFR)
        PSFR = std(CMFR)
        for idx in where(CMFR > PMFR+5*PSFR)[0]:
            LGNFR[idx,:] = 0.
            logging.info(f"   > Remove {idx} neuron - too high FR: {CMFR[idx]} > {PMFR}+5*{PSFR}")
        for rgcid in range( epos.shape[0] ):
            RGCFR[rgcid,:] = convolve(RGCFR[rgcid,:],xwindow,mode='same')
        for nid in range(ncells):
            LGNFR[nid,:]   = convolve(LGNFR[nid,:]  ,xwindow,mode='same')
        
        RGCcorr = corrcoef(RGCFR)
        for rgcid in range( epos.shape[0] ):RGCcorr[rgcid,:rgcid+1] = 10.
        RGCcorr = RGCcorr[ where(RGCcorr <= 1.) ]
        RGCcorr = RGCcorr.flatten()
        
        LGNcorr = corrcoef(LGNFR)
        for nid in range(ncells):LGNcorr[nid,:nid+1] = 10.
        LGNcorr = LGNcorr[ where(LGNcorr <= 1.) ]
        LGNcorr = LGNcorr.flatten()
        
        if not mth.check("/FR/CorrDist/bins") : mth["/FR/CorrDist/bins"] = 201
        if not mth.check("/FR/CorrDist/left") : mth["/FR/CorrDist/left"] =-1
        if not mth.check("/FR/CorrDist/right"): mth["/FR/CorrDist/right"]= 1
        
        RGCh,RGCb = histogram(RGCcorr, bins=mth["/FR/CorrDist/bins"], range=(mth["/FR/CorrDist/left"],mth["/FR/CorrDist/right"]) )
        RGCh,RGCb = RGCh/sum(RGCh), (RGCb[:-1]+RGCb[1:])/2.
        RGCbh     = column_stack((RGCb,RGCh))
        
        LGNh,LGNb = histogram(LGNcorr, bins=mth["/FR/CorrDist/bins"], range=(mth["/FR/CorrDist/left"],mth["/FR/CorrDist/right"]) )
        LGNh,LGNb = LGNh/sum(LGNh), (LGNb[:-1]+LGNb[1:])/2.
        LGNbh     = column_stack((LGNb,LGNh))
        
        xfname    = getXname(mth,"/FR/CorrDist/file")
        with stkdata(xfname) as sd:
            sd["/"+hashline+"/CorrDist/rGC"] = RGCbh
            sd["/"+hashline+"/CorrDist/LGN"] = LGNbh
            logging.info(f"   > saved into {xfname}")
        if mth.check("/FR/CorrDist/save2db"):
            mth["/CorrDist/rGC"] = RGCbh
            mth["/CorrDist/LGN"] = LGNbh
            logging.info(f"   > saved into database")
    else:
        logging.error(" > Cannot compute spike correlation some parameters are missing")
        logging.error("   check parameters /FR/CorrDist/window, /FR/CorrDist/negative, and /FR/CorrDist/positive")
        with stkdata(getXname(mth,"/FR/CorrDist/file")) as sd:
            sd["/"+hashline+"/CorrDist/rGC"] = None
            sd["/"+hashline+"/CorrDist/LGN"] = None
        if mth.check("/FR/CorrDist/save2db"):
            mth["/CorrDist/rGC"] = None
            mth["/CorrDist/LGN"] = None

    if mth.check("/FR/Spectrum/Fmax") and mth.check("/FR/Spectrum/dt") and\
       mth.check("/FR/Spectrum/kernel") and mth.check("/FR/Spectrum/width"):        
        logging.info(" > CMOMPUTING SPECTRUM DENSITY")
        f0 = 1000./mth["/FR/Spectrum/dt"]
        specdt = mth["/FR/Spectrum/dt"]
        nbins  = int(ceil(mth["/sim/Tmax"]/specdt) )+1
        RGCFR    = zeros( (epos.shape[0],int(ceil(mth["/sim/Tmax"])+1) ) )
        LGNFR    = zeros( (ncells       ,int(ceil(mth["/sim/Tmax"])+1) ) )
        with stkdata(getXname(mth,"/sim/record/spike"), 'ro') as sd:
            us = sd["/"+hashline+"/rGC/spikes",-1]
            for spt,spc in us:
                RGCFR[int(round(spc)),int(round(spt))] += 1
            for sp in sd["/"+hashline+"/spikes"]:
                for spt,spc in sp:
                    if spt > mth["/sim/Tmax"]: continue
                    LGNFR[int(round(spc)),int(round(spt))] += 1
        RGCFR[:,0] = 0
        LGNFR[:,0] = 0
        if not mth.check("/FR/Spectrum/filter-off"):
            fr_filter  = arange(-mth["/FR/Spectrum/width"],mth["/FR/Spectrum/width"],1.)
            fr_filter  = exp(-fr_filter**2/mth["/FR/Spectrum/kernel"]**2)
            for rgcid in range( epos.shape[0] ):
                RGCFR[rgcid,:] = convolve(RGCFR[rgcid,:],fr_filter,mode='same')
            for nid in range(ncells):
                LGNFR[nid,:]   = convolve(LGNFR[nid,:]  ,fr_filter,mode='same')
        RGCFR,LGNFR = sum(RGCFR,axis=0),sum(LGNFR,axis=0)
        if not mth.check("/FR/Spectrum/method"): mth["/FR/Spectrum/method"] = 'welch'
        if not mth.check("/FR/Spectrum/type"  ): mth["/FR/Spectrum/type"  ] = 'mean'
        rgcF,rgcP = compute_spectrum(RGCFR, f0, method=mth["/FR/Spectrum/method"], avg_type=mth["/FR/Spectrum/type"  ], nperseg=f0*2)
        rgcP,rgcF = rgcP[where(rgcF < mth["/FR/Spectrum/Fmax"])],rgcF[where(rgcF < mth["/FR/Spectrum/Fmax"])]
        rgcFP     = column_stack((rgcF,rgcP))
        lgnF,lgnP = compute_spectrum(LGNFR, f0, method=mth["/FR/Spectrum/method"], avg_type=mth["/FR/Spectrum/type"  ], nperseg=f0*2)
        lgnP,lgnF = lgnP[where(lgnF < mth["/FR/Spectrum/Fmax"])],lgnF[where(lgnF < mth["/FR/Spectrum/Fmax"])]
        lgnFP     = column_stack((lgnF,lgnP))
        xfname    = getXname(mth,"/FR/Spectrum/file")
        with stkdata(xfname) as sd:
            sd["/"+hashline+"/Spectrum/rGC"] = rgcFP
            sd["/"+hashline+"/Spectrum/LGN"] = lgnFP
            logging.info(f"   > saved into {xfname}")
        if mth.check("/FR/Spectrum/save2db"):
            mth["/Spectrum/rGC"] = rgcFP
            mth["/Spectrum/LGN"] = lgnFP
            logging.info(f"   > saved into database")
    else:
        logging.error(" > Cannot compute spectrum dencity some parameters are missing")
        logging.error("   check parameters /FR/Spectrum/Fmax, /FR/Spectrum/dt, /FR/Spectrum/kernel, and /FR/Spectrum/width")
        with stkdata(getXname(mth,"/FR/Spectrum/file")) as sd:
            sd["/"+hashline+"/Spectrum/rGC"] = None
            sd["/"+hashline+"/Spectrum/LGN"] = None
        if mth.check("/FR/Spectrum/save2db"):
            mth["/Spectrum/rGC"] = None
            mth["/Spectrum/LGN"] = None
        
    return mth
