#!/bin/sh
#SBATCH -o homeostasis-G-CONV-TRN-TFR0.50-N%02a.stdout
#SBATCH -e homeostasis-G-CONV-TRN-TFR0.50-N%02a.stderr
##MAIN>>
#SBATCH -t 13-23:59:59
#SBATCH -p defq -N 1
#<<<<<<
#DB>>
# SBATCH -t 4:00:00
# SBATCH -p debug-cpu -N 1
#<<<<
#SHORT>>
# SBATCH -t 23:59:59
# SBATCH -p short -N 1
#<<<<<<<

#SBATCH -J COV-TRN

module load gcc
module load openmpi/gcc/64/4.1.0
module load gsl/2.6
module load hdf5/1.10.5

PATH=$HOME/.local/bin:$HOME/bin:$PATH
LD_LIBRARY_PATH=$HOME/.local/lib:$LD_LIBRARY_PATH
export PATH LD_LIBRARY_PATH




date

TMPDIR="/tmp"
PREFIX="homeostasis-G"
KEYLET="CONV-TRN"
TIMESTAMP=$(date "+%Y%m%d-%H%M%S")
TRARGETFD="0.50"
PREFIX=$PREFIX-$KEYLET-TFR$TRARGETFD
SIMPRMS="/Figures/enable=False /sim/parallel=5"
worker(){
    #ARGS:
    #  Sim name
    #  CONVERGENCE
    #  TRN gsyn
    #  TRN delay
    PREFTMPST=$1 ; SIGMA=$2 ; TRNGSYN=-$3 ; TRNDLY=$4 

       
    for R in $(seq 0 9)
    do
       POSTFIX=R$R
       WORKPREFIX=$PREFTMPST-NMDA-$POSTFIX
    
       rm -f $WORKPREFIX.log $WORKPREFIX-blockTRN.log \
              $TMPDIR/$WORKPREFIX.stkdata $TMPDIR/$WORKPREFIX-simstate.stkdata \
              $TMPDIR/$WORKPREFIX-blockTRN.stkdata \
              $WORKPREFIX-blockTRN-FR.json $WORKPREFIX-FR.json \
              $PREFTMPST.stkdb
       python dLGNnetwork.py -l DEBUG -L $WORKPREFIX.log \
              -o $PREFTMPST.stkdb -m NMDA\ PREFIX:$PREFTMPST\ SIGMA:$SIGMA\ TRNGSYN:$TRNGSYN\ TRNDLY:$TRNDLY\ R:$R\ I:0 \
              $SIMPRMS /sim/record/cont=False \
              /network/load=False /network/save=False \
              /sim/Tmax=-1 \
              $NRNPRMS \
              /network/gj/geom/p=0 /block/gjcon=True $GJPRMS \
              /network/syn/geom/unit=\'G\' /network/syn/geom/pmax=1 /network/syn/geom/sig=float\($SIGMA\) \
              /network/syn/gsyn=-1. /network/syn/sig2gsyn=float\($SIGMA\) /network/syn/rand=False \
              /network/trn/enable=True /network/trn/gsyn=$TRNGSYN /network/trn/delay=$TRNDLY $TRNPRMS \
              /network/cx/enable=False \
              /network/home/enable=True  /network/home/continue=False /network/home/slope=0.05 /network/home/gmax=-10. /network/home/target_fr=$TRARGETFD \
              /sim/record/file=\'$TMPDIR/$WORKPREFIX.stkdata\' /sim/record/gsyn=True \
              /FR/Overall=\"$WORKPREFIX-FR.json\" \
              /sim/state/save=\'$TMPDIR/$WORKPREFIX-simstate.stkdata\' \
              || { echo "$WORKPREFIX FAILED I00"; exit 1 ; }

       let i=0
       while python FRchecker.py $WORKPREFIX-FR.json $TRARGETFD
       do
              let i=$i+1
              python dLGNnetwork.py -l DEBUG -L $WORKPREFIX.log \
                     -o $PREFTMPST.stkdb -m NMDA\ PREFIX:$PREFTMPST\ SIGMA:$SIGMA\ TRNGSYN:$TRNGSYN\ TRNDLY:$TRNDLY\ R:$R\ I:$i \
                     $SIMPRMS /sim/record/cont=False \
                     /network/load=False /network/save=False \
                     /sim/Tmax=-1 \
                     $NRNPRMS \
                     /network/gj/geom/p=0 /block/gjcon=True $GJPRMS \
                     /network/syn/geom/unit=\'G\' /network/syn/geom/pmax=1 /network/syn/geom/sig=float\($SIGMA\) \
                     /network/syn/gsyn=-1. /network/syn/sig2gsyn=float\($SIGMA\) /network/syn/rand=False \
                     /network/trn/enable=True /network/trn/gsyn=$TRNGSYN /network/trn/delay=$TRNDLY $TRNPRMS \
                     /network/cx/enable=False \
                     /network/home/enable=True  /network/home/continue=False /network/home/slope=0.05 /network/home/gmax=-10. /network/home/target_fr=$TRARGETFD \
                     /sim/record/file=\'$TMPDIR/$WORKPREFIX.stkdata\' /sim/record/gsyn=True \
                     /FR/Overall=\"$WORKPREFIX-FR.json\" \
                     /sim/state/load=\'$TMPDIR/$WORKPREFIX-simstate.stkdata\' /sim/state/save=\'$TMPDIR/$WORKPREFIX-simstate.stkdata\' \
                     || { echo "$WORKPREFIX FAILED I$i" ; exit 1 ; }
              (($i>11))&& break
       done
       python dLGNnetwork.py -l DEBUG -L $WORKPREFIX-blockTRN.log \
              -o $PREFTMPST.stkdb -m NMDA\ PREFIX:$PREFTMPST\ SIGMA:$SIGMA\ TRN:BLOCKED\ R:$R \
              $SIMPRMS /sim/record/cont=False \
              /network/load=False /network/save=False \
              /sim/Tmax=-1 \
              $NRNPRMS \
              /network/gj/geom/p=0 /block/gjcon=True $GJPRMS \
              /network/syn/geom/unit=\'G\' /network/syn/geom/pmax=1 /network/syn/geom/sig=float\($SIGMA\) \
              /network/syn/gsyn=-1. /network/syn/sig2gsyn=float\($SIGMA\) /network/syn/rand=False \
              /network/trn/enable=False /network/trn/gsyn=$TRNGSYN /network/trn/delay=$TRNDLY $TRNPRMS \
              /network/cx/enable=False \
              /network/home/enable=False  /network/home/continue=False /network/home/slope=0.05 /network/home/gmax=-10. /network/home/target_fr=$TRARGETFD \
              /sim/record/file=\'$TMPDIR/$WORKPREFIX-blockTRN.stkdata\' /sim/record/gsyn=True \
              /FR/Overall=\"$WORKPREFIX-blockTRN-FR.json\" \
              /sim/state/load=\'$TMPDIR/$WORKPREFIX-simstate.stkdata\' \
              || { echo "$WORKPREFIX FAILED TRNBLK" ; exit 1 ; }
       localpid=()
       xz -T0 -9 $TMPDIR/$WORKPREFIX.stkdata  & localpid+=($!) 
       xz -T0 -9 $TMPDIR/$WORKPREFIX-blockTRN.stkdata  & localpid+=($!) 
       xz -T0 -9 $TMPDIR/$WORKPREFIX-simstate.stkdata  & localpid+=($!) 
       xz -T0 -9 $WORKPREFIX.log & localpid+=($!)
       xz -T0 -9 $WORKPREFIX-blockTRN.log & localpid+=($!)
       for pid in ${localpid[*]}; do wait $pid; done  ;

       echo "$PREFTMPST : Run $R is finished"
    done
    popd && \
    for i in $TMPDIR/$PREFTMPST*.stkdata.xz
    do
        mv $i .
    done && \
    localpid=()
    zip -r $PREFTMPST-scripts-log-FR.zip \
        *.py lmods mods simtoolkit Maccione2014_P9_29March11_control_SpkTs_bursts_filtered.h5 \
        P07-selected-checked-gmin.json selectedP07N04v05.json \
        $PREFTMPST-*-FR.json $PREFTMPST.stkdb\
        $0 && \
    echo "$PREFTMPST : data has been arXived"
}

# rm $$PREFTMPST-FR.json $PREFTMPST.log $PREFTMPST.stkdb && \

