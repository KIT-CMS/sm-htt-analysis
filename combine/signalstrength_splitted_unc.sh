#!/bin/bash
set -e
source utils/bashFunctionCollection.sh
source utils/setup_cmssw.sh

ERA=$1
STXS_FIT=$2
DATACARDDIR=$3
CHANNEL=$4
TAG=$5

[[ -d $DATACARDDIR ]] || ( echo $DATACARDDIR is not a valid directory; exit 1 )
if [[ $STXS_FIT == "inclusive" || $STXS_FIT == "stxs_stage0" ]]; then
    STXS_SIGNALS=stxs_stage0
elif [[ $STXS_FIT == "stxs_stage1p1" ]] ; then
    STXS_SIGNALS=stxs_stage1p1
fi
WORKSPACE=$DATACARDDIR/${ERA}-${STXS_FIT}-workspace.root
ID=signal-strength-$ERA-$TAG-$CHANNEL-$STXS_FIT

LOGFILE="output/log/$ID.log"
OUTPUTFILE="output/signalStrength/$ID.txt"
# Set stack size to unlimited, otherwise the T2W tool throws a segfault if
# combining all ERAs
ulimit -s unlimited

# run fit and store the workspace
FITFILE=higgsCombine.${ID}.MultiDimFit.mH125_bestFit.root
logandrun combineTool.py \
    -n .$ID \
    -M MultiDimFit \
    -m 125 -d $WORKSPACE \
    --algo singles \
    --saveWorkspace \
    --robustFit 1 \
    --X-rtd MINIMIZER_analytic \
    --cminDefaultMinimizerStrategy 0 \
    --floatOtherPOIs 1 \
    -v1 \
    | tee $LOGFILE
mv higgsCombine.${ID}.MultiDimFit.mH125.root $FITFILE
logandrun python combine/print_fitresult.py $FITFILE | tee -a $LOGFILE | sed "s@\[INFO\] @@" | tail -n +2 | sort | sed -E "s@\s*:@@" | grep -E '^r' | tee $OUTPUTFILE

ID=only_stat_unc_signal-strength-$ERA-$TAG-$CHANNEL-$STXS_FIT
LOGFILE="output/log/$ID.log"
OUTPUTFILE="output/signalStrength/$ID.txt"

if [[ $STXS_FIT == "inclusive" ]]; then
  logandrun combineTool.py \
      -n .$ID \
      -M MultiDimFit \
      -m 125 -d $FITFILE \
      --algo singles \
      -w w --snapshotName "MultiDimFit" \
      --freezeParameters rgx{THU.*},rgx{BR.*},rgx{QCDScale.*},rgx{pdf.*},rgx{CMS.*},rgx{prop_bin.*},rgx{reducible.*} \
      --robustFit 1 \
      --X-rtd MINIMIZER_analytic \
      --cminDefaultMinimizerStrategy 0 \
      --floatOtherPOIs 1 \
      -v1 \
      | tee $LOGFILE
else 
  logandrun combineTool.py \
      -n .$ID \
      -M MultiDimFit \
      -m 125 -d $FITFILE \
      --algo singles \
      -w w --snapshotName "MultiDimFit" \
      --freezeParameters allConstrainedNuisances \
      --robustFit 1 \
      --X-rtd MINIMIZER_analytic \
      --cminDefaultMinimizerStrategy 0 \
      --floatOtherPOIs 1 \
      -v1 \
      | tee $LOGFILE
fi

logandrun python combine/print_fitresult.py higgsCombine.${ID}.MultiDimFit.mH125.root | tee -a $LOGFILE | sed "s@\[INFO\] @@" | tail -n +2 | sort | sed -E "s@\s*:@@" | grep -E '^r' | tee $OUTPUTFILE

ID=only_syst_unc_signal-strength-$ERA-$TAG-$CHANNEL-$STXS_FIT
LOGFILE="output/log/$ID.log"
OUTPUTFILE="output/signalStrength/$ID.txt"

logandrun combineTool.py \
    -n .$ID \
    -M MultiDimFit \
    -m 125 -d $FITFILE \
    --algo singles \
    -w w --snapshotName "MultiDimFit" \
    --freezeParameters rgx{THU.*},rgx{BR.*},rgx{QCDScale.*},rgx{pdf.*},rgx{prop_bin.*} \
    --robustFit 1 \
    --X-rtd MINIMIZER_analytic \
    --cminDefaultMinimizerStrategy 0 \
    --floatOtherPOIs 1 \
    -v1 \
    | tee $LOGFILE
logandrun python combine/print_fitresult.py higgsCombine.${ID}.MultiDimFit.mH125.root | tee -a $LOGFILE | sed "s@\[INFO\] @@" | tail -n +2 | sort | sed -E "s@\s*:@@" | grep -E '^r' | tee $OUTPUTFILE

ID=only_bbb_unc_signal-strength-$ERA-$TAG-$CHANNEL-$STXS_FIT
LOGFILE="output/log/$ID.log"
OUTPUTFILE="output/signalStrength/$ID.txt"

