#!/bin/bash

OUTPUT_PATH=$1

mkdir -p ${OUTPUT_PATH}
cp plots/*.png ${OUTPUT_PATH}
cp utils/index.php ${OUTPUT_PATH}

mkdir -p ${OUTPUT_PATH}/mt
cp ml/mt/*.png ${OUTPUT_PATH}/mt
cp utils/index.php ${OUTPUT_PATH}/mt

mkdir -p ${OUTPUT_PATH}/et
cp ml/et/*.png ${OUTPUT_PATH}/et
cp utils/index.php ${OUTPUT_PATH}/et

mkdir -p ${OUTPUT_PATH}/tt
cp ml/tt/*.png ${OUTPUT_PATH}/tt
cp utils/index.php ${OUTPUT_PATH}/tt

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
