#!/bin/bash

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
for FILENAME in `ls /storage/c/swozniewski/SM_Htautau/ntuples/Artus_2017-12-02/merged/`
do echo ${FILENAME}
python quantile-method/CreateCalibratedFriendTrees.py --channels et mt --shifts nominal btagEffDown btagEffUp btagMistagDown btagMistagUp jecUncDown jecUncUp metJetEnDown metJetEnUp metUnclusteredEnDown metUnclusteredEnUp tauEsOneProngDown tauEsOneProngUp tauEsOneProngPiZerosDown tauEsOneProngPiZerosUp tauEsThreeProngDown tauEsThreeProngUp tauJetFakeEsDown tauJetFakeEsUp -i /storage/c/swozniewski/SM_Htautau/ntuples/Artus_2017-12-02/merged/${FILENAME}/${FILENAME}.root
#python quantile-method/CreateCalibratedFriendTrees.py --channels et mt --shifts tauEsOneProngPiZerosDown tauEsOneProngPiZerosUp -i /storage/c/swozniewski/SM_Htautau/ntuples/Artus_2017-12-02/merged/${FILENAME}/${FILENAME}.root
done