if [[ $STXS_FIT == "inclusive" ]]; then
  logandrun combineTool.py \
      -n .$ID \
      -M MultiDimFit \
      -m 125 -d $FITFILE \
      --algo singles \
      -w w --snapshotName "MultiDimFit" \
      --freezeParameters rgx{THU.*},rgx{BR.*},rgx{QCDScale.*},rgx{pdf.*},rgx{lumi_.*},rgx{CMS.*Prong.*},rgx{CMS_ZLShape.*},rgx{CMS_eff.*},rgx{CMS_fake.*},rgx{CMS_ff.*},rgx{CMS_htt_boson.*},rgx{CMS_htt_doublemutrg.*},rgx{CMS_htt_dyShape.*},rgx{CMS_htt_eff_b_.*},rgx{CMS_htt_emb_ttbar_.*},rgx{CMS_htt_mistag_b.*},rgx{CMS_htt_qcd.*},rgx{CMS_htt_.*sec},rgx{CMS_htt_.*Shape},rgx{CMS_htt_vbf_scale.*},rgx{CMS_htt_ggH_scale.*},rgx{ZHlep_scale.*},rgx{ZH_scale.*},rgx{WHlep_scale.*},rgx{WH_scale.*},rgx{CMS_prefiring.*},rgx{CMS_res.*},rgx{CMS_scale.*},rgx{reducible.*},rgx{CMS.*} \
      --robustFit 1 \
      --X-rtd MINIMIZER_analytic \
      --cminDefaultMinimizerStrategy 0 \
      --floatOtherPOIs 1 \
      -v1 \
      | tee $LOGFILE
else
  logandrun combineTool.py \
      -n .$ID \
      -M MultiDimFit \
      -m 125 -d $FITFILE \
      --algo singles \
      -w w --snapshotName "MultiDimFit" \
      --freezeParameters rgx{THU.*},rgx{BR.*},rgx{QCDScale.*},rgx{pdf.*},rgx{lumi_.*},rgx{CMS.*Prong.*},rgx{CMS_ZLShape.*},rgx{CMS_eff.*},rgx{CMS_fake.*},rgx{CMS_ff.*},rgx{CMS_htt_boson.*},rgx{CMS_htt_doublemutrg.*},rgx{CMS_htt_dyShape.*},rgx{CMS_htt_eff_b_.*},rgx{CMS_htt_emb_ttbar_.*},rgx{CMS_htt_mistag_b.*},rgx{CMS_htt_qcd.*},rgx{CMS_htt_.*sec},rgx{CMS_htt_.*Shape},rgx{CMS_htt_vbf_scale.*},rgx{CMS_htt_ggH_scale.*},rgx{ZHlep_scale.*},rgx{ZH_scale.*},rgx{WHlep_scale.*},rgx{WH_scale.*},rgx{CMS_prefiring.*},rgx{CMS_res.*},rgx{CMS_scale.*},rgx{reducible.*},rgx{CMS.*} \
      --robustFit 1 \
      --X-rtd MINIMIZER_analytic \
      --cminDefaultMinimizerStrategy 0 \
      --floatOtherPOIs 1 \
      -v1 \
      | tee $LOGFILE
fi

logandrun python combine/print_fitresult.py higgsCombine.${ID}.MultiDimFit.mH125.root | tee -a $LOGFILE | sed "s@\[INFO\] @@" | tail -n +2 | sort | sed -E "s@\s*:@@" | grep -E '^r' | tee $OUTPUTFILE



ID=only_theo_unc_signal-strength-$ERA-$TAG-$CHANNEL-$STXS_FIT
LOGFILE="output/log/$ID.log"
OUTPUTFILE="output/signalStrength/$ID.txt"

logandrun combineTool.py \
    -n .$ID \
    -M MultiDimFit \
    -m 125 -d $FITFILE \
    --algo singles \
    -w w --snapshotName "MultiDimFit" \
    --freezeParameters rgx{CMS.*},rgx{lumi_.*},rgx{prop_bin.*},rgx{reducible.*} \
    --robustFit 1 \
    --X-rtd MINIMIZER_analytic \
    --cminDefaultMinimizerStrategy 0 \
    --floatOtherPOIs 1 \
    -v1 \
    | tee $LOGFILE
logandrun python combine/print_fitresult.py higgsCombine.${ID}.MultiDimFit.mH125.root | tee -a $LOGFILE | sed "s@\[INFO\] @@" | tail -n +2 | sort | sed -E "s@\s*:@@" | grep -E '^r' | tee $OUTPUTFILE

mv output/log/only_theo_unc_signal-strength-$ERA-$TAG-$CHANNEL-$STXS_FIT.log output/log/signal-strength-$ERA-theo_$STXS_FIT-$CHANNEL-$STXS_FIT.log
mv output/log/only_syst_unc_signal-strength-$ERA-$TAG-$CHANNEL-$STXS_FIT.log output/log/signal-strength-$ERA-syst_$STXS_FIT-$CHANNEL-$STXS_FIT.log
mv output/log/only_stat_unc_signal-strength-$ERA-$TAG-$CHANNEL-$STXS_FIT.log output/log/signal-strength-$ERA-stat_$STXS_FIT-$CHANNEL-$STXS_FIT.log
mv output/log/only_bbb_unc_signal-strength-$ERA-$TAG-$CHANNEL-$STXS_FIT.log output/log/signal-strength-$ERA-bbb_$STXS_FIT-$CHANNEL-$STXS_FIT.log
