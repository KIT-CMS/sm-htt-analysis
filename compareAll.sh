#!/usr/bin/env bash
### Skript to compare the training with embedding and mc samples in it's effect on the signal strength

## Detect if the script is being sourced
#mklement0 https://stackoverflow.com/questions/2683279/how-to-detect-if-a-script-is-being-sourced
([[ -n $ZSH_EVAL_CONTEXT && $ZSH_EVAL_CONTEXT =~ :file$ ]] ||
 [[ -n $KSH_VERSION && $(cd "$(dirname -- "$0")" &&
    printf '%s' "${PWD%/}/")$(basename -- "$0") != "${.sh.file}" ]] ||
 [[ -n $BASH_VERSION ]] && (return 0 2>/dev/null)) && sourced=1 || sourced=0

[[ $sourced != 1 ]] && set -ex # quit on error

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
IFS=',' read -r -a methods <<< $3
erasarg=$1
channelsarg=$2
methodsarg=$3

[[ "" = $( echo $eras ) ]] && eras=("2016" "2017" "2018") erasarg="2016,2017,2018"
[[ "" = $( echo $channels ) ]] && channels=("em" "et" "tt" "mt") channelsarg="em,et,tt,mt"
[[ "" = $( echo $methods ) ]] && methods=("mc_mc" "emb_mc" "mc_ff" "emb_ff") methodsarg="mc_mc,emb_mc,mc_ff,emb_ff"

loginfo Eras: $erasarg  Channels: $channelsarg

if [[ ! "" = $4 ]]; then
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
for method in ${methods[@]}; do
    if [[ ! "mc_mc emb_mc mc_ff emb_ff" =~ $method ]]; then
        logerror $method is not a valid method.
        exit 1
    fi
done


for DIRECTORY in shapes datacards combine plotting utils
do
    if [ ! -d "$DIRECTORY" ]; then
        logerror "Directory $DIRECTORY not found, you are not in the top-level directory of the analysis repository?"
        exit 1
    fi
done
############################################


############# Ensure all folders and files are available for mc and emb
for method in ${methods[@]}; do
    for era in ${eras[@]}; do
        for channel in ${channels[@]}; do
            mldir=$sm_htt_analysis_dir/ml/${era}_${channel}_${method}
            trainingConfFile=$sm_htt_analysis_dir/ml/${era}_${channel}_training_${method}.yaml
            if [[ ! -d $mldir ]]; then
                mkdir $mldir
                loginfo "Creating $mldir"
            fi
            if [[ ! -f $trainingConfFile ]]; then
                cp $sm_htt_analysis_dir/ml/${era}_${channel}_training.yaml $trainingConfFile
                loginfo "copying ml/${era}_${channel}_training.yaml to $trainingConfFile "
            fi
        done
    done
done


source completedMilestones
#trap "echo \"Current completed State: \$anaSSStep=$anaSSStep\"; echo $anaSSStep > completedMilestones " INT KILL FAIL EXIT

############ Hack for switching between MC and EMB sample ################
function setmethod () {
    m=$1
    loginfo Setting Zττ estimation method to $method, switching symlinks
    if [[ $method == *"emb"* ]]; then
        overridePar ml/create_training_dataset.sh "training-z-estimation-method" emb
    else
        overridePar ml/create_training_dataset.sh "training-z-estimation-method" mc
    fi
    if [[ $method == *"ff"* ]]; then
        overridePar ml/create_training_dataset.sh "training-jetfakes-estimation-method" ff
    else
        overridePar ml/create_training_dataset.sh "training-jetfakes-estimation-method" mc
    fi
    for era in ${eras[@]}; do
        for channel in ${channels[@]}; do
        	updateSymlink $sm_htt_analysis_dir/ml/${era}_${channel}_${method} $sm_htt_analysis_dir/ml/${era}_${channel}
        	updateSymlink $sm_htt_analysis_dir/ml/${era}_${channel}_training_${method}.yaml $sm_htt_analysis_dir/ml/${era}_${channel}_training.yaml
        done
        updateSymlink $batch_out_local/${era}_${method} $batch_out_local/${era}
    done

}

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

