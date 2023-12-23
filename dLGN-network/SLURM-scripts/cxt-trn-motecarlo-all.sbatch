#!/bin/sh
#SBATCH -o homeostasis-G-CONV-TRN-CXT-TFR1.00-N%02a.stdout
#SBATCH -e homeostasis-G-CONV-TRN-CXT-TFR1.00-N%02a.stderr
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

#SBATCH -J CONV-TRN-CTX

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
KEYLET="CONV-TRN-CXT"
TIMESTAMP=$(date "+%Y%m%d-%H%M%S")
TRARGETFD="1.00"
PREFIX=$PREFIX-$KEYLET-TFR$TRARGETFD
SIMPRMS="/Figures/enable=False /sim/parallel=4"
worker(){
    #ARGS:
    #  Sim name
    #  SIGMA
    #  TRN gsyn 
    #  TRN delay
    #  CX  gsyn/rGC gsyn
    #  CX delay

    PREFTMPST=$1 ; SIGMA=$2 ; TRNGSYN=$3 ; TRNDLY=$4 ; CXGSYN=$5 ; CXDLY=$6

       
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
              -o $PREFTMPST.stkdb -m NMDA\ PREFIX:$PREFTMPST\ SIGMA:$SIGMA\ TRNGSYN:$TRNGSYN\ TRNDLY:$TRNDLY\ CXTGSYN:$CXGSYN\ CXTDLY:$CXDLY\ R:$R\ I:0 \
              $SIMPRMS /sim/record/cont=False \
              /network/load=False /network/save=False \
              /sim/Tmax=-1 \
              $NRNPRMS \
              /network/gj/geom/p=0 /block/gjcon=True $GJPRMS \
              /network/syn/geom/unit=\'G\' /network/syn/geom/pmax=1 /network/syn/geom/sig=float\($SIGMA\) \
              /network/syn/gsyn=-1. /network/syn/sig2gsyn=float\($SIGMA\) /network/syn/rand=False \
              /network/trn/enable=True /network/trn/gsyn=$TRNGSYN /network/trn/delay=$TRNDLY $TRNPRMS \
              /network/cx/enable=True /network/cx/gsyn=$CXGSYN /network/cx/delay=$CXDLY $CXPRMS \
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
                     -o $PREFTMPST.stkdb -m NMDA\ PREFIX:$PREFTMPST\ SIGMA:$SIGMA\ TRNGSYN:$TRNGSYN\ TRNDLY:$TRNDLY\ CXTGSYN:$CXGSYN\ CXTDLY:$CXDLY\ R:$R\ I:$i \
                     $SIMPRMS /sim/record/cont=False \
                     /network/load=False /network/save=False \
                     /sim/Tmax=-1 \
                     $NRNPRMS \
                     /network/gj/geom/p=0 /block/gjcon=True $GJPRMS \
                     /network/syn/geom/unit=\'G\' /network/syn/geom/pmax=1 /network/syn/geom/sig=float\($SIGMA\) \
                     /network/syn/gsyn=-1. /network/syn/sig2gsyn=float\($SIGMA\) /network/syn/rand=False \
                     /network/trn/enable=True /network/trn/gsyn=$TRNGSYN /network/trn/delay=$TRNDLY $TRNPRMS \
                     /network/cx/enable=True /network/cx/gsyn=$CXGSYN /network/cx/delay=$CXDLY $CXPRMS \
                     /network/home/enable=True  /network/home/continue=False /network/home/slope=0.05 /network/home/gmax=-10. /network/home/target_fr=$TRARGETFD \
                     /sim/record/file=\'$TMPDIR/$WORKPREFIX.stkdata\' /sim/record/gsyn=True \
                     /FR/Overall=\"$WORKPREFIX-FR.json\" \
                     /sim/state/load=\'$TMPDIR/$WORKPREFIX-simstate.stkdata\' /sim/state/save=\'$TMPDIR/$WORKPREFIX-simstate.stkdata\' \
                     || { echo "$WORKPREFIX FAILED I$i" ; exit 1 ; }
              (($i>11))&& break
       done
       python dLGNnetwork.py -l DEBUG -L $WORKPREFIX-blockTRN.log \
              -o $PREFTMPST.stkdb -m NMDA\ PREFIX:$PREFTMPST\ SIGMA:$SIGMA\ TRN:BLOCKED\ CXTGSYN:$CXGSYN\ CXTDLY:$CXDLY\ R:$R \
              $SIMPRMS /sim/record/cont=False \
              /network/load=False /network/save=False \
              /sim/Tmax=-1 \
              $NRNPRMS \
              /network/gj/geom/p=0 /block/gjcon=True $GJPRMS \
              /network/syn/geom/unit=\'G\' /network/syn/geom/pmax=1 /network/syn/geom/sig=float\($SIGMA\) \
              /network/syn/gsyn=-1. /network/syn/sig2gsyn=float\($SIGMA\) /network/syn/rand=False \
              /network/trn/enable=False /network/trn/gsyn=$TRNGSYN /network/trn/delay=$TRNDLY $TRNPRMS \
              /network/cx/enable=True /network/cx/gsyn=$CXGSYN /network/cx/delay=$CXDLY $CXPRMS \
              /network/home/enable=False  /network/home/continue=False /network/home/slope=0.05 /network/home/gmax=-10. /network/home/target_fr=$TRARGETFD \
              /sim/record/file=\'$TMPDIR/$WORKPREFIX-blockTRN.stkdata\' /sim/record/gsyn=True \
              /FR/Overall=\"$WORKPREFIX-blockTRN-FR.json\" \
              /sim/state/load=\'$TMPDIR/$WORKPREFIX-simstate.stkdata\' \
              || { echo "$WORKPREFIX FAILED TRNBLK" ; }
#              || { echo "$WORKPREFIX FAILED TRNBLK" ; exit 1 ; }

       python dLGNnetwork.py -l DEBUG -L $WORKPREFIX-blockCTX.log \
              -o $PREFTMPST.stkdb -m NMDA\ PREFIX:$PREFTMPST\ SIGMA:$SIGMA\ TRNGSYN:$TRNGSYN\ TRNDLY:$TRNDLY\ CXT:BLOCKED\ R:$R\ I:$i \
              $SIMPRMS /sim/record/cont=False \
              /network/load=False /network/save=False \
              /sim/Tmax=-1 \
              $NRNPRMS \
              /network/gj/geom/p=0 /block/gjcon=True $GJPRMS \
              /network/syn/geom/unit=\'G\' /network/syn/geom/pmax=1 /network/syn/geom/sig=float\($SIGMA\) \
              /network/syn/gsyn=-1. /network/syn/sig2gsyn=float\($SIGMA\) /network/syn/rand=False \
              /network/trn/enable=False /network/trn/gsyn=$TRNGSYN /network/trn/delay=$TRNDLY $TRNPRMS \
              /network/cx/enable=False /network/cx/gsyn=$CXGSYN /network/cx/delay=$CXDLY $CXPRMS \
              /network/home/enable=False  /network/home/continue=False /network/home/slope=0.05 /network/home/gmax=-10. /network/home/target_fr=$TRARGETFD \
              /sim/record/file=\'$TMPDIR/$WORKPREFIX-blockCTX.stkdata\' /sim/record/gsyn=True \
              /FR/Overall=\"$WORKPREFIX-blockCTX-FR.json\" \
              /sim/state/load=\'$TMPDIR/$WORKPREFIX-simstate.stkdata\' \
              || { echo "$WORKPREFIX FAILED CTXBLK" ; }
#              || { echo "$WORKPREFIX FAILED CTXBLK" ; exit 1 ; }

       localpid=()
       xz -T0 -9 $TMPDIR/$WORKPREFIX.stkdata  & localpid+=($!) 
       xz -T0 -9 $TMPDIR/$WORKPREFIX-blockTRN.stkdata  & localpid+=($!) 
       xz -T0 -9 $TMPDIR/$WORKPREFIX-blockCTX.stkdata  & localpid+=($!) 
       xz -T0 -9 $TMPDIR/$WORKPREFIX-simstate.stkdata  & localpid+=($!) 
       xz -T0 -9 $WORKPREFIX.log & localpid+=($!)
       xz -T0 -9 $WORKPREFIX-blockTRN.log & localpid+=($!)
       xz -T0 -9 $WORKPREFIX-blockCTX.log & localpid+=($!)
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
if [ -z $1 ]; then
    echo "Need file with parameters"
    exit 1
fi
echo "SOURCE $1"
source $(pwd)/$1

echo "$PREFIX-N$(printf "%02d" $SLURM_ARRAY_TASK_ID)-CXXX-$TIMESTAMP : DONE MAIN RUN @"$(date)

TOTREPORT=$PREFIX-N$(printf "%02d" $SLURM_ARRAY_TASK_ID)-CXXX-$TIMESTAMP
cp homeostasis-G-CONV-TRN-CXT-TFR1.00-N$SLURM_ARRAY_TASK_ID.stdout $TOTREPORT.stdout && \
cp homeostasis-G-CONV-TRN-CXT-TFR1.00-N$SLURM_ARRAY_TASK_ID.stderr $TOTREPORT.stderr && \
xz -9 $TOTREPORT.stdout $TOTREPORT.stderr && \
echo 'FINISHED @'$(date)
