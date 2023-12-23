#!/usr/bin/env python
# coding: utf-8

stkdefault = """
/{

dLGN network desynchronization at P7-P10

Ruben Tikidji-Hamburyan GWU 2020-2022
}

/network/{
    /nprms/{
        /db    = '../P07-selected-checked-gmin-20220921.json' \;
                             ; file with neuron parameter database
        /lst   = 'models'    ; variable with list of parameters
        /gmin  = 'gsynmin'   ; variable with minimal conductance
        /threshold = 0.      ; spike threshold
    }
    /geom/{
        /shape = 'H'         ; H-hexagonal or S-square
        /x     = 7           ; number of columns
        /y     = 16          ; number of rows
    }
    /annoying_hetero = True \; If set True, it guaranties that all neurons in population are different. 
                             ; For this option, one needs database bigger than network size.
    /gj/{
        /geom/{
            /p     = 0.3    ; gap junction probability
            /unit  = 'n'   \; if 'n' - /network/gj/geom/p probability of connection per neuron.
                           \; if 'c' - /network/gj/geom/p is probability of connection per pear of neurons
                           \;     within maxd distance
                            ; if 'o' - /network/gj/geom/p is average number of GJ per neuron.
            /maxd  = 1.5    ; gap junction max distance
            /mind  = None   ; gap junction min distance
            /dir   = None   ; gap junction direction (random if None)
        }
        /r     = 600.      \; gap junction resistance.
                           \; 2022/02/04:
                           \; For current neuron database this resistance produces spikelets with
                           \; dV = 1.7 +- 0.22  mV and absolute range for all neurons [0.95,2.8] mV,
                           \; Coupling coefficients  mean = 0.4+-0.077 range=[0.087,0.58] aren't 
                           \; compatible with VBN coupling Lee et al. 2010, but spikelet 
                            ; amplitude is similar to spikelets in cat LGN Hughes et al. 2002
    }
    /syn/{
        /gsyn      = None  \; synaptic conductance: 
                           \; if positive - set for everyone, 
                           \; if negative - set the portion of minimal synaptic conductance for a neuron,
                            ; if None set to 1/3 of the  minimal synaptic conductance for each neuron.
        /rand      = False  ; If ture - gsyn randomly init between 0 and /syn/gsyn value
        /prenorm   = True  \; If true the total synaptic conductance will be set to /syn/gsyn value for 
                           \; each neuron in the **beginning**! 
                           \; It is active only in model building. For dynamical normalization 
                            ; see /network/btdp
        /geom/{
            /unit  = 'N'   \; Pattern of synaptic connectivity:
                           \; 'o' - one-to-one creates only one connection for each rGC to a closest LGN cell.
                           \; 'a' - all-to-all connections: each rGC connects all dLGN cells.
                           \;       This is the best configuration for btdp.
                           \;       You can use /network/syn/sig2gsyn to create a Gaussian distributions of weights
                           \; 'e' - exponential distribution uses /network/syn/geom/pmax for maximum probability and 
                           \;       /network/syn/geom/sig for sigma.
                           \; 'E' - same as e but distance computed from the closets rGC
                           \; 'g' - Gaussian distribution. it uses /network/syn/geom/pmax for maximum probability and 
                           \;       /network/syn/geom/sig for sigma.
                           \; 'G' - same as g but distance computed from the closets rGC
                           \; 'r' - random distribution
                           \; 'n' - random number between /network/syn/geom/nmin and /network/syn/geom/nmax
                           \;       for each TC is generated. rGC are picked randomly
                           \; 'c' - connect to closets (but not one) rGC
                           \; 'N' - same as n but closet rGC are picked
                            ; ADD HERE MORE IF NEEDED!
            /pmax  = None   ; peak of synaptic probability for exponential or Gauusian distributions.
            /sig   = None   ; sigma for exponential or Gauusian distributions.
            /nmin  = 7      ; minimum of rGC connection per TC
            /nmax  = 20     ; maximum of rGC connection per TC
        }
        /sig2gsyn  = None   ; sigma for create Gaussian distributions of weights with distance
        /AMPA/{
            /p      = 1     ; portion of AMPA conductance
            /tau1   = 1.    ; AMPA rising time constant
            /tau2   = 2.2  \; AMPA falling time contant From Chen & Regehr 2000 Table 1 P10-P14
                            ; Inconsistent with Hauser et al. 2014 AMPA $\\tau_d \\approx 5.47$ ms
        }
        /NMDA/{
            /p      = 2.25 \; portion of NMDA conductance
                           \; /AMPA/p and /NMDA/p are computed from Shah & Crair 2008 as followed:
                           \; For _P6–P7_ : $i_{AMPA}/i_{NMDA} = \\beta_{P7} =0.78 \pm 0.09$ (peak-to-peak)
                           \; comparable with $\\beta_{P10} = 0.5 \pm 0.1$ from Chen & Regehr 2000
                           \; for voltage clamp $i_{vl}=g_{vl}*(E-V_{vl})$ where $E=0$ reversal potential
                           \; for NMDA and AMPA, and $v_{VL}$ potential for voltage clamp.
                           \; $g_{vl}=i_{vl}/v_{vl}$ conductance
                           \; $\\frac{g_{AMPA}}{g_{NMDA}}=\\frac{i_{AMPA}}{i_{NMDA}} \\frac{\Delat_{NMDA}}{\Delat_{AMPA}}$,
                           \; where $\Delat_{NMDA}$ and $\Delat_{AMPA}$ are differences between 
                           \; holding potentials and the reversal potential for NMDA and AMPA currents
                           \; $\\frac{\Delat_{NMDA}}{\Delat_{AMPA}}$ = 40 mV / 70 mV = 0.57
                           \; $\\frac{g_{NMDA}}{g_{AMPA}} = \\frac{1}{0.57 \\beta_{P7}} \\approx 2.25$
                           \; Note that Dilger et al. 2015 estimated $\\beta_{P10} \\approx 1$ which
                           \; give /NMDA/p=1/0.57$\\approx 1.75$.
                           \; The value from from Chen & Regehr 2000 $\\beta_{P10} = 0.5 \pm 0.1$
                            ; gives /NMDA/p=1/(0.57*0.5)$\\approx 3.5$.
            /tau1   = 1.    ; NMDA rising time constant
            /tau2   = 150. \; NMDA falling time contant From Chen & Regehr 2000 Table 1 P10-P14
                            ; Consistent with Dilger et al 2015 
        }
        /ppr_u0     = 0.3  \; sets presynaptic single spike depression
                           \; it's adjusted to obtain paired-pulse ratio 0.73 
                            ; From Chen & Regehr 2000 Table 1 P10-P14
       /toneExc     = None  ; Conductance for tonic excitation (None to block)
       /toneInh     = None  ; Conductance for GABA_B receptors (None to block)
    }
    /file           = 'dLGN-network.stkdata' \;
                            ; save/read network configuration to/from this file
    /load           = True  ; read network from the file (if True) or from another file (if filename given)
    /save           = True  ; save network to   the file (if True) or to   another file (if filename given)
    /reload/{
        /nprms      = False\; sets specific record within the file from there neuron parameters will be
                            ;   reread or the first one if True
        /gjcon      = False\; sets specific record within the file from there gap-junction connections list
                            ;  will be reread or the first one if True
        /syncon     = False\; sets specific record within the file from there list of synaptic connections 
                            ;  will be reread or the first one if True
        /gsyncond   = False\; sets specific record within the file from there list of synaptic conductance
                            ;  will be reread or the first one if True
    }
    /reset/{
        /nprms      = False ; reset neuron parameters
        /gjcon      = False ; resets gap junction connections
        /syncon     = False ; resets list of synaptic connections
        /gsyncond   = False ; resets list of synaptic conductances
    }
    
    /annoying_reload/{
        /nprms      = True  ; If True and neuron parameters hash doesn't match it stops
        /gjcon      = False ; If True and gap junction connection list hash doesn't match it stops
        /syncon     = True  ; If True and synaptic connection hash doesn't match it stops
        /gsyncond   = False ; If True and synaptic conductance list hash doesn't match it stops
        /btdp       = False ; If True and /btdp/continue and /record/file does not have gsyn with correct hash - it stops
    }
    ; plasticity parameters 
    /btdp/{
        /enable     = False ; Set it to true for activation btdp
        /update     = 5000.\; update synaptic weights every # milliseconds.
                            ; if btdp is enable it resets /sim/record/interval
        /normgsyn   = None  ; Target level to which  ....
        /normn      = 4     ; strongest normn synapses are normalized, suppressing weaker synapses.
        /synthr     = -0.05\; the threshold  below with synapse assumed to be silent
                           \; same as for /syn/normg : positive sets the absolute level for the threshold,
                           \; negative sets a relative to minimal synaptic conductance for each neuron threshold
                            ; and None sets all synapses active
        /minact     = @/network/btdp/normn@ \; threshold of minimal number of active connections
                           \; if number of active synapses is below this number - it creates new random synapses.
                            ; **Note** if /network/btdp/synthr=None, this mechanism is disabled.
        /frthr      = 0.1  \; if max firing rate at given interval /network/btdp/update for any pre or postsyn
                           \; below this value, correlations term of leaning rule will not computed. 
                           \; **Note** if you set it in None, False, or below zero, correlation term will be compute
                            ; always - and two silent neurons will have very high correlation and ramp up connections.
        /frkernel   = 25.  \; kernel for smoothing firing-rate. Effectively, gaussian kernel low-pass
                           \; frequencies 4 time lower than kernel size.
                           \; Butts et al 1999, computed minimal jitter to perturb spacial information around
                            ; 100 ms, so ~25ms kernel should be OK.
        /frsmwidth  = @/network/btdp/frkernel@*10. ; one-side width of smoothing vector for firing-rate
        /continue   = True  ; reads last update from record and reset weights
    }
    ; firing rate homeostasis
    /home/{
        /enable     = False   ; Set it to true to activate homeostasis
        /update     =120000. \; update synaptic weights every # milliseconds.
                             \; if btdp is enable it will be set to /sim/btdp/update
                              ; if btdp is not enable, /home/update resets /sim/record/interval
        /tau        =60000.   ; homeostasis time constant in ms ~10 sec
        /target_fr  =0.5     \; Target firing rate in spikes/sec
                             \; from Murata & Colonnese 2018 Figure 5G1, it should be ~ 1 spike/sec, but
                              ; with blocked cortex it decreases ~50% Murata & Colonnese 2016 Fig 3.
;        /target_fr  =0.3730071897467958 ; Target firing rate in spikes/sec (mice unpublished data)
        /slope      = 1.      ; sloe slope of activation function is spikes/sec
        /gmax       = -2.     ; maximal synaptic conductance (notation is the same as in /network/syn/gsyn)
        /gmin       = 0.0     ; minimal synaptic conductance
        /delta      = -0.2/111; increment/decrement of synaptic weights
        /continue   = True    ; reads last update from the record and reset weights
    }
    ; cortical feedback
    /cx/{
        /enable     = False ; Set it to true for enabling **cortical feedback**
        /delay      = 15.   ; delay for spike travel to cortex and back
        /gsyn       = -0.005; synaptic conductance. ATTENTION! If negative it set ratio to mean RGC input
        /AMPA/{
            /p      = @/network/syn/AMPA/p@      ; portion of AMPA conductance
            /tau1   = @/network/syn/AMPA/tau1@   ; AMPA rising time constant
            /tau2   = @/network/syn/AMPA/tau2@   ; AMPA falling time constant
        }
        /NMDA/{
            /p      = @/network/syn/NMDA/p@      ; portion of NMDA conductance
            /tau1   = @/network/syn/NMDA/tau1@   ; NMDA rising time constant
            /tau2   = @/network/syn/NMDA/tau2@   ; NMDA falling time constant
        }
        /ppr_u0     = 0.7   ; sets presynaptic PP depression                        
    }
    ; TRN feedback
    /trn/{
        /enable     = False ; Set it to true for enabling **TRN inhibitory feedback**
        /delay      = 15.   ; delay for spike travel to TRN and back
        /gsyn       = -0.005; synaptic conductance (same as /syn/gsyn)
        /tau1       = 5.    ; GABA A rising time constant
        /tau2       = 50.   ; GABA A falling time constant
        /e          = -70.  ; inhibitory reversal potential
    }
}

/block{
    /gjcon          = False ; Block gap junction
    /syncon         = False ; Block synapses
}

/sim/{
    /temperature     = None\; model temperature in celsius,
                            ; if None it will try to find 'temperature' variable in the neuron database
    /Tmax  = 600000.       \; Simulation duration in ms. If negative (any negative number)
                            ; it defined by stimulation recording
    /record/{
        /interval    = 60000; record and clean buffers every /sim/record/interval milliseconds
        /file        = 'dLGN-record.stkdata' \;
                            ; save everything into this file
        /save        = True ; enable any recordings
        /spike       = True ; record spikes
        /gsyn        = False\; if a number records synaptic weights every n updates, 
                           \; if true records synaptic weights every update.
                            ; Works only if btdp or homeostasis are enabled
        /cont/{
            /dt      = 0.5  ; time step for continues recordings
            /cur     = False; record currents
            /volt    = True ; record voltages
            /meancur = True ; record current averaged through population
        }
    }
    /parallel       = True  ; sent number of cores or True for auto detection
    /Belly          = False ; ring the bell when simulation finishes
    /timestamp      = time.strftime("%Y%m%d-%H%M%S") \;
                            ; simulation time-stamp
}


/stim/{
    /iapp            = None ; inject constant current. Current is slowly ramping up first 1000 ms
    /rGC/{
        /file        = "../experimentaldata/Maccione2014_P9_29March11_control_SpkTs_bursts_filtered.h5" \;
                            ; reads positions and spikes of RG from this file
        /groups      = [                     \; recorded rGC IDs which will be used 
            824,825,826,827,828,829,830,831, \; for network stimulation
            849,850,851,852,853,854,855,856, \; if more than one neuron on one electrode
            875,876,877,878,879,880,881,882, \; spike can be lumped together by
                905,906,907,908,909,910      \; putting IDs into tuple (121,122,123)
            ]                                 ; for example
    }
    /trecstart       = 140000; remove first milliseconds of the recording.
    /shuffle         = False ; Shuffles spikes between electrodes
    /uniform         = False ; uniform distribution of the same number of spikes over each electrode
    /stimfile        = None \; used npy file with array (n,2) : [spike time,rGC] 
                             ;  instead of spikes in the original hd5 file
    /poisson         = None  ; Generate poisson firing rate with given rate
    
}

/FR/{
    /window = 100 ; windows size for filtering firing rate
    /kernel = 50. ; Gaussian kernel to smooth FR
    /kernelwidth = @/FR/kernel@*5\; 1/2 width of smoothing kernel
                \; (it is half, because +- boundary). It is set to 5 sigma 
                \; If /kernel and /kernelwidthare gaussian kernel is used to smooth 1ms bin histogram,
                 ; otherwise histogram with /FR/window will be plotted
    /CorrDist/{
        /positive    = 20.   \; Size of positive Gaussian kernel to smooth firing rate 
                              ; for computing  Correlation distribution
        /negative    = @/FR/CorrDist/positive@*4 ; size of negative Gaussian kernel
        /window      = @/FR/CorrDist/negative@*5 ; 1/2 of smoothing window size
        /bins        = False \; set a number of bins in correlation distribution (must be int); 
                              ; default 201
        /left        = False  ; left boundary of histogram range; default -1. 
        /right       = False  ; right boundary of histogram range; default 1.
    }
    /Spectrum/{
        /filter-off  = False  ; set False to remove filtration 
        /Fmax        = 39.    ; Maximal frequency (Hz)
        /dt          = 1.     ; Histogram bin-size in ms
        /kernel      = 20.    ; Gaussian kernel to smooth FR (different to from the above to have high frequency components)
        /width       = @/FR/Spectrum/kernel@*5 ; 5 sigma for 1/2 of the window (n /FR/Spectrum/dt time units)
    }
    /Overall         = True   ; computes overall FR for a run. If string is given, it jsones the list of overall FR into a file with this name.
}

/Figures{
    /enable            = True   \; if False will not generate figures and exit
                                 ; it will make a DB record only if -m message is provided and record won't have figures
    /X-term            = False   ; saves all figures into file with this prefix. If False - shows on screen
    /FigSize           = (21,16) ; XxY size of figures
    /FigLimit          = None    ; If any of /sim/record/cont/{cur,volt} is set True, will show every # neuron, and all if None
    /STKDB-Record      = True    ; Add figures into record
    /connectivity/flat = False   ; if True makes 2D plot of connectivity instead of 3D
    /disable/{
        /connectivity  = False   ; set True to disable connectivity plot
        /volt          = False   ; set True to disable voltage plot
        /cur           = False   ; set True to disable current plot
        /cordist       = False   ; set True to disable correlation distribution plot
        /spectrum      = False   ; set True to disable spectrum plot
        /2dspiking     = True    ; set False to activate interactive figure which can generates movies
    }
    /formats           = 'jpg svg'.split() ; list of figures formats
}

/analysis/{
    /connectivity    = True    ; statistics of RGC to LGN connectivity
    /gj              = True    ; statistics of number GJ per neuron
}
"""


