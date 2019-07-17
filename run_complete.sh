#!/usr/bin/env bash
### Skript to compare the training with embedding and mc samples in it's effect on the signal strength

set -e # quit on error
shopt -s checkjobs # wait for all jobs before exiting
export PARALLEL=1
export USE_BATCH_SYSTEM=1
export cluster=lxplus
export sm_htt_analysis_dir="/portal/ekpbms3/home/${USER}/sm-htt-analysis" ### local sm-htt repo !
export cmssw_src_local="/portal/ekpbms3/home/${USER}/CMSSW_10_2_14/src" ### local CMSSW !
export batch_out_local="/portal/ekpbms3/home/${USER}/batch-out"
source utils/bashFunctionCollection.sh


if [[ $USE_BATCH_SYSTEM == "1" ]]; then
    if [[ $cluster == "etp" ]]; then
        export batch_out=$batch_out_local
    elif [[ $cluster == "lxplus" ]]; then
        export batch_out="/afs/cern.ch/work/${USER::1}/${USER}/batch-out"
        export cmssw_src_dir="/afs/cern.ch/user/${USER::1}/${USER}/CMSSW_10_2_14/src" ## Remote CMSSW!
    fi
fi

########### Argument handling and Tests ##################
IFS=',' read -r -a eras <<< $1
IFS=',' read -r -a channels <<< $2
erasarg=$1
channelsarg=$2


[[ "" = $( echo $eras ) ]] && eras=("2016" "2017" "2018") erasarg="2016,2017,2018"
[[ "" = $( echo $channels ) ]] && channels=("em" "et" "tt" "mt") channelsarg="em,et,tt,mt"

loginfo Eras: $erasarg  Channels: $channelsarg

if [[ ! "" = $3 ]]; then
    logerror only takes 3 arguments, seperate multiple eras and channels by comma eg: 2016,2018 mt,em   or \"\" em
    exit 1
fi
for era in ${eras[@]}; do
    if [[ ! "2016 2017 2018" =~ $era ]]; then
        logerror $era is not a valid era.
        exit 1
    fi
done
for channel in ${channels[@]}; do
    if [[ ! "em et tt mt" =~ $channel ]]; then
        logerror $channel is not a valid channel.
        exit 1
    fi
done



for DIRECTORY in shapes datacards combine plotting utils
do
    if [ ! -d "$DIRECTORY" ]; then
        logerr "Directory $DIRECTORY not found, you are not in the top-level directory of the analysis repository?"
        exit 1
    fi
done
############################################

source completedMilestones
#trap "echo \"Current completed State: \$anaSSStep=$anaSSStep\"; echo $anaSSStep > completedMilestones " INT KILL FAIL EXIT

#### converts models to the form needed for submission to a batch system
function exportForApplication {
    era=$1
    channel=$2
    ./ml/translate_models.sh $era $channel
    ./ml/export_lwtnn.sh $era $channel
    ### Supply the generated models in the hard-coded path in the friendProducer
    llwtnndir=$cmssw_src_local/HiggsAnalysis/friend-tree-producer/data/inputs_lwtnn
    [[ ! -d $llwtnndir/${era}/${channel} ]] && mkdir -p $llwtnndir/${era}/${channel}
    for fold in 0 1;
    do
        updateSymlink $sm_htt_analysis_dir/ml/${era}_${channel}/fold${fold}_lwtnn.json  $llwtnndir/${era}/${channel}/fold${fold}_lwtnn.json
    done
}
################################################################
########## Define necessairy methods for the analysis ##########
################################################################

### produce datacard from era_shapes.root and run the statistical training_z_estimation_method
### plain text resultst to  "$sm_htt_analysis_dir/$METHOD-$STXS_SIGNALS-$STXS_FIT.txt"
export METHOD STXS_SIGNALS STXS_FIT PROD_NEW_DATACARDS
JETFAKES=1                  # options: 0, 1
EMBEDDING=1                 # options: 0, 1
CATEGORIES="stxs_stage1p1"

### Subroutine called by runStages
function runana() {
    echo "analysis for:"
    echo '$METHOD $STXS_SIGNALS $STXS_FIT $era $CATEGORIES $JETFAKES $EMBEDDING $channels'
    echo "$METHOD $STXS_SIGNALS $STXS_FIT $era $CATEGORIES $JETFAKES $EMBEDDING ${channels[@]}"
    if [[ $PROD_NEW_DATACARDS == 1 ]]; then
        echo "Prodcing datacard:"
        ## one could produce a datacard for stage1p1 and then just select the right one upon produce_workspace :)
        ./datacards/produce_datacard.sh $era $STXS_SIGNALS $CATEGORIES $JETFAKES $EMBEDDING ${channels[@]} > /dev/null
    fi
    ./datacards/produce_workspace.sh $era $STXS_FIT > /dev/null
    echo "writing to $sm_htt_analysis_dir/$METHOD-$STXS_SIGNALS-$STXS_FIT.txt"
    temp_file=$(mktemp)
    ./combine/signal_strength.sh $era $STXS_FIT > $temp_file
    cat $temp_file | sed -n -e '/ --- MultiDimFit ---/,$p'| sed  "/Printing Message Summary/q" | head -n -2 | grep -v INFO: | tee "$sm_htt_analysis_dir/$METHOD-$STXS_SIGNALS-$STXS_FIT.txt"

    ### add more analysis scripts here
    PROD_NEW_DATACARDS=0
}

