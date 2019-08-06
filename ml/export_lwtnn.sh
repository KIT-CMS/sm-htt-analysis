#!/bin/bash
set -e

ERA=$1
CHANNEL=$2

# source python3 LCG view
LCG_RELEASE=94python3
if uname -a | grep ekpdeepthought
then
    source /cvmfs/sft.cern.ch/lcg/views/LCG_93python3/x86_64-ubuntu1604-gcc54-opt/setup.sh
elif uname -a | grep -E 'el7' -q
then
    source /cvmfs/sft.cern.ch/lcg/views/LCG_${LCG_RELEASE}/x86_64-centos7-gcc62-opt/setup.sh
else
    source /cvmfs/sft.cern.ch/lcg/views/LCG_${LCG_RELEASE}/x86_64-slc6-gcc62-opt/setup.sh
fi

if [ ! -d "htt-ml/lwtnn" ]; then
    echo "[FATAL] Directory htt-ml/lwtnn not found, please checkout this submodule of htt-ml"
    exit 1
fi

[[ -z $method ]] && outdir=ml/out/${ERA}_${CHANNEL} || outdir=ml/out/${ERA}_${CHANNEL}_${method}
for fold in 0 1;
do
    python3 htt-ml/lwtnn/converters/keras2json.py ${outdir}/fold${fold}_keras_architecture.json  ${outdir}/fold${fold}_keras_variables.json ${outdir}/fold${fold}_keras_weights.h5 >  ${outdir}/fold${fold}_lwtnn.json
done

echo "Created lwtnn .json files:"
ls ${outdir}/*lwtnn.json -lrth
exit $!
