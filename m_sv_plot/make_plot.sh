#!/bin/bash
source utils/setup_cmssw.sh
source utils/setup_python.sh
source utils/bashFunctionCollection.sh

SHAPEFOLDER=$1
FITFILE=$2
# current bestfit file:
#FITFILE=/portal/ekpbms3/home/swozniewski/SM_Htautau_Legacy/Jul_09/sm-htt-analysis/output/datacards/all-final_stage0_expected-smhtt-ML/stxs_stage0/cmb/125/fitDiagnostics.hesse-all-final_stage0_expected-cmb-inclusive.MultiDimFit.mH125.root

CHANNELS="em,et,mt,tt"
STXS_SIGNALS="stxs_stage0"
CATEGORIES="gof"
VARIABLE="m_sv_puppi"
TAG="final_stage0"
JETFAKES=1
EMBEDDING=1

# Set stack size to unlimited, otherwise the T2W tool throws a segfault if
# combining all eras
ulimit -s unlimited


for ERA in "2016" "2017" "2018"; do
    for CHANNEL in "et" "mt" "tt" "em"; do
        inputfile=${SHAPEFOLDER}/${ERA}-${ERA}_${CHANNEL}_${VARIABLE}-${CHANNEL}-shapes.root
        [[ -f $inputfile ]] || ( logerror $inputfile not fould && exit 2 )
        logandrun python shapes/convert_to_synced_shapes.py \
            --era ${ERA} \
            --tag ${TAG} \
            --input $inputfile \
            --output ${SHAPEFOLDER}/synced
    done
    GOF_CATEGORY_NAME=${VARIABLE}

    OUTPUTDIR="m_sv_plot/datacards/${ERA}-cmb-${VARIABLE}-smhtt-gof"
    # Create datacards
    logandrun ${CMSSW_BASE}/bin/slc7_amd64_gcc700/MorphingSMRun2Legacy \
        --base_path=$PWD \
        --input_folder_mt="${SHAPEFOLDER}/synced" \
        --input_folder_et="${SHAPEFOLDER}/synced" \
        --input_folder_tt="${SHAPEFOLDER}/synced" \
        --input_folder_em="${SHAPEFOLDER}/synced" \
        --real_data=true \
        --classic_bbb=false \
        --binomial_bbb=true \
        --jetfakes=$JETFAKES \
        --embedding=$EMBEDDING \
        --ggh_wg1=true \
        --qqh_wg1=true \
        --midfix="-${TAG}-" \
        --channel=$CHANNELS \
        --auto_rebin=false \
        --rebin_categories=false \
        --stxs_signals=$STXS_SIGNALS \
        --categories="gof" \
        --gof_category_name=$GOF_CATEGORY_NAME \
        --era=$ERA \
        --output=${OUTPUTDIR} | tee m_sv_plot/log/datacard-gof-${ERA}-${CHANNEL}-${VARIABLE}-${JETFAKES}-${EMBEDDING}.log
    TARGET=m_sv_plot/datacards/all-cmb-m_sv_puppi-smhtt-gof/cmb

    DATACARDDIR=m_sv_plot/datacards/${ERA}-cmb-m_sv_puppi-smhtt-gof/cmb
    mkdir -p $TARGET/{125,common}
    # Make new directory with needed folder structure
    cp ${DATACARDDIR}/125/htt_*_${ERA}.txt $TARGET/125
    cp ${DATACARDDIR}/common/htt_input_${ERA}.root $TARGET/common
    for CHANNEL in "et" "mt" "tt" "em" "cmb"; do
        for FILE in $TARGET/125/*.txt
        do
            sed -i '$s/$/\n * autoMCStats 0.0/' $FILE
        done
    done
done
ERA="all"
CHANNEL="cmb"

LOGFILE=m_sv_plot/log/workspace-${ERA}-${CHANNEL}-${VARIABLE}.log
# Collect input directories for eras and define output path for workspace
INPUT="m_sv_plot/datacards/${ERA}-${CHANNEL}-${VARIABLE}-smhtt-gof/*/125"
echo "[INFO] Add datacards to workspace from path "${INPUT}"."
#OUTPUT=${ERA}_workspace.root
OUTPUT=${PWD}/m_sv_plot/datacards/${ERA}-${CHANNEL}-${VARIABLE}-smhtt-gof/${ERA}-${CHANNEL}-${VARIABLE}-workspace.root
echo "[INFO] Write workspace to "${OUTPUT}"."
# Define signals to be fitted and produce workspace
combineTool.py -M T2W -o ${OUTPUT} -i ${INPUT} --channel-masks --cc | tee $LOGFILE



ID=${ERA}-${CHANNEL}-${VARIABLE}
WORKSPACE=m_sv_plot/datacards/${ID}-smhtt-gof/${ID}-workspace.root

logandrun PostFitShapesFromWorkspace \
                -m 125 -w ${WORKSPACE} \
                -d m_sv_plot/datacards/all-cmb-m_sv_puppi-smhtt-gof/cmb/125/combined.txt.cmb \
                -o m_sv_plot/postfitshapes-${ID}.root \
                -f ${FITFILE}:fit_s --postfit --skip-prefit --print

logandrun PostFitShapesFromWorkspace \
                -m 125 -w ${WORKSPACE} \
                -d m_sv_plot/datacards/all-cmb-m_sv_puppi-smhtt-gof/cmb/125/combined.txt.cmb \
                -o m_sv_plot/prefitshapes-${ID}.root \
                -f ${FITFILE}:fit_s --print

python m_sv_plot/plot_m_sv_cmb.py -i m_sv_plot/postfitshapes-all-cmb-m_sv_puppi.root --combine-backgrounds

python m_sv_plot/plot_m_sv_cmb.py -i m_sv_plot/prefitshapes-all-cmb-m_sv_puppi.root --combine-backgrounds
