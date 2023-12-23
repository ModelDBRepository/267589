import sys, os, json, logging
from numpy import *
#from cell import dLGN
#from cNADltb import cNADltb as dLGN
import importlib
from neuron import h

    
def worker(nid,ampap,nmdap,xshow=False):
    #  (nid)
    parameters = models[nid]["parameters"]

    SS = 10000.
    
    nrns = [ dLGN() for x in range(11) ]
    for n in nrns:
        for p in parameters:
            try:
                exec("n."+p+"= parameters[p]")
            except BaseException as e:
                sys.stderr.write(f"Cannot set parameter {p} to {parameters[p]}:\n\t{e}\n")
                exit(1)
    
    hns = h.NetStim(0.5, sec=nrns[0].soma)
    hns.start    = SS
    hns.noise    = 0.
    hns.interval = 1.
    hns.number   = 1
    hsyn = [ h.AMPAandNMDAwithTone(0.5, sec = n.soma) for n in nrns ]
    for syn in hsyn:
        syn.AMPAt1  = 1.
        syn.AMPAt2  = 2.2
        syn.AMPAp   = ampap
        syn.NMDAt1  = 1.
        syn.NMDAt2  = 150.
        syn.NMDAp   = nmdap
        syn.e       = 0.
        syn.GLUTg   = 0.
        syn.GABABg  = opts.g_gaba_b
        syn.gsynmod = 1.
        syn.u0      = 0.30
    # #DB>>
    # for syn in hsyn:
        # print(f"ampa t1 = {syn.AMPAt1}")
        # print(f"ampa t2 = {syn.AMPAt2}")
        # print(f"ampa P  = {syn.AMPAp}")
        # print(f"nmda t1 = {syn.NMDAt1}")
        # print(f"nmda t2 = {syn.NMDAt2}")
        # print(f"nmda P  = {syn.NMDAp}")
        # print(f"E       = {syn.e}")
        # print(f"GLUTg   = {syn.GLUTg}")
        # print(f"GABABg  = {syn.GABABg}")
        # print(f"gsynmod = {syn.gsynmod}")

    # #<<DB

    hnc = [ h.NetCon(hns, syn, sec = n.soma) for syn,n in zip(hsyn,nrns)]

    hst = [ h.Vector() for n in nrns ]
    hsc = [ h.APCount(0.5, sec= n.soma) for n in nrns ]
    for isc,sc in enumerate(hsc):
        sc.thresh = 0.
        sc.record(hst[isc])

    gmin0, gmin1 = opts.min_gsyn, opts.max_gsyn
    while abs(gmin1-gmin0) > opts.accuracy:
        gsynlist = linspace(gmin0, gmin1,11)
        for nc,g in zip(hnc,gsynlist):
            nc.delay = 0
            nc.weight[0] = g



        for n in nrns:
            for x in n.soma : x.v = -76.

            if 'init' in models[nid]:
                for var in models[nid]['init']:
                    varinit = models[nid]['init'][var]
                    try:
                        exec(f"n."+var+"= varinit")
                    except BaseException as e:
                        sys.stderr.write(f"Cannot set dynamic variable{var} into initical condition {varinit}:\n\t{e}\n")
                        exit(1)
        recs = []
        if xshow and len(recs) == 0:
            for n in nrns:
                rec = h.Vector()
                rec.record(n.soma(0.5)._ref_v)
                recs.append(rec)
                
            trec  = h.Vector()
            trec.record(h._ref_t)

        h.celsius = opts.temp
        h.finitialize()
        h.fcurrent()
        h.frecord_init()
        h.t = 0.
        while h.t < SS + 5000. :h.fadvance()

        if xshow:
            trec = array(trec)
            for recid,rec in enumerate(recs):
                plot(trec+recid*200,array(rec)+40.*recid,"-")
            show()
        gid1 = None
        for gid,(st,g) in enumerate(zip(hst,gsynlist)):
            if array(st).shape[0] != 0:
                gid1  = gid
                gmin1 = g
                break
        if gid1 is None or gid1 == 0:
            sys.stderr.write(f" > Neuron #{nid}: stuck! Solution outside the range[ {gmin0}, {gmin1} ]\n")
            return gmin1
        else:
            gmin0 = gsynlist[gid1-1]

    logging.info(f" > Neuron #{nid} minimal synaptic conductance for Pampa={ampap:0.3f} and Pnmda={nmdap:0.3f} is between {gmin0} and {gmin1} : "+\
        ("within accuracy" if gmin0 is not None and gmin1 is not None and abs(gmin1-gmin0) < opts.accuracy else "low accuracy") + \
        f" CONDITIONS: GABAB={opts.g_gaba_b} temperature={opts.temp}"
        ) 
    return gmin1

