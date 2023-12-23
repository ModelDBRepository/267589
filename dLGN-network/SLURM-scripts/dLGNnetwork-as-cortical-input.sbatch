#!/bin/sh
#SBATCH -o homeostasis-G-LGN4CTX.stdout
#SBATCH -e homeostasis-G-LGN4CTX.stderr
##MAIN>>
#SBATCH -t 2-12:00:00
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

#SBATCH -J LGN4CTX

module load gcc
module load openmpi/gcc/64/4.1.0
module load gsl/2.6
module load hdf5/1.10.5

PATH=$HOME/.local/bin:$HOME/bin:$PATH
LD_LIBRARY_PATH=$HOME/.local/lib:$LD_LIBRARY_PATH
export PATH LD_LIBRARY_PATH

date


TMPDIR="/tmp"
[ -d $ $TMPDIR ]||{ mkdir $TMPDIR ;}

PREFIX="homeostasis-G"
KEYLET="LGN4CTX" 
SIMPRMS="/Figures/enable=False /sim/parallel=4"
TRARGETFD="0.50"
TIMESTAMP=$(date "+%Y%m%d-%H%M%S")
PREFIX=$PREFIX-$KEYLET-TFR$TRARGETFD


worker(){
    PPREFIX=$PREFIX-SIGMA04
    POSTFIX=R$1
    PREFTMPST=$PPREFIX-NMDA-$POSTFIX
    xz -d $TMPDIR/homeostasis-G-CONV-TFR0.50-SIGMA04-NMDA-R$1-simstate.stkdata.xz
    rm -f $TMPDIR/$PREFTMPST-2H.log $TMPDIR/$PREFTMPST-2H-ndata.stkdata $TMPDIR/$PREFTMPST-simstate.stkdata $PREFTMPST-2H-FR.json $PREFTMPST-2H.stkdb
    python dLGNnetwork.py -l DEBUG -L $TMPDIR/$PREFTMPST-2H.log \
        -o $PREFTMPST-2H.stkdb -m NMDA\ PREFIX:$PREFTMPST-2H\ CON:$SIGMA\ I:0 \
        $SIMPRMS /sim/record/cont=False \
        /network/load=False /network/save=False \
        /sim/Tmax=-1 \
        $NRNPRMS \
        /network/gj/geom/p=0 /block/gjcon=True $GJPRMS \
        /network/syn/geom/unit=\'G\' /network/syn/geom/pmax=1 /network/syn/geom/sig=4. \
        /network/syn/gsyn=-1. /network/syn/sig2gsyn=4. /network/syn/rand=False \
        /network/trn/enable=False /network/cx/enable=False \
        /network/home/enable=True  /network/home/continue=False /network/home/slope=0.05 /network/home/gmax=-10. /network/home/target_fr=$TRARGETFD \
        /sim/record/file=\'$TMPDIR/$PREFTMPST-2H-ndata.stkdata\' /sim/record/gsyn=True \
        /FR/Overall=\"$PREFTMPST-2H-FR.json\" \
        /sim/state/load=\'$TMPDIR/homeostasis-G-CONV-TFR0.50-SIGMA04-NMDA-R$1-simstate.stkdata\' /sim/state/save=\'$TMPDIR/$PREFTMPST-2H-simstate.stkdata\' \
        /sim/timestamp=\"SLURM$SLURM_ARRAY_TASK_ID-$PREFTMPST-2H-I00\" \
        || { echo "$PREFTMPST FAILED I00"; exit 1 ; }
    rm -f $TMPDIR/homeostasis-G-CONV-TFR0.50-SIGMA04-NMDA-R$1-simstate.stkdata
    
    for i in $(seq 1 5)
    do
        python dLGNnetwork.py -l DEBUG -L $TMPDIR/$PREFTMPST-2H.log \
            -o $PREFTMPST-2H.stkdb -m NMDA\ PREFIX:$PREFTMPST-2H\ CON:$SIGMA\ I:$i \
            $SIMPRMS /sim/record/cont=False \
            /network/load=False /network/save=False \
            /sim/Tmax=-1 \
            $NRNPRMS \
            /network/gj/geom/p=0 /block/gjcon=True $GJPRMS \
            /network/syn/geom/unit=\'G\' /network/syn/geom/pmax=1 /network/syn/geom/sig=4. \
            /network/syn/gsyn=-1. /network/syn/sig2gsyn=4. /network/syn/rand=False \
            /network/trn/enable=False /network/cx/enable=False \
            /network/home/enable=True  /network/home/continue=False /network/home/slope=0.05 /network/home/gmax=-10. /network/home/target_fr=$TRARGETFD \
            /sim/record/file=\'$TMPDIR/$PREFTMPST-2H-ndata.stkdata\' /sim/record/gsyn=True \
            /FR/Overall=\"$PREFTMPST-2H-FR.json\" \
            /sim/state/load=\'$TMPDIR/$PREFTMPST-2H-simstate.stkdata\' /sim/state/save=\'$TMPDIR/$PREFTMPST-2H-simstate.stkdata\' \
            /sim/timestamp=\"SLURM$SLURM_ARRAY_TASK_ID-$PREFTMPST-2H-I$(printf "%02d" $i)\" \
            || { echo "$PREFTMPST FAILED I$i" ; exit 1 ; }
    done

    PREFTMPST=$PPREFIX-AMPA-$POSTFIX
    xz -d $TMPDIR/homeostasis-G-CONV-TFR0.50-SIGMA04-AMPA-R$1-simstate.stkdata.xz
    rm -f $TMPDIR/$PREFTMPST-2H.log $TMPDIR/$PREFTMPST-2H-ndata.stkdata $TMPDIR/$PREFTMPST-2H-simstate.stkdata $PREFTMPST-2H-FR.json $PREFTMPST-2H.stkdb
    python dLGNnetwork.py -l DEBUG -L $TMPDIR/$PREFTMPST-2H.log \
        -o $PREFTMPST-2H.stkdb -m NMDA\ PREFIX:$PREFTMPST-2H\ CON:$SIGMA\ I:0 \
        $SIMPRMS /sim/record/cont=False \
        /network/load=False /network/save=False \
        /sim/Tmax=-1 \
        $NRNPRMS \
        /network/gj/geom/p=0 /block/gjcon=True $GJPRMS \
        /network/syn/geom/unit=\'G\' /network/syn/geom/pmax=1 /network/syn/geom/sig=4. \
        /network/syn/gsyn=-1. /network/syn/sig2gsyn=4. /network/syn/rand=False \
        /network/syn/NMDA/p=0. \
        /network/trn/enable=False /network/cx/enable=False \
        /network/home/enable=True  /network/home/continue=False /network/home/slope=0.05 /network/home/gmax=-10. /network/home/target_fr=$TRARGETFD \
        /sim/record/file=\'$TMPDIR/$PREFTMPST-2H-ndata.stkdata\' /sim/record/gsyn=True \
        /FR/Overall=\"$PREFTMPST-2H-FR.json\" \
        /sim/state/load=\'$TMPDIR/homeostasis-G-CONV-TFR0.50-SIGMA04-AMPA-R$1-simstate.stkdata\' /sim/state/save=\'$TMPDIR/$PREFTMPST-2H-simstate.stkdata\' \
        /sim/timestamp=\"SLURM$SLURM_ARRAY_TASK_ID-$PREFTMPST-2H-I00\" \
        || { echo "$PREFTMPST FAILED I00"; exit 1 ; }
    rm -f $TMPDIR/homeostasis-G-CONV-TFR0.50-SIGMA04-AMPA-R$1-simstate.stkdata
    
    for i in $(seq 1 5)
    do
        python dLGNnetwork.py -l DEBUG -L $TMPDIR/$PREFTMPST-2H.log \
            -o $PREFTMPST-2H.stkdb -m NMDA\ PREFIX:$PREFTMPST-2H\ CON:$SIGMA\ I:$i \
            $SIMPRMS /sim/record/cont=False \
            /network/load=False /network/save=False \
            /sim/Tmax=-1 \
            $NRNPRMS \
            /network/gj/geom/p=0 /block/gjcon=True $GJPRMS \
            /network/syn/geom/unit=\'G\' /network/syn/geom/pmax=1 /network/syn/geom/sig=4. \
            /network/syn/gsyn=-1. /network/syn/sig2gsyn=4. /network/syn/rand=False \
            /network/syn/NMDA/p=0. \
            /network/trn/enable=False /network/cx/enable=False \
            /network/home/enable=True  /network/home/continue=False /network/home/slope=0.05 /network/home/gmax=-10. /network/home/target_fr=$TRARGETFD \
            /sim/record/file=\'$TMPDIR/$PREFTMPST-2H-ndata.stkdata\' /sim/record/gsyn=True \
            /FR/Overall=\"$PREFTMPST-2H-FR.json\" \
            /sim/state/load=\'$TMPDIR/$PREFTMPST-2H-simstate.stkdata\' /sim/state/save=\'$TMPDIR/$PREFTMPST-2H-simstate.stkdata\' \
            /sim/timestamp=\"SLURM$SLURM_ARRAY_TASK_ID-$PREFTMPST-2H-I$(printf "%02d" $i)\" \
            || { echo "$PREFTMPST FAILED I$i" ; exit 1 ; }
    done
    echo "$PPREFIX-NMDA/AMPA-$POSTFIX : finished main ran"
    localpid=()
    xz -9  $TMPDIR/$PPREFIX-NMDA-$POSTFIX-2H-ndata.stkdata    & localpid+=($!) 
    xz -9  $TMPDIR/$PPREFIX-AMPA-$POSTFIX-2H-ndata.stkdata    & localpid+=($!) 
    xz -9  $TMPDIR/$PPREFIX-NMDA-$POSTFIX-2H-simstate.stkdata & localpid+=($!) 
    xz -9  $TMPDIR/$PPREFIX-AMPA-$POSTFIX-2H-simstate.stkdata & localpid+=($!) 
    xz -9  $TMPDIR/$PPREFIX-NMDA-$POSTFIX-2H.log & localpid+=($!)
    xz -9  $TMPDIR/$PPREFIX-AMPA-$POSTFIX-2H.log & localpid+=($!)
    for pid in ${localpid[*]}; do wait $pid; done  ;
    
    mv $TMPDIR/$PPREFIX-*-$POSTFIX-2H* .

    zip -r $PREFTMPST-scripts-db-FR.zip \
        *.py lmods mods simtoolkit Maccione2014_P9_29March11_control_SpkTs_bursts_filtered.h5 \
        P07-selected-checked-gmin.json selectedP07N04v05.json \
        $PPREFIX-*-$POSTFIX-2H-FR.json $PPREFIX-*-$POSTFIX-2H.stkdb\
        $0
    echo "$PPREFIX-NMDA/AMPA-$POSTFIX : data has been arXived"
}


    
pids=()
for REP in $(seq 0 9)
do
    worker $REP & pids+=($!)
done
for pid in ${pids[*]}; do wait $pid; done
echo 'FINISHED @'$(date) 'arXiving stdout/stderr'
xz -9 homeostasis-G-LGN4CTX.stdout homeostasis-G-LGN4CTX.stderr