pids=()
case $SLURM_ARRAY_TASK_ID in
    0)
       worker $PREFIX-N00-C000-$TIMESTAMP 1.0 0.0001 1.0 & pids+=($!)
       worker $PREFIX-N00-C001-$TIMESTAMP 1.0 0.0001 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N00-C002-$TIMESTAMP 1.0 0.0001 2.51188643150958 & pids+=($!)
       worker $PREFIX-N00-C003-$TIMESTAMP 1.0 0.0001 3.981071705534973 & pids+=($!)
       worker $PREFIX-N00-C004-$TIMESTAMP 1.0 0.0001 6.309573444801933 & pids+=($!)
       worker $PREFIX-N00-C005-$TIMESTAMP 1.0 0.0001 10.0 & pids+=($!)
       worker $PREFIX-N00-C006-$TIMESTAMP 1.0 0.0001 15.848931924611142 & pids+=($!)
       worker $PREFIX-N00-C007-$TIMESTAMP 1.0 0.0001 25.11886431509581 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    1)
       worker $PREFIX-N01-C008-$TIMESTAMP 1.0 0.0001 39.810717055349734 & pids+=($!)
       worker $PREFIX-N01-C009-$TIMESTAMP 1.0 0.0001 63.09573444801933 & pids+=($!)
       worker $PREFIX-N01-C010-$TIMESTAMP 1.0 0.0001 100.0 & pids+=($!)
       worker $PREFIX-N01-C011-$TIMESTAMP 1.0 0.00015848931924611142 1.0 & pids+=($!)
       worker $PREFIX-N01-C012-$TIMESTAMP 1.0 0.00015848931924611142 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N01-C013-$TIMESTAMP 1.0 0.00015848931924611142 2.51188643150958 & pids+=($!)
       worker $PREFIX-N01-C014-$TIMESTAMP 1.0 0.00015848931924611142 3.981071705534973 & pids+=($!)
       worker $PREFIX-N01-C015-$TIMESTAMP 1.0 0.00015848931924611142 6.309573444801933 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    2)
       worker $PREFIX-N02-C016-$TIMESTAMP 1.0 0.00015848931924611142 10.0 & pids+=($!)
       worker $PREFIX-N02-C017-$TIMESTAMP 1.0 0.00015848931924611142 15.848931924611142 & pids+=($!)
       worker $PREFIX-N02-C018-$TIMESTAMP 1.0 0.00015848931924611142 25.11886431509581 & pids+=($!)
       worker $PREFIX-N02-C019-$TIMESTAMP 1.0 0.00015848931924611142 39.810717055349734 & pids+=($!)
       worker $PREFIX-N02-C020-$TIMESTAMP 1.0 0.00015848931924611142 63.09573444801933 & pids+=($!)
       worker $PREFIX-N02-C021-$TIMESTAMP 1.0 0.00015848931924611142 100.0 & pids+=($!)
       worker $PREFIX-N02-C022-$TIMESTAMP 1.0 0.00025118864315095795 1.0 & pids+=($!)
       worker $PREFIX-N02-C023-$TIMESTAMP 1.0 0.00025118864315095795 1.5848931924611136 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    3)
       worker $PREFIX-N03-C024-$TIMESTAMP 1.0 0.00025118864315095795 2.51188643150958 & pids+=($!)
       worker $PREFIX-N03-C025-$TIMESTAMP 1.0 0.00025118864315095795 3.981071705534973 & pids+=($!)
       worker $PREFIX-N03-C026-$TIMESTAMP 1.0 0.00025118864315095795 6.309573444801933 & pids+=($!)
       worker $PREFIX-N03-C027-$TIMESTAMP 1.0 0.00025118864315095795 10.0 & pids+=($!)
       worker $PREFIX-N03-C028-$TIMESTAMP 1.0 0.00025118864315095795 15.848931924611142 & pids+=($!)
       worker $PREFIX-N03-C029-$TIMESTAMP 1.0 0.00025118864315095795 25.11886431509581 & pids+=($!)
       worker $PREFIX-N03-C030-$TIMESTAMP 1.0 0.00025118864315095795 39.810717055349734 & pids+=($!)
       worker $PREFIX-N03-C031-$TIMESTAMP 1.0 0.00025118864315095795 63.09573444801933 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    4)
       worker $PREFIX-N04-C032-$TIMESTAMP 1.0 0.00025118864315095795 100.0 & pids+=($!)
       worker $PREFIX-N04-C033-$TIMESTAMP 1.0 0.00039810717055349735 1.0 & pids+=($!)
       worker $PREFIX-N04-C034-$TIMESTAMP 1.0 0.00039810717055349735 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N04-C035-$TIMESTAMP 1.0 0.00039810717055349735 2.51188643150958 & pids+=($!)
       worker $PREFIX-N04-C036-$TIMESTAMP 1.0 0.00039810717055349735 3.981071705534973 & pids+=($!)
       worker $PREFIX-N04-C037-$TIMESTAMP 1.0 0.00039810717055349735 6.309573444801933 & pids+=($!)
       worker $PREFIX-N04-C038-$TIMESTAMP 1.0 0.00039810717055349735 10.0 & pids+=($!)
       worker $PREFIX-N04-C039-$TIMESTAMP 1.0 0.00039810717055349735 15.848931924611142 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    5)
       worker $PREFIX-N05-C040-$TIMESTAMP 1.0 0.00039810717055349735 25.11886431509581 & pids+=($!)
       worker $PREFIX-N05-C041-$TIMESTAMP 1.0 0.00039810717055349735 39.810717055349734 & pids+=($!)
       worker $PREFIX-N05-C042-$TIMESTAMP 1.0 0.00039810717055349735 63.09573444801933 & pids+=($!)
       worker $PREFIX-N05-C043-$TIMESTAMP 1.0 0.00039810717055349735 100.0 & pids+=($!)
       worker $PREFIX-N05-C044-$TIMESTAMP 1.0 0.000630957344480193 1.0 & pids+=($!)
       worker $PREFIX-N05-C045-$TIMESTAMP 1.0 0.000630957344480193 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N05-C046-$TIMESTAMP 1.0 0.000630957344480193 2.51188643150958 & pids+=($!)
       worker $PREFIX-N05-C047-$TIMESTAMP 1.0 0.000630957344480193 3.981071705534973 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    6)
       worker $PREFIX-N06-C048-$TIMESTAMP 1.0 0.000630957344480193 6.309573444801933 & pids+=($!)
       worker $PREFIX-N06-C049-$TIMESTAMP 1.0 0.000630957344480193 10.0 & pids+=($!)
       worker $PREFIX-N06-C050-$TIMESTAMP 1.0 0.000630957344480193 15.848931924611142 & pids+=($!)
       worker $PREFIX-N06-C051-$TIMESTAMP 1.0 0.000630957344480193 25.11886431509581 & pids+=($!)
       worker $PREFIX-N06-C052-$TIMESTAMP 1.0 0.000630957344480193 39.810717055349734 & pids+=($!)
       worker $PREFIX-N06-C053-$TIMESTAMP 1.0 0.000630957344480193 63.09573444801933 & pids+=($!)
       worker $PREFIX-N06-C054-$TIMESTAMP 1.0 0.000630957344480193 100.0 & pids+=($!)
       worker $PREFIX-N06-C055-$TIMESTAMP 1.0 0.001 1.0 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    7)
       worker $PREFIX-N07-C056-$TIMESTAMP 1.0 0.001 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N07-C057-$TIMESTAMP 1.0 0.001 2.51188643150958 & pids+=($!)
       worker $PREFIX-N07-C058-$TIMESTAMP 1.0 0.001 3.981071705534973 & pids+=($!)
       worker $PREFIX-N07-C059-$TIMESTAMP 1.0 0.001 6.309573444801933 & pids+=($!)
       worker $PREFIX-N07-C060-$TIMESTAMP 1.0 0.001 10.0 & pids+=($!)
       worker $PREFIX-N07-C061-$TIMESTAMP 1.0 0.001 15.848931924611142 & pids+=($!)
       worker $PREFIX-N07-C062-$TIMESTAMP 1.0 0.001 25.11886431509581 & pids+=($!)
       worker $PREFIX-N07-C063-$TIMESTAMP 1.0 0.001 39.810717055349734 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    8)
       worker $PREFIX-N08-C064-$TIMESTAMP 1.0 0.001 63.09573444801933 & pids+=($!)
       worker $PREFIX-N08-C065-$TIMESTAMP 1.0 0.001 100.0 & pids+=($!)
       worker $PREFIX-N08-C066-$TIMESTAMP 1.0 0.001584893192461114 1.0 & pids+=($!)
       worker $PREFIX-N08-C067-$TIMESTAMP 1.0 0.001584893192461114 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N08-C068-$TIMESTAMP 1.0 0.001584893192461114 2.51188643150958 & pids+=($!)
       worker $PREFIX-N08-C069-$TIMESTAMP 1.0 0.001584893192461114 3.981071705534973 & pids+=($!)
       worker $PREFIX-N08-C070-$TIMESTAMP 1.0 0.001584893192461114 6.309573444801933 & pids+=($!)
       worker $PREFIX-N08-C071-$TIMESTAMP 1.0 0.001584893192461114 10.0 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    9)
       worker $PREFIX-N09-C072-$TIMESTAMP 1.0 0.001584893192461114 15.848931924611142 & pids+=($!)
       worker $PREFIX-N09-C073-$TIMESTAMP 1.0 0.001584893192461114 25.11886431509581 & pids+=($!)
       worker $PREFIX-N09-C074-$TIMESTAMP 1.0 0.001584893192461114 39.810717055349734 & pids+=($!)
       worker $PREFIX-N09-C075-$TIMESTAMP 1.0 0.001584893192461114 63.09573444801933 & pids+=($!)
       worker $PREFIX-N09-C076-$TIMESTAMP 1.0 0.001584893192461114 100.0 & pids+=($!)
       worker $PREFIX-N09-C077-$TIMESTAMP 1.0 0.002511886431509582 1.0 & pids+=($!)
       worker $PREFIX-N09-C078-$TIMESTAMP 1.0 0.002511886431509582 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N09-C079-$TIMESTAMP 1.0 0.002511886431509582 2.51188643150958 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    10)
       worker $PREFIX-N10-C080-$TIMESTAMP 1.0 0.002511886431509582 3.981071705534973 & pids+=($!)
       worker $PREFIX-N10-C081-$TIMESTAMP 1.0 0.002511886431509582 6.309573444801933 & pids+=($!)
       worker $PREFIX-N10-C082-$TIMESTAMP 1.0 0.002511886431509582 10.0 & pids+=($!)
       worker $PREFIX-N10-C083-$TIMESTAMP 1.0 0.002511886431509582 15.848931924611142 & pids+=($!)
       worker $PREFIX-N10-C084-$TIMESTAMP 1.0 0.002511886431509582 25.11886431509581 & pids+=($!)
       worker $PREFIX-N10-C085-$TIMESTAMP 1.0 0.002511886431509582 39.810717055349734 & pids+=($!)
       worker $PREFIX-N10-C086-$TIMESTAMP 1.0 0.002511886431509582 63.09573444801933 & pids+=($!)
       worker $PREFIX-N10-C087-$TIMESTAMP 1.0 0.002511886431509582 100.0 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    11)
       worker $PREFIX-N11-C088-$TIMESTAMP 1.0 0.003981071705534973 1.0 & pids+=($!)
       worker $PREFIX-N11-C089-$TIMESTAMP 1.0 0.003981071705534973 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N11-C090-$TIMESTAMP 1.0 0.003981071705534973 2.51188643150958 & pids+=($!)
       worker $PREFIX-N11-C091-$TIMESTAMP 1.0 0.003981071705534973 3.981071705534973 & pids+=($!)
       worker $PREFIX-N11-C092-$TIMESTAMP 1.0 0.003981071705534973 6.309573444801933 & pids+=($!)
       worker $PREFIX-N11-C093-$TIMESTAMP 1.0 0.003981071705534973 10.0 & pids+=($!)
       worker $PREFIX-N11-C094-$TIMESTAMP 1.0 0.003981071705534973 15.848931924611142 & pids+=($!)
       worker $PREFIX-N11-C095-$TIMESTAMP 1.0 0.003981071705534973 25.11886431509581 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    12)
       worker $PREFIX-N12-C096-$TIMESTAMP 1.0 0.003981071705534973 39.810717055349734 & pids+=($!)
       worker $PREFIX-N12-C097-$TIMESTAMP 1.0 0.003981071705534973 63.09573444801933 & pids+=($!)
       worker $PREFIX-N12-C098-$TIMESTAMP 1.0 0.003981071705534973 100.0 & pids+=($!)
       worker $PREFIX-N12-C099-$TIMESTAMP 1.0 0.00630957344480193 1.0 & pids+=($!)
       worker $PREFIX-N12-C100-$TIMESTAMP 1.0 0.00630957344480193 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N12-C101-$TIMESTAMP 1.0 0.00630957344480193 2.51188643150958 & pids+=($!)
       worker $PREFIX-N12-C102-$TIMESTAMP 1.0 0.00630957344480193 3.981071705534973 & pids+=($!)
       worker $PREFIX-N12-C103-$TIMESTAMP 1.0 0.00630957344480193 6.309573444801933 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    13)
       worker $PREFIX-N13-C104-$TIMESTAMP 1.0 0.00630957344480193 10.0 & pids+=($!)
       worker $PREFIX-N13-C105-$TIMESTAMP 1.0 0.00630957344480193 15.848931924611142 & pids+=($!)
       worker $PREFIX-N13-C106-$TIMESTAMP 1.0 0.00630957344480193 25.11886431509581 & pids+=($!)
       worker $PREFIX-N13-C107-$TIMESTAMP 1.0 0.00630957344480193 39.810717055349734 & pids+=($!)
       worker $PREFIX-N13-C108-$TIMESTAMP 1.0 0.00630957344480193 63.09573444801933 & pids+=($!)
       worker $PREFIX-N13-C109-$TIMESTAMP 1.0 0.00630957344480193 100.0 & pids+=($!)
       worker $PREFIX-N13-C110-$TIMESTAMP 1.0 0.01 1.0 & pids+=($!)
       worker $PREFIX-N13-C111-$TIMESTAMP 1.0 0.01 1.5848931924611136 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    14)
       worker $PREFIX-N14-C112-$TIMESTAMP 1.0 0.01 2.51188643150958 & pids+=($!)
       worker $PREFIX-N14-C113-$TIMESTAMP 1.0 0.01 3.981071705534973 & pids+=($!)
       worker $PREFIX-N14-C114-$TIMESTAMP 1.0 0.01 6.309573444801933 & pids+=($!)
       worker $PREFIX-N14-C115-$TIMESTAMP 1.0 0.01 10.0 & pids+=($!)
       worker $PREFIX-N14-C116-$TIMESTAMP 1.0 0.01 15.848931924611142 & pids+=($!)
       worker $PREFIX-N14-C117-$TIMESTAMP 1.0 0.01 25.11886431509581 & pids+=($!)
       worker $PREFIX-N14-C118-$TIMESTAMP 1.0 0.01 39.810717055349734 & pids+=($!)
       worker $PREFIX-N14-C119-$TIMESTAMP 1.0 0.01 63.09573444801933 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    15)
       worker $PREFIX-N15-C120-$TIMESTAMP 1.0 0.01 100.0 & pids+=($!)
       worker $PREFIX-N15-C121-$TIMESTAMP 1.0 0.01584893192461114 1.0 & pids+=($!)
       worker $PREFIX-N15-C122-$TIMESTAMP 1.0 0.01584893192461114 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N15-C123-$TIMESTAMP 1.0 0.01584893192461114 2.51188643150958 & pids+=($!)
       worker $PREFIX-N15-C124-$TIMESTAMP 1.0 0.01584893192461114 3.981071705534973 & pids+=($!)
       worker $PREFIX-N15-C125-$TIMESTAMP 1.0 0.01584893192461114 6.309573444801933 & pids+=($!)
       worker $PREFIX-N15-C126-$TIMESTAMP 1.0 0.01584893192461114 10.0 & pids+=($!)
       worker $PREFIX-N15-C127-$TIMESTAMP 1.0 0.01584893192461114 15.848931924611142 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    16)
       worker $PREFIX-N16-C128-$TIMESTAMP 1.0 0.01584893192461114 25.11886431509581 & pids+=($!)
       worker $PREFIX-N16-C129-$TIMESTAMP 1.0 0.01584893192461114 39.810717055349734 & pids+=($!)
       worker $PREFIX-N16-C130-$TIMESTAMP 1.0 0.01584893192461114 63.09573444801933 & pids+=($!)
       worker $PREFIX-N16-C131-$TIMESTAMP 1.0 0.01584893192461114 100.0 & pids+=($!)
       worker $PREFIX-N16-C132-$TIMESTAMP 1.0 0.025118864315095822 1.0 & pids+=($!)
       worker $PREFIX-N16-C133-$TIMESTAMP 1.0 0.025118864315095822 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N16-C134-$TIMESTAMP 1.0 0.025118864315095822 2.51188643150958 & pids+=($!)
       worker $PREFIX-N16-C135-$TIMESTAMP 1.0 0.025118864315095822 3.981071705534973 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    17)
       worker $PREFIX-N17-C136-$TIMESTAMP 1.0 0.025118864315095822 6.309573444801933 & pids+=($!)
       worker $PREFIX-N17-C137-$TIMESTAMP 1.0 0.025118864315095822 10.0 & pids+=($!)
       worker $PREFIX-N17-C138-$TIMESTAMP 1.0 0.025118864315095822 15.848931924611142 & pids+=($!)
       worker $PREFIX-N17-C139-$TIMESTAMP 1.0 0.025118864315095822 25.11886431509581 & pids+=($!)
       worker $PREFIX-N17-C140-$TIMESTAMP 1.0 0.025118864315095822 39.810717055349734 & pids+=($!)
       worker $PREFIX-N17-C141-$TIMESTAMP 1.0 0.025118864315095822 63.09573444801933 & pids+=($!)
       worker $PREFIX-N17-C142-$TIMESTAMP 1.0 0.025118864315095822 100.0 & pids+=($!)
       worker $PREFIX-N17-C143-$TIMESTAMP 1.0 0.039810717055349734 1.0 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    18)
       worker $PREFIX-N18-C144-$TIMESTAMP 1.0 0.039810717055349734 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N18-C145-$TIMESTAMP 1.0 0.039810717055349734 2.51188643150958 & pids+=($!)
       worker $PREFIX-N18-C146-$TIMESTAMP 1.0 0.039810717055349734 3.981071705534973 & pids+=($!)
       worker $PREFIX-N18-C147-$TIMESTAMP 1.0 0.039810717055349734 6.309573444801933 & pids+=($!)
       worker $PREFIX-N18-C148-$TIMESTAMP 1.0 0.039810717055349734 10.0 & pids+=($!)
       worker $PREFIX-N18-C149-$TIMESTAMP 1.0 0.039810717055349734 15.848931924611142 & pids+=($!)
       worker $PREFIX-N18-C150-$TIMESTAMP 1.0 0.039810717055349734 25.11886431509581 & pids+=($!)
       worker $PREFIX-N18-C151-$TIMESTAMP 1.0 0.039810717055349734 39.810717055349734 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    19)
       worker $PREFIX-N19-C152-$TIMESTAMP 1.0 0.039810717055349734 63.09573444801933 & pids+=($!)
       worker $PREFIX-N19-C153-$TIMESTAMP 1.0 0.039810717055349734 100.0 & pids+=($!)
       worker $PREFIX-N19-C154-$TIMESTAMP 1.0 0.06309573444801936 1.0 & pids+=($!)
       worker $PREFIX-N19-C155-$TIMESTAMP 1.0 0.06309573444801936 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N19-C156-$TIMESTAMP 1.0 0.06309573444801936 2.51188643150958 & pids+=($!)
       worker $PREFIX-N19-C157-$TIMESTAMP 1.0 0.06309573444801936 3.981071705534973 & pids+=($!)
       worker $PREFIX-N19-C158-$TIMESTAMP 1.0 0.06309573444801936 6.309573444801933 & pids+=($!)
       worker $PREFIX-N19-C159-$TIMESTAMP 1.0 0.06309573444801936 10.0 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    20)
       worker $PREFIX-N20-C160-$TIMESTAMP 1.0 0.06309573444801936 15.848931924611142 & pids+=($!)
       worker $PREFIX-N20-C161-$TIMESTAMP 1.0 0.06309573444801936 25.11886431509581 & pids+=($!)
       worker $PREFIX-N20-C162-$TIMESTAMP 1.0 0.06309573444801936 39.810717055349734 & pids+=($!)
       worker $PREFIX-N20-C163-$TIMESTAMP 1.0 0.06309573444801936 63.09573444801933 & pids+=($!)
       worker $PREFIX-N20-C164-$TIMESTAMP 1.0 0.06309573444801936 100.0 & pids+=($!)
       worker $PREFIX-N20-C165-$TIMESTAMP 1.0 0.1 1.0 & pids+=($!)
       worker $PREFIX-N20-C166-$TIMESTAMP 1.0 0.1 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N20-C167-$TIMESTAMP 1.0 0.1 2.51188643150958 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    21)
       worker $PREFIX-N21-C168-$TIMESTAMP 1.0 0.1 3.981071705534973 & pids+=($!)
       worker $PREFIX-N21-C169-$TIMESTAMP 1.0 0.1 6.309573444801933 & pids+=($!)
       worker $PREFIX-N21-C170-$TIMESTAMP 1.0 0.1 10.0 & pids+=($!)
       worker $PREFIX-N21-C171-$TIMESTAMP 1.0 0.1 15.848931924611142 & pids+=($!)
       worker $PREFIX-N21-C172-$TIMESTAMP 1.0 0.1 25.11886431509581 & pids+=($!)
       worker $PREFIX-N21-C173-$TIMESTAMP 1.0 0.1 39.810717055349734 & pids+=($!)
       worker $PREFIX-N21-C174-$TIMESTAMP 1.0 0.1 63.09573444801933 & pids+=($!)
       worker $PREFIX-N21-C175-$TIMESTAMP 1.0 0.1 100.0 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    22)
       worker $PREFIX-N22-C176-$TIMESTAMP 4.0 0.0001 1.0 & pids+=($!)
       worker $PREFIX-N22-C177-$TIMESTAMP 4.0 0.0001 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N22-C178-$TIMESTAMP 4.0 0.0001 2.51188643150958 & pids+=($!)
       worker $PREFIX-N22-C179-$TIMESTAMP 4.0 0.0001 3.981071705534973 & pids+=($!)
       worker $PREFIX-N22-C180-$TIMESTAMP 4.0 0.0001 6.309573444801933 & pids+=($!)
       worker $PREFIX-N22-C181-$TIMESTAMP 4.0 0.0001 10.0 & pids+=($!)
       worker $PREFIX-N22-C182-$TIMESTAMP 4.0 0.0001 15.848931924611142 & pids+=($!)
       worker $PREFIX-N22-C183-$TIMESTAMP 4.0 0.0001 25.11886431509581 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    23)
       worker $PREFIX-N23-C184-$TIMESTAMP 4.0 0.0001 39.810717055349734 & pids+=($!)
       worker $PREFIX-N23-C185-$TIMESTAMP 4.0 0.0001 63.09573444801933 & pids+=($!)
       worker $PREFIX-N23-C186-$TIMESTAMP 4.0 0.0001 100.0 & pids+=($!)
       worker $PREFIX-N23-C187-$TIMESTAMP 4.0 0.00015848931924611142 1.0 & pids+=($!)
       worker $PREFIX-N23-C188-$TIMESTAMP 4.0 0.00015848931924611142 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N23-C189-$TIMESTAMP 4.0 0.00015848931924611142 2.51188643150958 & pids+=($!)
       worker $PREFIX-N23-C190-$TIMESTAMP 4.0 0.00015848931924611142 3.981071705534973 & pids+=($!)
       worker $PREFIX-N23-C191-$TIMESTAMP 4.0 0.00015848931924611142 6.309573444801933 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    24)
       worker $PREFIX-N24-C192-$TIMESTAMP 4.0 0.00015848931924611142 10.0 & pids+=($!)
       worker $PREFIX-N24-C193-$TIMESTAMP 4.0 0.00015848931924611142 15.848931924611142 & pids+=($!)
       worker $PREFIX-N24-C194-$TIMESTAMP 4.0 0.00015848931924611142 25.11886431509581 & pids+=($!)
       worker $PREFIX-N24-C195-$TIMESTAMP 4.0 0.00015848931924611142 39.810717055349734 & pids+=($!)
       worker $PREFIX-N24-C196-$TIMESTAMP 4.0 0.00015848931924611142 63.09573444801933 & pids+=($!)
       worker $PREFIX-N24-C197-$TIMESTAMP 4.0 0.00015848931924611142 100.0 & pids+=($!)
       worker $PREFIX-N24-C198-$TIMESTAMP 4.0 0.00025118864315095795 1.0 & pids+=($!)
       worker $PREFIX-N24-C199-$TIMESTAMP 4.0 0.00025118864315095795 1.5848931924611136 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    25)
       worker $PREFIX-N25-C200-$TIMESTAMP 4.0 0.00025118864315095795 2.51188643150958 & pids+=($!)
       worker $PREFIX-N25-C201-$TIMESTAMP 4.0 0.00025118864315095795 3.981071705534973 & pids+=($!)
       worker $PREFIX-N25-C202-$TIMESTAMP 4.0 0.00025118864315095795 6.309573444801933 & pids+=($!)
       worker $PREFIX-N25-C203-$TIMESTAMP 4.0 0.00025118864315095795 10.0 & pids+=($!)
       worker $PREFIX-N25-C204-$TIMESTAMP 4.0 0.00025118864315095795 15.848931924611142 & pids+=($!)
       worker $PREFIX-N25-C205-$TIMESTAMP 4.0 0.00025118864315095795 25.11886431509581 & pids+=($!)
       worker $PREFIX-N25-C206-$TIMESTAMP 4.0 0.00025118864315095795 39.810717055349734 & pids+=($!)
       worker $PREFIX-N25-C207-$TIMESTAMP 4.0 0.00025118864315095795 63.09573444801933 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    26)
       worker $PREFIX-N26-C208-$TIMESTAMP 4.0 0.00025118864315095795 100.0 & pids+=($!)
       worker $PREFIX-N26-C209-$TIMESTAMP 4.0 0.00039810717055349735 1.0 & pids+=($!)
       worker $PREFIX-N26-C210-$TIMESTAMP 4.0 0.00039810717055349735 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N26-C211-$TIMESTAMP 4.0 0.00039810717055349735 2.51188643150958 & pids+=($!)
       worker $PREFIX-N26-C212-$TIMESTAMP 4.0 0.00039810717055349735 3.981071705534973 & pids+=($!)
       worker $PREFIX-N26-C213-$TIMESTAMP 4.0 0.00039810717055349735 6.309573444801933 & pids+=($!)
       worker $PREFIX-N26-C214-$TIMESTAMP 4.0 0.00039810717055349735 10.0 & pids+=($!)
       worker $PREFIX-N26-C215-$TIMESTAMP 4.0 0.00039810717055349735 15.848931924611142 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    27)
       worker $PREFIX-N27-C216-$TIMESTAMP 4.0 0.00039810717055349735 25.11886431509581 & pids+=($!)
       worker $PREFIX-N27-C217-$TIMESTAMP 4.0 0.00039810717055349735 39.810717055349734 & pids+=($!)
       worker $PREFIX-N27-C218-$TIMESTAMP 4.0 0.00039810717055349735 63.09573444801933 & pids+=($!)
       worker $PREFIX-N27-C219-$TIMESTAMP 4.0 0.00039810717055349735 100.0 & pids+=($!)
       worker $PREFIX-N27-C220-$TIMESTAMP 4.0 0.000630957344480193 1.0 & pids+=($!)
       worker $PREFIX-N27-C221-$TIMESTAMP 4.0 0.000630957344480193 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N27-C222-$TIMESTAMP 4.0 0.000630957344480193 2.51188643150958 & pids+=($!)
       worker $PREFIX-N27-C223-$TIMESTAMP 4.0 0.000630957344480193 3.981071705534973 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    28)
       worker $PREFIX-N28-C224-$TIMESTAMP 4.0 0.000630957344480193 6.309573444801933 & pids+=($!)
       worker $PREFIX-N28-C225-$TIMESTAMP 4.0 0.000630957344480193 10.0 & pids+=($!)
       worker $PREFIX-N28-C226-$TIMESTAMP 4.0 0.000630957344480193 15.848931924611142 & pids+=($!)
       worker $PREFIX-N28-C227-$TIMESTAMP 4.0 0.000630957344480193 25.11886431509581 & pids+=($!)
       worker $PREFIX-N28-C228-$TIMESTAMP 4.0 0.000630957344480193 39.810717055349734 & pids+=($!)
       worker $PREFIX-N28-C229-$TIMESTAMP 4.0 0.000630957344480193 63.09573444801933 & pids+=($!)
       worker $PREFIX-N28-C230-$TIMESTAMP 4.0 0.000630957344480193 100.0 & pids+=($!)
       worker $PREFIX-N28-C231-$TIMESTAMP 4.0 0.001 1.0 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    29)
       worker $PREFIX-N29-C232-$TIMESTAMP 4.0 0.001 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N29-C233-$TIMESTAMP 4.0 0.001 2.51188643150958 & pids+=($!)
       worker $PREFIX-N29-C234-$TIMESTAMP 4.0 0.001 3.981071705534973 & pids+=($!)
       worker $PREFIX-N29-C235-$TIMESTAMP 4.0 0.001 6.309573444801933 & pids+=($!)
       worker $PREFIX-N29-C236-$TIMESTAMP 4.0 0.001 10.0 & pids+=($!)
       worker $PREFIX-N29-C237-$TIMESTAMP 4.0 0.001 15.848931924611142 & pids+=($!)
       worker $PREFIX-N29-C238-$TIMESTAMP 4.0 0.001 25.11886431509581 & pids+=($!)
       worker $PREFIX-N29-C239-$TIMESTAMP 4.0 0.001 39.810717055349734 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    30)
       worker $PREFIX-N30-C240-$TIMESTAMP 4.0 0.001 63.09573444801933 & pids+=($!)
       worker $PREFIX-N30-C241-$TIMESTAMP 4.0 0.001 100.0 & pids+=($!)
       worker $PREFIX-N30-C242-$TIMESTAMP 4.0 0.001584893192461114 1.0 & pids+=($!)
       worker $PREFIX-N30-C243-$TIMESTAMP 4.0 0.001584893192461114 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N30-C244-$TIMESTAMP 4.0 0.001584893192461114 2.51188643150958 & pids+=($!)
       worker $PREFIX-N30-C245-$TIMESTAMP 4.0 0.001584893192461114 3.981071705534973 & pids+=($!)
       worker $PREFIX-N30-C246-$TIMESTAMP 4.0 0.001584893192461114 6.309573444801933 & pids+=($!)
       worker $PREFIX-N30-C247-$TIMESTAMP 4.0 0.001584893192461114 10.0 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    31)
       worker $PREFIX-N31-C248-$TIMESTAMP 4.0 0.001584893192461114 15.848931924611142 & pids+=($!)
       worker $PREFIX-N31-C249-$TIMESTAMP 4.0 0.001584893192461114 25.11886431509581 & pids+=($!)
       worker $PREFIX-N31-C250-$TIMESTAMP 4.0 0.001584893192461114 39.810717055349734 & pids+=($!)
       worker $PREFIX-N31-C251-$TIMESTAMP 4.0 0.001584893192461114 63.09573444801933 & pids+=($!)
       worker $PREFIX-N31-C252-$TIMESTAMP 4.0 0.001584893192461114 100.0 & pids+=($!)
       worker $PREFIX-N31-C253-$TIMESTAMP 4.0 0.002511886431509582 1.0 & pids+=($!)
       worker $PREFIX-N31-C254-$TIMESTAMP 4.0 0.002511886431509582 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N31-C255-$TIMESTAMP 4.0 0.002511886431509582 2.51188643150958 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    32)
       worker $PREFIX-N32-C256-$TIMESTAMP 4.0 0.002511886431509582 3.981071705534973 & pids+=($!)
       worker $PREFIX-N32-C257-$TIMESTAMP 4.0 0.002511886431509582 6.309573444801933 & pids+=($!)
       worker $PREFIX-N32-C258-$TIMESTAMP 4.0 0.002511886431509582 10.0 & pids+=($!)
       worker $PREFIX-N32-C259-$TIMESTAMP 4.0 0.002511886431509582 15.848931924611142 & pids+=($!)
       worker $PREFIX-N32-C260-$TIMESTAMP 4.0 0.002511886431509582 25.11886431509581 & pids+=($!)
       worker $PREFIX-N32-C261-$TIMESTAMP 4.0 0.002511886431509582 39.810717055349734 & pids+=($!)
       worker $PREFIX-N32-C262-$TIMESTAMP 4.0 0.002511886431509582 63.09573444801933 & pids+=($!)
       worker $PREFIX-N32-C263-$TIMESTAMP 4.0 0.002511886431509582 100.0 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    33)
       worker $PREFIX-N33-C264-$TIMESTAMP 4.0 0.003981071705534973 1.0 & pids+=($!)
       worker $PREFIX-N33-C265-$TIMESTAMP 4.0 0.003981071705534973 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N33-C266-$TIMESTAMP 4.0 0.003981071705534973 2.51188643150958 & pids+=($!)
       worker $PREFIX-N33-C267-$TIMESTAMP 4.0 0.003981071705534973 3.981071705534973 & pids+=($!)
       worker $PREFIX-N33-C268-$TIMESTAMP 4.0 0.003981071705534973 6.309573444801933 & pids+=($!)
       worker $PREFIX-N33-C269-$TIMESTAMP 4.0 0.003981071705534973 10.0 & pids+=($!)
       worker $PREFIX-N33-C270-$TIMESTAMP 4.0 0.003981071705534973 15.848931924611142 & pids+=($!)
       worker $PREFIX-N33-C271-$TIMESTAMP 4.0 0.003981071705534973 25.11886431509581 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    34)
       worker $PREFIX-N34-C272-$TIMESTAMP 4.0 0.003981071705534973 39.810717055349734 & pids+=($!)
       worker $PREFIX-N34-C273-$TIMESTAMP 4.0 0.003981071705534973 63.09573444801933 & pids+=($!)
       worker $PREFIX-N34-C274-$TIMESTAMP 4.0 0.003981071705534973 100.0 & pids+=($!)
       worker $PREFIX-N34-C275-$TIMESTAMP 4.0 0.00630957344480193 1.0 & pids+=($!)
       worker $PREFIX-N34-C276-$TIMESTAMP 4.0 0.00630957344480193 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N34-C277-$TIMESTAMP 4.0 0.00630957344480193 2.51188643150958 & pids+=($!)
       worker $PREFIX-N34-C278-$TIMESTAMP 4.0 0.00630957344480193 3.981071705534973 & pids+=($!)
       worker $PREFIX-N34-C279-$TIMESTAMP 4.0 0.00630957344480193 6.309573444801933 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    35)
       worker $PREFIX-N35-C280-$TIMESTAMP 4.0 0.00630957344480193 10.0 & pids+=($!)
       worker $PREFIX-N35-C281-$TIMESTAMP 4.0 0.00630957344480193 15.848931924611142 & pids+=($!)
       worker $PREFIX-N35-C282-$TIMESTAMP 4.0 0.00630957344480193 25.11886431509581 & pids+=($!)
       worker $PREFIX-N35-C283-$TIMESTAMP 4.0 0.00630957344480193 39.810717055349734 & pids+=($!)
       worker $PREFIX-N35-C284-$TIMESTAMP 4.0 0.00630957344480193 63.09573444801933 & pids+=($!)
       worker $PREFIX-N35-C285-$TIMESTAMP 4.0 0.00630957344480193 100.0 & pids+=($!)
       worker $PREFIX-N35-C286-$TIMESTAMP 4.0 0.01 1.0 & pids+=($!)
       worker $PREFIX-N35-C287-$TIMESTAMP 4.0 0.01 1.5848931924611136 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    36)
       worker $PREFIX-N36-C288-$TIMESTAMP 4.0 0.01 2.51188643150958 & pids+=($!)
       worker $PREFIX-N36-C289-$TIMESTAMP 4.0 0.01 3.981071705534973 & pids+=($!)
       worker $PREFIX-N36-C290-$TIMESTAMP 4.0 0.01 6.309573444801933 & pids+=($!)
       worker $PREFIX-N36-C291-$TIMESTAMP 4.0 0.01 10.0 & pids+=($!)
       worker $PREFIX-N36-C292-$TIMESTAMP 4.0 0.01 15.848931924611142 & pids+=($!)
       worker $PREFIX-N36-C293-$TIMESTAMP 4.0 0.01 25.11886431509581 & pids+=($!)
       worker $PREFIX-N36-C294-$TIMESTAMP 4.0 0.01 39.810717055349734 & pids+=($!)
       worker $PREFIX-N36-C295-$TIMESTAMP 4.0 0.01 63.09573444801933 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    37)
       worker $PREFIX-N37-C296-$TIMESTAMP 4.0 0.01 100.0 & pids+=($!)
       worker $PREFIX-N37-C297-$TIMESTAMP 4.0 0.01584893192461114 1.0 & pids+=($!)
       worker $PREFIX-N37-C298-$TIMESTAMP 4.0 0.01584893192461114 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N37-C299-$TIMESTAMP 4.0 0.01584893192461114 2.51188643150958 & pids+=($!)
       worker $PREFIX-N37-C300-$TIMESTAMP 4.0 0.01584893192461114 3.981071705534973 & pids+=($!)
       worker $PREFIX-N37-C301-$TIMESTAMP 4.0 0.01584893192461114 6.309573444801933 & pids+=($!)
       worker $PREFIX-N37-C302-$TIMESTAMP 4.0 0.01584893192461114 10.0 & pids+=($!)
       worker $PREFIX-N37-C303-$TIMESTAMP 4.0 0.01584893192461114 15.848931924611142 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    38)
       worker $PREFIX-N38-C304-$TIMESTAMP 4.0 0.01584893192461114 25.11886431509581 & pids+=($!)
       worker $PREFIX-N38-C305-$TIMESTAMP 4.0 0.01584893192461114 39.810717055349734 & pids+=($!)
       worker $PREFIX-N38-C306-$TIMESTAMP 4.0 0.01584893192461114 63.09573444801933 & pids+=($!)
       worker $PREFIX-N38-C307-$TIMESTAMP 4.0 0.01584893192461114 100.0 & pids+=($!)
       worker $PREFIX-N38-C308-$TIMESTAMP 4.0 0.025118864315095822 1.0 & pids+=($!)
       worker $PREFIX-N38-C309-$TIMESTAMP 4.0 0.025118864315095822 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N38-C310-$TIMESTAMP 4.0 0.025118864315095822 2.51188643150958 & pids+=($!)
       worker $PREFIX-N38-C311-$TIMESTAMP 4.0 0.025118864315095822 3.981071705534973 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    39)
       worker $PREFIX-N39-C312-$TIMESTAMP 4.0 0.025118864315095822 6.309573444801933 & pids+=($!)
       worker $PREFIX-N39-C313-$TIMESTAMP 4.0 0.025118864315095822 10.0 & pids+=($!)
       worker $PREFIX-N39-C314-$TIMESTAMP 4.0 0.025118864315095822 15.848931924611142 & pids+=($!)
       worker $PREFIX-N39-C315-$TIMESTAMP 4.0 0.025118864315095822 25.11886431509581 & pids+=($!)
       worker $PREFIX-N39-C316-$TIMESTAMP 4.0 0.025118864315095822 39.810717055349734 & pids+=($!)
       worker $PREFIX-N39-C317-$TIMESTAMP 4.0 0.025118864315095822 63.09573444801933 & pids+=($!)
       worker $PREFIX-N39-C318-$TIMESTAMP 4.0 0.025118864315095822 100.0 & pids+=($!)
       worker $PREFIX-N39-C319-$TIMESTAMP 4.0 0.039810717055349734 1.0 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    40)
       worker $PREFIX-N40-C320-$TIMESTAMP 4.0 0.039810717055349734 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N40-C321-$TIMESTAMP 4.0 0.039810717055349734 2.51188643150958 & pids+=($!)
       worker $PREFIX-N40-C322-$TIMESTAMP 4.0 0.039810717055349734 3.981071705534973 & pids+=($!)
       worker $PREFIX-N40-C323-$TIMESTAMP 4.0 0.039810717055349734 6.309573444801933 & pids+=($!)
       worker $PREFIX-N40-C324-$TIMESTAMP 4.0 0.039810717055349734 10.0 & pids+=($!)
       worker $PREFIX-N40-C325-$TIMESTAMP 4.0 0.039810717055349734 15.848931924611142 & pids+=($!)
       worker $PREFIX-N40-C326-$TIMESTAMP 4.0 0.039810717055349734 25.11886431509581 & pids+=($!)
       worker $PREFIX-N40-C327-$TIMESTAMP 4.0 0.039810717055349734 39.810717055349734 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    41)
       worker $PREFIX-N41-C328-$TIMESTAMP 4.0 0.039810717055349734 63.09573444801933 & pids+=($!)
       worker $PREFIX-N41-C329-$TIMESTAMP 4.0 0.039810717055349734 100.0 & pids+=($!)
       worker $PREFIX-N41-C330-$TIMESTAMP 4.0 0.06309573444801936 1.0 & pids+=($!)
       worker $PREFIX-N41-C331-$TIMESTAMP 4.0 0.06309573444801936 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N41-C332-$TIMESTAMP 4.0 0.06309573444801936 2.51188643150958 & pids+=($!)
       worker $PREFIX-N41-C333-$TIMESTAMP 4.0 0.06309573444801936 3.981071705534973 & pids+=($!)
       worker $PREFIX-N41-C334-$TIMESTAMP 4.0 0.06309573444801936 6.309573444801933 & pids+=($!)
       worker $PREFIX-N41-C335-$TIMESTAMP 4.0 0.06309573444801936 10.0 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    42)
       worker $PREFIX-N42-C336-$TIMESTAMP 4.0 0.06309573444801936 15.848931924611142 & pids+=($!)
       worker $PREFIX-N42-C337-$TIMESTAMP 4.0 0.06309573444801936 25.11886431509581 & pids+=($!)
       worker $PREFIX-N42-C338-$TIMESTAMP 4.0 0.06309573444801936 39.810717055349734 & pids+=($!)
       worker $PREFIX-N42-C339-$TIMESTAMP 4.0 0.06309573444801936 63.09573444801933 & pids+=($!)
       worker $PREFIX-N42-C340-$TIMESTAMP 4.0 0.06309573444801936 100.0 & pids+=($!)
       worker $PREFIX-N42-C341-$TIMESTAMP 4.0 0.1 1.0 & pids+=($!)
       worker $PREFIX-N42-C342-$TIMESTAMP 4.0 0.1 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N42-C343-$TIMESTAMP 4.0 0.1 2.51188643150958 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    43)
       worker $PREFIX-N43-C344-$TIMESTAMP 4.0 0.1 3.981071705534973 & pids+=($!)
       worker $PREFIX-N43-C345-$TIMESTAMP 4.0 0.1 6.309573444801933 & pids+=($!)
       worker $PREFIX-N43-C346-$TIMESTAMP 4.0 0.1 10.0 & pids+=($!)
       worker $PREFIX-N43-C347-$TIMESTAMP 4.0 0.1 15.848931924611142 & pids+=($!)
       worker $PREFIX-N43-C348-$TIMESTAMP 4.0 0.1 25.11886431509581 & pids+=($!)
       worker $PREFIX-N43-C349-$TIMESTAMP 4.0 0.1 39.810717055349734 & pids+=($!)
       worker $PREFIX-N43-C350-$TIMESTAMP 4.0 0.1 63.09573444801933 & pids+=($!)
       worker $PREFIX-N43-C351-$TIMESTAMP 4.0 0.1 100.0 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    44)
       worker $PREFIX-N44-C352-$TIMESTAMP 9.0 0.0001 1.0 & pids+=($!)
       worker $PREFIX-N44-C353-$TIMESTAMP 9.0 0.0001 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N44-C354-$TIMESTAMP 9.0 0.0001 2.51188643150958 & pids+=($!)
       worker $PREFIX-N44-C355-$TIMESTAMP 9.0 0.0001 3.981071705534973 & pids+=($!)
       worker $PREFIX-N44-C356-$TIMESTAMP 9.0 0.0001 6.309573444801933 & pids+=($!)
       worker $PREFIX-N44-C357-$TIMESTAMP 9.0 0.0001 10.0 & pids+=($!)
       worker $PREFIX-N44-C358-$TIMESTAMP 9.0 0.0001 15.848931924611142 & pids+=($!)
       worker $PREFIX-N44-C359-$TIMESTAMP 9.0 0.0001 25.11886431509581 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    45)
       worker $PREFIX-N45-C360-$TIMESTAMP 9.0 0.0001 39.810717055349734 & pids+=($!)
       worker $PREFIX-N45-C361-$TIMESTAMP 9.0 0.0001 63.09573444801933 & pids+=($!)
       worker $PREFIX-N45-C362-$TIMESTAMP 9.0 0.0001 100.0 & pids+=($!)
       worker $PREFIX-N45-C363-$TIMESTAMP 9.0 0.00015848931924611142 1.0 & pids+=($!)
       worker $PREFIX-N45-C364-$TIMESTAMP 9.0 0.00015848931924611142 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N45-C365-$TIMESTAMP 9.0 0.00015848931924611142 2.51188643150958 & pids+=($!)
       worker $PREFIX-N45-C366-$TIMESTAMP 9.0 0.00015848931924611142 3.981071705534973 & pids+=($!)
       worker $PREFIX-N45-C367-$TIMESTAMP 9.0 0.00015848931924611142 6.309573444801933 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    46)
       worker $PREFIX-N46-C368-$TIMESTAMP 9.0 0.00015848931924611142 10.0 & pids+=($!)
       worker $PREFIX-N46-C369-$TIMESTAMP 9.0 0.00015848931924611142 15.848931924611142 & pids+=($!)
       worker $PREFIX-N46-C370-$TIMESTAMP 9.0 0.00015848931924611142 25.11886431509581 & pids+=($!)
       worker $PREFIX-N46-C371-$TIMESTAMP 9.0 0.00015848931924611142 39.810717055349734 & pids+=($!)
       worker $PREFIX-N46-C372-$TIMESTAMP 9.0 0.00015848931924611142 63.09573444801933 & pids+=($!)
       worker $PREFIX-N46-C373-$TIMESTAMP 9.0 0.00015848931924611142 100.0 & pids+=($!)
       worker $PREFIX-N46-C374-$TIMESTAMP 9.0 0.00025118864315095795 1.0 & pids+=($!)
       worker $PREFIX-N46-C375-$TIMESTAMP 9.0 0.00025118864315095795 1.5848931924611136 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    47)
       worker $PREFIX-N47-C376-$TIMESTAMP 9.0 0.00025118864315095795 2.51188643150958 & pids+=($!)
       worker $PREFIX-N47-C377-$TIMESTAMP 9.0 0.00025118864315095795 3.981071705534973 & pids+=($!)
       worker $PREFIX-N47-C378-$TIMESTAMP 9.0 0.00025118864315095795 6.309573444801933 & pids+=($!)
       worker $PREFIX-N47-C379-$TIMESTAMP 9.0 0.00025118864315095795 10.0 & pids+=($!)
       worker $PREFIX-N47-C380-$TIMESTAMP 9.0 0.00025118864315095795 15.848931924611142 & pids+=($!)
       worker $PREFIX-N47-C381-$TIMESTAMP 9.0 0.00025118864315095795 25.11886431509581 & pids+=($!)
       worker $PREFIX-N47-C382-$TIMESTAMP 9.0 0.00025118864315095795 39.810717055349734 & pids+=($!)
       worker $PREFIX-N47-C383-$TIMESTAMP 9.0 0.00025118864315095795 63.09573444801933 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    48)
       worker $PREFIX-N48-C384-$TIMESTAMP 9.0 0.00025118864315095795 100.0 & pids+=($!)
       worker $PREFIX-N48-C385-$TIMESTAMP 9.0 0.00039810717055349735 1.0 & pids+=($!)
       worker $PREFIX-N48-C386-$TIMESTAMP 9.0 0.00039810717055349735 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N48-C387-$TIMESTAMP 9.0 0.00039810717055349735 2.51188643150958 & pids+=($!)
       worker $PREFIX-N48-C388-$TIMESTAMP 9.0 0.00039810717055349735 3.981071705534973 & pids+=($!)
       worker $PREFIX-N48-C389-$TIMESTAMP 9.0 0.00039810717055349735 6.309573444801933 & pids+=($!)
       worker $PREFIX-N48-C390-$TIMESTAMP 9.0 0.00039810717055349735 10.0 & pids+=($!)
       worker $PREFIX-N48-C391-$TIMESTAMP 9.0 0.00039810717055349735 15.848931924611142 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    49)
       worker $PREFIX-N49-C392-$TIMESTAMP 9.0 0.00039810717055349735 25.11886431509581 & pids+=($!)
       worker $PREFIX-N49-C393-$TIMESTAMP 9.0 0.00039810717055349735 39.810717055349734 & pids+=($!)
       worker $PREFIX-N49-C394-$TIMESTAMP 9.0 0.00039810717055349735 63.09573444801933 & pids+=($!)
       worker $PREFIX-N49-C395-$TIMESTAMP 9.0 0.00039810717055349735 100.0 & pids+=($!)
       worker $PREFIX-N49-C396-$TIMESTAMP 9.0 0.000630957344480193 1.0 & pids+=($!)
       worker $PREFIX-N49-C397-$TIMESTAMP 9.0 0.000630957344480193 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N49-C398-$TIMESTAMP 9.0 0.000630957344480193 2.51188643150958 & pids+=($!)
       worker $PREFIX-N49-C399-$TIMESTAMP 9.0 0.000630957344480193 3.981071705534973 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    50)
       worker $PREFIX-N50-C400-$TIMESTAMP 9.0 0.000630957344480193 6.309573444801933 & pids+=($!)
       worker $PREFIX-N50-C401-$TIMESTAMP 9.0 0.000630957344480193 10.0 & pids+=($!)
       worker $PREFIX-N50-C402-$TIMESTAMP 9.0 0.000630957344480193 15.848931924611142 & pids+=($!)
       worker $PREFIX-N50-C403-$TIMESTAMP 9.0 0.000630957344480193 25.11886431509581 & pids+=($!)
       worker $PREFIX-N50-C404-$TIMESTAMP 9.0 0.000630957344480193 39.810717055349734 & pids+=($!)
       worker $PREFIX-N50-C405-$TIMESTAMP 9.0 0.000630957344480193 63.09573444801933 & pids+=($!)
       worker $PREFIX-N50-C406-$TIMESTAMP 9.0 0.000630957344480193 100.0 & pids+=($!)
       worker $PREFIX-N50-C407-$TIMESTAMP 9.0 0.001 1.0 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    51)
       worker $PREFIX-N51-C408-$TIMESTAMP 9.0 0.001 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N51-C409-$TIMESTAMP 9.0 0.001 2.51188643150958 & pids+=($!)
       worker $PREFIX-N51-C410-$TIMESTAMP 9.0 0.001 3.981071705534973 & pids+=($!)
       worker $PREFIX-N51-C411-$TIMESTAMP 9.0 0.001 6.309573444801933 & pids+=($!)
       worker $PREFIX-N51-C412-$TIMESTAMP 9.0 0.001 10.0 & pids+=($!)
       worker $PREFIX-N51-C413-$TIMESTAMP 9.0 0.001 15.848931924611142 & pids+=($!)
       worker $PREFIX-N51-C414-$TIMESTAMP 9.0 0.001 25.11886431509581 & pids+=($!)
       worker $PREFIX-N51-C415-$TIMESTAMP 9.0 0.001 39.810717055349734 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    52)
       worker $PREFIX-N52-C416-$TIMESTAMP 9.0 0.001 63.09573444801933 & pids+=($!)
       worker $PREFIX-N52-C417-$TIMESTAMP 9.0 0.001 100.0 & pids+=($!)
       worker $PREFIX-N52-C418-$TIMESTAMP 9.0 0.001584893192461114 1.0 & pids+=($!)
       worker $PREFIX-N52-C419-$TIMESTAMP 9.0 0.001584893192461114 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N52-C420-$TIMESTAMP 9.0 0.001584893192461114 2.51188643150958 & pids+=($!)
       worker $PREFIX-N52-C421-$TIMESTAMP 9.0 0.001584893192461114 3.981071705534973 & pids+=($!)
       worker $PREFIX-N52-C422-$TIMESTAMP 9.0 0.001584893192461114 6.309573444801933 & pids+=($!)
       worker $PREFIX-N52-C423-$TIMESTAMP 9.0 0.001584893192461114 10.0 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    53)
       worker $PREFIX-N53-C424-$TIMESTAMP 9.0 0.001584893192461114 15.848931924611142 & pids+=($!)
       worker $PREFIX-N53-C425-$TIMESTAMP 9.0 0.001584893192461114 25.11886431509581 & pids+=($!)
       worker $PREFIX-N53-C426-$TIMESTAMP 9.0 0.001584893192461114 39.810717055349734 & pids+=($!)
       worker $PREFIX-N53-C427-$TIMESTAMP 9.0 0.001584893192461114 63.09573444801933 & pids+=($!)
       worker $PREFIX-N53-C428-$TIMESTAMP 9.0 0.001584893192461114 100.0 & pids+=($!)
       worker $PREFIX-N53-C429-$TIMESTAMP 9.0 0.002511886431509582 1.0 & pids+=($!)
       worker $PREFIX-N53-C430-$TIMESTAMP 9.0 0.002511886431509582 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N53-C431-$TIMESTAMP 9.0 0.002511886431509582 2.51188643150958 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    54)
       worker $PREFIX-N54-C432-$TIMESTAMP 9.0 0.002511886431509582 3.981071705534973 & pids+=($!)
       worker $PREFIX-N54-C433-$TIMESTAMP 9.0 0.002511886431509582 6.309573444801933 & pids+=($!)
       worker $PREFIX-N54-C434-$TIMESTAMP 9.0 0.002511886431509582 10.0 & pids+=($!)
       worker $PREFIX-N54-C435-$TIMESTAMP 9.0 0.002511886431509582 15.848931924611142 & pids+=($!)
       worker $PREFIX-N54-C436-$TIMESTAMP 9.0 0.002511886431509582 25.11886431509581 & pids+=($!)
       worker $PREFIX-N54-C437-$TIMESTAMP 9.0 0.002511886431509582 39.810717055349734 & pids+=($!)
       worker $PREFIX-N54-C438-$TIMESTAMP 9.0 0.002511886431509582 63.09573444801933 & pids+=($!)
       worker $PREFIX-N54-C439-$TIMESTAMP 9.0 0.002511886431509582 100.0 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    55)
       worker $PREFIX-N55-C440-$TIMESTAMP 9.0 0.003981071705534973 1.0 & pids+=($!)
       worker $PREFIX-N55-C441-$TIMESTAMP 9.0 0.003981071705534973 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N55-C442-$TIMESTAMP 9.0 0.003981071705534973 2.51188643150958 & pids+=($!)
       worker $PREFIX-N55-C443-$TIMESTAMP 9.0 0.003981071705534973 3.981071705534973 & pids+=($!)
       worker $PREFIX-N55-C444-$TIMESTAMP 9.0 0.003981071705534973 6.309573444801933 & pids+=($!)
       worker $PREFIX-N55-C445-$TIMESTAMP 9.0 0.003981071705534973 10.0 & pids+=($!)
       worker $PREFIX-N55-C446-$TIMESTAMP 9.0 0.003981071705534973 15.848931924611142 & pids+=($!)
       worker $PREFIX-N55-C447-$TIMESTAMP 9.0 0.003981071705534973 25.11886431509581 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    56)
       worker $PREFIX-N56-C448-$TIMESTAMP 9.0 0.003981071705534973 39.810717055349734 & pids+=($!)
       worker $PREFIX-N56-C449-$TIMESTAMP 9.0 0.003981071705534973 63.09573444801933 & pids+=($!)
       worker $PREFIX-N56-C450-$TIMESTAMP 9.0 0.003981071705534973 100.0 & pids+=($!)
       worker $PREFIX-N56-C451-$TIMESTAMP 9.0 0.00630957344480193 1.0 & pids+=($!)
       worker $PREFIX-N56-C452-$TIMESTAMP 9.0 0.00630957344480193 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N56-C453-$TIMESTAMP 9.0 0.00630957344480193 2.51188643150958 & pids+=($!)
       worker $PREFIX-N56-C454-$TIMESTAMP 9.0 0.00630957344480193 3.981071705534973 & pids+=($!)
       worker $PREFIX-N56-C455-$TIMESTAMP 9.0 0.00630957344480193 6.309573444801933 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    57)
       worker $PREFIX-N57-C456-$TIMESTAMP 9.0 0.00630957344480193 10.0 & pids+=($!)
       worker $PREFIX-N57-C457-$TIMESTAMP 9.0 0.00630957344480193 15.848931924611142 & pids+=($!)
       worker $PREFIX-N57-C458-$TIMESTAMP 9.0 0.00630957344480193 25.11886431509581 & pids+=($!)
       worker $PREFIX-N57-C459-$TIMESTAMP 9.0 0.00630957344480193 39.810717055349734 & pids+=($!)
       worker $PREFIX-N57-C460-$TIMESTAMP 9.0 0.00630957344480193 63.09573444801933 & pids+=($!)
       worker $PREFIX-N57-C461-$TIMESTAMP 9.0 0.00630957344480193 100.0 & pids+=($!)
       worker $PREFIX-N57-C462-$TIMESTAMP 9.0 0.01 1.0 & pids+=($!)
       worker $PREFIX-N57-C463-$TIMESTAMP 9.0 0.01 1.5848931924611136 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    58)
       worker $PREFIX-N58-C464-$TIMESTAMP 9.0 0.01 2.51188643150958 & pids+=($!)
       worker $PREFIX-N58-C465-$TIMESTAMP 9.0 0.01 3.981071705534973 & pids+=($!)
       worker $PREFIX-N58-C466-$TIMESTAMP 9.0 0.01 6.309573444801933 & pids+=($!)
       worker $PREFIX-N58-C467-$TIMESTAMP 9.0 0.01 10.0 & pids+=($!)
       worker $PREFIX-N58-C468-$TIMESTAMP 9.0 0.01 15.848931924611142 & pids+=($!)
       worker $PREFIX-N58-C469-$TIMESTAMP 9.0 0.01 25.11886431509581 & pids+=($!)
       worker $PREFIX-N58-C470-$TIMESTAMP 9.0 0.01 39.810717055349734 & pids+=($!)
       worker $PREFIX-N58-C471-$TIMESTAMP 9.0 0.01 63.09573444801933 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    59)
       worker $PREFIX-N59-C472-$TIMESTAMP 9.0 0.01 100.0 & pids+=($!)
       worker $PREFIX-N59-C473-$TIMESTAMP 9.0 0.01584893192461114 1.0 & pids+=($!)
       worker $PREFIX-N59-C474-$TIMESTAMP 9.0 0.01584893192461114 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N59-C475-$TIMESTAMP 9.0 0.01584893192461114 2.51188643150958 & pids+=($!)
       worker $PREFIX-N59-C476-$TIMESTAMP 9.0 0.01584893192461114 3.981071705534973 & pids+=($!)
       worker $PREFIX-N59-C477-$TIMESTAMP 9.0 0.01584893192461114 6.309573444801933 & pids+=($!)
       worker $PREFIX-N59-C478-$TIMESTAMP 9.0 0.01584893192461114 10.0 & pids+=($!)
       worker $PREFIX-N59-C479-$TIMESTAMP 9.0 0.01584893192461114 15.848931924611142 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    60)
       worker $PREFIX-N60-C480-$TIMESTAMP 9.0 0.01584893192461114 25.11886431509581 & pids+=($!)
       worker $PREFIX-N60-C481-$TIMESTAMP 9.0 0.01584893192461114 39.810717055349734 & pids+=($!)
       worker $PREFIX-N60-C482-$TIMESTAMP 9.0 0.01584893192461114 63.09573444801933 & pids+=($!)
       worker $PREFIX-N60-C483-$TIMESTAMP 9.0 0.01584893192461114 100.0 & pids+=($!)
       worker $PREFIX-N60-C484-$TIMESTAMP 9.0 0.025118864315095822 1.0 & pids+=($!)
       worker $PREFIX-N60-C485-$TIMESTAMP 9.0 0.025118864315095822 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N60-C486-$TIMESTAMP 9.0 0.025118864315095822 2.51188643150958 & pids+=($!)
       worker $PREFIX-N60-C487-$TIMESTAMP 9.0 0.025118864315095822 3.981071705534973 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    61)
       worker $PREFIX-N61-C488-$TIMESTAMP 9.0 0.025118864315095822 6.309573444801933 & pids+=($!)
       worker $PREFIX-N61-C489-$TIMESTAMP 9.0 0.025118864315095822 10.0 & pids+=($!)
       worker $PREFIX-N61-C490-$TIMESTAMP 9.0 0.025118864315095822 15.848931924611142 & pids+=($!)
       worker $PREFIX-N61-C491-$TIMESTAMP 9.0 0.025118864315095822 25.11886431509581 & pids+=($!)
       worker $PREFIX-N61-C492-$TIMESTAMP 9.0 0.025118864315095822 39.810717055349734 & pids+=($!)
       worker $PREFIX-N61-C493-$TIMESTAMP 9.0 0.025118864315095822 63.09573444801933 & pids+=($!)
       worker $PREFIX-N61-C494-$TIMESTAMP 9.0 0.025118864315095822 100.0 & pids+=($!)
       worker $PREFIX-N61-C495-$TIMESTAMP 9.0 0.039810717055349734 1.0 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    62)
       worker $PREFIX-N62-C496-$TIMESTAMP 9.0 0.039810717055349734 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N62-C497-$TIMESTAMP 9.0 0.039810717055349734 2.51188643150958 & pids+=($!)
       worker $PREFIX-N62-C498-$TIMESTAMP 9.0 0.039810717055349734 3.981071705534973 & pids+=($!)
       worker $PREFIX-N62-C499-$TIMESTAMP 9.0 0.039810717055349734 6.309573444801933 & pids+=($!)
       worker $PREFIX-N62-C500-$TIMESTAMP 9.0 0.039810717055349734 10.0 & pids+=($!)
       worker $PREFIX-N62-C501-$TIMESTAMP 9.0 0.039810717055349734 15.848931924611142 & pids+=($!)
       worker $PREFIX-N62-C502-$TIMESTAMP 9.0 0.039810717055349734 25.11886431509581 & pids+=($!)
       worker $PREFIX-N62-C503-$TIMESTAMP 9.0 0.039810717055349734 39.810717055349734 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    63)
       worker $PREFIX-N63-C504-$TIMESTAMP 9.0 0.039810717055349734 63.09573444801933 & pids+=($!)
       worker $PREFIX-N63-C505-$TIMESTAMP 9.0 0.039810717055349734 100.0 & pids+=($!)
       worker $PREFIX-N63-C506-$TIMESTAMP 9.0 0.06309573444801936 1.0 & pids+=($!)
       worker $PREFIX-N63-C507-$TIMESTAMP 9.0 0.06309573444801936 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N63-C508-$TIMESTAMP 9.0 0.06309573444801936 2.51188643150958 & pids+=($!)
       worker $PREFIX-N63-C509-$TIMESTAMP 9.0 0.06309573444801936 3.981071705534973 & pids+=($!)
       worker $PREFIX-N63-C510-$TIMESTAMP 9.0 0.06309573444801936 6.309573444801933 & pids+=($!)
       worker $PREFIX-N63-C511-$TIMESTAMP 9.0 0.06309573444801936 10.0 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    64)
       worker $PREFIX-N64-C512-$TIMESTAMP 9.0 0.06309573444801936 15.848931924611142 & pids+=($!)
       worker $PREFIX-N64-C513-$TIMESTAMP 9.0 0.06309573444801936 25.11886431509581 & pids+=($!)
       worker $PREFIX-N64-C514-$TIMESTAMP 9.0 0.06309573444801936 39.810717055349734 & pids+=($!)
       worker $PREFIX-N64-C515-$TIMESTAMP 9.0 0.06309573444801936 63.09573444801933 & pids+=($!)
       worker $PREFIX-N64-C516-$TIMESTAMP 9.0 0.06309573444801936 100.0 & pids+=($!)
       worker $PREFIX-N64-C517-$TIMESTAMP 9.0 0.1 1.0 & pids+=($!)
       worker $PREFIX-N64-C518-$TIMESTAMP 9.0 0.1 1.5848931924611136 & pids+=($!)
       worker $PREFIX-N64-C519-$TIMESTAMP 9.0 0.1 2.51188643150958 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
    65)
       worker $PREFIX-N65-C520-$TIMESTAMP 9.0 0.1 3.981071705534973 & pids+=($!)
       worker $PREFIX-N65-C521-$TIMESTAMP 9.0 0.1 6.309573444801933 & pids+=($!)
       worker $PREFIX-N65-C522-$TIMESTAMP 9.0 0.1 10.0 & pids+=($!)
       worker $PREFIX-N65-C523-$TIMESTAMP 9.0 0.1 15.848931924611142 & pids+=($!)
       worker $PREFIX-N65-C524-$TIMESTAMP 9.0 0.1 25.11886431509581 & pids+=($!)
       worker $PREFIX-N65-C525-$TIMESTAMP 9.0 0.1 39.810717055349734 & pids+=($!)
       worker $PREFIX-N65-C526-$TIMESTAMP 9.0 0.1 63.09573444801933 & pids+=($!)
       worker $PREFIX-N65-C527-$TIMESTAMP 9.0 0.1 100.0 & pids+=($!)
       for pid in ${pids[*]}; do wait $pid; done  
    ;;
esac
echo "$PREFIX-N$(printf "%02d" $SLURM_ARRAY_TASK_ID)-CXXX-$TIMESTAMP : DONE MAIN RUN @"$(date)

TOTREPORT=$PREFIX-N$(printf "%02d" $SLURM_ARRAY_TASK_ID)-CXXX-$TIMESTAMP
cp homeostasis-G-CONV-TRN-$SLURM_ARRAY_TASK_ID.stdout $TOTREPORT.stdout && \
cp homeostasis-G-CONV-TRN-$SLURM_ARRAY_TASK_ID.stderr $TOTREPORT.stderr && \
xz -9 $TOTREPORT.stdout $TOTREPORT.stderr && \
echo 'FINISHED @'$(date)
