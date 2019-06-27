#!/bin/bash

LCG_RELEASE=94

if uname -a | grep ekpdeepthought
then
    source /cvmfs/sft.cern.ch/lcg/views/LCG_${LCG_RELEASE}/x86_64-ubuntu1604-gcc54-opt/setup.sh

	export PYTHONPATH=$HOME/.local/lib/python2.7/site-packages:$PYTHONPATH
	## This option enables locally installed packages and is needed for the ekpdeepthought, as tensorflow-gpu is not supplied by the lcga and needs to be installed locally.
	#If this option is enabled on the bms123 by a user with tensorflow-gpu locally installed, the job fails due to a lack of cuda/gpus 
elif uname -a | grep bms1
then
    source /cvmfs/sft.cern.ch/lcg/views/LCG_${LCG_RELEASE}/x86_64-centos7-gcc62-opt/setup.sh
else
    source /cvmfs/sft.cern.ch/lcg/views/LCG_${LCG_RELEASE}/x86_64-slc6-gcc62-opt/setup.sh
fi
