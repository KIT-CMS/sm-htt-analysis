#!/bin/bash


source utils/setup_cmssw.sh

rm -rf /home/sjoerger/workspace/up_down_shift/not-an-adversarial/datacards/significance.txt
rm -rf /home/sjoerger/workspace/up_down_shift/not-an-adversarial/datacards/MultiDimFit.txt

for BIN in {0..48}
do
    echo "Currently on bin $BIN"
    combine -M Significance /home/sjoerger/workspace/up_down_shift/not-an-adversarial/datacards/datacard_bin=$BIN.txt | tee -a /home/sjoerger/workspace/up_down_shift/not-an-adversarial/datacards/significance.txt
    combine -M MultiDimFit /home/sjoerger/workspace/up_down_shift/not-an-adversarial/datacards/datacard_bin=$BIN.txt --algo singles --setParameterRanges r=-10,10 --robustFit 1 | tee -a /home/sjoerger/workspace/up_down_shift/not-an-adversarial/datacards/MultiDimFit.txt
done