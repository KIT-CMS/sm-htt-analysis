#!/bin/bash
LCG_RELEASE=95
if uname -a | grep ekpdeepthought
then
    source /cvmfs/sft.cern.ch/lcg/views/LCG_${LCG_RELEASE}/x86_64-ubuntu1604-gcc54-opt/setup.sh
    source /cvmfs/sft.cern.ch/lcg/views/LCG_94/x86_64-ubuntu1604-gcc54-opt/setup.sh
elif uname -a | grep bms1
then
    source /cvmfs/sft.cern.ch/lcg/views/LCG_${LCG_RELEASE}/x86_64-centos7-gcc8-opt/setup.sh
else
    source /cvmfs/sft.cern.ch/lcg/views/LCG_${LCG_RELEASE}/x86_64-slc6-gcc8-opt/setup.sh
fi
