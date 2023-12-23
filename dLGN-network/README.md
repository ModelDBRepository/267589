# dLGN model at P7-P10

Before running any simulations, please compile NEURON modules by the command
```
nrnivmodl lmods mods
```

Launch the `dLGNnetwork.py` script with or without additional arguments that alter parameters to run a simulation.
The complete list of command line arguments is given below.

## Convergence Figure 2
To replicate the full simulations for Figure 2 on an HPC computer, use SLURM script `SLURM-scripts/converegence.sbatch`

```
cp SLURM-scripts/converegence.sbatch .
sbatch -a 1-9 converegence.sbatch
```

Just to plot results from the cumulative database, run `convergence-reader.py` with the database.
For NMDA+AMPA mixture 

```
python convergence-reader.py -l homeostasis-G-CONV-TFR0.50-SIGMAXX-NMDA.json 
```

For AMPA only

```
python convergence-reader.py -l homeostasis-G-CONV-TFR0.50-SIGMAXX-AMPA.json 
```

## TRN inhibition Figure 4
To replicate full simulation for Figure 3 on HPC computer use SLURM script `SLURM-scripts/trn-scan.sbatch`
```
cp SLURM-scripts/trn-scan.sbatch .
sbatch -a 0-65 trn-scan.sbatch
```
To plot results from the cumulative database, run `trn-scan-reader.py` with the database.
For NMDA+AMPA mixture 
```
python trn-scan-reader.py -l homeostasis-G-CONV-TRN-TFR0.50-NMDA.json -M 2.3
```

## CTX excitation and TRN inhibition Figure 5
To replicate the full simulations for Figure 4 on an HPC computer, use SLURM script 'SLURM-scripts/dLGNnetwork-as-cortical-input.sbatch` and one of two setting files.
Because overall simulation takes about 300 days on 16 nodes, 40 core in each node, we used Monte-Carlo sampling, which runs in two batches
```
for i in SLURM-scripts/dLGNnetwork-as-cortical-input.sbatch SLURM-scripts/homeostasis-G-CONV-TRN-CXT-TFR1.00-Nxx-Cxxx-20220816-100511.sbatch SLURM-scripts/homeostasis-G-CONV-TRN-CXT-TFR1.00-Nxx-Cxxx-20220816-100545.sbatch
do
    cp $i .
done
sbatch -a 0-15 dLGNnetwork-as-cortical-input.sbatch homeostasis-G-CONV-TRN-CXT-TFR1.00-Nxx-Cxxx-20220816-100511.sbatch
sbatch -a 0-15 dLGNnetwork-as-cortical-input.sbatch homeostasis-G-CONV-TRN-CXT-TFR1.00-Nxx-Cxxx-20220816-100545.sbatch
```

To plot results from the cumulative database, run `cxt-trn-motecarlo-reader.py` with the database.
```
python cxt-trn-motecarlo-reader.py -l homeostasis-G-CONV-TRN-CXT-TFR1.00-vX.json --cor-minmax 0.6 -I
```


## Files and directories here

|File or directory           | Description                                                                                                             |
|:---------------------------|:------------------------------------------------------------------------------------------------------------------------|
|dLGNnetwork.py              | The main script to run simulations for Figure 2, 4, and 5                                                               |
|dLGNanalysis.py             | collection of tools to analyze simulation results                                                                       | 
|dLGNgraphs.py               | graphical unities                                                                                                       | 
|simtoolkit                  | module for support manipulation with model parameters and storage for bulky results (should be on GitHub and PyPI soon) |
| mods                       | NEURON modules for TC neuron                                                                                            |
| lmods                      | NEURON modules for synapses and vector activation                                                                       |
|SLURM-scripts               | scripts to run simulations on HPC                                                                                       |
|convergence-reader.py       | reader for results of converegence.sbatch script                                                                        |
|homeostasis-G-CONV-TFR0.50-SIGMAXX-NMDA.json | database with cumulative results of NMDA+AMPA run                                                      |
|homeostasis-G-CONV-TFR0.50-SIGMAXX-AMPA.json | database with cumulative results of AMPA only run                                                      |
|trn-scan-reader.py          | reader for results of trn-scan.sbatch script                                                                            |
|homeostasis-G-CONV-TRN-TFR0.50-NMDA.json     | database with cumulative results of TRN run                                                            |
|cxt-trn-motecarlo-reader.py | reader for results of dLGNnetwork-as-cortical-input.sbatch script                                                       |
|homeostasis-G-CONV-TRN-CXT-TFR1.00-vX.json   | database with cumulative results of CTX-TRN run                                                        |