import logging, sys, os, io, shutil, gzip ,csv,glob,json, time
from functools import reduce
import random as pyrandom

try:
    import cPickle as pkl
except:
    import pickle as pkl
#import multiprocessing as mps

from datetime import datetime as date_and_time
from optparse import OptionParser
from numpy import *
from numpy import random as rnd
import scipy         as sp
import scipy.fftpack as spfft
import scipy.io      as spio
from scipy           import signal
from scipy.stats     import gaussian_kde as kerden
from scipy.integrate import quad

from simtoolkit import methods
from simtoolkit import db as stkdb
from simtoolkit import data as stkdata



recdb = sys.argv[0][:]
if recdb.endswith('.py'): recdb = recdb[:-3]
recdb += ".stkdb"

oprs = OptionParser("USAGE: %prog [flags] [variable]",add_help_option=False)
#oprs.add_option("-d", "--stk-database",  dest="db", default=None,  help="Read record from data base (default None). Example -d xxx.stkdb:/connections" )
#oprs.add_option("-c", "--stk-config"  ,  dest="cf", default=None,  help="Read record from configuration (default None). Example -c xxx.stkconf:/connections" )
oprs.add_option("-o", "--stkdb-record",  dest="rd", default=recdb,  \
  help="Record the simulation in data base (default {})".format(recdb) )
oprs.add_option("-m", "--stkdb-message", dest="rm", default=None,   type="str", \
  help="Supply database record with a massage. Useful when run scripts (default None)" )
oprs.add_option("-c", "--stkdb-cmd"    , dest="rc", default=True,   \
  help="Add end command line to data base (doesn't change model hash sum)'", action="store_false")
oprs.add_option("-L", "--log"         ,  dest="lg", default=None,   \
  help="Output log to the file (default on the screen)")
oprs.add_option("-l", "--log-level"   ,  dest="ll", default="INFO", \
  help="Level of logging may be CRITICAL, ERROR, WARNING, INFO, or DEBUG (default INFO)") 
oprs.add_option("-h", "--help"        ,  dest="hp", default=False,  \
  help="Print this help", action="store_true")
options, args = oprs.parse_args()

if options.lg is None:
    logging.basicConfig(format='%(asctime)s:%(lineno)-6d%(levelname)-8s:%(message)s',\
     level=eval("logging."+options.ll) )
else:
    logging.basicConfig(filename=options.lg, \
     format='%(asctime)s:%(name)-33s%(lineno)-6d%(levelname)-8s:%(message)s', \
     level=eval("logging."+options.ll) )
logging.info("----:-------------------------------------------------------------------")
logging.info("CMD : "+" ".join(sys.argv) )
logging.info("----:-------------------------------------------------------------------")

try:
    import h5py
except:
    logging.error("Cannot import h5py")
    exit(1)


mth = methods(stkdefault, 'mth', locals(), argvs = args )
if options.hp:
    from textwrap import TextWrapper
    ncolumns = int(os.environ.get('COLUMNS',120))
    print("\n\n"+mth.mainmessage)
    oprs.set_usage("""USAGE: %prog %prog [options] [parameters]\n
Any model parameter can be altered by /parameter_name=parameter_value in command line""")
    oprs.print_help()
    #print(mth.printhelp()) #prints tree structure which may not be very useful
    print("\nParameters:")
    for p,v,hm in mth.genhelp():
        print("{: <31s} = {}".format(p,v))
        #print("{: <31s} : {}".format('',hm))
        print(TextWrapper(initial_indent=" "*31+" : ", subsequent_indent=" "*31+" : ",width=ncolumns).fill(hm))
        print()
    exit(0)

mth.generate()

if mth.check("/Figures/enable"):
    import matplotlib
    if mth.check("/Figures/X-term"):
        matplotlib.use('Agg')
        logging.info(" > Set Agg backend")
    matplotlib.rcParams["savefig.directory"] = ""
    from matplotlib.pyplot import *
    import matplotlib.mlab as mlab
    import matplotlib.image as img


logging.info( "======================================")
logging.info( "===     GENERATED PARAMETERS       ===")
for p,k,s in mth.methods.printnames():
    if k is None:
        logging.info(p)
    else :
        logging.info(p+"{}".format(mth.methods[k])  )

now       = date_and_time.now()
hashline  = mth.gethash("/")
timestamp = "%d-%d-%d %d:%d:%d.%d"%(now.year, now.month, now.day, now.hour, now.minute, now.second, rnd.randint(0,999))
logging.info( "======================================")
logging.info( "===           BUILDING             ===")
logging.info(f" > DataBase     : {options.rd}" )
logging.info(f" > HASH         : {hashline}"  )
logging.info(f" > TIME STAMP   : {timestamp}" )
logging.info( " > MODEL PREFIX : {}".format(mth["/sim/timestamp"] ) )
logging.info(f" > MESSAGE      : {options.rm}" )




if mth.check("/sim/state/load"):
    if not mth.check("/sim/state/id"):
        mth["/sim/state/id"] = -1
    with stkdata(mth["/sim/state/load"]) as sd:
        posxy = sd["posxy",mth["/sim/state/id"]]
    logging.info(" > posxy is loaded from {}:{}".format(mth["/sim/state/load"],mth["/sim/state/id"]))
elif   mth["/network/geom/shape"] == "H" or mth["/network/geom/shape"] == "h":
    logging.info(" > Geometry     : Hexagonal")
    logging.info(" > Nx x Ny      : {} x {}".format(mth["/network/geom/x"],mth["/network/geom/y"]) )
    posxy = array([ (float(i)+(0.5 if j%2 == 0 else 0),float(j)*sqrt(3)/2) for i in range(mth["/network/geom/x"]) for j in range(mth["/network/geom/y"]) ])
elif mth["/network/geom/shape"] == "S" or mth["/network/geom/shape"] == "s":
    logging.info(" > Geometry     : Square")
    logging.info(" > Nx x Ny      : {} x {}".format(mth["/network/geom/x"],mth["/network/geom/y"]) )
    posxy = array([ (float(i),float(j)) for i in range(mth["/network/geom/x"]) for j in range(mth["/network/geom/y"]) ])
    
posxm = amin(posxy[:,0]),amax(posxy[:,0])
posmy = amin(posxy[:,1]),amax(posxy[:,1])

from neuron import h
#>>>
# from cell import dLGN
import importlib



if mth.check("/network/nprms/db"):
    #from selectedP07N04v05 import selected, selected_min_g, selected_min_nmda
    with open(mth["/network/nprms/db"]) as fd:
        j = json.load(fd)
    modulename   = mth["/network/nprms/modulename"] if mth.check("/network/nprms/modulename") else "module"
    if not modulename in j:
        logging.error(f"Cannot find {modulename} record in neurondb: don't know which module should be imported")
        raise RuntimeError(f"Cannot find {modulename} record in neurondb: don't know which module should be imported")
    modulename = j[modulename]
    if type(modulename) is not str:
        logging.error(f"Module name in neurondb isn't a string but {type(modulename)}")
        raise RuntimeError(f"Module name in neurondb isn't a string but {type(modulename)}")
    cellname   = mth["/network/nprms/cellname"] if mth.check("/network/nprms/cellname") else "cell"
    if not cellname in j:
        logging.error(f"Cannot find {cellname} record in neurondb: don't know which object import from the module")
        raise RuntimeError(f"Cannot find {cellname} record in neurondb: don't know which object import from the module")
    cellname = j[cellname]
    if type(cellname) is not str:
        logging.error(f"Cell name in neurondb isn't a string but {type(cellname)}")
        raise RuntimeError(f"Cell name in neurondb isn't a string but {type(cellname)}")
    try:
        mod  = importlib.import_module(modulename)
        dLGN = eval("mod."+cellname)
    except BaseException as e:
        logging.error(f"Cannot import neuron model {cellname} from module {modulename}: {e}")
        raise RuntimeError(f"Cannot import neuron model {cellname} from module {modulename}: {e}")
    logging.info(f" > Neuron {cellname} is imported from module {modulename} succesfully")
    setcable = j["setcable"] if "setcable" in j else None
    ntemeraturedb = j["temperature"] if "temperature" in j else None    
        

    neurons = [ dLGN(nid=i) for i,xy in enumerate(posxy) ]
    logging.info(f" > Population   : {len(neurons)} neurons has been creared")
    
    modellstname = mth["/network/nprms/lst"]        if mth.check("/network/nprms/lst") else "models"
    if not modellstname in j:
        logging.error(f"Cannot find {modellstname} neurondb")
        raise RuntimeError(f"Cannot find {modellstname} neurondb")
    minsyname     =  mth["/network/nprms/gmin"] if mth.check("/network/nprms/gmin") else "gsynmin"
    if not minsyname in j:
        logging.error(f"Cannot find synaptic conductance index ({minsyname}) in the _root_ of model DB")
        raise RuntimeError(f"Cannot find synaptic conductance index ({minsyname}) in the _root_ of model DB")
    if not any([ minsyname in m for m in j[modellstname] if m is not None ]):
        logging.error(f"Cannot find minimal synaptic conductance ({minsyname}) for one or more neurons in the model DB")
        raise RuntimeError(f"Cannot find minimal synaptic conductance ({minsyname}) for one or more neurons in the model DB")
    # selected_min_g = [ x[minsyname] for x in j[modellstname] if x is not None]
    gsynmin_idx   = array(j[minsyname])
    selected      = [
        [ x["parameters"],
         (x["init"] if 'init' in x else None),
          array(x[minsyname]),
         (x["id"]   if 'id' in x else i),
        ] for i,x in enumerate(j[modellstname]) if x is not None ]
    logging.info(" > Have read neuron DB and minimal conductance index from {}".format(mth["/network/nprms/db"]))
else:
    logging.error("Cannot find /network/nprms/db parameter")
    raise RuntimeError("Cannot find /network/nprms/db parameter")

if mth.check("/sim/temperature"):
    h.celsius = mth["/sim/temperature"]
else:
    if ntemeraturedb is None:
        logging.error("Temperature is not set by parameter /sim/temperature or by temperature variable in the neuron database")
        raise RuntimeError("Temperature is not set by parameter /sim/temperature or by temperature variable in the neuron database")
    h.celsius = ntemeraturedb
    logging.info(f" > Read temperature  from the database")
    
    
logging.info(f" > Set temperature =  {h.celsius} C")
    

# Lists of networks elements: neuron parameters, gap junctions, synaptic connections, and synaptic weights 
nprms     = None
gjcon     = None
syncon    = None
gsyncond  = None
# Model hash for each list. So we can safely read from the file if hashes are the same
nprms_hash     = mth.gethash("/network/geom")+":"+mth.gethash("/network/nprms")
gjcon_hash     = mth.gethash("/network/geom")+":"+mth.gethash("/network/gj/geom")
syncon_hash    = mth.gethash("/network/geom")+":"+mth.gethash("/stim/rGC")+":"+mth.gethash("/network/syn/geom")
gsyncond_hash  = mth.gethash("/network/geom")+":"+mth.gethash("/stim/rGC")+":"+mth.gethash("/network/syn")

if mth.check("/network/load"):
    def loadcomponent(idt,varname,varhash,xfile):
        if   f'/{varname}' in idt and f"/nethash/{varname}" in idt: 
            if   not mth.check(f"/network/reload/{varname}")         : mth[f"/network/reload/{varname}"] = -1
            elif not  type(mth[f"/network/reload/{varname}"]) is int : mth[f"/network/reload/{varname}"] = -1
            if idt[f"/nethash/{varname}",mth[f"/network/reload/{varname}"]] == varhash :
                return idt[f'/{varname}',mth[f"/network/reload/{varname}"]]
            if not mth.check[f"/network/annoying_reload/{varname}"]:
                return idt[f'/{varname}',mth[f"/network/reload/{varname}"]]
            else:
                logging.error("Cannot find matched hash sum for network configuration in the recording {}[{}] of {} file:\n\t\t{}\n\t\t{}".format(
                    varname,mth[f"/network/reload/{varname}"],xfile,idt[f"/nethash/{varname}",mth[f"/network/reload/{varname}"]], varhash))
                if mth.check(f"/network/annoying_reload/{varname}") : exit(1)
        else:
            logging.error(f"Cannot find /{varname} or /nethash/{varname}  form the file {xfile}")
            if mth.check(f"/network/annoying_reload/{varname}") : exit(1)
        return None
        
    if type(mth["/network/load"]) is str: xfile =  mth["/network/load"] 
    elif mth.check("/network/file")     : xfile =  mth["/network/file"]
    else :
        logging.error("/network/load is not a string and /network/file is not set properly")
        exit(1)
    if not os.access( xfile, os.R_OK):
        logging.error("Cannot read network file {}".format(xfile) )
        exit(1)
    with stkdata(xfile) as idt:
        logging.info(" > reading file {}".format(xfile))
        
        if not mth.check("/network/reset/nrn"):
            nprms = loadcomponent(idt,'nprms',nprms_hash,xfile)
            if nprms is not None:
                logging.info(" > have read neuron parameters parameters from the file")
            else:
                logging.warning(f" > cannot read neuron parameters parameters from the file {xfile}")
        
        if not mth.check("/network/reset/gjcon") and not mth.check("/block/gjcon"):
            gjcon =  loadcomponent(idt,'gjcon',gjcon_hash,xfile)
            if gjcon is not None:
                logging.info(" > have read gap junction list  from the file")
            else:
                logging.warning(f" > cannot read gap junction list  from the file {xfile}")
        
        if not mth.check("/network/reset/syncon") and not mth.check("/block/syncon"):
            if   '/syncon' in idt and "/nethash/syncon" in idt:
                syncon = loadcomponent(idt,'syncon',syncon_hash, xfile)
                if syncon is not None:
                    logging.info(" > have read list of synaptic connection  from the file")
                else:
                    logging.warning(f" > cannot read list of synaptic connection  from the file {xfile}")
                
        if not mth.check("/network/reload/gsyncond") and not mth.check("/block/syncon"):
            gsyncond = loadcomponent(idt,'gsyncond',gsyncond_hash,xfile)
            if gsyncond is not None:
                logging.info(" > have read list of synaptic conductance  from the file")  
            else:
                logging.warning(f" > cannot read list of synaptic conductance  from the file {xfile}")

if mth.check("/sim/state/load"):
    with stkdata(mth["/sim/state/load"]) as sd:
        nprms     = sd["nprms"   ,mth["/sim/state/id"]]
        gjcon     = sd["gjcon"   ,mth["/sim/state/id"]]
        syncon    = sd["syncon"  ,mth["/sim/state/id"]]
        gsyncond  = sd["gsyncond",mth["/sim/state/id"]]
    logging.info(" > nprms, gjcon, syncon, gsyncond are loaded from {}:{}".format(mth["/sim/state/load"],mth["/sim/state/id"]))

