#!/bin/bash
set -e
ulimit -s unlimited

id=htt_${CHANNEL}_${CATEGORY}_${ERA}
echo " --------------"
echo " Running Shape extraction for id: $id"
echo "PostFitShapesFromWorkspace --mass 125 --workspace $SUBMITDIR/output/datacards/all-$TAG-smhtt-ML/$STXS_FIT/cmb/125/all-$STXS_FIT-workspace.root --datacard $SUBMITDIR/output/datacards/all-$TAG-smhtt-ML/$STXS_FIT/cmb/125/combined.txt.cmb --output ${id}.root --fitresult $FITFILE:fit_s --restrict-to-bin ${id} --postfit --skip-prefit"
echo " --------------"
echo " --------------"
echo " Starting plot Production ! "
if [[ $MODE == *"postfit"* ]]; then
PostFitShapesFromWorkspace --mass 125 --workspace $SUBMITDIR/output/datacards/all-$TAG-smhtt-ML/$STXS_FIT/cmb/125/all-$STXS_FIT-workspace.root --datacard $SUBMITDIR/output/datacards/all-$TAG-smhtt-ML/$STXS_FIT/cmb/125/combined.txt.cmb --output ${id}.root --fitresult $FITFILE:fit_s --restrict-to-bin ${id} --postfit --skip-prefit
elif [[ $MODE == *"prefit"* ]]; then
    PostFitShapesFromWorkspace --mass 125 --workspace $SUBMITDIR/output/datacards/all-$TAG-smhtt-ML/$STXS_FIT/cmb/125/all-$STXS_FIT-workspace.root --datacard $SUBMITDIR/output/datacards/all-$TAG-smhtt-ML/$STXS_FIT/cmb/125/combined.txt.cmb --output ${id}.root --restrict-to-bin ${id}
fi
echo " Finished plot Production ! "
echo " --------------"
