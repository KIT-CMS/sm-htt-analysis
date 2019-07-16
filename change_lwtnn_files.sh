#!/bin/bash

FOLDER=$1

rm -rf CMSSW_10_2_14/src/HiggsAnalysis/friend-tree-producer/data/inputs_lwtnn/2017/em/fold0_lwtnn.json
rm -rf CMSSW_10_2_14/src/HiggsAnalysis/friend-tree-producer/data/inputs_lwtnn/2017/em/fold1_lwtnn.json
rm -rf CMSSW_10_2_14/src/HiggsAnalysis/friend-tree-producer/data/inputs_lwtnn/2017/et/fold0_lwtnn.json
rm -rf CMSSW_10_2_14/src/HiggsAnalysis/friend-tree-producer/data/inputs_lwtnn/2017/et/fold1_lwtnn.json
rm -rf CMSSW_10_2_14/src/HiggsAnalysis/friend-tree-producer/data/inputs_lwtnn/2017/mt/fold0_lwtnn.json
rm -rf CMSSW_10_2_14/src/HiggsAnalysis/friend-tree-producer/data/inputs_lwtnn/2017/mt/fold1_lwtnn.json
rm -rf CMSSW_10_2_14/src/HiggsAnalysis/friend-tree-producer/data/inputs_lwtnn/2017/tt/fold0_lwtnn.json
rm -rf CMSSW_10_2_14/src/HiggsAnalysis/friend-tree-producer/data/inputs_lwtnn/2017/tt/fold1_lwtnn.json

echo "Removed all .json files from friend-tree-producer"

cp -r ml/2017_em${FOLDER}/fold0_lwtnn.json CMSSW_10_2_14/src/HiggsAnalysis/friend-tree-producer/data/inputs_lwtnn/2017/em
cp -r ml/2017_em${FOLDER}/fold1_lwtnn.json CMSSW_10_2_14/src/HiggsAnalysis/friend-tree-producer/data/inputs_lwtnn/2017/em
cp -r ml/2017_mt${FOLDER}/fold1_lwtnn.json CMSSW_10_2_14/src/HiggsAnalysis/friend-tree-producer/data/inputs_lwtnn/2017/mt
cp -r ml/2017_mt${FOLDER}/fold0_lwtnn.json CMSSW_10_2_14/src/HiggsAnalysis/friend-tree-producer/data/inputs_lwtnn/2017/mt
cp -r ml/2017_et${FOLDER}/fold0_lwtnn.json CMSSW_10_2_14/src/HiggsAnalysis/friend-tree-producer/data/inputs_lwtnn/2017/et
cp -r ml/2017_et${FOLDER}/fold1_lwtnn.json CMSSW_10_2_14/src/HiggsAnalysis/friend-tree-producer/data/inputs_lwtnn/2017/et
cp -r ml/2017_tt${FOLDER}/fold0_lwtnn.json CMSSW_10_2_14/src/HiggsAnalysis/friend-tree-producer/data/inputs_lwtnn/2017/tt
cp -r ml/2017_tt${FOLDER}/fold1_lwtnn.json CMSSW_10_2_14/src/HiggsAnalysis/friend-tree-producer/data/inputs_lwtnn/2017/tt

echo "Copied new .json files from folder ml/2017_tt${FOLDER}"