if nprms is None:
    if len(selected) < len(neurons):
        logging.error(f" > Number of neurons in database smaller than number of neurons in the network")
        if mth.check("/network/annoying_hetero"): exit(1)
        logging.warning(f"=== THERE WILL BE THE SAME NEURONS IN THE NETWORK ===")
    elif not mth.check("/network/annoying_hetero"):
        logging.warning(f"=== ATTANTION! /network/annoying_hetero is OFF!  ===")
        logging.warning(f"=== THERE MAY BE THE SAME NEURONS IN THE NETWORK ===")
    nidlst = [ nid for nid in range(len(selected)) ]
    #xnprms = array([ int(rnd.choice(nidlst)) for n in neurons ])
    xnprms = []
    while len(xnprms) < len(neurons):
        x = int(rnd.choice(nidlst))
        if x in xnprms and mth.check("/network/annoying_hetero"): continue
        xnprms.append(x)
    xnprms = array(xnprms)
    logging.info(f" > set neurons parameter index : {xnprms.tolist()}" )
    logging.info(f" > set neurons parameter DBIDs : {[ selected[n][-1] for n in xnprms]}")
else:
    xnprms = nprms


for nid,prmsid in enumerate( xnprms ):
    prms  = selected[prmsid][0]
    for pname in prms:
        pvalue = prms[pname]
        exec( f"neurons[nid].{pname} = pvalue" )
    neurons[nid].type    = prmsid
    logging.debug(f"== Neuron #{nid} ===")
    logging.debug(f" > prmsid={prmsid}" )
    logging.debug(f" > n.type={neurons[nid].type}" )
    logging.debug(f" > prms  ={prms}" )
    init  = selected[prmsid][1]
    # n.axon.nseg = 2
    for vname in init:
        value = init[vname]        
        if value is not None:
            exec( f"neurons[nid].{vname} = value" )
        else:
            exec( f"neurons[nid].{vname} = -62.0" )
    if setcable is not None:
        exec("neurons[nid]."+setcable)
        logging.debug(f" > {setcable} is called" )
    if mth.check( "/sim/record/spike" ):
        neurons[nid].spks = h.Vector()
        neurons[nid].thr  = h.APCount(0.5,sec=neurons[nid].soma)
        neurons[nid].thr.thresh = mth["/network/nprms/threshold"] \
            if mth.check("/network/nprms/threshold") else -20.
        neurons[nid].thr.record(neurons[nid].spks)
    if mth.check("/sim/record/cont/volt"):
        neurons[nid].volt = h.Vector()
        neurons[nid].volt.record(neurons[nid].soma(0.5)._ref_v)
    
        
#DB>>
# for nid,(prmsid,n) in enumerate(zip(xnprms,neurons)):
    # print(f"NRN #{nid} : {prmsid}")
    # print(" > ","type",n.type,prmsid)
    # prms  = selected[prmsid][0]
    # for pname in prms:
        # print(" > ", pname,eval("n."+pname),prms[pname])
    # init  = selected[prmsid][1]
    # print(f" init > {init}")
    # print(f" soma > {[ x.v for x in n.soma ]}")
    # print(f" axon > {[ x.v for x in n.axon ]}")
    
# exit(0)
#<<DB
logging.info(" > neurons parameters have been set" )
   
### === rGC === ###
for rgcp in "/stim/rGC/file","/stim/rGC/groups":
    if not mth.check(rgcp):
        logging.error("Cannot find {} parameter!".format(rgcp))
        exit(1)
    
if not os.access(mth["/stim/rGC/file"], os.R_OK):
     mth["/stim/rGC/file"] = os.path.basename(mth["/stim/rGC/file"])

with h5py.File(mth["/stim/rGC/file"],"r") as fd:
    epos = array(fd["epos"]).T
    sCount = array(fd["sCount"])
    spikes = array(fd["spikes"])

logging.info(" > Have read h5 file {}".format(mth["/stim/rGC/file"]) )
cellid = zeros(spikes.shape).astype(int)
previd = 0
for nidx,idx in enumerate(sCount):
    cellid[previd:previd+idx] = nidx
    previd += idx
sCount = sCount.shape[0]                              # number of neurons
rlength = amax(spikes) * 1e3
spikes = spikes * 1e3                                 # convert to ms
logging.info("  > total number of rGCs : {:d}".format(sCount) )
logging.info("  > rec.length           : {:g} (ms)".format(rlength) )

usespikes = []
if mth.check("/stim/stimfile"):
    spktr    = load(mth["/stim/stimfile"])
    spktr    = spktr["spk"]
    rgcidmin = int( floor( amin(spktr[:,1]) ) )
    for rgdi in range( len(mth["/stim/rGC/groups"]) ):
        chsp = spktr[where( abs(spktr[:,1]- rgcidmin - rgdi) < 0.1 )]
        if chsp.shape[0] < 1:
            usespikes.append( empty((0,2)) )
        else:
            usespikes.append( array([ [grpid,spkt] for spkt,grpid in chsp]) )
    logging.info("Red spikes from {}".format(mth["/stim/rGC/stimfile"]) )
elif mth.check("/stim/poisson"):
    if not mth.check("/sim/Tmax"):
        logging.error("Need /sim/Tmax to generate poisson process")
    luse = len(mth["/stim/rGC/groups"])
    for x in range(luse):
        negexp,expidx,xfr = rnd.exponential(scale=1000./mth["/stim/poisson"],size=1000),1,[]
        xfr.append([x,negexp[0]])
        while xfr[-1][1] < mth["/sim/Tmax"] :
            xfr.append([x,xfr[-1][1]+negexp[expidx] ])
            expidx += 1
            if expidx >= 1000:
                negexp,expidx = rnd.exponential(scale=1000./mth["/stim/poisson"],size=1000),0        
        usespikes.append( array(xfr) )
    logging.info(" > Set input spikes as poisson process with rate  {}".format(mth["/stim/rGC/poisson"]) )
else:
    for grpid,grp in enumerate(mth["/stim/rGC/groups"]):
        spk = array([])
        if type(grp) is tuple or type(grp) is list:
            for i in grp:
                if not type(i) is int:
                    logging.error("CellID {} in {} isn't integer....".format(i,grp))
                    exit(1)
                spk = append(spk,spikes[where(cellid == i)])
        elif type(grp) is int:
            spk = spikes[where(cellid == grp)]
        else:
            logging.error("wrong type of group {}....".format(grp) )
            exit(1)
        spk = spk[where(spk>mth["/stim/trecstart"])] - mth["/stim/trecstart"]
        usespikes.append(column_stack( (float(grpid)*ones(spk.shape[0]),spk ) ))
    logging.info(" > Set spikes from h5 file")
    logging.info(f" > Total number of rGC sources are {len(usespikes)}")

if not mth.check("/sim/Tmax"):mth["/sim/Tmax"] = -1.
if mth["/sim/Tmax"] < 0: 
    for us in usespikes:
        if mth["/sim/Tmax"] < amax(us[:,1]) :mth["/sim/Tmax"] = amax(us[:,1])
    logging.info(" > Set Tmax   : {}".format(mth["/sim/Tmax"]) )

if mth.check("/stim/iapp"):
    tCC, iCC= h.Vector(), []
    tCC.from_python([0,1000.,mth["/sim/Tmax"]+1])
    for n in neurons:
        ivec = h.Vector()
        ivec.from_python([0.,mth["/stim/iapp"],mth["/stim/iapp"]])
        icl  = h.IClamp(0.5, sec=n.soma)
        icl.amp   = 0
        icl.dur   = mth["/sim/Tmax"]+1e9
        icl.delay = 0.
        ivec.play(icl._ref_amp,tCC,1)
        iCC.append( (ivec,icl) )
    logging.info(" > Set Iapp : {}".format(mth["/stim/iapp"]))


epos   = epos[[i[0] if type(i) is tuple or type(i) is list else i for i in mth["/stim/rGC/groups"]],:]
xmxm   = amin(epos[:,0]),amax(epos[:,0])
ymym   = amin(epos[:,1]),amax(epos[:,1])
# size of unique position in x is number of Y column and vice versa 
n2n    = unique(epos[:,1]).shape[0], unique(epos[:,0]).shape[0]
xscale = (posxm[1]-posxm[0])*float(n2n[0])/(xmxm[1]-xmxm[0])/(n2n[0]+1)
yscale = (posmy[1]-posmy[0])*float(n2n[1])/(ymym[1]-ymym[0])/(n2n[1]+1)
epos[:,0] = (epos[:,0]-xmxm[0])*xscale+(posxm[1]-posxm[0])/(n2n[0]+1)/2
epos[:,1] = (epos[:,1]-ymym[0])*yscale+(posmy[1]-posmy[0])/(n2n[1]+1)/2
rad    = max((posxm[1]-posxm[0])/n2n[0],(posmy[1]-posmy[0])/n2n[1])

logging.info(f" > Minimum radius (each dLGN cell has at leas one synapses from rGC) = {rad}")

#DB>>
#savez("Positions.npz",
   #posxy = posxy,
   #epos  = epos,
   #rad   = rad
#)
#exit(0)
#<<DB

mmfr = [
    array([ us[where((us[:,1]>=float(i*mth["/FR/window"]))*(us[:,1]<float(i*mth["/FR/window"]+mth["/FR/window"])))].shape[0]/mth["/FR/window"]  for i in range( int(floor(us[-1,1]/mth["/FR/window"])) )])
    for us in usespikes
]
mmfr = array([
    [amin(fr), mean(fr), amax(fr)] for fr in mmfr
])
for i,us in enumerate(usespikes):
    logging.debug(" > Electrode  :{:d}".format(i))
    logging.debug("   >  mean FR : {}".format(mmfr[i,1] ) )
    logging.debug("   >  min  FR : {}".format(mmfr[i,0] ) )
    logging.debug("   >  max  FR : {}".format(mmfr[i,2] ) )

usespikes = [
    us[where(us[:,1]<mth["/sim/Tmax"])] for us in usespikes
]

if mth.check("/stim/uniform"):
    for us in usespikes:
        us[:,1] = rnd.rand(us.shape[0])* mth["/sim/Tmax"]
        us.sort(axis=0)
    logging.info(" > Set UNIFORM spiking for rGC")
if mth.check("/stim/shuffle"):
    luse = len(usespikes)
    for x in range(luse*1000):
        i1,i2 = rnd.randint(luse),rnd.randint(luse)
        while i1 == i2:
            i1,i2 = rnd.randint(luse),rnd.randint(luse)
        s1,s2 = usespikes[i1],usespikes[i2]
        nshuf = min(s1.shape[0],s2.shape[0])//10
        for s in range(nshuf):
            i1,i2 = rnd.randint(s1.shape[0]),rnd.randint(s2.shape[0])
            s2[i2,1],s1[i1,1] = s1[i1,1],s2[i2,1]
    for us in usespikes:
        us.sort(axis=0)
    logging.info(" > Shuffled all rGC spikes")



#spike sources
rGCs = [ [h.VecStim(),h.Vector()] for us in usespikes ]
for (rgc,vec),spk in zip(rGCs,usespikes):
    if spk.shape[0] != 0:
        vec.from_python(spk[:,1])
    else:
        vec.from_python([mth["/sim/Tmax"]])
    rgc.play(vec)
logging.info(" > Set vplays" )

gj  = []
if not mth.check("/block/gjcon"):
    if gjcon is None:
        xgjcon = []
        for i,n1 in enumerate(neurons):
            for j,n2 in enumerate(neurons[i+1:]):
                d = sqrt(sum((posxy[i,:]-posxy[j+i+1,:])**2) )
                p = arctan2( posxy[j+i+1,1]-posxy[i,1], posxy[j+i+1,0]-posxy[i,0] )
                if mth.check("/network/gj/geom/maxd") and d > mth["/network/gj/geom/maxd"] : continue
                if mth.check("/network/gj/geom/mind") and d < mth["/network/gj/geom/mind"] : continue
                if mth.check("/network/gj/geom/dir" ) and\
                    min(abs(mth["/network/gj/geom/dir"] - p),abs(mth["/network/gj/geom/dir"]+2*pi - p)) > .25: continue
                xgjcon.append( [i,j+i+1] )
                
                
        if not mth.check("/network/gj/geom/unit"): mth["/network/gj/geom/unit"] = 'n'
        if mth.check("/network/gj/geom/maxcon") and type(mth["/network/gj/geom/maxcon"]) is not int:
            logging.error(" === /network/gj/geom/maxcon is set but it is not an integer! ===" )
            exit(1)
        if   mth["/network/gj/geom/unit"] == 'n':
            if mth.check("/network/gj/geom/maxcon"):
                vlst = []
                nlst = [ 0 for n in neurons ]
                ncnt = 0
                while len(vlst)*2/len(neurons) < mth["/network/gj/geom/p"]:
                    ncnt += 1
                    if ncnt > len(nlst)*10000:
                        logging.warning(f"Cannot achieve gj connectivity after {ncnt} iterations: will go with {len(vlst)*2/len(neurons)} insead of "+"{}".format(mth["/network/gj/geom/p"]))
                        break
                    x = xgjcon[rnd.randint(len(xgjcon))]
                    if nlst[x[0]] >= mth["/network/gj/geom/maxcon"] or nlst[x[1]] >= mth["/network/gj/geom/maxcon"]: continue
                    vlst.append(x)
                    nlst[x[0]] += 1
                    nlst[x[1]] += 1
            else:
                vlst = []
                nlst = []
                ncnt = 0
                while len(vlst)*2/len(neurons) < mth["/network/gj/geom/p"]:
                    ncnt += 1
                    if ncnt > len(neurons)*10000:
                        logging.warning(f"Cannot achieve gj connectivity after {ncnt} iterations: will go with {len(vlst)*2/len(neurons)} insead of "+"{}".format(mth["/network/gj/geom/p"]))
                        break
                    x = xgjcon[rnd.randint(len(xgjcon))]
                    if x[0] in nlst or x[1] in nlst: continue
                    vlst.append(x)
                    nlst += x
            xgjcon = vlst
            
        elif mth["/network/gj/geom/unit"] == 'o' or mth["/network/gj/geom/unit"] == 'o2':
            numgjcon = int( round( mth["/network/gj/geom/p"]*len(neurons) ) ) if mth["/network/gj/geom/unit"] == 'o2' else int( round( mth["/network/gj/geom/p"]*len(neurons)/2 ) )
            if mth.check("/network/gj/geom/maxcon"):
                vlst = []
                nlst = [ 0 for n in neurons ]
                pyrandom.shuffle(xgjcon)
                pyrandom.shuffle(xgjcon)
                for xcon in xgjcon:
                    if nlst[xcon[0]] >= mth["/network/gj/geom/maxcon"] or nlst[xcon[1]] >= mth["/network/gj/geom/maxcon"]: continue
                    vlst.append(xcon)
                    nlst[xcon[0]] += 1
                    nlst[xcon[1]] += 1
                    if len(vlst) >= numgjcon: break
                xgjcon = vlst
            else:
                xgjcon = pyrandom.sample(xgjcon, numgjcon)
        elif mth["/network/gj/geom/unit"] == 'c':
            numgjcon = int( round( mth["/network/gj/geom/p"]*len(xgjcon)  ) )
            if mth.check("/network/gj/geom/maxcon"):
                vlst = []
                nlst = [ 0 for n in neurons ]
                pyrandom.shuffle(xgjcon)
                pyrandom.shuffle(xgjcon)
                for xcon in xgjcon:
                    if nlst[xcon[0]] >= mth["/network/gj/geom/maxcon"] or nlst[xcon[1]] >= mth["/network/gj/geom/maxcon"]: continue
                    vlst.append(xcon)
                    nlst[xcon[0]] += 1
                    nlst[xcon[1]] += 1
                    if len(vlst) >= numgjcon: break
                xgjcon = vlst
            else:
                xgjcon = pyrandom.sample(xgjcon, numgjcon)
        else:
            logging.error("Invalid unit for GJ statistics. should be n, o, o2, or c")
            exit(1)
                    
        xgjcon = array(xgjcon)
        logging.info(" > Generated new GJ list" )
    else:
        xgjcon = gjcon
        logging.debug("Using GJ list:{}".format(xgjcon.tolist() ) )
    if mth.check("/analysis/gj"):
        xgjc = zeros( len(neurons) )
        for n1,n2 in xgjcon:
            xgjc[n1] += 1
            xgjc[n2] += 1
        mth["/stats/GJ/mean"] = mean(xgjc)
        mth["/stats/GJ/std" ] =  std(xgjc)
        mth["/stats/GJ/min" ] = amin(xgjc)
        mth["/stats/GJ/max" ] = amax(xgjc)
        logging.info(" > GJ statistics gj/n")
        logging.info("     mean = {}".format(mth["/stats/GJ/mean"]) )
        logging.info("     std  = {}".format(mth["/stats/GJ/std" ]) )
        logging.info("     min  = {}".format(mth["/stats/GJ/min" ]) )
        logging.info("     max  = {}".format(mth["/stats/GJ/max" ]) )
        del xgjc
        
    for i,j in xgjcon:
        n1,n2 = neurons[i], neurons[j]
        gj0,gj1 = h.gap(0.5, sec=n1.soma), h.gap(0.5, sec=n2.soma)
        h.setpointer(n2.soma(.5)._ref_v, 'vgap', gj0)
        h.setpointer(n1.soma(.5)._ref_v, 'vgap', gj1)
        gj0.r, gj1.r = mth["/network/gj/r"],mth["/network/gj/r"]
        if mth.check("/sim/record/cont/cur") or mth.check("/sim/record/cont/meancur"):
            reci01 = h.Vector()
            reci01.record(gj0._ref_i)
            gj.append( (gj0,gj1,i,j,reci01) )
        else:
            gj.append( (gj0,gj1,i,j) )
    logging.info(" > connected GJ")