istuplist = lambda x: type(x) is tuple or type(x) is list
from optparse import OptionParser
oprs = OptionParser("USAGE: %prog [flags] input-json-file")
oprs.add_option("-n", "--neuron-id"   ,  dest="nid"     , default=None, type='int'  , help="Sets neuron ID")#,action="store_true")
oprs.add_option("-o", "--output"      ,  dest="output"  , default=None, type='str'  , help="Sets output json file. If if isn't set output is the same as imput")#,action="store_true")
oprs.add_option("-A", "--p-AMPA"      ,  dest="p_ampa",   default=None, type='str',   help="Pampa it can be a float number, or a list with all possible velues or tuple with linspace parameters")
oprs.add_option("-N", "--p-NMDA"      ,  dest="p_nmda",   default=None, type='str',   help="Pnmda it can be a float number, or a list with all possible velues or tuple with linspace parameters")
oprs.add_option("-G", "--max-gsyn"    ,  dest="max_gsyn", default=2e-1, type='float', help="Maximal synaptic conductance (defalut 200e-3)")
oprs.add_option("-g", "--min-gsyn"    ,  dest="min_gsyn", default=0.  , type='float', help="Minimal synaptic conductance (defalut 0)")
oprs.add_option("-a", "--accuracy"    ,  dest="accuracy", default=1e-3, type='float', help="Sets accuracy of the minimal gsyn detection (default is 1e-3)")
oprs.add_option("-X", "--show"        ,  dest="xshow",    default=False,              help="Shows one trial. For this option --p-AMPA and --p-NMDA should be set in float numbers",action="store_true")
oprs.add_option("-p", "--parallel"    ,  dest="parallel", default=os.cpu_count(),\
                                                                        type='int',   help="Number of cores/cpus to use")
oprs.add_option("-B", "--g-GABA-B"    ,  dest="g_gaba_b", default=0.,   type='float', help="Conductance GABA_B")
oprs.add_option("-T", "--temperature" ,  dest="temp"    , default=None,  type='float', help="temperature")

opts, args = oprs.parse_args()

logging.basicConfig(format='%(asctime)s:%(lineno)-6d%(levelname)-8s:%(message)s', level=logging.INFO )

if len(args) < 1:
    sys.stderr.write(f"USAGE: {sys.argv[0]} [flags] input-json-file \n")
    exit(1)

if opts.output is None:
    opts.output = args[0]

if opts.p_ampa is None:
    opts.p_ampa = linspace(0.,1.,11)
else:
    try:
        opts.p_ampa = eval(opts.p_ampa)
    except BaseException as e:
        sys.stderr.write(f"Cannot convert p-ampa={p_ampa} into numbers/lists :\n\t{e}\n")
        exit(1)
    if not istuplist(opts.p_ampa):
        opts.p_ampa = float(opts.p_ampa)
    elif type(opts.p_ampa) is tuple:
         opts.p_ampa = linspace(*opts.p_ampa).tolist()
if opts.p_nmda is None:
    opts.p_nmda = linspace(1.,0.,11)
else:
    try:
        opts.p_nmda = eval(opts.p_nmda)
    except BaseException as e:
        sys.stderr.write(f"Cannot convert p-ampa={p_ampa} into numbers/lists :\n\t{e}\n")
        exit(1)
    if not istuplist(opts.p_nmda):
        opts.p_nmda = float(opts.p_nmda)
    elif type(opts.p_nmda) is tuple:
         opts.p_nmda = linspace(*opts.p_nmda).tolist()

#gsynlist = around(linspace(0.,opts.max_gsyn,int(ceil(opts.max_gsyn/opts.accuracy))+1),int(-log10(opts.accuracy)+1)).tolist()

try:
    with open(args[0]) as fd:
        j = json.load(fd)
except BaseException as e:
    sys.stderr.write(f"Cannot read parameter database {args[0]}:\n\t{e}\n")
    exit(1)
if not "models" in j:
    sys.stderr.write(f"Cannot find \"models\" list in {args[1]}\n")
    exit(1)
models = [ m for m in j["models"] if m is not None ]