### Subroutine called by runstages
function runana() {
    echo "analysis for:"
    echo '$era $STXS_SIGNALS $CATEGORIES $JETFAKES $EMBEDDING $method ${channels[@]}'
    echo "$era $STXS_SIGNALS $CATEGORIES $JETFAKES $EMBEDDING $method ${channels[@]}"

    if [[ $PROD_NEW_DATACARDS == 1 ]]; then
        echo "Prodcing datacard:"
        ## one could produce a datacard for stage1p1 and then just select the right one upon produce_workspace :)
        for channel in ${channels[@]}; do
            updateSymlink htt_${channel}_${method}.inputs-sm-Run${era}-ML.root htt_${channel}.inputs-sm-Run${era}-ML.root
        done
        ./datacards/produce_datacard.sh $era $STXS_SIGNALS $CATEGORIES $JETFAKES $EMBEDDING $method ${channels[@]} > /dev/null
    fi
    ./datacards/produce_workspace.sh ${era} $STXS_FIT > /dev/null
    echo "writing to $method-$STXS_SIGNALS-$STXS_FIT.txt"
    temp_file=$(mktemp)
    ./combine/signal_strength.sh $era $STXS_FIT > $temp_file
    cat $temp_file | sed -n -e '/ --- MultiDimFit ---/,$p'| sed  "/Printing Message Summary/q" | head -n -2 | grep -v INFO:  | tee "signal-strength-tt-$method-$STXS_SIGNALS-$STXS_FIT.txt"
    ### add more analysis scripts here
    PROD_NEW_DATACARDS=0
}

function genshapes() {
    for method in ${methods[@]}; do
        cd $sm_htt_analysis_dir
        setmethod $m
        for era in ${eras[@]}; do
            redoConversion=0
            if [[ ! -f ${era}_${method}_shapes.root  ]]; then
                loginfo Producing shapes for $era $method ${channels[@]}
                ./shapes/produce_shapes.sh $era $method ${channels[@]}
                redoConversion=1
            else
                loginfo Skipping shape generation as ${era}_${method}_shapes.root exists
            fi
            for channel in ${channels[@]}; do
		        fn=htt_${channel}_${method}.inputs-sm-Run${era}-ML.root
                if [[ ! -f $fn ]]; then
			        [[ $redoConversion != 1 ]] && logwarn $fn does not exist: rerunning shape syncing
                    redoConversion=1
                fi
            done
            if [[ $redoConversion == 1 ]]; then
                loginfo Syncing shapes for $era ${channels[@]}
                ./shapes/convert_to_synced_shapes.sh $era $method
            fi
        done
    done
}



### run the analysis for mc and emb and all stages
function runstages() {
    #export STXS_SIGNALS STXS_FIT PROD_NEW_DATACARDS
    JETFAKES=1                  # options: 0, 1
    EMBEDDING=1                 # options: 0, 1
    CATEGORIES="stxs_stage1p1"
    for method in ${methods[@]}; do
        cd $sm_htt_analysis_dir
        METHOD=$m
        setmethod $m
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

    done
}

### compares Signal strengths of the Samples classified on the training based on MCvsEMB dataset creation
function compareSignRes {
    for channel in ${channels[@]}; do
        for x in stage0-inclusive stage0-stxs_stage0 stage1p1-stxs_stage1p1; do
            echo signal-strength-$channel-mc_{mc,ff}-stxs_$x.txt | xargs ls
        done
    done
    # for mcfile in mc-stxs_stage*txt; do
    #     embfile=$( echo $mcfile | sed 's@mc@emb@')
    #     ./utils/inlinediff.py <(echo $mcfile; cat $mcfile ) <(echo $embfile; cat $embfile) | sort
    # done
}

#################################################################################################
### Main procedure. Ensures, no completed step is run again by sourcing completedMilestones
### in the beginning and overwriting variables upon completion of the step
#################################################################################################