else:
    mth["/stats/GJ/mean"] = 0.
    mth["/stats/GJ/std" ] = 0.
    mth["/stats/GJ/min" ] = 0.
    mth["/stats/GJ/max" ] = 0.


con = []
def getWeights():
    return array([ c.weight[0] for c in con ])

def setWeights(wsyn):#pass
    for c,w in zip(con,wsyn):
        c.weight[0] = w

def getCXweights():
    return array([ c.weight[0] for c in cxfeedback ]),\
           array([ [f,t] for t in range(posxy.shape[0]) for f in range(posxy.shape[0]) ])

def setCXweights(wsyn):#pass
    for c,w in zip(cxfeedback,wsyn):
        c.weight[0] = w
        
        
if not mth.check("/block/syncon"):
    if syncon is None:
        xsyncon = []
        gsyncond= None # reset conductance too!
        ##### For Compatibility with old version ##########################
        
        if not  mth.check("/network/syn/geom/unit"):
            if   mth.check("/network/syn/geom/o2o"): mth['/network/syn/geom/unit'] = 'o'
            elif mth.check("/network/syn/geom/a2a"): mth['/network/syn/geom/unit'] = 'a'
            elif mth.check("/network/syn/geom/pmax") and mth.check("/network/syn/geom/sig"):
                mth['/network/syn/geom/unit'] = 'e'
            elif mth.check("/network/syn/geom/pmax") and mth.check("/network/syn/geom/sig2"):
                mth['/network/syn/geom/unit'] = 'g'
                mth['/network/syn/geom/sig' ] = mth['/network/syn/geom/sig2']
            elif mth.check("/network/syn/geom/pmax"): mth['/network/syn/geom/unit'] = 'r'
            else:
                logging.error("Synaptic geometry isn't defined and /network/syn/geom/unit is not set")
                raise BaseException("Synaptic geometry isn't defined and /network/syn/geom/unit is not set")
        if mth['/network/syn/geom/unit'] == 'o':
            logging.info(" > Generating one-to-one connections")
            for cid,(cnx,cny) in enumerate(posxy):
                d = sqrt((epos[:,0]-cnx)**2+(epos[:,1]-cny)**2)
                xsyncon.append([argmin(d),cid])
        elif mth['/network/syn/geom/unit'] == 'a':
            logging.info(" > Generating all-to-all connections")
            for gid,(gcx,gcy) in enumerate(epos):
                xsyncon += [ [gid,cid] for cid in range(len(posxy)) ]
        elif mth['/network/syn/geom/unit'] == 'e':
            if  not mth.check("/network/syn/geom/pmax"):
                logging.error("Cannot find maximum probability /network/syn/geom/pmax for exponential distribution")
                raise BaseException("Cannot find /network/syn/geom/pmax for exponential distribution")
            if  not mth.check("/network/syn/geom/sig"):
                logging.error("Cannot find sigma /network/syn/geom/sig for exponential distribution")
                raise BaseException("Cannot find /network/syn/geom/sig for exponential distribution")
            logging.info(" > Generating connections with exponential distribution: p={} sigma={}".format(mth["/network/syn/geom/pmax"],mth["/network/syn/geom/sig"]) )
            for gid,(gcx,gcy) in enumerate(epos):
                for cid,(cnx,cny) in enumerate(posxy):
                    d = sqrt((gcx-cnx)**2+(gcy-cny)**2)
                    if rnd.rand() < mth["/network/syn/geom/pmax"]*exp(-d/mth["/network/syn/geom/sig"]):
                        xsyncon.append([gid,cid])
        elif mth['/network/syn/geom/unit'] == 'E':
            if  not mth.check("/network/syn/geom/pmax"):
                logging.error("Cannot find maximum probability /network/syn/geom/pmax for exponential distribution")
                raise BaseException("Cannot find /network/syn/geom/pmax for exponential distribution")
            if  not mth.check("/network/syn/geom/sig"):
                logging.error("Cannot find sigma /network/syn/geom/sig for exponential distribution")
                raise BaseException("Cannot find /network/syn/geom/sig for exponential distribution")
            logging.info(" > Generating connections with exponential distribution aligned to the closets rGC: p={} sigma={}".format(mth["/network/syn/geom/pmax"],mth["/network/syn/geom/sig"]) )
            for gid,(gcx,gcy) in enumerate(epos):
                for cid,(cnx,cny) in enumerate(posxy):
                    d = sqrt((epos[:,0]-cnx)**2+(epos[:,1]-cny)**2)
                    xcnx,xcny = epos[argmin(d),:]
                    d = sqrt((gcx-xcnx)**2+(gcy-xcny)**2)
                    if rnd.rand() < mth["/network/syn/geom/pmax"]*exp(-d/mth["/network/syn/geom/sig"]):
                        xsyncon.append([gid,cid])
        elif mth['/network/syn/geom/unit'] == 'g':
            if  not mth.check("/network/syn/geom/pmax"):
                logging.error("Cannot find maximum probability /network/syn/geom/pmax for Gaussian distribution")
                raise BaseException("Cannot find /network/syn/geom/pmax for Gaussian distribution")
            if  not mth.check("/network/syn/geom/sig"):
                logging.error("Cannot find sigma /network/syn/geom/sig for Gaussian distribution")
                raise BaseException("Cannot find /network/syn/geom/sig for Gaussian distribution")
            logging.info(" > Generating connections with Gaussian distribution: p={} sigma={}".format(mth["/network/syn/geom/pmax"],mth["/network/syn/geom/sig"]) )
            for gid,(gcx,gcy) in enumerate(epos):
                for cid,(cnx,cny) in enumerate(posxy):
                    d = (gcx-cnx)**2+(gcy-cny)**2
                    if rnd.rand() < mth["/network/syn/geom/pmax"]*exp(-d/mth["/network/syn/geom/sig"]**2):
                        xsyncon.append([gid,cid])
        elif mth['/network/syn/geom/unit'] == 'G':
            if  not mth.check("/network/syn/geom/pmax"):
                logging.error("Cannot find maximum probability /network/syn/geom/pmax for Gaussian distribution")
                raise BaseException("Cannot find /network/syn/geom/pmax for Gaussian distribution")
            if  not mth.check("/network/syn/geom/sig"):
                logging.error("Cannot find sigma /network/syn/geom/sig for Gaussian distribution")
                raise BaseException("Cannot find /network/syn/geom/sig for Gaussian distribution")
            logging.info(" > Generating connections with Gaussian distribution aligned to the closets rGC: p={} sigma={}".format(mth["/network/syn/geom/pmax"],mth["/network/syn/geom/sig"]) )
            for gid,(gcx,gcy) in enumerate(epos):
                for cid,(cnx,cny) in enumerate(posxy):
                    d = sqrt((epos[:,0]-cnx)**2+(epos[:,1]-cny)**2)
                    xcnx,xcny = epos[argmin(d),:]
                    d = (gcx-xcnx)**2+(gcy-xcny)**2
                    p = mth["/network/syn/geom/pmax"]*exp(-d/mth["/network/syn/geom/sig"]**2)
                    a = rnd.rand() < mth["/network/syn/geom/pmax"]*exp(-d/mth["/network/syn/geom/sig"]**2)
                    if a:
                        xsyncon.append([gid,cid])
                        # #DB>>
                        # print(gid,'->',cid,':',cnx,cny,"=>",xcnx,xcny,':',gcx,gcy,"=",d,p,a)
                        # #<<DB
        elif mth['/network/syn/geom/unit'] == 'r':
            if  not mth.check("/network/syn/geom/pmax"):
                logging.error("Cannot find maximum probability /network/syn/geom/pmax for random distribution")
                raise BaseException("Cannot find /network/syn/geom/pmax for random distribution")
            logging.info(" > Generating connections with random distribution: p={}".format(mth["/network/syn/geom/pmax"]) )
            for cid,(cnx,cny) in enumerate(posxy):
                if rnd.rand() < mth["/network/syn/geom/pmax"]:
                    xsyncon.append([gid,cid])
        elif mth['/network/syn/geom/unit'] == 'c':
            logging.info(" > Generating connections with closest rGCs" )
            for cid,(cnx,cny) in enumerate(posxy):
                d = sqrt((gcx-cnx)**2+(gcy-cny)**2)
                if d < rad: xsyncon.append([gid,cid])
        elif mth['/network/syn/geom/unit'] == 'n':
            if  not mth.check("/network/syn/geom/nmin"):
                logging.error("Cannot find maximum probability /network/syn/geom/nmin for discreet distribution")
                raise BaseException("Cannot find /network/syn/geom/nmin for discreet distribution")
            if  not mth.check("/network/syn/geom/nmax"):
                logging.error("Cannot find sigma /network/syn/geom/nmax for discreet distribution")
                raise BaseException("Cannot find /network/syn/geom/nmax for discreet distribution")
            logging.info(" > Generating random connections when echa TC has from {} to {} synapses".format(mth["/network/syn/geom/nmin"],mth["/network/syn/geom/nmax"]) )
            for cid,(cnx,cny) in enumerate(posxy):
                ncon = rnd.randint(mth['/network/syn/geom/nmin'],mth['/network/syn/geom/nmax']+1)
                for gid in rnd.choice(arange(epos.shape[0]), size=ncon, replace=False):
                    xsyncon.append([gid,cid])
        elif mth['/network/syn/geom/unit'] == 'N':
            if  not mth.check("/network/syn/geom/nmin"):
                logging.error("Cannot find maximum probability /network/syn/geom/nmin for discreet distribution")
                raise BaseException("Cannot find /network/syn/geom/nmin for discreet distribution")
            if  not mth.check("/network/syn/geom/nmax"):
                logging.error("Cannot find sigma /network/syn/geom/nmax for discreet distribution")
                raise BaseException("Cannot find /network/syn/geom/nmax for discreet distribution")
            logging.info(" > Generating random connections when echa TC has from {} to {} synapses with closet rGCs".format(mth["/network/syn/geom/nmin"],mth["/network/syn/geom/nmax"]) )
            for cid,(cnx,cny) in enumerate(posxy):
                ncon = rnd.randint(mth['/network/syn/geom/nmin'],mth['/network/syn/geom/nmax']+1)
                d = sqrt((epos[:,0]-cnx)**2+(epos[:,1]-cny)**2)
                ids = argsort(d)[-ncon:]
                for gid in ids:
                    xsyncon.append([gid,cid])

        else:
            logging.error("Unknown pattern of synaptic conections {}".format(mth['/network/syn/geom/unit']))
            raise BaseException("Unknown pattern of synaptic conections {}".format(mth['/network/syn/geom/unit']))
            
                            
        logging.info(" > Have generated new connections list!")
        logging.debug("New connection list is {}".format(xsyncon))
        xsyncon = array(xsyncon)
    else:
        xsyncon = syncon
        logging.debug("Using connection list is {}".format(xsyncon.tolist()))

    

    for nid,n in enumerate(neurons):
        n.s = h.AMPAandNMDAwithTone(0.5,sec=n.soma)
        n.s.e                = 0.
            
        if mth.check("/network/syn/toneExc") : n.s.GLUTg  = mth["/network/syn/toneExc"]
        if mth.check("/network/syn/toneExc") : n.s.GABABg = mth["/network/syn/toneExc"]
                    
        # Set NMDA
        for sprm in "/network/syn/NMDA/tau1","/network/syn/NMDA/tau2","/network/syn/NMDA/p":
            if not mth.check(sprm):
                logging.error("Cannot find parameter {}".format(sprm) )
                exit(1)
        n.s.NMDAt1,n.s.NMDAt2,n.s.NMDAp = \
            mth["/network/syn/NMDA/tau1"],\
            mth["/network/syn/NMDA/tau2"],\
            mth["/network/syn/NMDA/p"]

        # Set AMPA
        for sprm in "/network/syn/AMPA/tau1","/network/syn/AMPA/tau2","/network/syn/AMPA/p":
            if not mth.check(sprm):
                logging.error("Cannot find parameter {}".format(sprm) )
                exit(1)
        n.s.AMPAt1,n.s.AMPAt2,n.s.AMPAp = \
            mth["/network/syn/AMPA/tau1"],\
            mth["/network/syn/AMPA/tau2"],\
            mth["/network/syn/AMPA/p"]
        
        n.s.u0 = mth["/network/syn/ppr_u0"] if mth.check("/network/syn/ppr_u0") else 1.
        n.s.gsynmod = 1. # there is no modulation all the time
        if mth.check("/sim/record/cont/cur") or mth.check("/sim/record/cont/meancur"):
            if mth["/network/syn/AMPA/p"] > 0.:
                n.ampairec = h.Vector()
                n.ampairec.record(n.s._ref_ampai)
            if mth["/network/syn/NMDA/p"] > 0.:
                n.nmdairec = h.Vector()
                n.nmdairec.record(n.s._ref_nmdai)
        synidx = (mth["/network/syn/NMDA/p"] - mth["/network/syn/AMPA/p"])/(mth["/network/syn/NMDA/p"] + mth["/network/syn/AMPA/p"])
        if gsynmin_idx[0] > gsynmin_idx[-1]:
            n.ming = interp(synidx, gsynmin_idx[::-1], selected[n.type][2][::-1])
        else:
            n.ming = interp(synidx, gsynmin_idx, selected[n.type][2])
        #DB>>
        # print(synidx)
        # print(gsynmin_idx)
        # print(selected[n.type])
        # print(selected[n.type][2])
        # print(n.ming)
        # exit(0)
        #<<DB
        logging.debug("> SYN:{} E:{} AMPAt1:{} AMPAt2:{} AMPAp:{} NMDAt1:{} NMDAt2:{} NMDAp:{} U0:{} Tone: GUT:{} GABAB:{}".format(\
            nid,n.s.e,\
            n.s.AMPAt1,n.s.AMPAt2,n.s.AMPAp,\
            n.s.NMDAt1,n.s.NMDAt2,n.s.NMDAp,\
            n.s.u0,n.s.GLUTg,n.s.GABABg,n.ming )\
        )
    logging.info(" > set synapses")

    

    if gsyncond is None:
        xgsyncond = []
        for rgcid,nid in xsyncon:
            ming = neurons[nid].ming
            if mth.check("/network/syn/sig2gsyn") and mth.check("/network/syn/rand"):
                d = sum((epos[rgcid,:]-posxy[nid,:])**2)
                if mth.check("/network/syn/gsyn"):
                    if mth["/network/syn/gsyn"] > 0.:
                        xgsyn = mth["/network/syn/gsyn"]*rnd.random()*exp(-d/mth["/network/syn/sig2gsyn"]**2)
                    if mth["/network/syn/gsyn"] < 0.:
                        xgsyn = -mth["/network/syn/gsyn"]*ming*rnd.random()*exp(-d/mth["/network/syn/sig2gsyn"]**2)
                else:
                    xgsyn = ming*rnd.random()*exp(-d/mth["/network/syn/sig2gsyn"]**2)
            elif mth.check("/network/syn/sig2gsyn"):
                d = sum((epos[rgcid,:]-posxy[nid,:])**2)
                if mth.check("/network/syn/gsyn"):
                    if mth["/network/syn/gsyn"] > 0.:
                        xgsyn = mth["/network/syn/gsyn"]*exp(-d/mth["/network/syn/sig2gsyn"]**2)
                        # #DB>>
                        # print(nid,rgcid,d,xgsyn)
                        # #<<DB
                    if mth["/network/syn/gsyn"] < 0.:
                        xgsyn = -mth["/network/syn/gsyn"]*ming*exp(-d/mth["/network/syn/sig2gsyn"]**2)
                else:
                    xgsyn = ming*exp(-d/mth["/network/syn/sig2gsyn"]**2)
            elif mth.check("/network/syn/gsyn"):
                if mth["/network/syn/gsyn"] > 0.:
                    xgsyn = mth["/network/syn/gsyn"]*(rnd.random() if mth.check("/network/syn/rand") else 1.) 
                if mth["/network/syn/gsyn"] < 0.:
                    xgsyn = -mth["/network/syn/gsyn"]*ming*(rnd.random() if mth.check("/network/syn/rand") else 1.)
            else:
                xgsyn = ming*(rnd.random() if mth.check("/network/syn/rand") else 1./3.)
            #>> There aren't big reason add few ms delays with such huge desynchronization rGC 
            # if mth.check("/network/syn/delay"):
                # if mth.check("/network/syn/delay/min") and mth.check("/network/syn/delay/max"):
                    
            # else:
                # dly = 0.1
            dly = 0.1
            xgsyncond.append( (xgsyn,dly) )
        logging.info(" > Have generated new connections weights and delays!")
        logging.debug("New conductance list is {}".format(xgsyncond))
        xgsyncond = array(xgsyncond)
    else:
        xgsyncond = gsyncond
        logging.debug("Using conductance {}".format(xgsyncond.tolist()))
    
    if mth.check("/network/syn/prenorm") and gsyncond is None:
        logging.debug("Normalize weights within population.")
        for nid,n in enumerate(neurons):
            if mth.check("/network/syn/gsyn"):
                if mth["/network/syn/gsyn"] > 0.:  norm =  mth["/network/syn/gsyn"]
                if mth["/network/syn/gsyn"] < 0.:  norm = -mth["/network/syn/gsyn"]*n.ming
            else:
                norm = n.ming / 3.
            n2synidx, = where(xsyncon[:,1] == nid)
            logging.debug(" NID:{:03d} Total weight={} Normalized should be={}".format(nid,sum(xgsyncond[n2synidx,0]),norm) )
            norm = norm/sum(xgsyncond[n2synidx,0])
            xgsyncond[n2synidx,0] = norm*xgsyncond[n2synidx,0]
            logging.debug("         Norm coefficient={}, Total weight after normalization={}".format(norm,sum(xgsyncond[n2synidx,0])) )
        logging.info(" > total synaptic weights have been normalized")
    
    if mth.check("/analysis/connectivity"):
        xrgc = zeros( len(rGCs)    )
        xlgn = zeros( len(neurons) )
        for rgcid,nid in xsyncon:
            xrgc[rgcid] += 1
            xlgn[nid]   += 1
        mth["/stats/connectivity/rGC/mean"] = mean(xrgc)
        mth["/stats/connectivity/rGC/std" ] =  std(xrgc)
        mth["/stats/connectivity/rGC/min" ] = amin(xrgc)
        mth["/stats/connectivity/rGC/max" ] = amax(xrgc)
        logging.info(" > number of synapses from rGC")
        logging.info("       > mean = {}".format(mth["/stats/connectivity/rGC/mean"]))
        logging.info("       > std  = {}".format(mth["/stats/connectivity/rGC/std" ]))
        logging.info("       > min  = {}".format(mth["/stats/connectivity/rGC/min" ]))
        logging.info("       > max  = {}".format(mth["/stats/connectivity/rGC/max" ]))
        mth["/stats/connectivity/LGN/mean"] = mean(xlgn)
        mth["/stats/connectivity/LGN/std" ] =  std(xlgn)
        mth["/stats/connectivity/LGN/min" ] = amin(xlgn)
        mth["/stats/connectivity/LGN/max" ] = amax(xlgn)
        logging.info(" > number of synapses to LGN")
        logging.info("       > mean = {}".format(mth["/stats/connectivity/LGN/mean"]))
        logging.info("       > std  = {}".format(mth["/stats/connectivity/LGN/std" ]))
        logging.info("       > min  = {}".format(mth["/stats/connectivity/LGN/min" ]))
        logging.info("       > max  = {}".format(mth["/stats/connectivity/LGN/max" ]))
        del xrgc,xlgn

    if mth.check("/sim/state/load"):
        with stkdata(mth["/sim/state/load"]) as sd:
            gsynstate  = sd["gsynstate",mth["/sim/state/id"]]
        logging.info(" > gsynstate is loaded from {}:{}".format(mth["/sim/state/load"],mth["/sim/state/id"]))
        for (rgcid,nid),(gsyn,dly),(y,z,tsyn) in zip(xsyncon,xgsyncond,gsynstate):
            rgc,s = rGCs[rgcid][0], neurons[nid].s
            c = h.NetCon(rgc,s)
            c.weight[0] = gsyn
            c.weight[1] = y
            c.weight[2] = z
            c.weight[3] = 0. #tsyn
            c.delay     = dly
            con.append(c)
    else:
        for (rgcid,nid),(gsyn,dly) in zip(xsyncon,xgsyncond):
            rgc,s = rGCs[rgcid][0], neurons[nid].s
            c = h.NetCon(rgc,s)
            c.weight[0] = gsyn
            c.delay = dly
            con.append(c)
    logging.info(" > synapses are connected")
