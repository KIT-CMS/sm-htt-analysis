#!/bin/bash

ERA=$1
OUTPUT_PATH=$2

mkdir -p ${OUTPUT_PATH}
cp plots/*.png ${OUTPUT_PATH}
cp utils/index.php ${OUTPUT_PATH}

mkdir -p ${OUTPUT_PATH}/${ERA}_mt
cp ml/${ERA}_mt/*.png ${OUTPUT_PATH}/${ERA}_mt
cp utils/index.php ${OUTPUT_PATH}/${ERA}_mt

mkdir -p ${OUTPUT_PATH}/${ERA}_et
cp ml/${ERA}_et/*.png ${OUTPUT_PATH}/${ERA}_et
cp utils/index.php ${OUTPUT_PATH}/${ERA}_et

mkdir -p ${OUTPUT_PATH}/${ERA}_tt
cp ml/${ERA}_tt/*.png ${OUTPUT_PATH}/${ERA}_tt
cp utils/index.php ${OUTPUT_PATH}/${ERA}_tt

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
