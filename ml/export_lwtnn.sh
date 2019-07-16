#!/bin/bash

ERA=$1
CHANNEL=$2

# source python3 LCG view
source /cvmfs/sft.cern.ch/lcg/views/LCG_94python3/x86_64-slc6-gcc62-opt/setup.sh

if [ ! -d "htt-ml/lwtnn" ]; then
    echo "[FATAL] Directory htt-ml/lwtnn not found, please checkout this submodule of htt-ml"
    exit 1
fi

#for fold in 0 1;
#do
#    python3 htt-ml/lwtnn/converters/keras2json.py ml/${ERA}_${CHANNEL}_significance/fold${fold}_keras_architecture.json  ml/${ERA}_${CHANNEL}_significance/fold${fold}_keras_variables.json ml/${ERA}_${CHANNEL}_significance/fold${fold}_keras_weights.h5 >  ml/${ERA}_${CHANNEL}_significance/fold${fold}_lwtnn.json
#done

#for fold in 0 1;
#do
#    python3 htt-ml/lwtnn/converters/kerasfunc2json.py ml/${ERA}_${CHANNEL}_significance/fold${fold}_keras_architecture.json ml/${ERA}_${CHANNEL}_significance/fold${fold}_keras_weights.h5 >  ml/${ERA}_${CHANNEL}_significance/fold${fold}_variables.json
#done
#
#echo "Created variables .json files:"
#ls ml/${ERA}_${CHANNEL}_significance/*variables.json -lrth

for fold in 0 1;
do
    python3 htt-ml/lwtnn/converters/keras2json.py ml/${ERA}_${CHANNEL}_significance/fold${fold}_keras_architecture.json  ml/${ERA}_${CHANNEL}_significance/fold${fold}_keras_variables.json ml/${ERA}_${CHANNEL}_significance/fold${fold}_keras_weights.h5 >  ml/${ERA}_${CHANNEL}_significance/fold${fold}_lwtnn.json
done

echo "Created lwtnn .json files:"
ls ml/${ERA}_${CHANNEL}_significance/*lwtnn.json -lrth
