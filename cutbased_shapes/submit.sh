###############################
# Submit shape jobs to condor #
###############################
# create error log out folder if not existens
mkdir -p error log out

# jobs will be submitted directly from this repository, so the logfiles created by the job will be updated.
ERA=$1
VARIABLE=$2
CHANNELS=${@:3}
NUMCORES=8

./write_submit_arguments.py \
    -c $CHANNELS \
    -v $VARIABLE \
    -e $ERA \
    -n $NUMCORES \
    -s sm_signals # backgrounds sm_signals bbH ggH_t ggH_b ggH_i ggA_t ggA_b ggA_i ggh_t ggh_b ggh_i

## source LCG Stack and submit the job
WORKDIR=$(dirname `pwd`)

if uname -a | grep -E 'el7' -q
then
    source /cvmfs/sft.cern.ch/lcg/views/LCG_96/x86_64-centos7-gcc8-opt/setup.sh
    condor_submit ${WORKDIR}/cutbased_shapes/produce_shapes_cc7.jdl
elif uname -a | grep -E 'el6' -q
then
    source /cvmfs/sft.cern.ch/lcg/views/LCG_94/x86_64-slc6-gcc8-opt/setup.sh
    condor_submit ${WORKDIR}/cutbased_shapes/produce_shapes_slc6.jdl
else
    echo "Maschine unknown, i don't know what to do !"
fi
