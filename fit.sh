#!/bin/bash
set -e
source utils/setup_cmssw.sh
source utils/setup_python.sh

ERA=$1

combine \
            -M MultiDimFit \
            -n _initialFit_Test \
            --algo singles \
            --redefineSignalPOIs taues,r \
           --setParameterRanges taues=-1.2,0.2:r=0.8,1.2 \
            --robustFit 1 \
            -m 0 -d ${ERA}_workspace.root \
            --setParameters taues=-0.489,r=1.0 \
                --setRobustFitAlgo=Minuit2 \
                --setRobustFitStrategy=0 \
                --setRobustFitTolerance=0.2 \
                --X-rtd FITTER_NEW_CROSSING_ALGO \
                --X-rtd FITTER_NEVER_GIVE_UP \
                --X-rtd FITTER_BOUND \
                --cminFallbackAlgo  "Minuit2,0:0.1" \
                --cminFallbackAlgo  "Minuit,0:0.1"


combineTool.py -M MultiDimFit -d ${ERA}_workspace.root \
    --algo grid \
    --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
    -P taues \
    --setParameters taues=-0.489 \
    --floatOtherPOIs 1 \
    --points 800 \
    --setParameterRanges taues=-1.2,0.2 \
    --robustFit 1 \
    -n ${ERA}_taues

# combineTool.py -M MultiDimFit \
#             -d ${ERA}_workspace.root \
#             --algo grid --points 800 \
#             --redefineSignalPOIs taues \
#             --floatOtherPOIs 1 \
#             --setParameters taues=-0.5  \
#             --setParameterRanges taues=-1.0,0.0 \
#                 --setRobustFitAlgo=Minuit2 \
#                 --setRobustFitStrategy=0 \
#                 --setRobustFitTolerance=0.2 \
#                 --X-rtd FITTER_NEW_CROSSING_ALGO \
#                 --X-rtd FITTER_NEVER_GIVE_UP \
#                 --X-rtd FITTER_BOUND \
#                 --cminFallbackAlgo  "Minuit2,0:0.1" \
#                 --cminFallbackAlgo  "Minuit,0:0.1" \
#                  \
#                 --cminPreScan \
#         --robustFit=1  \
#         --name scanning.1D.taues --parallel 12


python combine/plot1DScan.py \
    --main higgsCombine${ERA}_taues.MultiDimFit.mH120.root \
    --POI taues \
    --output ${ERA}_taues_plot_nll \
    --translate combine/translate.json
