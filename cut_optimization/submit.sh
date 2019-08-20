###############################
# Submit shape jobs to condor #
###############################
# create error log out folder if not existens
mkdir -p error log out

# jobs will be submitted directly from this repository, so the logfiles created by the job will be updated.
ERA=$1
CHANNELS=${@:2}
PWD=`pwd`
# write arguments.txt
WORKDIR=`dirname $PWD`
NUMCORES=12

for CHANNEL in $CHANNELS 
do  
    for VARIABLE in ME_vbf_vs_Z DiTauDeltaR dijetpt jdeta mjj pt_tt pt_tt_puppi pt_ttjj pt_ttjj_puppi mt_1 pZetaMissVis mTdileptonMET mt_1_puppi pZetaPuppiMissVis mTdileptonMET_puppi
    do
        echo "$WORKDIR $NUMCORES $ERA $VARIABLE $CHANNEL"
    done
done > arguments.txt

## source LCG Stack and submit the job

if uname -a | grep -E 'bms1|ams2|sg0|sm0' -q
then
    source /cvmfs/sft.cern.ch/lcg/views/LCG_96/x86_64-centos7-gcc8-opt/setup.sh
    condor_submit $WORKDIR/condor_jobs/produce_shapes_cc7.jdl
elif uname -a | grep -E 'bms2|bms3|cms6' -q
then
    source /cvmfs/sft.cern.ch/lcg/views/LCG_94/x86_64-slc6-gcc8-opt/setup.sh
    condor_submit $WORKDIR/condor_jobs/produce_shapes_slc6.jdl
else
    echo "Maschine unknown, i don't know what to do !"
fi