else:
    mth["/stats/connectivity/rGC/mean"] = 0.
    mth["/stats/connectivity/rGC/std" ] = 0.
    mth["/stats/connectivity/rGC/min" ] = 0.
    mth["/stats/connectivity/rGC/max" ] = 0.
    mth["/stats/connectivity/LGN/mean"] = 0.
    mth["/stats/connectivity/LGN/std" ] = 0.
    mth["/stats/connectivity/LGN/min" ] = 0.
    mth["/stats/connectivity/LGN/max" ] = 0.


if mth.check("/network/cx/enable"):
    cxfeedback = []
    if mth.check("/sim/state/load"):
        with stkdata(mth["/sim/state/load"]) as sd:
            cxsynstat  = sd["cxsynstate",mth["/sim/state/id"]]
        logging.info(" > cxsynstat is loaded from {}:{}".format(mth["/sim/state/load"],mth["/sim/state/id"]))
    if mth["/network/cx/gsyn"] < 0 :
        wsyn = getWeights()
    for nid,n in enumerate(neurons):
        n.cxs = h.AMPAandNMDAwithTone(0.5,sec=n.soma)
        n.cxs.e                = 0.
        n.cxs.AMPAt1,n.cxs.AMPAt2,n.cxs.AMPAp  = mth["/network/cx/AMPA/tau1"],mth["/network/cx/AMPA/tau2"],mth["/network/cx/AMPA/p"]
        n.cxs.NMDAt1,n.cxs.NMDAt2,n.cxs.NMDAp  = mth["/network/cx/NMDA/tau1"],mth["/network/cx/NMDA/tau2"],mth["/network/cx/NMDA/p"]
        if mth.check("/network/cx/toneExc") : n.cxs.GLUTg  = mth["/network/cx/toneExc"]
        if mth.check("/network/cx/toneExc") : n.cxs.GABABg = mth["/network/cx/toneExc"]
        
        
        n.cxs.u0 = mth["/network/cx/ppr_u0"] if mth.check("/network/cx/ppr_u0") else 0.3
        n.cxs.gsynmod = 1. # there is no modulation all the time
        if mth.check("/network/cx/gsyn"):
            if mth["/network/cx/gsyn"] > 0.:
                cxgsyn =  mth["/network/cx/gsyn"]
            else:
                synidx, = where(xsyncon[:,1] == nid)
                # meanRGC = sum(wsyn[synidx])/synidx.shape[0]
                # cxgsyn = -mth["/network/cx/gsyn"]*meanRGC/len(neurons)
                totalRGC = sum(wsyn[synidx])
                cxgsyn = -mth["/network/cx/gsyn"]*totalRGC/len(neurons)
        else:
            cxgsyn = n.ming / 3.

        if mth.check("/sim/record/cont/cur") or mth.check("/sim/record/cont/meancur"):
            n.cxampairec = h.Vector()
            n.cxampairec.record(n.cxs._ref_ampai)
            n.cxnmdairec = h.Vector()
            n.cxnmdairec.record(n.cxs._ref_nmdai)
        logging.debug("> CX SYN:{} E:{} AMPAt1:{} AMPAt2:{} AMPAp:{} NMDAt1:{} NMDAt2:{} NMDAp:{} U0:{} Tone: GUT:{} GABAB:{} Gmax: {}".format(\
            nid,n.cxs.e,n.cxs.AMPAt1,n.cxs.AMPAt2,n.cxs.AMPAp,n.cxs.NMDAt1,n.cxs.NMDAt2,n.cxs.NMDAp,\
            n.cxs.u0,n.cxs.GLUTg,n.cxs.GABABg,cxgsyn )\
        )
        if mth.check("/sim/state/load"):
            for npre in neurons:
                c = h.NetCon(npre.soma(0.5)._ref_v,n.cxs,sec=npre.soma)
                cxfeedback.append(c)        
        else:
            for npre in neurons:
                c = h.NetCon(npre.soma(0.5)._ref_v,n.cxs,sec=npre.soma)
                c.weight[0] = cxgsyn
                c.delay     = mth["/network/cx/delay"] if mth.check("/network/cx/delay") else 0.1
                cxfeedback.append(c)
    if mth.check("/sim/state/load"):
        for c,(cxgsyn,y,z,tsyn,cxdly) in zip(cxfeedback,cxsynstat):
            c.weight[0] = cxgsyn
            c.weight[1] = y
            c.weight[2] = z
            c.weight[3] = tsyn
            c.delay     = cxdly

    logging.info(" > set and connect cortical feedback")

if mth.check("/network/trn/enable"):
    trnfeedback = []
    if mth.check("/sim/state/load"):
        with stkdata(mth["/sim/state/load"]) as sd:
            trnsynstate  = sd["trnsynstate",mth["/sim/state/id"]]
        logging.info(" > trnsynstate is loaded from {}:{}".format(mth["/sim/state/load"],mth["/sim/state/id"]))
    for nid,n in enumerate(neurons):
        n.trns = h.Exp2Syn(0.5,sec=n.soma)
        n.trns.e                 = mth["/network/trn/e"]
        n.trns.tau1,n.trns.tau2  = mth["/network/trn/tau1"],mth["/network/trn/tau2"]
        
        if mth.check("/network/trn/gsyn"):
            if mth["/network/trn/gsyn"] > 0.:
                trngsyn =  mth["/network/trn/gsyn"]
            else:
                trngsyn = -mth["/network/trn/gsyn"]*n.ming
        else:
            trngsyn = n.ming / 3.

        if mth.check("/sim/record/cont/cur") or mth.check("/sim/record/cont/meancur"):
            n.trngabairec = h.Vector()
            n.trngabairec.record(n.trns._ref_i)
        logging.debug("> trn SYN:{} E:{} tau1:{} tau2:{} gmax:{}".format(\
            nid,n.trns.e,n.trns.tau1,n.trns.tau2,trngsyn )\
        )
        if mth.check("/sim/state/load"):
            for npre in neurons:
                c = h.NetCon(npre.soma(0.5)._ref_v,n.trns,sec=npre.soma)
                trnfeedback.append(c)
        else:
            for npre in neurons:
                c = h.NetCon(npre.soma(0.5)._ref_v,n.trns,sec=npre.soma)
                c.weight[0] = trngsyn
                c.delay     = mth["/network/trn/delay"] if mth.check("/network/trn/delay") else 0.1
                trnfeedback.append(c)
    if mth.check("/sim/state/load"):
        for c,(trngsyn,trndly) in zip(trnfeedback,trnsynstate):
            c.weight[0] = trngsyn
            c.delay     = trndly
            
    logging.info(" > set and connect TRN inhibitory feedback")

if mth.check("/network/save"):
    if type(mth["/network/save"]) is str: xfile =  mth["/network/save"] 
    elif mth.check("/network/file")     : xfile =  mth["/network/file"]
    else :
        logging.error("/network/save is not a string and /network/file is not set properly")
        exit(1)
    with stkdata(xfile) as idt:
        logging.info(" > saving into file file {}".format(xfile))
        if mth.check("/network/reset/nprms") or nprms is None \
            or not '/nprms' in idt or sum( (xnprms - idt['/nprms',-1])**2) > 1e-12:
            idt['/nprms']         = xnprms
            idt["/nethash/nprms"] = nprms_hash
            #DB>>
            # print("/nethash/nprms",idt["/nethash/nprms",-1],nprms_hash)
            #<<DB
            logging.info(" > have saved neuron parameters into the file")
                
        if (mth.check("/network/reset/gjcon") or gjcon is None \
            or not '/gjcon' in idt or sum( (xgjcon - idt['/gjcon',-1])**2) > 1e-12) and not mth.check("/block/gjcon"):
            idt['/gjcon']         = xgjcon
            idt["/nethash/gjcon"] = gjcon_hash
            #DB>>
            # print("/nethash/gjcon",idt["/nethash/gjcon",-1],gjcon_hash)
            #<<DB
            logging.info(" > have saved gap junction list  into the file")
        
        if (mth.check("/network/reset/syncon") or syncon is None \
            or not '/syncon' in idt or sum( (xsyncon - idt['/syncon',-1])**2) > 1e-12) and not mth.check("/block/syncon"):
            idt['/syncon']         = xsyncon
            idt['/nethash/syncon'] = syncon_hash
            logging.info(" > have saved list of synaptic connections into the file")
                
        if (mth.check("/network/reset/gsyncond") or gsyncond is None \
            or not '/gsyncond' in idt or sum( (xgsyncond - idt['/gsyncond',-1])**2) > 1e-12) and not mth.check("/block/syncon"):
            idt['/gsyncond']         = xgsyncond
            idt['/nethash/gsyncond'] = gsyncond_hash
            logging.info(" > have saved list of synaptic conductance into the file")  

#DB>>
# for nid, (n, nx) in enumerate(zip(neurons, xnprms)):
    # if not nid%4: print()
    # print(f"{nx:3d}:{n.type:3d} ",end="")