function compenv() {
    varnames=(era channel method eras  channels  methods erasarg channelsarg methodsarg mldir trainingConfFile anaSSStep  llwtnndir temp_file PROD_NEW_DATACARDS redoConversion fn JETFAKES EMBEDDING CATEGORIES METHOD PROD_NEW_DATACARDS STXS_SIGNALS STXS_FIT USE_BATCH_SYSTEM)
    vars=($era $channel $method $eras $channels $methods $erasarg $channelsarg $methodsarg $mldir $trainingConfFile $anaSSStep $llwtnndir $temp_file $PROD_NEW_DATACARDS $redoConversion $fn $JETFAKES $EMBEDDING $CATEGORIES $METHOD $PROD_NEW_DATACARDS $STXS_SIGNALS $STXS_FIT $USE_BATCH_SYSTEM)
    for (( i=0; i<${#vars[@]}; i++ )); do
        echo "${varnames[$i]}=${vars[$i]}"
    done
}

function create_training_dataset() {
    logandrun ./ml/create_training_dataset.sh $erasarg $channelsarg
    loginfo All $method datasets created
}
function sum_training_weights() {
    logandrun ./ml/sum_training_weights.sh $erasarg $channelsarg
    loginfo All $method class weights calculated
}

function mltrain() {
    for era in ${eras[@]}; do
        for channel in ${channels[@]}; do
            loginfo ./ml/run_training.sh $era $channel
            ./ml/run_training.sh $era $channel
        done
    done
}

function mltest() {
    for era in ${eras[@]}; do
        for channel in ${channels[@]}; do
            loginfo ./ml/run_testing.sh $era $channel
            ./ml/run_testing.sh $era $channel
        done
    done
}

function main() {
    if [[ $anaSSStep < 1 ]]; then
        for method in ${methods[@]}; do
            setmethod $m
            ##### Create training dataset:
            if [[ ! $( getPar completedMilestones ${method}_ds_created ) == 1  ]]; then
                create_training_dataset
                overridePar completedMilestones ${method}_ds_created 1

            else
                loginfo Skipping $method training dataset creation
            fi

            #### Correct the class weight in ml/era_channel_training.yaml
            if [[ ! $( getPar completedMilestones ${method}_sum_training_weights ) == 1  ]]; then
                sum_training_weights
                overridePar completedMilestones ${method}_sum_training_weights 1
            else
                loginfo Skipping $method class weight calculation
            fi

            ### Run trainings ml/era_channel_training.yaml ml/era_channel/merge_foldX_*.root -> ml/era_channel/foldX_keras_model.h5
            if [[ ! $( getPar completedMilestones ${method}_training  ) == 1  ]]; then
                mltrain
                overridePar completedMilestones ${method}_training 1
                loginfo All $method trainings completed
            else
                loginfo Skipping $method training
            fi
            ### Run testings ml/era_channel_testing.yaml
            if [[ ! $( getPar completedMilestones ${method}_testing  ) == 1  ]]; then
                mltest
                overridePar completedMilestones ${method}_testing 1
                loginfo All $method testings completed
            else
                loginfo Skipping $method testing
            fi

            if [[ $USE_BATCH_SYSTEM == 1 ]]; then
                ### convert the models to lwtnn format ml/era_channel/foldX_keras_model.h5 -> ml/era_channel/foldX_lwtnn.json
                if [[ ! $( getPar completedMilestones ${method}_models_exported  ) == 1  ]]; then
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
                    overridePar completedMilestones ${method}_models_exported 1
                    loginfo Models for $method application exported
                else
                    loginfo Skipping $method model export
                fi

                ### Apply the model ml/era_channel/foldX_keras_model.h5 oder ml/era_channel/foldX_lwtnn.json + ntuples -> NNScore friendTree
                if [[ ! $( getPar completedMilestones ${method}_NNApplication_started  ) == 1  ]]; then
                    ## NNScore Friend Tree Production on the etp
                    cd $sm_htt_analysis_dir
                    for era in ${eras[@]}; do
                        ./batchrunNNApplication.sh ${era} $channelsarg $cluster "submit" ${era}_${method}
                    done
                    overridePar completedMilestones ${method}_NNApplication_started 1
                    loginfo "Jobs for $method application created. Submit the jobs and, in completedMilestones, set ${method}_NNApplication_ended to 1 if the jobs ran successfull or you need to resubmit"
                    exit 0
                else
                    loginfo Skipping $method batch submission for NNScore FriendTrees
                fi

                ### check if finished resubmit if needed
                if [[ $( getPar completedMilestones ${method}_NNApplication_started  ) == "1"  ]] && [[ $( getPar completedMilestones ${method}_NNApplication_ended  ) == "0"  ]] ; then
                    cd $sm_htt_analysis_dir
                    for era in ${eras[@]}; do
                        ./batchrunNNApplication.sh ${era} $channelsarg $cluster "check" ${era}_${method}
                    done
                    loginfo  In completedMilestones set ${method}_NNApplication_ended to 1 if the jobs ran successfull
                    exit 0
                else
                    loginfo Skipping $method NNScore FriendTree batch resubmission
                fi

                if [[ ! $( getPar completedMilestones ${method}_NNApplication_collected  ) == 1  ]]; then
                    cd $sm_htt_analysis_dir
                    for era in ${eras[@]}; do
                        ./batchrunNNApplication.sh ${era} $channelsarg $cluster "collect" ${era}_${method}
                    done
                    overridePar completedMilestones ${method}_NNApplication_collected 1
                    loginfo Jobs for $method application completed and collected. Move outputs now!
                else
                    loginfo Skipping $method NNScore FriendTree Batch collection
                fi

                if [[ ! $( getPar completedMilestones ${method}_NNApplication_synced ) = 1  ]]; then
                    if [[ $cluster == etp ]]; then
                            loginfo Cluster is ept, no need to sync.
                    elif [[ $cluster == lxplus ]]; then
                        read -p "Sync files from $USER@lxplus.cern.ch:$batch_out/${era}_${method} to $batch_out/${era}_${method} now? y/[n]" yn
                        if [[ ! $yn == "y" ]]; then
                            logerror "!=y \n aborting"
                            exit 0
                        fi

                        for era in ${eras[@]}; do
                            [[ ! -d $batch_out_local/${era}_${method}/NNScore_workdir/NNScore_collected  ]] && mkdir -p $batch_out_local/${era}_${method}/NNScore_workdir/NNScore_collected
                            loginfo lxrsync $USER@lxplus.cern.ch:$batch_out/${era}_${method}/NNScore_workdir/NNScore_collected/ $batch_out_local/${era}_${method}/NNScore_workdir/NNScore_collected
                            lxrsync $USER@lxplus.cern.ch:$batch_out/${era}_${method}/NNScore_workdir/NNScore_collected/ $batch_out_local/${era}_${method}/NNScore_workdir/NNScore_collected
                        done
                    fi
                    overridePar completedMilestones ${method}_NNApplication_synced 1
                    loginfo $method NNScore FriendTree sync completed
                else
                    loginfo Skipping $method NNScore FriendTree sync
                fi
            else ## USE_BATCH_SYSTEM==0
                for era in ${eras[@]}; do
                    for channel in ${channels[@]}; do
                        ./ml/run_application $era $channel
                    done
                done
            fi
        done ## for method in mc, emb
        overridePar completedMilestones anaSSStep 1
        anaSSStep=1
    fi
    loginfo reached analysis!
    if [[ $anaSSStep < 2 ]]; then
    	loginfo generating shapes
        genshapes
        loginfo Done generating and syncing shapes
        overridePar completedMilestones anaSSStep 2
        anaSSStep=2
    fi
    if [[ $anaSSStep < 3 ]]; then
        loginfo running stages
        runstages
	    loginfo completed stages
        overridePar completedMilestones anaSSStep 3
        anaSSStep=3
    fi
    if [[ $anaSSStep < 4 ]]; then
        compareSignRes
        read -p "Run finished. Start new run? y/[n]" yn
        if [[ $yn == "y" ]]; then
            sed -E -r "s@(\w+)(\s+|=)\w+@\1\20@" completedMilestones
            echo ""
        fi
    fi
}

[[ $sourced == 1 ]] && [[ ! "bash" =~ $0 ]] && logerror "shell is sourced by another shell than bash, aborting" && exit 1
[[ $sourced == 0 ]] && main
echo