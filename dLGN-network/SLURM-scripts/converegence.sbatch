#!/bin/sh
#SBATCH -o homeostasis-G-CONV-%a.stdout
#SBATCH -e homeostasis-G-CONV-%a.stderr
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

#SBATCH -J LGN-TRN

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
KEYLET="CONV"
SIMPRMS="/Figures/enable=False /sim/parallel=4"
TRARGETFD="0.50"
TIMESTAMP=$(date "+%Y%m%d-%H%M%S")
PREFIX=$PREFIX-$KEYLET-TFR$TRARGETFD

worker(){
    SIGMA=$1
    R=$2
    PPREFIX=$PREFIX-$(printf "SIGMA%02d" $SIGMA)
    POSTFIX=R$R
    PREFTMPST=$PPREFIX-NMDA-$POSTFIX
    rm -f $PREFTMPST.log $TMPDIR/$PREFTMPST.stkdata $TMPDIR/$PREFTMPST-simstate.stkdata $PREFTMPST-FR.json $PREFTMPST.stkdb
    python dLGNnetwork.py -l DEBUG -L $PREFTMPST.log \
        -o $PREFTMPST.stkdb -m NMDA\ PREFIX:$PREFTMPST\ CON:$SIGMA\ I:0 \
        $SIMPRMS /sim/record/cont=False \
        /network/load=False /network/save=False \
        /sim/Tmax=-1 \
        $NRNPRMS \
        /network/gj/geom/p=0 /block/gjcon=True $GJPRMS \
        /network/syn/geom/unit=\'G\' /network/syn/geom/pmax=1 /network/syn/geom/sig=float\($SIGMA\) \
        /network/syn/gsyn=-1. /network/syn/sig2gsyn=float\($SIGMA\) /network/syn/rand=False \
        /network/trn/enable=False /network/cx/enable=False \
        /network/home/enable=True  /network/home/continue=False /network/home/slope=0.05 /network/home/gmax=-10. /network/home/target_fr=$TRARGETFD \
        /sim/record/file=\'$TMPDIR/$PREFTMPST-ndata.stkdata\' /sim/record/gsyn=True \
        /FR/Overall=\"$PREFTMPST-FR.json\" \
        /sim/state/save=\'$TMPDIR/$PREFTMPST-simstate.stkdata\' \
        /sim/timestamp=\"SLURM$SLURM_ARRAY_TASK_ID-$PREFTMPST-I00\" \
        || { echo "FAILED I00"; exit 1 ; }

    let i=0
    while python FRchecker.py $PREFTMPST-FR.json $TRARGETFD
    do
        let i=$i+1
        python dLGNnetwork.py -l DEBUG -L $PREFTMPST.log \
            -o $PREFTMPST.stkdb -m NMDA\ PREFIX:$PREFTMPST\ CON:$SIGMA\ I:$i \
            $SIMPRMS /sim/record/cont=False \
            /network/load=False /network/save=False \
            /sim/Tmax=-1 \
            $NRNPRMS \
            /network/gj/geom/p=0 /block/gjcon=True $GJPRMS \
            /network/syn/geom/unit=\'G\' /network/syn/geom/pmax=1 /network/syn/geom/sig=float\($SIGMA\) \
            /network/syn/gsyn=-1. /network/syn/sig2gsyn=float\($SIGMA\) /network/syn/rand=False \
            /network/trn/enable=False /network/cx/enable=False \
            /network/home/enable=True  /network/home/continue=False /network/home/slope=0.05 /network/home/gmax=-10. /network/home/target_fr=$TRARGETFD \
            /sim/record/file=\'$TMPDIR/$PREFTMPST-ndata.stkdata\' /sim/record/gsyn=True \
            /FR/Overall=\"$PREFTMPST-FR.json\" \
            /sim/state/load=\'$TMPDIR/$PREFTMPST-simstate.stkdata\' /sim/state/save=\'$TMPDIR/$PREFTMPST-simstate.stkdata\' \
            /sim/timestamp=\"SLURM$SLURM_ARRAY_TASK_ID-$PREFTMPST-I$(printf "%02d" $i)\" \
            || { echo "FAILED I$i" ; exit 1 ; }
        (($i>11))&& break
    done


    PREFTMPST=$PPREFIX-AMPA-$POSTFIX
    rm -f $PREFTMPST.log $TMPDIR/$PREFTMPST.stkdata $TMPDIR/$PREFTMPST-simstate.stkdata $PREFTMPST-FR.json $PREFTMPST.stkdb
    python dLGNnetwork.py -l DEBUG -L $PREFTMPST.log \
        -o $PREFTMPST.stkdb -m NMDA\ PREFIX:$PREFTMPST\ CON:$SIGMA\ I:0 \
        $SIMPRMS /sim/record/cont=False \
        /network/load=False /network/save=False \
        /sim/Tmax=-1 \
        $NRNPRMS \
        /network/gj/geom/p=0 /block/gjcon=True $GJPRMS \
        /network/syn/geom/unit=\'G\' /network/syn/geom/pmax=1 /network/syn/geom/sig=float\($SIGMA\) \
        /network/syn/gsyn=-1. /network/syn/sig2gsyn=float\($SIGMA\) /network/syn/rand=False \
        /network/syn/NMDA/p=0. \
        /network/trn/enable=False /network/cx/enable=False \
        /network/home/enable=True  /network/home/continue=False /network/home/slope=0.05 /network/home/gmax=-10. /network/home/target_fr=$TRARGETFD \
        /sim/record/file=\'$TMPDIR/$PREFTMPST-ndata.stkdata\' /sim/record/gsyn=True \
        /FR/Overall=\"$PREFTMPST-FR.json\" \
        /sim/state/save=\'$TMPDIR/$PREFTMPST-simstate.stkdata\' \
        /sim/timestamp=\"SLURM$SLURM_ARRAY_TASK_ID-$PREFTMPST-I00\" \
        || { echo "FAILED I00"; exit 1 ; }

    let i=0
    while python FRchecker.py $PREFTMPST-FR.json $TRARGETFD
    do
        let i=$i+1
        python dLGNnetwork.py -l DEBUG -L $PREFTMPST.log \
            -o $PREFTMPST.stkdb -m NMDA\ PREFIX:$PREFTMPST\ CON:$SIGMA\ I:$i \
            $SIMPRMS /sim/record/cont=False \
            /network/load=False /network/save=False \
            /sim/Tmax=-1 \
            $NRNPRMS \
            /network/gj/geom/p=0 /block/gjcon=True $GJPRMS \
            /network/syn/geom/unit=\'G\' /network/syn/geom/pmax=1 /network/syn/geom/sig=float\($SIGMA\) \
            /network/syn/gsyn=-1. /network/syn/sig2gsyn=float\($SIGMA\) /network/syn/rand=False \
            /network/syn/NMDA/p=0. \
            /network/trn/enable=False /network/cx/enable=False \
            /network/home/enable=True  /network/home/continue=False /network/home/slope=0.05 /network/home/gmax=-10. /network/home/target_fr=$TRARGETFD \
            /sim/record/file=\'$TMPDIR/$PREFTMPST-ndata.stkdata\' /sim/record/gsyn=True \
            /FR/Overall=\"$PREFTMPST-FR.json\" \
            /sim/state/load=\'$TMPDIR/$PREFTMPST-simstate.stkdata\' /sim/state/save=\'$TMPDIR/$PREFTMPST-simstate.stkdata\' \
            /sim/timestamp=\"SLURM$SLURM_ARRAY_TASK_ID-$PREFTMPST-I$(printf "%02d" $i)\" \
            || { echo "FAILED I$i" ; exit 1 ; }
        (($i>11))&& break
    done
    echo "$PPREFIX-NMDA/AMPA-$POSTFIX : finished main ran"
    pushd $TMPDIR && \
    {
       localpid=()
       xz -T0 -9  $PPREFIX-NMDA-$POSTFIX-ndata.stkdata    & localpid+=($!) 
       xz -T0 -9  $PPREFIX-AMPA-$POSTFIX-ndata.stkdata    & localpid+=($!) 
       xz -T0 -9  $PPREFIX-NMDA-$POSTFIX-simstate.stkdata & localpid+=($!) 
       xz -T0 -9  $PPREFIX-AMPA-$POSTFIX-simstate.stkdata & localpid+=($!) 
       for pid in ${localpid[*]}; do wait $pid; done  ;
    }
    popd && \
    for i in $TMPDIR/$PPREFIX-*-$POSTFIX*.stkdata.xz
    do
        mv $i .
    done && \

    localpid=()
    zip -r $PREFTMPST-scripts-log-FR.zip \
        *.py lmods mods simtoolkit Maccione2014_P9_29March11_control_SpkTs_bursts_filtered.h5 \
        P07-selected-checked-gmin.json selectedP07N04v05.json \
        $PPREFIX-*-$POSTFIX-FR.json $PPREFIX-*-$POSTFIX.log $PPREFIX-*-$POSTFIX.stkdb\
        $0 & localpid+=($!)
    xz -9 $PREFTMPST-NMDA.log & localpid+=($!)
    xz -9 $PREFTMPST-AMPA.log & localpid+=($!)
    xz -9 $PREFTMPST-NMDA-blockTRN.log & localpid+=($!)
    xz -9 $PREFTMPST-AMPA-blockTRN.log & localpid+=($!)
    for pid in ${localpid[*]}; do wait $pid; done && \
    echo "$PPREFIX-NMDA/AMPA-$POSTFIX : data has been arXived"
}

pids=()
for REP in $(seq 0 9)
do
    worker $SLURM_ARRAY_TASK_ID $REP & pids+=($!)
done
for pid in ${pids[*]}; do wait $pid; done
cp homeostasis-G-CONV-$SLURM_ARRAY_TASK_ID.stdout $PREFIX-SIGMA$(printf "%02d" $SLURM_ARRAY_TASK_ID)-RX-$TIMESTAMP.stdout && \
cp homeostasis-G-CONV-$SLURM_ARRAY_TASK_ID.stderr $PREFIX-SIGMA$(printf "%02d" $SLURM_ARRAY_TASK_ID)-RX-$TIMESTAMP.stderr && \
xz -9 $PREFIX-SIGMA$(printf "%02d" $SLURM_ARRAY_TASK_ID)-RX-$TIMESTAMP.stdout $PREFIX-N$(printf "%02d" $SLURM_ARRAY_TASK_ID)-RX-$TIMESTAMP.stderr && \
echo 'FINISHED @'$(date)