# print()
# for gjid,(f,t) in enumerate(xgjcon):
    # if not gjid%4: print()
    # print(f"({f:3d})>==<({t:3d})  ", end="")
# print()
# print(xsyncon)
# print(xgsyncond)
# exit(0)
#<<DB

    
def norm_neuron_weights(ngsyn,nid,ming=None):
    if ming is None: ming = neurons[nid].ming
    if mth.check("/network/btdp/normgsyn"):
        if mth["/network/btdp/normgsyn"] > 0.: 
            xgsyn =  mth["/network/btdp/normgsyn"]
        if mth["/network/btdp/normgsyn"] < 0.:
            xgsyn = -mth["/network/btdp/normgsyn"]*ming
    else:
        xgsyn = ming
    logging.debug("       Norm #{:03d} norm gsyn={}".format(nid,xgsyn) )
    if mth.check("/network/btdp/synthr") and mth.check("/network/btdp/minact"):
        maxgs  = argsort(ngsyn)
        sumMaxN = sum(ngsyn[maxgs[-mth["/network/btdp/normn"]:]])
        scalier = xgsyn/sumMaxN
        logging.debug("       -----> sum max {:02d}      = {}".format(len(maxgs[-mth["/network/btdp/normn"]:]), sumMaxN) )
        logging.debug("       -----> scalier         = {}".format(scalier) )
        ngsyn *= scalier
        synthr = mth["/network/btdp/synthr"] if mth["/network/btdp/synthr"] > 0 else (-ming*mth["/network/btdp/synthr"])
        nact   = len(where(ngsyn>synthr)[0])
        logging.debug("       -----> active syn nact = {} : synthr={} : minact={}".format(nact,synthr,mth["/network/btdp/minact"]))
        while nact < mth["/network/btdp/minact"]:
            logging.debug("       -----> add more to {}".format(nid) )
            ngsyn[rnd.randint(nGCs)] = ming*rnd.random()
            sumMaxN = sum(ngsyn[maxgs[-mth["/network/btdp/normn"]:]])
            scalier = xgsyn/sumMaxN
            logging.debug("       -----> sum max {:02d}      = {}".format(len(maxgs[-mth["/network/btdp/normn"]:]), sumMaxN) )
            logging.debug("       -----> scalier         = {}".format(scalier) )
            ngsyn *= scalier
            nact   = len(where(ngsyn>synthr)[0])
            logging.debug("       -----> active syn nact = {} : synthr={} : minact={}".format(nact,synthr,mth["/network/btdp/minact"]))
    else:
        maxgs  = argsort(ngsyn)
        sumMaxN = sum(ngsyn[maxgs[-mth["/network/btdp/normn"]:]])
        scalier = xgsyn/sumMaxN
        logging.debug("       -----> sum max {:02d}      = {}".format(len(maxgs[-mth["/network/btdp/normn"]:]), sumMaxN) )
        logging.debug("       -----> scalier         = {}".format(scalier) )
        ngsyn *= scalier
    return ngsyn
    
def norm_weights():
    logging.debug(" Normalize everyone weight! ")
    wsyn = getWeights()
    for nid,n in enumerate(neurons):
        synidx, = where(xsyncon[:,1] == nid)
        wsyn[synidx]  = norm_neuron_weights(wsyn[synidx],nid,n.ming)
    setWeights(wsyn)

if mth.check("/network/btdp/enable"):
    norm_weights()

if ( mth.check("/network/btdp/enable") and mth.check("/network/btdp/continue") ) or\
   ( mth.check("/network/home/enable") and mth.check("/network/home/continue") ):
    xfile = None
    if   type(mth["/network/btdp/continue"]) is str:
        xfile = mth["/network/btdp/continue"]
    elif type(mth["/network/home/continue"]) is str:
        xfile = mth["/network/home/continue"]
    elif type(mth["/sim/record/gsyn"]) is str:
        xfile = mth["/sim/record/gsyn"]
    elif type(mth["/sim/record/save"]) is str:
        xfile = mth["/sim/record/save"] 
    elif mth.check("/sim/record/file"):
        xfile = mth["/sim/record/file"] 
    else:
        logging.error("Cannot determent from which file read synaptic conductance for continuation BTDP and/or homeostasis")
        if mth.check("/network/annoying_reload/btdp") : exit(1)
    if xfile is not None:
        with stkdata(xfile) as fd:
            basehashline = fd["/hash",-1]
            if "/"+basehashline+"/gsyn" in fd:
                setWeights(fd["/"+basehashline+"/gsyn",-1])
                logging.info(f" > have read synaptic conductance from {xfile} to continue BTDP/homeostasis")
            else:
                logging.error(f"Cannot find previous record for this model in {xfile}" )
                if mth.check("/network/annoying_reload/btdp") : exit(1)
    


if mth.check("/sim/record/save"):
    if type(mth["/sim/record/save"]) is str:
        xfile = mth["/sim/record/save"] 
    elif mth.check("/sim/record/file"):
        xfile = mth["/sim/record/file"] 
    else:
        logging.error("/sim/record/save is not a string and /sim/record/file is not set properly")
        exit(1)
    with stkdata(xfile) as fd:
        if not "/hash" in fd or not hashline in fd["/hash",None]:
            fd["/"+hashline+"/model"]       = mth.methods.exp()
            fd["/"+hashline+"/n-neurons"]   = len(neurons)
            fd["/"+hashline+"/epos"]        = epos
            fd["/"+hashline+"/posxy"]       = posxy
            fd["/"+hashline+'/nprms']       = [ selected[x] for x in xnprms ]
            fd["/"+hashline+'/gjcon']       = None if mth.check("/block/gjcon")  else xgjcon
            fd["/"+hashline+'/syncon']      = None if mth.check("/block/syncon") else xsyncon
            fd["/"+hashline+'/gsyncond']    = None if mth.check("/block/syncon") else xgsyncond

        fd["/timestamp"] = timestamp
        fd["/hash"]      = hashline
        
        # if mth.check("/sim/record/spike") and not type(mth["/sim/record/spike"]) is str:
            # rGCspks = sorted([ (spt,rid) for us in usespikes if us.shape[0] != 0 for rid,spt in us ])
            # fd["/"+hashline+"/rGC/spikes"] = array(rGCspks) if len (rGCspks) != 0 else empty((0,2))
        # if  mth.check("/network/btdp/enable") and mth.check("/sim/record/gsyn") and not type(mth["/sim/record/gsyn"]) is str:
            # fd["/"+hashline+"/gsyn"] = getWeights()

    if mth.check("/sim/record/spike"):
        yfile = mth["/sim/record/spike"] if type(mth["/sim/record/spike"]) is str else xfile
        with stkdata(yfile) as fd:        
            rGCspks = sorted([ (spt,rid) for us in usespikes if us.shape[0] != 0 for rid,spt in us ])
            fd["/"+hashline+"/rGC/spikes"] = array(rGCspks) if len (rGCspks) != 0 else empty((0,2))

    if  ( mth.check("/network/btdp/enable") or mth.check("/network/home/enable") )and mth.check("/sim/record/gsyn"):
        yfile =  mth["/sim/record/gsyn"] if type(mth["/sim/record/gsyn"]) is str else xfile
        with stkdata(yfile) as fd:
            fd["/"+hashline+"/gsyn"] = getWeights()

def save_anything(t0,t1,nupdt):
    def resizevector(vec):
        return vec[::int( round(mth["/sim/record/cont/dt"]/h.dt) )] if mth.check("/sim/record/cont/dt") else vec
    logging.info(" > Init recording #{} interval {},{}".format(nupdt,t0,t1))
    simpref = "/"+hashline
    if type(mth["/sim/record/save"]) is str:
        xfile = mth["/sim/record/save"] 
    elif mth.check("/sim/record/file"):
        xfile = mth["/sim/record/file"] 
    else:
        logging.error("/sim/record/save is not a string and /sim/record/file is not set properly")
        exit(1)
    maxbuffersize=mth["/sim/record/buffersize"] if mth.check("/sim/record/buffersize") else 0
    def recordstate(xfile,var,value):
        with stkdata(xfile,maxbuffersize=maxbuffersize) as sd:
            sd[var] = value
    if  ( mth.check("/network/btdp/enable") or mth.check("/network/home/enable") ) and mth.check("/sim/record/gsyn"):
        if type(mth["/sim/record/gsyn"]) is int:
            if nupdt%mth["/sim/record/gsyn"] == 0: recordstate(xfile                  ,simpref+"/gsyn",getWeights() )
        elif type(mth["/sim/record/gsyn"]) is str: recordstate(mth["/sim/record/gsyn"],simpref+"/gsyn",getWeights() )
        else                                     : recordstate(xfile                  ,simpref+"/gsyn",getWeights() )
        logging.info(" > Saved synaptic conductance into the file")
    
    if mth.check("/sim/record/spike"):
        popspks = []
        for nid,n in enumerate(neurons):
            popspks += [ (spt,nid) for spt in array(n.spks)]
        popspks = empty((0,2)) if len(popspks) == 0 else array(popspks)
        if type(mth["/sim/record/spike"]) is str: recordstate(mth["/sim/record/spike"],simpref+"/spikes", popspks)
        else                                    : recordstate(xfile                   ,simpref+"/spikes", popspks)
        logging.info(" > Saved spikes into the file")
    if not mth.check("/sim/record/cont"):
        logging.info(f" > All continues-variable recordings are disabled")
        logging.info(f" > Finish recording #{nupdt} interval {t0},{t1}")
        return
    xtrec = resizevector( array(trec) )
    xtinc = False
    if mth.check("/sim/record/cont/volt"):
        if type(mth["/sim/record/cont/volt"]) is str:
            with stkdata(mth["/sim/record/cont/volt"],maxbuffersize=maxbuffersize) as sd:
                sd[simpref+"/cont/time"] = xtrec[:-1]
                for nid,n in enumerate(neurons):
                    sd[simpref+f"/cont/volt/{nid:03d}"] = resizevector( array(n.volt) )[:-1]
        else:
            with stkdata(xfile,maxbuffersize=maxbuffersize) as sd:
                if not xtinc:
                    sd[simpref+"/cont/time"] = xtrec[:-1]
                    xtinc = True
                    logging.info(" > Saved time into the file")
                for nid,n in enumerate(neurons):
                    sd[simpref+f"/cont/volt/{nid:03d}"] = resizevector( array(n.volt) )[:-1]
        logging.info(" > Saved voltages into the file")

    logging.info(" > Currents")
    meancur = mth.check("/sim/record/cont/meancur")
    ampaenable = mth["/network/syn/AMPA/p"] > 0.
    nmdaenable = mth["/network/syn/NMDA/p"] > 0.
    logging.info("   > "+("Record mean currents" if meancur else "Mean current recordings are disabled"))
    logging.info("   > "+("Record cont currents" if mth.check("/sim/record/cont/cur") else "Continues current recordings are disabled"))
    logging.info("   > "+("AMPA is active" if ampaenable else "AMPA is blocked"))
    logging.info("   > "+("NMDA is active" if nmdaenable else "NMDA is blocked"))
    if mth.check("/sim/record/cont/cur") or meancur:
        if not mth.check("/block/syncon"):
            if mth.check("/sim/record/cont/cur"):
                if type(mth["/sim/record/cont/cur"]) is str:
                    cfile, themainfile = mth["/sim/record/cont/cur"], False
                else:
                    cfile, themainfile = xfile                      , True
                with stkdata(cfile,maxbuffersize=maxbuffersize) as sd:
                    if not xtinc and themainfile:
                        sd[simpref+"/cont/time"] = xtrec[:-1]
                        xtinc = True
                        logging.info(" > Saved time into the file")
                    elif not themainfile:
                        sd[simpref+"/cont/time"] = xtrec[:-1]
                    for nid,n in enumerate(neurons):
                        if ampaenable:
                            amparec = resizevector( array(n.ampairec) )[:-1]
                            sd[simpref+f"/cont/cur/syn/ampa/{nid:03d}"] = amparec
                            if meancur:
                                if nid == 0: meanampa  = copy(amparec)
                                else       : meanampa += amparec

                        if nmdaenable:
                            nmdarec =  resizevector( array(n.nmdairec) )[:-1]
                            sd[simpref+f"/cont/cur/syn/nmda/{nid:03d}"] = nmdarec
                            if meancur:
                                if nid == 0: meannmda  = copy(nmdarec)
                                else       : meannmda += nmdarec
                    if not ampaenable: sd[simpref+f"/cont/cur/syn/ampa"] = None
                    if not nmdaenable: sd[simpref+f"/cont/cur/syn/nmda"] = None
                logging.info("   > Saved continues currents" )
            else:
                for nid,n in enumerate(neurons):
                    if ampaenable:
                        if nid == 0: meanampa  = resizevector( array(n.ampairec) )[:-1]
                        else       : meanampa += resizevector( array(n.ampairec) )[:-1]
                    if nmdaenable:
                        if nid == 0: meannmda  = resizevector( array(n.nmdairec) )[:-1]
                        else       : meannmda += resizevector( array(n.nmdairec) )[:-1]
            if meancur:
                if type(mth["/sim/record/cont/meancur"]) is str:
                    cfile, themainfile = mth["/sim/record/cont/meancur"], False
                else:
                    cfile, themainfile = xfile                          , True
                with stkdata(cfile,maxbuffersize=maxbuffersize) as sd:
                    if not xtinc and themainfile:
                        sd[simpref+"/cont/time"] = xtrec[:-1]
                        xtinc = True
                        logging.info(" > Saved time into the file")
                    elif not themainfile:
                        sd[simpref+"/cont/time"] = xtrec[:-1]  
                    sd[simpref+"/cont/cur/syn/mean/ampa" ] =\
                        meanampa/len(neurons) if ampaenable else None
                    sd[simpref+"/cont/cur/syn/mean/nmda" ] =\
                        meannmda/len(neurons) if nmdaenable else None
                logging.info("   > Saved mean currents" )
        else:
            if mth.check("/sim/record/cont/cur"):
                if type(mth["/sim/record/cont/cur"]) is str:
                    cfile, themainfile = mth["/sim/record/cont/cur"], False
                else:
                    cfile, themainfile = xfile                      , True
                with stkdata(cfile,maxbuffersize=maxbuffersize) as sd:
                    if not xtinc and themainfile:
                        sd[simpref+"/cont/time"] = xtrec[:-1]
                        xtinc = True
                        logging.info(" > Saved time into the file")
                    elif not themainfile:
                        sd[simpref+"/cont/time"] = xtrec[:-1]
                    sd[simpref+"/cont/cur/syn/ampa"] = None
                    sd[simpref+"/cont/cur/syn/nmda"] = None
            if meancur:
                if type(mth["/sim/record/cont/meancur"]) is str:
                    cfile, themainfile = mth["/sim/record/cont/meancur"], False
                else:
                    cfile, themainfile = xfile                          , True
                with stkdata(cfile,maxbuffersize=maxbuffersize) as sd:
                    if not xtinc and themainfile:
                        sd[simpref+"/cont/time"] = xtrec[:-1]
                        xtinc = True
                        logging.info(" > Saved time into the file")
                    elif not themainfile:
                        sd[simpref+"/cont/time"] = xtrec[:-1]  
                    sd[simpref+"/cont/cur/syn/mean/ampa" ] = None
                    sd[simpref+"/cont/cur/syn/mean/nmda" ] = None
            
        if not mth.check("/block/gjcon"):
            logging.info("   > GJ are active")
            if meancur: meangj = None
            if mth.check("/sim/record/cont/cur"):
                if type(mth["/sim/record/cont/cur"]) is str:
                    cfile, themainfile = mth["/sim/record/cont/cur"], False
                else:
                    cfile, themainfile = xfile                      , True
                with stkdata(cfile,maxbuffersize=maxbuffersize) as sd:
                    if not xtinc and themainfile:
                        sd[simpref+"/cont/time"] = xtrec[:-1]
                        xtinc = True
                        logging.info(" > Saved time into the file")
                    elif not themainfile:
                        sd[simpref+"/cont/time"] = xtrec[:-1]
                    for ngj,(_,_,i,j,recigj) in enumerate(gj):
                        sd[simpref+"/cont/cur/gj/{:03d}x{:03d}".format(i,j)] = abs( resizevector( array(recigj) )[:-1] )
                        if meancur:
                            if meangj is None:
                                meangj  = copy( abs( resizevector( array(recigj) )[:-1] ) )
                            else:
                                meangj += abs( resizevector( array(recigj) )[:-1] )
            elif meancur:
                for ngj,(_,_,i,j,recigj) in enumerate(gj):
                    if meangj is None:
                        meangj  = copy( abs( resizevector( array(recigj) )[:-1] ) )
                    else:
                        meangj += abs( resizevector( array(recigj) )[:-1] )

            if meancur:
                if type(mth["/sim/record/cont/meancur"]) is str:
                    cfile, themainfile = mth["/sim/record/cont/meancur"], False
                else:
                    cfile, themainfile = xfile                          , True
                with stkdata(cfile,maxbuffersize=maxbuffersize) as sd:
                    if not xtinc and themainfile:
                        sd[simpref+"/cont/time"] = xtrec[:-1]
                        xtinc = True
                        logging.info(" > Saved time into the file")
                    elif not themainfile:
                        sd[simpref+"/cont/time"] = xtrec[:-1]
                    sd[simpref+"/cont/cur/gj/mean" ] = meangj/len(gj)
            logging.info("   > Saved GJ current into the file")
        else:
            logging.info("   > GJ are blocked - no recs")
            if mth.check("/sim/record/cont/cur"):
                if type(mth["/sim/record/cont/cur"]) is str:
                    cfile, themainfile = mth["/sim/record/cont/cur"], False
                else:
                    cfile, themainfile = xfile                      , True
                with stkdata(cfile,maxbuffersize=maxbuffersize) as sd:
                    if not xtinc and themainfile:
                        sd[simpref+"/cont/time"] = xtrec[:-1]
                        xtinc = True
                        logging.info(" > Saved time into the file")
                    elif not themainfile:
                        sd[simpref+"/cont/time"] = xtrec[:-1]
                    sd[simpref+"/cont/cur/gj"] = None 
            if meancur:
                if type(mth["/sim/record/cont/meancur"]) is str:
                    cfile, themainfile = mth["/sim/record/cont/meancur"], False
                else:
                    cfile, themainfile = xfile                          , True
                with stkdata(cfile,maxbuffersize=maxbuffersize) as sd:
                    if not xtinc and themainfile:
                        sd[simpref+"/cont/time"] = xtrec[:-1]
                        xtinc = True
                        logging.info(" > Saved time into the file")
                    elif not themainfile:
                        sd[simpref+"/cont/time"] = xtrec[:-1]
                    sd[simpref+"/cont/cur/gj/mean" ] = None

        if mth.check("/network/cx/enable"):
            cxampaenable = mth["/network/cx/AMPA/p"] > 0.
            cxnmdaenable = mth["/network/cx/NMDA/p"] > 0.
            if mth.check("/sim/record/cont/cur"):
                if type(mth["/sim/record/cont/cur"]) is str:
                    cfile, themainfile = mth["/sim/record/cont/cur"], False
                else:
                    cfile, themainfile = xfile                      , True
                with stkdata(cfile,maxbuffersize=maxbuffersize) as sd:
                    if not xtinc and themainfile:
                        sd[simpref+"/cont/time"] = xtrec[:-1]
                        xtinc = True
                        logging.info(" > Saved time into the file")
                    elif not themainfile:
                        sd[simpref+"/cont/time"] = xtrec[:-1]
                    for nid,n in enumerate(neurons):
                        if cxampaenable:
                            amparec = resizevector( array(n.cxampairec) )[:-1]
                            sd[simpref+f"/cont/cur/cxsyn/ampa/{nid:03d}"] = amparec
                            if meancur:
                                if nid == 0: cxmeanampa  = copy(amparec)
                                else       : cxmeanampa += amparec

                        if cxnmdaenable:
                            nmdarec =  resizevector( array(n.cxnmdairec) )[:-1]
                            sd[simpref+f"/cont/cur/cxsyn/nmda/{nid:03d}"] = nmdarec
                            if meancur:
                                if nid == 0: cxmeannmda  = copy(nmdarec)
                                else       : cxmeannmda += nmdarec
                    if not cxampaenable: sd[simpref+f"/cont/cur/cxsyn/ampa"] = None
                    if not cxnmdaenable: sd[simpref+f"/cont/cur/cxsyn/nmda"] = None
            else:
                for nid,n in enumerate(neurons):
                    if cxampaenable:
                        if nid == 0: cxmeanampa  = resizevector( array(n.cxampairec) )[:-1]
                        else       : cxmeanampa += resizevector( array(n.cxampairec) )[:-1]
                    if cxnmdaenable:
                        if nid == 0: cxmeannmda  = resizevector( array(n.cxnmdairec) )[:-1]
                        else       : cxmeannmda += resizevector( array(n.cxnmdairec) )[:-1]
            if meancur:
                if type(mth["/sim/record/cont/meancur"]) is str:
                    cfile, themainfile = mth["/sim/record/cont/meancur"], False
                else:
                    cfile, themainfile = xfile                          , True
                with stkdata(cfile,maxbuffersize=maxbuffersize) as sd:
                    if not xtinc and themainfile:
                        sd[simpref+"/cont/time"] = xtrec[:-1]
                        xtinc = True
                        logging.info(" > Saved time into the file")
                    elif not themainfile:
                        sd[simpref+"/cont/time"] = xtrec[:-1]  
                    sd[simpref+"/cont/cur/cxsyn/mean/ampa" ] =\
                        cxmeanampa/len(neurons) if cxampaenable else None
                    sd[simpref+"/cont/cur/cxsyn/mean/nmda" ] =\
                        cxmeannmda/len(neurons) if cxnmdaenable else None
            logging.info("   > Saved cortical current into the file")
        else:
            logging.info("   > Cortex isn't active")
            if mth.check("/sim/record/cont/cur"):
                if type(mth["/sim/record/cont/cur"]) is str:
                    cfile, themainfile = mth["/sim/record/cont/cur"], False
                else:
                    cfile, themainfile = xfile                      , True
                with stkdata(cfile,maxbuffersize=maxbuffersize) as sd:
                    if not xtinc and themainfile:
                        sd[simpref+"/cont/time"] = xtrec[:-1]
                        xtinc = True
                        logging.info(" > Saved time into the file")
                    elif not themainfile:
                        sd[simpref+"/cont/time"] = xtrec[:-1]
                    sd[simpref+"/cont/cur/cxsyn/ampa"] = None
                    sd[simpref+"/cont/cur/cxsyn/nmda"] = None
            if meancur:
                if type(mth["/sim/record/cont/meancur"]) is str:
                    cfile, themainfile = mth["/sim/record/cont/meancur"], False
                else:
                    cfile, themainfile = xfile                          , True
                with stkdata(cfile,maxbuffersize=maxbuffersize) as sd:
                    if not xtinc and themainfile:
                        sd[simpref+"/cont/time"] = xtrec[:-1]
                        xtinc = True
                        logging.info(" > Saved time into the file")
                    elif not themainfile:
                        sd[simpref+"/cont/time"] = xtrec[:-1]  
                    sd[simpref+"/cont/cur/cxsyn/mean/ampa" ] = None
                    sd[simpref+"/cont/cur/cxsyn/mean/nmda" ] = None