function genshapes() {
    cd $sm_htt_analysis_dir
    for era in ${eras[@]}; do
        redoConversion=0
    lf=$sm_htt_analysis_dir/${era}_shapes.root
    rf=$batch_out_local/${era}/${era}_shapes.root
        if [[ ! -f $rf  ]]; then
            updateSymlink $rf $lf
            loginfo Producing shapes for $era ${channels[@]}
            ./shapes/produce_shapes.sh $era ${channels[@]}
            rm normalize_shifts.log
            redoConversion=1
        else
            loginfo Skipping shape generation as $batch_out_local/${era}/${era}_shapes.root exists
        fi
        for channel in ${channels[@]}; do
	fn=$batch_out_local/${era}/htt_${channel}.inputs-sm-Run${era}-ML.root
            if [[ ! -f $fn  ]]; then
		logwarn $fn does not exist: rerunning shape syncing
                redoConversion=1
            fi
        done
        if [[ $redoConversion == 1 ]]; then
            loginfo Syncing shapes for $era ${channels[@]}
            for channel in ${channels[@]}; do
                updateSymlink "$sm_htt_analysis_dir/htt_${channel}.inputs-sm-Run${era}-ML.root" "$batch_out_local/${era}/htt_${channel}.inputs-sm-Run${era}-ML.root"
            done
	### This writes in to the symlinks
            ./shapes/convert_to_synced_shapes.sh $era
        fi
    done
}



### run the analysis for mc and emb and all stages
function runStages() {
genshapes
cd $sm_htt_analysis_dir
for channel in ${channels[@]}; do
    updateSymlink "$batch_out_local/${era}/htt_${channel}.inputs-sm-Run${era}-ML.root" "$sm_htt_analysis_dir/htt_${channel}.inputs-sm-Run${era}-ML.root"
done
for s in "stxs_stage0" "stxs_stage1p1"; do
    PROD_NEW_DATACARDS=1 ## "inclusive" "stxs_stage0" can use the same datacards
    STXS_SIGNALS=$s
    if [[ "$s" == "stxs_stage0" ]]; then
        for f in "inclusive" "stxs_stage0"; do
            STXS_FIT=$f
            runana
        done
    elif [[ "$s" == "stxs_stage1p1" ]]; then
        STXS_FIT="stxs_stage1p1"
        runana
    fi
done
}

#################################################################################################
### Main procedure. Ensures, no completed step is run again by sourcing completedMilestones
### in the beginning and overwriting variables upon completion of the step
#################################################################################################