if not "module" in j:
    sys.stderr.write(f"Cannot find \"module\" to import in the file {args[1]}\n")
    exit(1)
try:
    mod  = importlib.import_module(j["module"])
except BaseException as e:
    mod=j["module"]
    sys.stderr.write(f"Cannot imoirt module {mod}:\n\t{e}\n")
    exit(1)
if not "cell" in j:
    sys.stderr.write(f"Cannot find \"cell\" name for object in the file {args[1]}\n")
    exit(1)
try:        
    dLGN = eval("mod."+j['cell'])
except BaseException as e:
    mod=j["module"]
    cel=j["cell"]
    sys.stderr.write(f"Cannot imoirt {cel} neuron from module {mod}:\n\t{e}\n")
    exit(1)

if opts.temp is None:
    if not "temperature" in j:
        sys.stderr.write(f"Temperature isn't given as an option -T and there is no \'temperature\' parameter in the database")
        exit(1)
    opts.temp = j["temperature"]
    
logging.info("Searching min conductance")
logging.info( " > model     = {}.{}".format(j["module"],j["cell"]))
logging.info(f" > database  = {args[0]}")
logging.info(f" > neuron    = {opts.nid}")
logging.info(f" > p nmda    = {opts.p_nmda}")
logging.info(f" > p ampa    = {opts.p_ampa}")
logging.info(f" > accuracy = {opts.accuracy}")
logging.info(f" > gsyn min = {opts.min_gsyn}")
logging.info(f" > gsyn max = {opts.max_gsyn}")
logging.info(f" > output   = {opts.output}")
logging.info(f" > GABA B   = {opts.g_gaba_b}")
logging.info(f" > temp     = {opts.temp} C")

if opts.xshow:
    if type(opts.p_nmda) is not float:
        sys.stderr.write(f"For -X or --show flags --p-NMDA must be a float number, {type(opts.p_nmda)} is given\n")
        exit(1)
    if type(opts.p_ampa) is not float:
        sys.stderr.write(f"For -X or --show flags --p-AMPA must be a float number, {type(opts.p_ampa)} is given\n")
        exit(1)
    if type(opts.nid) is not int:
        sys.stderr.write(f"For -X or --show flags neuron ID must be set by -i option, {type(opts.nid)} is given\n")
        exit(1)
    if opts.nid > len(models):
        sys.stderr.write(f"Neuron ID is too big, we have just {len(models)} models in the {args[0]} database\n")
        exit(1)
    from matplotlib.pyplot import *
    worker(opts.nid,opts.p_ampa,opts.p_nmda,xshow=True)
else:
    if type(opts.nid) is not int:
        allparam = [ [nid,pampa,pnmda] for nid in range(len(models))  for pampa,pnmda in zip(opts.p_ampa, opts.p_nmda) ]
    else:
        allparam = [ [nid,pampa,pnmda] for nid in range(opts.nid)     for pampa,pnmda in zip(opts.p_ampa, opts.p_nmda) ]
    logging.info(f" > TOTAL    = { len(allparam)}")
    import multiprocessing as mp
    pool = mp.Pool(processes=opts.parallel)
    
    result = [pool.apply_async(worker,prms) for prms in allparam ]
    pool.close()
    pool.join()
    result = [r.get() for r in result]

    j['gsynmin'] = [ (n-a)/(n+a) for a,n in zip(opts.p_ampa, opts.p_nmda) ]
    gmin = array(result)
    ntests = len(opts.p_ampa)
    gmin = gmin.reshape((gmin.shape[0]//ntests,ntests))
    logging.info(f" > gmin     = {gmin.tolist()}")
    
    for nid,gm in enumerate(gmin):
        j["models"][nid]['gsynmin'] = gm.tolist()
        j["models"][nid]['id']      = nid
    with open(opts.output,'w') as fd:
        fd.write("{\n")
        for n in j:
            if n == "models": continue
            fd.write(f"\t\"{n}\" : "+json.dumps(j[n])+",\n")
        fd.write(f"\t\"models\" :[ \n")
        if type(opts.nid) is not int:
            for m in j["models"]:
                if m is None : continue
                fd.write(f"\t\t{json.dumps(m)},\n")
        else:
            for m in j["models"][:opts.nid]:
                if m is None : continue
                fd.write(f"\t\t{json.dumps(m)},\n")
        fd.write(f"\t\t{json.dumps(None)}\n"+"\t]\n}")