####################
        if mth.check("/network/trn/enable"):
            if mth.check("/sim/record/cont/cur"):
                if type(mth["/sim/record/cont/cur"]) is str:
                    cfile, themainfile = mth["/sim/record/cont/cur"], False
                else:
                    cfile, themainfile = xfile                      , True
                with stkdata(cfile,maxbuffersize=maxbuffersize) as sd:
                    if not xtinc and themainfile:
                        sd[simpref+"/cont/time"] = xtrec[:-1]
                        xtinc = True
                        logging.info(" > Saved time into the file")
                    elif not themainfile:
                        sd[simpref+"/cont/time"] = xtrec[:-1]
                    for nid,n in enumerate(neurons):
                        gabarec = resizevector( array(n.trngabairec) )[:-1]
                        sd[simpref+f"/cont/cur/trmsyn/gaba/{nid:03d}"] = gabarec
                        if meancur:
                            if nid == 0: trnmeangaba  = copy(gabarec)
                            else       : trnmeangaba += gabarec

            else:
                for nid,n in enumerate(neurons):
                    gabarec = resizevector( array(n.trngabairec) )[:-1]
                    if nid == 0: trnmeangaba  = copy(gabarec)
                    else       : trnmeangaba += gabarec
            if meancur:
                if type(mth["/sim/record/cont/meancur"]) is str:
                    cfile, themainfile = mth["/sim/record/cont/meancur"], False
                else:
                    cfile, themainfile = xfile                          , True
                with stkdata(cfile,maxbuffersize=maxbuffersize) as sd:
                    if not xtinc and themainfile:
                        sd[simpref+"/cont/time"] = xtrec[:-1]
                        xtinc = True
                        logging.info(" > Saved time into the file")
                    elif not themainfile:
                        sd[simpref+"/cont/time"] = xtrec[:-1]  
                    sd[simpref+"/cont/cur/trnsyn/mean/gaba" ] = trnmeangaba/len(neurons)
            logging.info("   > Saved TRN current into the file")
        else:
            logging.info("   > TRN isn't active")
            if mth.check("/sim/record/cont/cur"):
                if type(mth["/sim/record/cont/cur"]) is str:
                    cfile, themainfile = mth["/sim/record/cont/cur"], False
                else:
                    cfile, themainfile = xfile                      , True
                with stkdata(cfile,maxbuffersize=maxbuffersize) as sd:
                    if not xtinc and themainfile:
                        sd[simpref+"/cont/time"] = xtrec[:-1]
                        xtinc = True
                        logging.info(" > Saved time into the file")
                    elif not themainfile:
                        sd[simpref+"/cont/time"] = xtrec[:-1]
                    sd[simpref+"/cont/cur/trnsyn/gaba"] = None
            if meancur:
                if type(mth["/sim/record/cont/meancur"]) is str:
                    cfile, themainfile = mth["/sim/record/cont/meancur"], False
                else:
                    cfile, themainfile = xfile                          , True
                with stkdata(cfile,maxbuffersize=maxbuffersize) as sd:
                    if not xtinc and themainfile:
                        sd[simpref+"/cont/time"] = xtrec[:-1]
                        xtinc = True
                        logging.info(" > Saved time into the file")
                    elif not themainfile:
                        sd[simpref+"/cont/time"] = xtrec[:-1]  
                    sd[simpref+"/cont/cur/trnsyn/mean/gaba" ] = None

####################    

 
    logging.info(" > Finish recording #{} interval {},{}".format(nupdt,t0,t1))


if mth.check("/network/btdp/enable") and not( mth.check("/network/btdp/frkernel") and mth.check("/network/btdp/frsmwidth") ):
    logging.error("Parameters /network/btdp/frkernel and /network/btdp/frsmwidth are needed for firing rate convolution")
    exit(1)
else:
    kernel  = arange(-mth["/network/btdp/frsmwidth"],mth["/network/btdp/frsmwidth"],1.)
    kernel  = exp(- kernel**2/mth["/network/btdp/frkernel"]**2)
    kernel /= sum(kernel)

def compute_corr(t0,t1):
    wsyn = getdWeights()    

    pre_fr= zeros( (nGCs,int(ceil(mth["/network/btdp/update"])+2)) )
    for usid,us in enumerate(usespikes):
        fsp =  us[where(us  >  t0)]
        fsp = fsp[where(fsp <= t1)] - t0
        if fsp.shape[0] < 1:continue
        for tsp in fsp:
            pre_fr[usid,int( ceil(tsp) )] += 1
        pre_fr[usid,:] = convolve(pre_fr[usid,:],kernel,mode='same')
    mpre_fr = sum(pre_fr,axis=1)*1000./mth["/network/btdp/update"]
    logging.debug("Update [{},{}] presynaptic FR={}".format(t0,t1,mpre_fr.tolist()))
    
    
    postfr= zeros( (len(neurons)  ,int(ceil(mth["/network/btdp/update"])+2)) )
    for nid,n in enumerate(neurons):
        fsp = array(n.spks)
        fsp = fsp[where(fsp > t0)] - t0
        if fsp.shape[0] < 1:continue
        for tsp in fsp:
            postfr[nid,int( ceil(tsp) )] += 1
        postfr[nid,:] = convolve(postfr[nid,:],kernel,mode='same')
    mpostfr = sum(postfr,axis=1)*1000./mth["/network/btdp/update"]
    logging.debug("Update [{},{}] postsynaptic FR={}".format(t0,t1,mpostfr.tolist()))
    
    if mth.check("/network/btdp/frthr"):
        pre_id = where(mpre_fr > mth["/network/btdp/frthr"])[0]
        postid = where(mpostfr > mth["/network/btdp/frthr"])[0]
        logging.debug("FR threshold presynaptic  ID : {}".format(pre_id.tolist()))
        logging.debug("FR threshold postsynaptic ID : {}".format(postid.tolist()))
    else:
        pre_id = [ i for i in range(len(usespikes))]
        postid = [ i for i in range(len(neurons  ))]
    
    for nid in postid:
        cc = corrcoef(postfr[nid,:],pre_fr[pre_id,:])[0,1:]
        logging.debug("Neuron {:03d} correlation: {}".format(nid,",".join(["{:0.02f}".format(c) for c in cc]) ) )
        logging.debug("       weights before: {}".format(wsyn[nid,pre_id].tolist() ) )
        
        synidx        = [cid for cid,(rid,xnid) in enumerate(xsyncon) if xnid == nid and rid in pre_id]
        wsyn[synidx] += wsyn[synidx]*cc
        logging.debug("       prescale      : {}".format(wsyn[nid,:].tolist() ) )

        synidx,       = where(xsyncon[:,1] == nid)
        wsyn[synidx]  = norm_neuron_weights(wsyn[synidx],nid)
        logging.debug("       postscale     : {}".format(wsyn[nid,:].tolist() ) )
        logging.debug("       active weights: {}".format(wsyn[nid,pre_id].tolist() ) )
    
    # if mth.check("/network/btdp/stimNF"):
        # if mth["/network/btdp/stimNF"] > 0.:
            # for nid,(s,ming) in enumerate(syn):
                # if not nid in postid:
                    # wsyn[nid,:] += mth["/network/btdp/stimNF"]
        # if mth["/network/btdp/stimNF"] < 0.:
            # for nid,(s,ming) in enumerate(syn):
                # if not nid in postid:
                    # wsyn[nid,:] -= mth["/network/btdp/stimNF"]*ming
    setWeights(wsyn)

