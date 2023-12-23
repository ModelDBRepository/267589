## Synaptic and circuit mechanisms prevent detrimentally precise correlation in the developing mammalian visual system

by _Ruben A. Tikidji-Hamburyan, Gubbi Govindaiah, William Guido, Matthew T. Colonnese_

eLife 2023; 12:e84333. DOI: https://doi.org/10.7554/eLife.84333.

### Required software
For any simulation in this record, one needs `Python`(version 3.9.9 and higher) and libraries `cython`, `numpy`, `scipy` and `matplotlib`.
```bash
$pip3 install --user numpy scipy matplotlib cython
```

Additional libraries:

|                  |                                         |
|:-----------------|:----------------------------------------|
|Figure 1          | `NEURON`, `pyabf` and `inspyred`        |
|Figure 2,4,5      | `NEURON`, `h5py`, and `neurodsp`        |

To install all libraries for all scripts, use a single command
```bash
$pip3 install --user numpy scipy matplotlib cython NEURON pyabf inspyred h5py neurodsp brian2
```




### Files, directories, and models in this record 

|File or directory           | Description                                                           |
|:---------------------------|:----------------------------------------------------------------------|
|[TC-fitting](https://senselab.med.yale.edu/modeldb/ShowModel?model=267589&file=/dLGN-decorrelation-2023/TC-fitting/README.html#tabs-2) | Fitting procedure and associated files for Figure 1 in the manuscript |
|[dLGN-network](https://senselab.med.yale.edu/modeldb/ShowModel?model=267589&file=/dLGN-decorrelation-2023/dLGN-network/README.html#tabs-2) | Thalamic network at P7-P10 for Figures 2, 4, and 5 in the manuscript  |
|experimentaldata            | an example of a neuron recording and mask file for the optimization as well as Maccione et al. 2014 recording from [_waverepo_ repository on GitHub](https://github.com/sje30/waverepo) | 
|[P07-selected-checked-gmin-20220921.json](https://github.com/rat-h/DevelopmentOfThalamocorticalNeurons) | A reduced, fully validated, and human-evaluated database of 286 models of thalamocortical neurons in visual LGN at P7-P10, enough to reproduce any results in the manuscript |

