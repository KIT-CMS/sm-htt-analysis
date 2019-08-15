###############################
# Submit shape jobs to condor #
###############################

# jobs will be submitted directly from this repository, so the logfiles created by the job will be updated.
ERA=$1
CHANNELS=${@:2}
PWD=`pwd`
# write arguments.txt
WORKDIR=`dirname $PWD`
cat > arguments.txt << EOF 
$WORKDIR $ERA $CHANNELS 
EOF
pwd

## source LCG Stack and submit the job

if uname -a | grep -E 'bms1|sg0|sm0' -q
then
    source /cvmfs/sft.cern.ch/lcg/views/LCG_96/x86_64-centos7-gcc8-opt/setup.sh
    condor_submit produce_shapes_cc7.jdl
elif uname -a | grep -E 'bms2|bms3' -q
then
    source /cvmfs/sft.cern.ch/lcg/views/LCG_94/x86_64-slc6-gcc8-opt/setup.sh
    condor_submit produce_shapes_slc6.jdl
else
    echo "Maschine unknown, i don't know what to do !"
fi