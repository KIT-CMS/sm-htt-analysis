#!/bin/bash


### Setup of CMSSW release
NUM_CORES=10
CMSSW=CMSSW_10_2_14

if [ "$1" == "" ]; then
  echo "$0: Explicit CMSSW version is not provided. Checking out as default $CMSSW"
fi

if [ ! "$1" == "" ]; then
  CMSSW=$1
  echo "$0: Checking out $CMSSW"
fi


export SCRAM_ARCH=slc6_amd64_gcc700
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh

scramv1 project $CMSSW; pushd $CMSSW/src
eval `scramv1 runtime -sh`

### Checkout of external software

# SVfit and fastMTT
git clone https://github.com/SVfit/ClassicSVfit TauAnalysis/ClassicSVfit -b fastMTT_19_02_2019
git clone https://github.com/SVfit/SVfitTF TauAnalysis/SVfitTF

# MELA
git clone https://github.com/cms-analysis/HiggsAnalysis-ZZMatrixElement ZZMatrixElement -b v2.2.0
# NOTE: The following two lines should be needed following the wiki, but it
# seems to work either way. However, these lines introduce a dependency on AFS.
# Wiki: https://twiki.cern.ch/twiki/bin/view/CMS/MELAProject#Checkout_instructions
#cp ZZMatrixElement/MELA/data/mcfm.xml ../config/toolbox/$SCRAM_ARCH/tools/selected/
#scram setup mcfm
cd ZZMatrixElement/
bash setup.sh -j $NUM_CORES
cd ..

# TODO NN mass

# FF weights
git clone ssh://git@github.com/CMS-HTT/Jet2TauFakes.git HTTutilities/Jet2TauFakes
cd HTTutilities/Jet2TauFakes
git checkout v0.2.2
#git clone -b 2016 ssh://git@gitlab.cern.ch:7999/cms-htt/Jet2TauFakesFiles.git data_2016
#git clone -b 2017 ssh://git@gitlab.cern.ch:7999/cms-htt/Jet2TauFakesFiles.git data_2017
#git clone -b 2018 ssh://git@gitlab.cern.ch:7999/cms-htt/Jet2TauFakesFiles.git data_2018
cd ../..
git clone https://github.com/KIT-CMS/fake-factor-application.git HiggsAnalysis/fake-factor-application

# TODO NN MET

# TODO NN max score 

# TODO single-tau HLT

### Checkout of friend tree producer setup
git clone https://github.com/KIT-CMS/friend-tree-producer.git HiggsAnalysis/friend-tree-producer

# Data sources
mkdir HiggsAnalysis/friend-tree-producer/data/input_params
cd HiggsAnalysis/friend-tree-producer/data/input_params
read -p "lxplus-username: " USERNMLXP
scp ${USERNMLXP}@lxplus.cern.ch:/eos/home-s/swozniew/friend-tree-producer-input-params/* ./
wget https://raw.githubusercontent.com/KIT-CMS/datasets/master/datasets.json
cd -

### Compiling under CMSSW
scram b -j $NUM_CORES
popd
