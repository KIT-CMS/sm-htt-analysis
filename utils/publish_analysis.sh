#!/bin/bash

ERA=$1
OUTPUT_PATH=$2

mkdir -p ${OUTPUT_PATH}
cp plots/*.png ${OUTPUT_PATH}
cp utils/index.php ${OUTPUT_PATH}

for CHANNEL in "et" "mt" "tt"
do
    mkdir -p ${OUTPUT_PATH}/${ERA}_${CHANNEL}
    cp ml/${ERA}_${CHANNEL}/*.png ${OUTPUT_PATH}/${ERA}_${CHANNEL}/
    cp ml/${ERA}_${CHANNEL}/*.txt ${OUTPUT_PATH}/${ERA}_${CHANNEL}/
    cp utils/index.php ${OUTPUT_PATH}/${ERA}_${CHANNEL}
done

mkdir -p ${OUTPUT_PATH}/log
cp *.log ${OUTPUT_PATH}/log
cp utils/index.php ${OUTPUT_PATH}/log

mkdir -p ${OUTPUT_PATH}/datacard
cp *.txt ${OUTPUT_PATH}/datacard
cp *.root ${OUTPUT_PATH}/datacard
cp utils/index.php ${OUTPUT_PATH}/datacard

mkdir -p ${OUTPUT_PATH}/pulls
cp *.html ${OUTPUT_PATH}/pulls
cp utils/index.php ${OUTPUT_PATH}/pulls
