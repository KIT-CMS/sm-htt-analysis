## Analysis Scripts
`run_complete.sh`
:   This is a control script for a complete run from generating the training datasets to the analysis. Has a set of milestones defined in `completedMilestones`, will only run those set to 0. May call `batchrunNNApplication.sh` if `USE_BATCH_SYSTEM=0` to run the application on the lxplus|etp cluster. Uses the expect script lxrsync. To avoid using lxrsync, replace lxrsync with rsync.
    Arguments: `run_complete.sh 2016,2017 , ` will run it 2016 and 2017 for all channels

`compareTrainingMCvsEMb.sh`
:   Mostly the same as `run_complete.sh`, but has one run with MC as the ztt-estimation method and one with EMB. Can be expandedto compare more methods. Compares the signal strength of both.


`batchrunNNApplication.sh`
:   runs the NNScore friendTree generation on a cluster, at the moment etp and lxplus. Uses the expect script lxrun. To avoid using lxrun, replace lxrun with cat and copy-paste the output tolxplus.
Arguments: `./batchrunNNApplication.sh ${era} $channels $cluster "submit|check|collect" ${era}_${m}`