def homeostasis(t0,t1):
    if (t1-t0)<1e-3: return
    logging.debug(" > Homeostatic weight adjustment! ")
    decay = exp(-(t1-t0)/mth["/network/home/tau"])
    slope = mth["/network/home/slope"]
    wsyn = getWeights()
    if mth.check("/network/cx/enable"):
        cxwsyn,cxsynidx = getCXweights()
    for nid,n in enumerate(neurons):
        #--- g min/max
        gmax,gmin,gdelta = n.ming,0,n.ming/10
        if mth.check("/network/home/gmax"):
            gmax = mth["/network/home/gmax"]\
                if mth["/network/home/gmax"] > 0 else\
                  (-mth["/network/home/gmax"]*n.ming)
        if mth.check("/network/home/gmin"):
            gmin = mth["/network/home/gmin"]\
                if mth["/network/home/gmin"] > 0 else\
                  (-mth["/network/home/gmin"]*n.ming)
        if mth.check("/network/home/delta"):
            gdelta = mth["/network/home/delta"]\
                if mth["/network/home/delta"] > 0 else\
                  (-mth["/network/home/delta"]*n.ming)

        #--- firing rate and weight decay
        fsk = array(n.spks)
        fsp = float(fsk[where(fsk > t0)].shape[0])*1000./(t1-t0)
        dlt = mth["/network/home/target_fr"] - fsp
        hact = tanh(slope*dlt)
        #--- estimation for weight = 1
        synidx, = where(xsyncon[:,1] == nid)
        totpre = sum(wsyn[synidx])
        #if mth.check("/network/home/decay"):
            #wsyn[synidx]  = clip( wsyn[synidx]*decay+hact*gdelta,gmin,gmax )
        #else:
            #wsyn[synidx]  = clip( wsyn[synidx]      +hact*gdelta,gmin,gmax )
        
        wsyn[synidx]  = clip( wsyn[synidx]*(1+hact),gmin,gmax )

        totpst = sum(wsyn[synidx])
        logging.debug(f"    > Neuron #{nid}")
        logging.debug(f"      > spikes = {fsk.tolist()}")
        logging.debug(f"      > valid  = {fsk[where(fsk > t0)].tolist()}")
        logging.debug(f"      > count  = {fsk[where(fsk > t0)].shape}")
        #logging.debug(f"      > Fr     = {fsp}, Delta={dlt}, decay={decay}")
        #logging.debug(f"      > tanh   = {hact}, active={hact*gdelta}")
        #logging.debug(f"      > tanh   = {hact}, active={1+hact}")
        #logging.debug(f"      > gdelta = {gdelta}, gmin   = {n.ming}, clipped between [{gmin}, {gmax}]")
        logging.debug(f"      > Fr     = {fsp},  Delta  = {dlt}, slope =  {slope}")
        logging.debug(f"      > tanh   = {hact}, active = {1+hact}")
        logging.debug(f"      > gmin   = {n.ming},     clipped between = [{gmin}, {gmax}]")
        logging.debug(f"      > total  = {totpre} -> {totpst}")
        if mth.check("/network/cx/enable"):
            logging.debug(f"      > CORTEX ENABLE")
            synidx, = where(cxsynidx[:,1] == nid)
            totpre = sum(cxwsyn[synidx])
            cxwsyn[synidx]  = clip( cxwsyn[synidx]*(1+hact),gmin,gmax )
            totpst = sum(cxwsyn[synidx])
            logging.debug(f"         > total  = {totpre} -> {totpst}")
            
        
    setWeights(wsyn)
    if mth.check("/network/cx/enable"): setCXweights(cxwsyn)

if mth.check("/FR/Overall"):
    logging.info(" > Overall Fring rate is enabled")
    TotalFR = [ 0 for n in neurons ]

                    

if mth.check("/sim/disable"):
    logging.info(" > Simulations are canceled: relax!")
    exit(0)


logging.info( "======================================")
logging.info( "===          SIMULATION            ===")
if mth.check("/sim/parallel"):
    hpc  = h.ParallelContext()
    ncpu = mth["/sim/parallel"]\
        if type(mth["/sim/parallel"]) is int else\
        os.cpu_count()
    hpc.nthread(ncpu)
    logging.info(" > Utilize    : {} CPUs ".format(ncpu))
    
if   mth.check("/network/btdp/enable") and mth.check("/network/btdp/update"):
    mth["/sim/record/interval"] = mth["/network/btdp/update"]
    logging.info(" > BTDP is active : set /sim/record/interval = /network/btdp/update = {}".format(mth["/network/btdp/update"]) )
elif mth.check("/network/home/enable") and mth.check("/network/home/update"):
    mth["/sim/record/interval"] = mth["/network/home/update"]
    logging.info(" > Homeostasis is active : set /sim/record/interval = /network/home/update = {}".format(mth["/network/home/update"]) )
if mth.check("/sim/record/interval"):
    stoppoints = arange(0,mth["/sim/Tmax"],mth["/sim/record/interval"])
    stoppoints += stoppoints[1] if stoppoints.shape[0] > 1 else mth["/sim/Tmax"]
    if stoppoints[-1] > mth["/sim/Tmax"]:
        stoppoints[-1] = mth["/sim/Tmax"]
else:
    stoppoints = [mth["/sim/Tmax"]]

if mth.check("/sim/record/cont/volt") or mth.check("/sim/record/cont/cur") or mth.check("/sim/record/cont/meancur"):
    trec = h.Vector()
    trec.record(h._ref_t)

h.finitialize()
h.fcurrent()

tprev = 0
logging.info(" > Duration   : {} ms ".format(mth["/sim/Tmax"]))
logging.info(" > with       : {} stops ".format(len(stoppoints)-1))

# if mth.check("/sim/state/load"):
    # with stkdata(mth["/sim/state/load"]) as sd:
        # nrnstate  = sd["nrnstate",mth["/sim/state/id"]]
    # logging.info(" > nrnstate is loaded from {}:{}".format(mth["/sim/state/load"],mth["/sim/state/id"]))
    # for n,(v,
    # SK_E2.z, TC_HH.m, TC_HH.h, TC_HH.n,
    # TC_iT_Dec98.m, TC_iT_Dec98.h,
    # TC_ih_Bud97.m,
    # TC_Nap_Et2.m, TC_Nap_Et2.h,
    # TC_cad.cai,
    # TC_iA.m1,TC_iA.m2,TC_iA.h1,TC_iA.h2,
    
    
    # s.ampaA, s.ampaB, s.nmdaA, s.nmdaB


for nupdt,trenorm in enumerate(stoppoints):
    h.frecord_init()
    if nupdt != 0: logging.info(" > resume simulations")
    while h.t < trenorm :h.fadvance()
    logging.info(" > Update at {}".format(trenorm) )
    if mth.check("/network/btdp/enable"): compute_corr(tprev,trenorm)
    if mth.check("/network/home/enable"): homeostasis(tprev,trenorm)
    save_anything(tprev,trenorm,nupdt)
    #Release memory and reinit recordings
    if mth.check("/sim/record/cont/volt") or mth.check("/sim/record/cont/cur") or mth.check("/sim/record/cont/meancur"):
        trec.resize(0)
    if mth.check("/FR/Overall"):
        for nid,n in enumerate(neurons):
            fsk           = array(n.spks)
            TotalFR[nid] += fsk[where(fsk > tprev)].shape[0]
    for n in neurons:
        n.spks.resize(0)
        if mth.check("/sim/record/cont/volt"):
            n.volt.resize(0)
            #logging.debug("resize voltage")
        if mth.check("/sim/record/cont/cur") or mth.check("/sim/record/cont/meancur"):
            if not mth.check("/block/syncon"):
                if mth["/network/syn/AMPA/p"] > 0.:
                    n.ampairec.resize(0)
                if mth["/network/syn/NMDA/p"] > 0.:
                    n.nmdairec.resize(0)
            if not mth.check("/block/gjcon"):
                for _,_,_,_,recigj in gj:
                    recigj.resize(0)
            if mth.check("/network/cx/enable"):
                if mth["/network/cx/AMPA/p"] > 0.:
                    n.cxampairec.resize(0)
                if mth["/network/cx/NMDA/p"] > 0.:
                    n.cxnmdairec.resize(0)
    tprev = trenorm
    logging.info(" > reinit vectors")

if mth.check("/network/btdp/enable"):
    compute_corr(tprev,nupdt)
save_anything(tprev,trenorm,nupdt+1)
if mth.check("/FR/Overall"):
    TotalFR = [ nspk*1000/h.t for nspk in TotalFR ]
    if type(mth["/FR/Overall"]) is str:
        with open(mth["/FR/Overall"],"a") as fd:
            fd.write(json.dumps(TotalFR)+"\n")
        logging.info(" > Overall Faring rate is saved into {}".format(mth["/FR/Overall"]) )
    else:
        mth["/FR/Overall"] = TotalFR
    logging.info(f" > Overall Firing rate : {TotalFR} spikes/second")
logging.info(" > saved final synaptic conductance into {}".format(xfile) )
logging.info("===             DONE               ===")
logging.info("======================================")
if mth.check("/sim/state/save"):
    with stkdata(mth["/sim/state/save"]) as sd:
        sd["hash"     ] = hashline
        sd["timestamp"] = timestamp
        sd["posxy"    ] = posxy
        sd["nprms"    ] = xnprms
        sd["gjcon"    ] = xgjcon if not mth.check("/block/gjcon") else None
        sd["syncon"   ] = xsyncon
        sd["gsyncond" ] = array([
            [c.weight[0], c.delay]
            for c in con
        ])
        sd["gsynstate"] = array([
            [c.weight[1], c.weight[2], c.weight[3]]
            for c in con
        ])
        
        if mth.check("/network/cx/enable"):
            sd["cxsynstate"] = array([
                [c.weight[0],c.weight[1], c.weight[2], c.weight[3], c.delay]
                for c in cxfeedback
            ])
        if mth.check("/network/trn/enable"):
            sd["trnsynstate"] = array([
                [c.weight[0],c.delay]
                for c in trnfeedback
            ])
    logging.info(" > States are saved into {}".format(mth["/sim/state/save"]))

if options.rc:
    mth["/CMD"]=" ".join(sys.argv)+"\n"

logging.info( "===           ANALYSIS             ===")
from dLGNanalysis import mkanalysis
mth = mkanalysis(mth=mth,hashline=hashline)
logging.info("===             DONE               ===")
logging.info("======================================")

if not mth.check("/Figures/enable"): 
    if not options.rd in 'None . _ :'.split() :
        if options.rm is not None :
            stkdb(options.rd).record(mth,options.rm,rechash=hashline)
            logging.info("======================================")
            logging.info("===     SimToolKit Data Base       ===")
            logging.info(" >  DataBase    : {}".format(options.rd) )
            logging.info(" >  HASH        : {}".format(hashline) )
            logging.info(" >  Time Stamp  : {}".format(timestamp) )
            logging.info(" > MODEL PREFIX : {}".format(mth["/sim/timestamp"] ) )
            logging.info("===Has been recorded with no figures===")
        else:
            logging.warning("Figures and GUI are disabled but message for DB was not provided")
            logging.warning("EXIT without stkdb recording")
    else:
        logging.warning("SKIP stkdb recording")
    exit(0)

logging.info( "===            GRAPHS              ===")    
from dLGNgraphs import mkgraphs, savegraphs
(f1,f2,f3,f4,f5,f6),(f1data,f2data,f3data,f4data,f5data,f6data) = mkgraphs(mth=mth,hashline=hashline)
logging.info("===             DONE               ===")
logging.info("======================================")

if mth.check("/sim/Belly"):
    print("\a")
    time.sleep(5)


# STKDB record
if options.rm is not None:
    stkdb(options.rd).record(mth,options.rm,rechash=hashline)
    logging.info("======================================")
    logging.info("===     SimToolKit Data Base       ===")
    logging.info(" > DataBase     : {}".format(options.rd) )
    logging.info(" > HASH         : {}".format(hashline) )
    logging.info(" > Time Stamp   : {}".format(timestamp) )
    logging.info(" > MODEL PREFIX : {}".format(mth["/sim/timestamp"] ) )
    logging.info(" > MESSAGE      : {}".format(options.rm) )
    if mth.check("/Figures/STKDB-Record"):
        if not f1data is None:
            stkdb(options.rd).setmm(hashline,"Connectivity",f1data) 
            logging.info(" >  Figure 1     : Connectivity" )
        if not f2data is None:
            stkdb(options.rd).setmm(hashline,"Raster",f2data) 
            logging.info(" >  Figure 2     : Raster" )
        if not f3data is None:
            stkdb(options.rd).setmm(hashline,"Voltage",f3data) 
            logging.info(" >  Figure 3     : Voltage" )
        if not f4data is None:
            stkdb(options.rd).setmm(hashline,"Currents",f4data) 
            logging.info(" >  Figure 4     : Currents" )
        if not f5data is None:
            stkdb(options.rd).setmm(hashline,"Correlation",f5data) 
            logging.info(" >  Figure 5     : Correlation" )
        if not f6data is None:
            stkdb(options.rd).setmm(hashline,"Spectrum",f6data) 
            logging.info(" >  Figure 6     : Spectrum" )
    logging.info("===      Has been recorded         ===")
    rec = None
else:
    from simtoolkit import __config__
    if   "/STKDB/editor" in __config__.stk_config:
        editor = __config__.stk_config["/STKDB/editor"]
    elif "/GENERAL/editor" in __config__.stk_config:
        editor = __config__.stk_config["/GENERAL/editor"]
    else:
        editor = "gedit"
    #DB>>
    # print(editor)
    #<<DB
    rec = {
        "hash"        : hashline,
        "timestamp"   : timestamp,
        "tree"        : mth.methods,
        'messagefile' : ".stkdb-"+hashline+".msg"
    }
    with open(rec['messagefile'],"w") as fd:
        fd.write("\n\n#HASH:{} TIMESTAMP:{}\n#Please enter a message for this simulation here.\n#Lines starting with '#' will be ignored.\n#An empty message aborts the database record. \n".format(
            hashline,timestamp) )
    rec['message-timestamp'] = os.stat(rec['messagefile']).st_mtime
    os.system( editor + " " + rec['messagefile'] + " 1>/dev/null 2>/dev/null &")

        
if mth.check("/Figures/X-term"):

    savegraphs(mth,f1,f2,f3,f4,f5,f6)
    if not rec is None:
        logging.error("Cannot record into STKDB - there is no message and GUI is killed")
        exit(1)
else:
    show()

if rec is not None:
        nstp = os.stat(rec['messagefile']).st_mtime
        if nstp == rec['message-timestamp']:
            os.remove(rec['messagefile'])
            logging.error("----------------------------------------------------")
            logging.error("--- Cannot record stkdb. No message was provided ---")
            logging.error("----------------------------------------------------")        
            raise ValueError("Cannot record stkdb: No message was provided")
        fsize = os.path.getsize(rec['messagefile'])
        with open(rec['messagefile']) as fd:
            rec["message"] = fd.read(fsize)
        os.remove(rec['messagefile'])
        rec["message"] = re.sub(r"\r", r"",\
                                re.sub(r"#.*\n",r"",rec["message"]) 
                        ).strip(' \t\n\r')
        stkdb(options.rd).record(mth,rec["message"],rechash=rec["hash"],timestamp=rec["timestamp"])
        logging.info("======================================")
        logging.info("===     SimToolKit Data Base       ===")
        logging.info(" >  DataBase     : {}".format(options.rd) )
        logging.info(" >  HASH         : {}".format(rec["hash"]) )
        logging.info(" >  Time Stamp   : {}".format(rec["timestamp"]) )
        logging.info(" >  MODEL PREFIX : {}".format(mth["/sim/timestamp"] ) )
        
        if mth.check("/Figures/STKDB-Record"):
            if not f1data is None:
                stkdb(options.rd).setmm(rec["hash"],"Connectivity",f1data) 
                logging.info(" >  Figure 1     : Connectivity" )
            if not f2data is None:
                stkdb(options.rd).setmm(rec["hash"],"Raster",f2data) 
                logging.info(" >  Figure 2     : Raster plot and firing rates" )
            if not f3data is None:
                stkdb(options.rd).setmm(rec["hash"],"Voltage",f3data) 
                logging.info(" >  Figure 3     : Voltages " )
            if not f4data is None:
                stkdb(options.rd).setmm(rec["hash"],"Currents",f4data) 
                logging.info(" >  Figure 4     : Currents" )
            if not f5data is None:
                stkdb(options.rd).setmm(rec["hash"],"Correlation",f5data) 
                logging.info(" >  Figure 5     : Correlation" )
            if not f6data is None:
                stkdb(options.rd).setmm(hashline,"Spectrum",f6data) 
                logging.info(" >  Figure 6     : Spectrum" )
        logging.info("===      Has been recorded         ===")

logging.info("======================================")
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    
