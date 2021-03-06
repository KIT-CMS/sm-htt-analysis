#!/bin/bash
source utils/setup_cmssw.sh

ERA=$1
STXS_FIT=$2
DATACARDDIR=$3
[[ $STXS_FIT == "stxs_stage1p1" ]] && STXS_SIGNALS=stxs_stage1p1 || STXS_SIGNALS=stxs_stage0

WORKSPACE=$DATACARDDIR/${ERA}-${STXS_FIT}-workspace.root
[[ -z $4 ]] && LOGFILE="output/log/postfit-shapes-$ERA-$STXS_FIT.log" || LOGFILE="output/log/postfit-shapes-$4-$ERA-$STXS_FIT.log"
[[ -z $4 ]] && OUTPUTFILE="shape-${ERA}-${STXS_FIT}.root" || OUTPUTFILE="shape-${ERA}-${4}-${STXS_FIT}.root"
# Set stack size to unlimited, otherwise the T2W tool throws a segfault if
# combining all eras

# Prefit shapes
# NOTE: The referenced datacard is used for rebinning
PostFitShapesFromWorkspace -m 125 -w ${WORKSPACE} \
    -d ${DATACARDDIR}/combined.txt.cmb -o ${DATACARDDIR}/prefit${OUTPUTFILE}


# Postfit shapes
#FITFILE=$DATACARDDIR/fitDiagnostics${ERA}-${STXS_FIT}.MultiDimFit.mH125.root
#PostFitShapesFromWorkspace -m 125 -w ${WORKSPACE} \
    #-d ${DATACARDDIR}/combined.txt.cmb -o ${DATACARDDIR}/postfit${OUTPUTFILE} -f ${FITFILE}:fit_s --postfit