function main() {
    if [[ $anaSSStep < 1 ]]; then
        ##### Create training dataset:
        if [[ ! $( getPar completedMilestones ds_created ) == 1  ]]; then
            loginfo "./ml/create_training_dataset.sh" $erasarg $channelsarg
            ./ml/create_training_dataset.sh $erasarg $channelsarg
            overridePar completedMilestones ds_created 1
            loginfo All datasets created
        else
            loginfo Skipping training dataset creation
        fi

        #### Correct the class weight in ml/era_channel_training.yaml
        if [[ ! $( getPar completedMilestones sum_training_weights ) == 1  ]]; then
            loginfo "./ml/sum_training_weights.sh" $erasarg $channelsarg
            ./ml/sum_training_weights.sh $erasarg $channelsarg
            overridePar completedMilestones sum_training_weights 1
            loginfo All class weights calculated
        else
            loginfo Skipping class weight calculation
        fi

        ### Run trainings ml/era_channel_training.yaml ml/era_channel/merge_foldX_*.root -> ml/era_channel/foldX_keras_model.h5
        if [[ ! $( getPar completedMilestones training  ) == 1  ]]; then
            for era in ${eras[@]}; do
                for channel in ${channels[@]}; do
                    loginfo ./ml/run_training.sh $era $channel
                    ./ml/run_training.sh $era $channel
                done
            done
            overridePar completedMilestones training 1
            loginfo All trainings completed
        else
            loginfo Skipping training
        fi
        if [[ $USE_BATCH_SYSTEM == 1 ]]; then
            ### convert the models to lwtnn format ml/era_channel/foldX_keras_model.h5 -> ml/era_channel/foldX_lwtnn.json
            if [[ ! $( getPar completedMilestones models_exported  ) == 1  ]]; then
                for era in ${eras[@]}; do
                    for channel in ${channels[@]}; do
                        exportForApplication $era $channel
                    done
                done
                updateSymlink $sm_htt_analysis_dir/datasets/datasets.json $cmssw_src_local/HiggsAnalysis/friend-tree-producer/data/input_params/datasets.json
                if [[ $cluster == lxplus ]]; then
                    loginfo lxrsync ${cmssw_src_local}/HiggsAnalysis/friend-tree-producer/data/ lxplus.cern.ch:${cmssw_src_dir}/HiggsAnalysis/friend-tree-producer/data
                    lxrsync ${cmssw_src_local}/HiggsAnalysis/friend-tree-producer/data/ lxplus.cern.ch:${cmssw_src_dir}/HiggsAnalysis/friend-tree-producer/data
                fi
                overridePar completedMilestones models_exported 1
                loginfo Models for application exported
            else
                loginfo Skipping model export
            fi

            ### Apply the model ml/era_channel/foldX_keras_model.h5 oder ml/era_channel/foldX_lwtnn.json + ntuples -> NNScore friendTree
            if [[ ! $( getPar completedMilestones NNApplication_started  ) == 1  ]]; then
                ## NNScore Friend Tree Production on the etp
                cd $sm_htt_analysis_dir
                for era in ${eras[@]}; do
                    ./batchrunNNApplication.sh ${era} $channelsarg $cluster "submit" ${era}
                done
                overridePar completedMilestones NNApplication_started 1
                loginfo "Jobs for application created. Submit the jobs and, in completedMilestones, set NNApplication_ended to 1 if the jobs ran successfull or you need to resubmit"
                exit 0
            else
                loginfo Skipping batch submission for NNScore FriendTrees
            fi

            ### check if finished resubmit if needed
            if [[ $( getPar completedMilestones NNApplication_started  ) == "1"  ]] && [[ $( getPar completedMilestones NNApplication_ended  ) == "0"  ]] ; then
                cd $sm_htt_analysis_dir
                for era in ${eras[@]}; do
                    ./batchrunNNApplication.sh ${era} $channelsarg $cluster "check" ${era}
                done
                loginfo  In completedMilestones set NNApplication_ended to 1 if the jobs ran successfull
                exit 0
            else
                loginfo Skipping NNScore FriendTree batch resubmission
            fi

            if [[ ! $( getPar completedMilestones NNApplication_collected  ) == 1  ]]; then
                cd $sm_htt_analysis_dir
                for era in ${eras[@]}; do
                    ./batchrunNNApplication.sh ${era} $channelsarg $cluster "collect" ${era}
                done
                overridePar completedMilestones NNApplication_collected 1
                loginfo Jobs for application completed and collected. Move outputs now!
            else
                loginfo Skipping NNScore FriendTree Batch collection
            fi

            if [[ ! $( getPar completedMilestones NNApplication_synced ) = 1  ]]; then
                if [[ $cluster == etp ]]; then
                        loginfo Cluster is ept, no need to sync.
                elif [[ $cluster == lxplus ]]; then
                    read -p "Sync files from $USER@lxplus.cern.ch:$batch_out/${era} to $batch_out/${era} now? y/[n]" yn
                    if [[ ! $yn == "y" ]]; then
                        logerror "!=y \n aborting"
                        exit 0
                    fi
                    for era in ${eras[@]}; do
                        [[ ! -d $batch_out_local/${era}/NNScore_workdir/NNScore_collected  ]] && mkdir -p $batch_out_local/${era}/NNScore_workdir/NNScore_collected
                        loginfo lxrsync $USER@lxplus.cern.ch:$batch_out/${era}/NNScore_workdir/NNScore_collected/ $batch_out_local/${era}/NNScore_workdir/NNScore_collected
                        lxrsync $USER@lxplus.cern.ch:$batch_out/${era}/NNScore_workdir/NNScore_collected/ $batch_out_local/${era}/NNScore_workdir/NNScore_collected
                    done
                fi
                overridePar completedMilestones NNApplication_synced 1
                loginfo NNScore FriendTree sync completed
            else
                loginfo Skipping NNScore FriendTree sync
            fi
        else ## USE_BATCH_SYSTEM==0
            for era in ${eras[@]}; do
                for channel in ${channels[@]}; do
                    ./ml/run_application $era $channel
                done
            done
        fi
        overridePar completedMilestones anaSSStep 1
        anaSSStep=1
    fi
    loginfo reached analysis!
    if [[ $anaSSStep < 2 ]]; then
        runStages
	loginfo completed stages
        overridePar completedMilestones anaSSStep 2
        anaSSStep=2
    fi
    if [[ $anaSSStep < 3 ]]; then
        for x in mc-stxs_stage*txt; do
            cat $x
        done
        read -p "Run finished. Start new run? y/[n]" yn
        if [[ $yn == "y" ]]; then
            sed -E -r "s@(\w+)(\s+|=)\w+@\1\20@" completedMilestones
            echo ""
        fi
    fi
}

main