---

## The full list of command line arguments for the main script
```
$python dLGNnetwork.py --help

dLGN network desynchronization at P7-P10
Ruben Tikidji-Hamburyan GWU 2020-2022


Usage: python dLGNnetwork.py [options] [parameters]

Any model parameter can be altered by /parameter_name=parameter_value in the command line

Options:
  -o RD, --stkdb-record=RD
                        Record the simulation in database (default
                        dLGNnetwork.stkdb)
  -m RM, --stkdb-message=RM
                        Supply database record with a massage. Useful when run
                        scripts (default None)
  -c, --stkdb-cmd       Add end command line to the data base (doesn't change
                        model hash sum)'
  -L LG, --log=LG       Output log to the file (default on the screen)
  -l LL, --log-level=LL
                        Level of logging may be CRITICAL, ERROR, WARNING,
                        INFO, or DEBUG (default INFO)
  -h, --help            Print this help

Parameters:
/network/nprms/db               = 'P07-selected-checked-gmin.json'
                                : file with neuron parameter database

/network/nprms/lst              = 'models'
                                : variable with list of parameters

/network/nprms/gmin             = 'gsynmin'
                                : variable with minimal conductance

/network/nprms/threshold        = 0.
                                : spike threshold

/network/geom/shape             = 'H'
                                : H-hexagonal or S-square

/network/geom/x                 = 7
                                : number of columns

/network/geom/y                 = 16
                                : number of rows

/network/annoying_hetero        = True
                                : If set True, it guarantees that all neurons in the population are different.   For this
                                : option, one needs a database bigger than network size.

/network/gj/geom/p              = 0.3
                                : gap junction probability

/network/gj/geom/unit           = 'n'
                                : if 'n' - /network/gj/geom/p probability of connection per neuron.  if 'c' -
                                : /network/gj/geom/p is probability of connection per pear of neurons      within maxd
                                : distance  if 'o' - /network/gj/geom/p is average number of GJ per neuron.

/network/gj/geom/maxd           = 1.5
                                : gap junction max distance

/network/gj/geom/mind           = None
                                : gap junction min distance

/network/gj/geom/dir            = None
                                : gap junction direction (random if None)

/network/gj/r                   = 600.
                                : gap junction resistance.  2022/02/04:  For current neuron database this resistance
                                : produces spikelets with  dV = 1.7 +- 0.22  mV and absolute range for all neurons
                                : [0.95,2.8] mV,  Coupling coefficients  mean = 0.4+-0.077 range=[0.087,0.58] aren't
                                : Compatible with VBN coupling Lee et al. 2010, but spikelet   amplitude is similar to
                                : spikelets in cat LGN Hughes et al. 2002

/network/syn/gsyn               = None
                                : synaptic conductance:   if positive - set for everyone,   if negative - set the
                                : portion of minimal synaptic conductance for a neuron,  if None set to 1/3 of the
                                : minimal synaptic conductance for each neuron.

/network/syn/rand               = False
                                : If ture - gsyn randomly init between 0 and /syn/gsyn value

/network/syn/prenorm            = True
                                : If true the total synaptic conductance will be set to /syn/gsyn value for   each
                                : neuron in the **beginning**!   It is active only in model building. For dynamical
                                : normalization   see /network/btdp

/network/syn/geom/unit          = 'N'
                                : Pattern of synaptic connectivity: 
                                :  'o' - one-to-one creates only one connection for each rGC to a closest LGN cell.
                                :  'a' - all-to-all connections: each rGC connects all dLGN cells. This is the best configuration for btdp. 
                                :        You can use /network/syn/sig2gsyn to create a Gaussian distributions of weights  
                                :  'e' - exponential distribution uses /network/syn/geom/pmax for maximum probability and
                                :        /network/syn/geom/sig for sigma.
                                :  'E' - same as e but distance computed from the closets rGC 
                                :  'g' - Gaussian distribution. it uses /network/syn/geom/pmax for maximum probability and
                                :         /network/syn/geom/sig for sigma.
                                :  'G' - same as g but distance computed from the closets rGC
                                :  'r' - random distribution 
                                :  'n' - random number between /network/syn/geom/nmin and /network/syn/geom/nmax for each TC is generated.
                                :         rGC are picked randomly
                                :  'c' - connect to closets (but not one) rGC  
                                :  'N' - same as n butcloset rGC are picked
                                :  ADD HERE MORE IF NEEDED!

/network/syn/geom/pmax          = None
                                : peak of synaptic probability for exponential or Gaussian distributions.

/network/syn/geom/sig           = None
                                : sigma for exponential or Gaussian distributions.

/network/syn/geom/nmin          = 7
                                : minimum of rGC connection per TC

/network/syn/geom/nmax          = 20
                                : maximum of rGC connection per TC

/network/syn/sig2gsyn           = None
                                : sigma for create Gaussian distributions of weights with distance

/network/syn/AMPA/p             = 1
                                : portion of AMPA conductance

/network/syn/AMPA/tau1          = 1.
                                : AMPA rising time constant

/network/syn/AMPA/tau2          = 2.2
                                : AMPA falling time contant From Chen & Regehr 2000 Table 1 P10-P14  Inconsistent with
                                : Hauser et al. 2014 AMPA $\tau_d \approx 5.47$ ms

/network/syn/NMDA/p             = 2.25
                                : portion of NMDA conductance  /AMPA/p and /NMDA/p are computed from Shah & Crair 2008
                                : as followed:  For _P6–P7_ : $i_{AMPA}/i_{NMDA} = \beta_{P7} =0.78 \pm 0.09$ (peak-to-
                                : peak)  comparable with $\beta_{P10} = 0.5 \pm 0.1$ from Chen & Regehr 2000  for
                                : voltage clamp $i_{vl}=g_{vl}*(E-V_{vl})$ where $E=0$ reversal potential  for NMDA and
                                : AMPA, and $v_{VL}$ potential for voltage clamp.  $g_{vl}=i_{vl}/v_{vl}$ conductance
                                : $\frac{g_{AMPA}}{g_{NMDA}}=\frac{i_{AMPA}}{i_{NMDA}}
                                : \frac{\Delat_{NMDA}}{\Delat_{AMPA}}$,  where $\Delat_{NMDA}$ and $\Delat_{AMPA}$ are
                                : differences between   holding potentials and the reversal potential for NMDA and AMPA
                                : currents  $\frac{\Delat_{NMDA}}{\Delat_{AMPA}}$ = 40 mV / 70 mV = 0.57
                                : $\frac{g_{NMDA}}{g_{AMPA}} = \frac{1}{0.57 \beta_{P7}} \approx 2.25$  Note that Dilger
                                : et al. 2015 estimated $\beta_{P10} \approx 1$ which  give /NMDA/p=1/0.57$\approx
                                : 1.75$.  The value from from Chen & Regehr 2000 $\beta_{P10} = 0.5 \pm 0.1$  gives
                                : /NMDA/p=1/(0.57*0.5)$\approx 3.5$.

/network/syn/NMDA/tau1          = 1.
                                : NMDA rising time constant

/network/syn/NMDA/tau2          = 150.
                                : NMDA falling time contant From Chen & Regehr 2000 Table 1 P10-P14  Consistent with
                                : Dilger et al 2015

/network/syn/ppr_u0             = 0.3
                                : sets presynaptic single spike depression  it's adjusted to obtain paired-pulse ratio
                                : 0.73   From Chen & Regehr 2000 Table 1 P10-P14

/network/syn/toneExc            = None
                                : Conductance for tonic excitation (None to block)

/network/syn/toneInh            = None
                                : Conductance for GABA_B receptors (None to block)

/network/file                   = 'dLGN-network.stkdata'
                                : save/read network configuration to/from this file

/network/load                   = True
                                : read network from the file (if True) or from another file (if filename given)

/network/save                   = True
                                : save network to   the file (if True) or to   another file (if filename given)

/network/reload/nprms           = False
                                : sets specific record within the file from there neuron parameters will be    reread or
                                : the first one if True

/network/reload/gjcon           = False
                                : sets specific record within the file from there gap-junction connections list   will
                                : be reread or the first one if True

/network/reload/syncon          = False
                                : sets specific record within the file from there list of synaptic connections    will
                                : be reread or the first one if True

/network/reload/gsyncond        = False
                                : sets specific record within the file from there list of synaptic conductance   will be
                                : reread or the first one if True

/network/reset/nprms            = False
                                : reset neuron parameters

/network/reset/gjcon            = False
                                : resets gap junction connections

/network/reset/syncon           = False
                                : resets list of synaptic connections

/network/reset/gsyncond         = False
                                : resets list of synaptic conductances

/network/annoying_reload/nprms  = True
                                : If True and neuron parameters hash doesn't match it stops

/network/annoying_reload/gjcon  = False
                                : If True and gap junction connection list hash doesn't match it stops

/network/annoying_reload/syncon = True
                                : If True and synaptic connection hash doesn't match it stops

/network/annoying_reload/gsyncond = False
                                : If True and synaptic conductance list hash doesn't match it stops

/network/annoying_reload/btdp   = False
                                : If True and /btdp/continue and /record/file does not have gsyn with correct hash - it
                                : stops

/network/btdp/enable            = False
                                : Set it to true for activation btdp

/network/btdp/update            = 5000.
                                : update synaptic weights every # milliseconds.  if btdp is enable it resets
                                : /sim/record/interval

/network/btdp/normgsyn          = None
                                : Target level to which  ....

/network/btdp/normn             = 4
                                : strongest normn synapses are normalized, suppressing weaker synapses.

/network/btdp/synthr            = -0.05
                                : the threshold  below with synapse assumed to be silent  same as for /syn/normg :
                                : positive sets the absolute level for the threshold,  negative sets a relative to
                                : minimal synaptic conductance for each neuron threshold  and None sets all synapses
                                : active

/network/btdp/minact            = @/network/btdp/normn@
                                : threshold of minimal number of active connections  if the number of active synapses is
                                : below this number - it creates new random synapses.  **Note** if
                                : /network/btdp/synthr=None, this mechanism is disabled.

/network/btdp/frthr             = 0.1
                                : if max firing rate at given interval /network/btdp/update for any pre or postsyn
                                : below this value, correlations term of leaning rule will not computed.   **Note** if
                                : you set it in None, False, or below zero, correlation term will be compute  always -
                                : and two silent neurons will have very high correlation and ramp up connections.

/network/btdp/frkernel          = 25.
                                : kernel for smoothing firing-rate. Effectively, gaussian kernel low-pass  frequencies 4
                                : time lower than kernel size.  Butts et al 1999, computed minimal jitter to perturb
                                : spacial information around  100 ms, so ~25ms kernel should be OK.

/network/btdp/frsmwidth         = @/network/btdp/frkernel@*10.
                                : one-side width of smoothing vector for firing-rate

/network/btdp/continue          = True
                                : reads last update from record and reset weights

/network/home/enable            = False
                                : Set it to true to activate homeostasis

/network/home/update            = 120000.
                                : update synaptic weights every # milliseconds.  if btdp is enable it will be set to
                                : /sim/btdp/update  if btdp is not enable, /home/update resets /sim/record/interval

/network/home/tau               = 60000.
                                : homeostasis time constant in ms ~10 sec

/network/home/target_fr         = 0.5
                                : Target firing rate in spikes/sec  from Murata & Colonnese 2018 Figure 5G1, it should
                                : be ~ 1 spike/sec, but  with blocked cortex it decreases ~50% Murata & Colonnese 2016
                                : Fig 3.

/network/home/slope             = 1.
                                : sloe slope of activation function is spikes/sec

/network/home/gmax              = -2.
                                : maximal synaptic conductance (notation is the same as in /network/syn/gsyn)

/network/home/gmin              = 0.0
                                : minimal synaptic conductance

/network/home/delta             = -0.2/111
                                : increment/decrement of synaptic weights

/network/home/continue          = True
                                : reads last update from the record and reset weights

/network/cx/enable              = False
                                : Set it to true for enabling **cortical feedback**

/network/cx/delay               = 15.
                                : delay for spike travel to cortex and back

/network/cx/gsyn                = -0.005
                                : synaptic conductance. ATTENTION! If negative it set ratio to mean RGC input

/network/cx/AMPA/p              = @/network/syn/AMPA/p@
                                : portion of AMPA conductance

/network/cx/AMPA/tau1           = @/network/syn/AMPA/tau1@
                                : AMPA rising time constant

/network/cx/AMPA/tau2           = @/network/syn/AMPA/tau2@
                                : AMPA falling time constant

/network/cx/NMDA/p              = @/network/syn/NMDA/p@
                                : portion of NMDA conductance

/network/cx/NMDA/tau1           = @/network/syn/NMDA/tau1@
                                : NMDA rising time constant

/network/cx/NMDA/tau2           = @/network/syn/NMDA/tau2@
                                : NMDA falling time constant

/network/cx/ppr_u0              = 0.7
                                : sets presynaptic PP depression

/network/trn/enable             = False
                                : Set it to true for enabling **TRN inhibitory feedback**

/network/trn/delay              = 15.
                                : delay for spike travel to TRN and back

/network/trn/gsyn               = -0.005
                                : synaptic conductance (same as /syn/gsyn)

/network/trn/tau1               = 5.
                                : GABA A rising time constant

/network/trn/tau2               = 50.
                                : GABA A falling time constant

/network/trn/e                  = -70.
                                : inhibitory reversal potential

/block/gjcon                    = False
                                : Block gap junction

/block/syncon                   = False
                                : Block synapses

/sim/temperature                = None
                                : model temperature in celsius,  if None it will try to find 'temperature' variable in
                                : the neuron database

/sim/Tmax                       = 600000.
                                : Simulation duration in ms. If negative (any negative number)  it defines by
                                : stimulation recording

/sim/record/interval            = 60000
                                : record and clean buffers every /sim/record/interval milliseconds

/sim/record/file                = 'dLGN-record.stkdata'
                                : save everything into this file

/sim/record/save                = True
                                : enable any recordings

/sim/record/spike               = True
                                : record spikes

/sim/record/gsyn                = False
                                : if a number records synaptic weights every n updates,   if true records synaptic
                                : weights every update.  Works only if btdp or homeostasis are enabled

/sim/record/cont/dt             = 0.5
                                : time step for continues recordings

/sim/record/cont/cur            = False
                                : record currents

/sim/record/cont/volt           = True
                                : record voltages

/sim/record/cont/meancur        = True
                                : record current averaged through population

/sim/parallel                   = True
                                : sent number of cores or True for auto-detection

/sim/Belly                      = False
                                : ring the bell when simulation finishes

/sim/timestamp                  = time.strftime("%Y%m%d-%H%M%S")
                                : simulation time-stamp

/stim/iapp                      = None
                                : inject constant current. Current is slowly ramping up first 1000 ms

/stim/rGC/file                  = "../experimentaldata/Maccione2014_P9_29March11_control_SpkTs_bursts_filtered.h5"
                                : reads positions and spikes of RG from this file

/stim/rGC/groups                = [                     824,825,826,827,828,829,830,831, 849,850,851,852,853,854,855,856, 875,876,877,878,879,880,881,882, 905,906,907,908,909,910      ]
                                : recorded rGC IDs which will be used   for network stimulation  if more than one neuron
                                : on one electrode  spike can be lumped together by  putting IDs into tuple
                                : (121,122,123)  for example

/stim/trecstart                 = 140000
                                : remove first milliseconds of the recording.

/stim/shuffle                   = False
                                : Shuffles spikes between electrodes

/stim/uniform                   = False
                                : uniform distribution of the same number of spikes over each electrode

/stim/stimfile                  = None
                                : used npy file with array (n,2) : [spike time,rGC]    instead of spikes in the original
                                : hd5 file

/stim/poisson                   = None
                                : Generate Poisson firing rate with given rate

/FR/window                      = 100
                                : windows size for filtering firing rate

/FR/kernel                      = 50.
                                : Gaussian kernel to smooth FR

/FR/kernelwidth                 = @/FR/kernel@*5
                                : 1/2 width of smoothing kernel  (it is half, because +- boundary). It is set to 5 sigma
                                : If /kernel and /kernelwidthare gaussian kernel is used to smooth 1ms bin histogram,
                                : otherwise histogram with /FR/window will be plotted

/FR/CorrDist/positive           = 20.
                                : Size of positive Gaussian kernel to smooth firing rate   for computing  Correlation
                                : distribution

/FR/CorrDist/negative           = @/FR/CorrDist/positive@*4
                                : size of negative Gaussian kernel

/FR/CorrDist/window             = @/FR/CorrDist/negative@*5
                                : 1/2 of smoothing window size

/FR/CorrDist/bins               = False
                                : set a number of bins in correlation distribution (must be int);   default 201

/FR/CorrDist/left               = False
                                : left boundary of histogram range; default -1.

/FR/CorrDist/right              = False
                                : right boundary of histogram range; default 1.

/FR/Spectrum/filter-off         = False
                                : set False to remove filtration

/FR/Spectrum/Fmax               = 39.
                                : Maximal frequency (Hz)

/FR/Spectrum/dt                 = 1.
                                : Histogram bin-size in ms

/FR/Spectrum/kernel             = 20.
                                : Gaussian kernel to smooth FR (different to from the above to have high frequency
                                : components)

/FR/Spectrum/width              = @/FR/Spectrum/kernel@*5
                                : 5 sigma for 1/2 of the window (n /FR/Spectrum/dt time units)

/FR/Overall                     = True
                                : computes overall FR for a run. If string is given, it jsones the list of overall FR
                                : into a file with this name.

/Figures/enable                 = True
                                : if False will not generate figures and exit  it will make a DB record only if -m
                                : message is provided and the record won't have figures

/Figures/X-term                 = False
                                : saves all figures into a file with this prefix. If False - shows on screen

/Figures/FigSize                = (21,16)
                                : XxY size of figures

/Figures/FigLimit               = None
                                : If any of /sim/record/cont/{cur,volt} is set True, will show every # neuron, and all
                                : if None

/Figures/STKDB-Record           = True
                                : Add figures into record

/Figures/connectivity/flat      = False
                                : if True makes 2D plot of connectivity instead of 3D

/Figures/disable/connectivity   = False
                                : set True to disable connectivity plot

/Figures/disable/volt           = False
                                : set True to disable voltage plot

/Figures/disable/cur            = False
                                : set True to disable current plot

/Figures/disable/cordist        = False
                                : set True to disable correlation distribution plot

/Figures/disable/spectrum       = False
                                : set True to disable spectrum plot

/Figures/disable/2dspiking      = True
                                : set False to activate interactive figure which can generates movies

/Figures/formats                = 'jpg svg'.split()
                                : list of figures formats

/analysis/connectivity          = True
                                : statistics of RGC to LGN connectivity

/analysis/gj                    = True
                                : statistics of number GJ per neuron

```
