#!/bin/bash

ERA=$1
OUTPUT_PATH=$2

# Category plots
mkdir -p ${OUTPUT_PATH}/${ERA}_plots
cp utils/index.php ${OUTPUT_PATH}/
cp ${ERA}_plots/*.png ${OUTPUT_PATH}/${ERA}_plots
cp ${ERA}_plots/*.pdf ${OUTPUT_PATH}/${ERA}_plots
cp utils/index.php ${OUTPUT_PATH}/${ERA}_plots

# ML
for CHANNEL in "et" "mt" "tt"
do
    mkdir -p ${OUTPUT_PATH}/${ERA}_${CHANNEL}
    cp utils/index.php ${OUTPUT_PATH}/${ERA}_${CHANNEL}

    cp ml/${ERA}_${CHANNEL}/*.png ${OUTPUT_PATH}/${ERA}_${CHANNEL}/
    cp ml/${ERA}_${CHANNEL}/*.pdf ${OUTPUT_PATH}/${ERA}_${CHANNEL}/
    cp ml/${ERA}_${CHANNEL}/*.txt ${OUTPUT_PATH}/${ERA}_${CHANNEL}/
    cp ml/${ERA}_${CHANNEL}/*.h5 ${OUTPUT_PATH}/${ERA}_${CHANNEL}/
    cp ml/${ERA}_${CHANNEL}/*.pickle ${OUTPUT_PATH}/${ERA}_${CHANNEL}/
done

# Logs
mkdir -p ${OUTPUT_PATH}/log
cp utils/index.php ${OUTPUT_PATH}/log
cp *.log ${OUTPUT_PATH}/log

# Datacard
mkdir -p ${OUTPUT_PATH}/datacard
cp utils/index.php ${OUTPUT_PATH}/datacard
cp *.txt ${OUTPUT_PATH}/datacard
cp *.root ${OUTPUT_PATH}/datacard

# Pulls and impacts
mkdir -p ${OUTPUT_PATH}/pulls
cp utils/index.php ${OUTPUT_PATH}/pulls
cp *.html ${OUTPUT_PATH}/pulls
cp *impacts.pdf ${OUTPUT_PATH}/pulls
