###############################
# Submit shape jobs to condor #
###############################
# create error log out folder if not existens
mkdir -p error log out

# jobs will be submitted directly from this repository, so the logfiles created by the job will be updated.
ERA=$1
VARIABLE=$2
CHANNELS=${@:3}
PWD=`pwd`
NUMCORES=12
# write arguments.txt
WORKDIR=`dirname $PWD`

for CHANNEL in $CHANNELS 
do  
    for SHAPEGROUP in backgrounds sm_signals bbH ggH_t ggH_b ggH_i ggA_t ggA_b ggA_i ggh_t ggh_b ggh_i
    do
        echo "$WORKDIR $NUMCORES $ERA $VARIABLE $SHAPEGROUP $CHANNEL"
    done
done > arguments.txt

## source LCG Stack and submit the job

if uname -a | grep -E 'el7' -q
then
    source /cvmfs/sft.cern.ch/lcg/views/LCG_96/x86_64-centos7-gcc8-opt/setup.sh
    condor_submit ${WORKDIR}/condor_jobs/produce_shapes_cc7.jdl
elif uname -a | grep -E 'el6' -q
then
    source /cvmfs/sft.cern.ch/lcg/views/LCG_94/x86_64-slc6-gcc8-opt/setup.sh
    condor_submit ${WORKDIR}/produce_shapes_slc6.jdl
else
    echo "Maschine unknown, i don't know what to do !"
fi
