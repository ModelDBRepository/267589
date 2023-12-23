# Neuron Optimization Pipeline

The main code for the optimization procedure is in the  `pyneuronautofit` directory for local usage. 
For permanent installation, use the `pip(3)` command.
```
pip3 install pyneuronautofit (--user)
```
The flag `--user` is needed if you don't have root/sudo privileges and what to install `pyneuronautofit` in the user directory.

Before launching optimization, you have to compile NEURON modules
```
nrnivmodl mods
```

To run NSGA2 optimization procedure for the given example of the recorded neuron, use the command
```
python -m pyneuronautofit -A NSGA2  -m OV -G 1536 -P 240 -E 0  -U 0 -c 3 -t -10 -k ../experimentaldata/P07-04.20205021-mask.json ../experimentaldata/P07-04.20205021.abf
```

To run KAMOGA optimization procedure for the same example, use the command
```
python -m pyneuronautofit -A K      -m OV -G 1536 -P 240 -E 30 -U 0 -c 3 -t -10 -k ../experimentaldata/P07-04.20205021-mask.json ../experimentaldata/P07-04.20205021.abf
```


## The complete list of command line flags is given below.
```
python -m pyneuronautofit --help
Usage: -m pyneuronautofit [flags] input_file_with_currents_and_target_stats (abf,npz,or json)

Options:
  -h, --help            show this help message and exit

  Fitting:
    Parameters related to Evolutionary Optimization

    -A ALGOR, --algorithm=ALGOR
                        Algorithm for multiobjective evaluation. It can be:
                        Krayzman - for Krayzman's fitness weighting; NSGA2 -
                        for Pareto nondominate selection; Max - for max scaled
                        summation; PositiveCor - positive correlation (the same
                        as Krayzman's procedure, but with the goal of making all
                        correlations positive). An algorithm can be given by first
                        letter K, N, M or P correspondingly. (Default is K)
    -P PSZ, --population-size=PSZ
                        population size (default 256). If it is a negative
                        number: the population size is the length of the
                        fitness vector multiple by the absolute value of this
                        option.
    -G NGN, --number-generation=NGN
                        number of generations (default 256)
    -E ELITES, --number-elites=ELITES
                        number of elites in the replacement (default 32)
    -L, --off-log-scale
                        enable log scaling
    -I INITPOP, --init-population=INITPOP
                        file with a set of an initial population
    -N KRTHR, --Krayzman-threshould=KRTHR
                        The threshold for Krayzman's iteration procedure of
                        weights adaptation (default 0.05)
    -U UPDATE, --scales-update=UPDATE
                        vector length * this scale is the number of fitness
                        vectors before updating Krayzman's weights or max
                        scalers (default 10)
    -y, --norm-space    normalize space under the curve
    -H, --hold-weights-normalization
                        hold weights without normalization in iteration
                        procedure (default disable)
    -b BOUNDKGA, --bound-Krayzman-weights=BOUNDKGA
                        bound weights by [1/x,x] (default disable)
    -M MRATE, --mutation-rate=MRATE
                        Basic mutation rate (default 10%%)
    -S AMSLOPE, --adaptive-mutation-slope=AMSLOPE
                        Adaptive mutation slope
    -Q VPVSIZE, --v-dvdt-hist-size=VPVSIZE
                        v dv/dt histogram size (default 12)
    -J, --inJect-elits  enable dynamic elits

  Model:
    Conditions for model running and evaluation

    -m EMODE, --eval-mode=EMODE
                        mode for evaluation T-spike time, S-spike shape,
                        U-subthreshold voltage dynamics, W-spike width, R -
                        resting potential, L - post-stimulus tail, M - voltage
                        stimulus statistics, A - average spike shape, N -
                        number of spikes (default RAMN)
    -k EMASK, --eval-mask=EMASK
                        mask to limit analysis
    -c ESPC, --spike-count=ESPC
                        number of spikes for evaluation (2)
    -t ETHSH, --spike-threshold=ETHSH
                        spike threshold (default 0.)
    -l ELEFT, --left-spike-samples=ELEFT
                        left window of a spike (default 70)
    -r ERGHT, --right-spike-samples=ERGHT
                        right window of a spike (default 140)
    -q TEMP, --temperature=TEMP
                        temperature (default 35)
    -z SPWTGH, --spike-Zoom=SPWTGH
                        if positive -- the absolute weight of voltage diff during
                        spike; if negative -- related scaler
    -e, --collapse-diff
                        Collapse difference between a model and data in a
                        vector with size = number of tests (i.e. for  -m RAMNT
                        the diff vector will be length 5)

  Run:
    Options for entire EC running and logging

    -n NTH, --number-threads=NTH
                        number of threads (default None - autodetection)
    --dt=SIMDT          if positive absolute simulation dt; if negative scaler
                        for recorded dt
    -v LL, --log-level=LL
                        Level of logging.[CRITICAL, ERROR, WARNING, INFO, or
                        DEBUG] (default INFO)
    -u, --log-to-screen
                        log to screen
    -Z, --Krayzman-debug
                        enable debug dump for adaptation weight
    -p NCH, --printed-checkpoints=NCH
                        print out checkpoints every # generation (do not print
                        out if negative)
    -d DCH, --dump-checkpoints=DCH
                        dump out checkpoints into checkpoint file every #
                        generation (do not dump out if negative, default 8)
    -i RITER, --iteration=RITER
                        adds iteration number to the runs stamp
    -a RSTEMP, --run-stamp=RSTEMP
                        Use this run stamp instead of generated
    --slurm-id=SLURMID  Add SLURM ID into timestamp
    --log-population    record population into log file
    --log-archive       record archive into log file
    --dry-run           exit after init everything

```


## Files and directories here

|File or directory | Description                                                                                                             |
|:-----------------|:------------------------------------------------------------------------------------------------------------------------|
|CheckSelection.py | validates models in the database |
|FinalCheck.py     | plots current-clamp models vs neuron for human evaluation|
| search-init.py   | searches initial steady-states for all models in the database |
|                  |`python search-init.py   <input database>  <output database>`|
|search-synmin-v2.py | searches for minimal synaptic conductance for all models in the database |
|                  |`python search-synmin-v2.py -A 'linspace(1.,0.,41).tolist()' -N 'linspace(0.,1.,41).tolist()' -G 0.4 -a 1e-4  <database>` |
|plot-parmdist.py  | plots parameters kde (Figure 1B) and PCA (Figure 1 -- Figure Supplement 1) for the database |
|                  |`python plot-parmdist.py ../P07-selected-checked-gmin-20220921.json`
|  mods            | directory with NEURON mod file for ion channels and calcium dynamics|


