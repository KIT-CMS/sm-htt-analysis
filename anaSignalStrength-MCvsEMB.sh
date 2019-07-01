#!/usr/bin/env bash
### Skript to compare the training with embedding and mc samples in it's effect on the signal strength

set -e # quit on error
shopt -s checkjobs # wait for all jobs before exiting

for DIRECTORY in shapes datacards combine plotting utils
do
    if [ ! -d "$DIRECTORY" ]; then
        echo "[FATAL] Directory $DIRECTORY not found, you are not in the top-level directory of the analysis repository?"
        exit 1
    fi
done

outdir=$(pwd)
cd ~/sm-htt

# if [[ $setupSourced != 1 ]]; then
#     source utils/setup_cvmfs_sft.sh
#     source utils/setup_python.sh
#     source utils/setup_samples.sh $ERA
#     export setupSourced=1
# fi
# export PARALLEL=1

export METHOD STXS_SIGNALS STXS_FIT PROD_NEW_DATACARDS
ERA=2017 #$1               # options: 2016, 2017
CHANNELS="tt" #${@:2}      # options: em, et, mt, tt

JETFAKES=1                  # options: 0, 1
EMBEDDING=1                 # options: 0, 1
CATEGORIES="stxs_stage1p1"

source completedMilestones
#trap "echo \"Current completed State: \$anaSSStep=$anaSSStep\"; echo $anaSSStep > completedMilestones " INT KILL FAIL EXIT

function setmethod () {
    m=$1
    ln -s -f "/home/mscham/data/mcToEMB-Run2/analysis/$m/htt_tt.inputs-sm-Run2017-ML.root" "htt_tt.inputs-sm-Run2017-ML.root"
    overridePar ml/create_training_dataset.sh "training-z-estimation-method" $m
    # cd /home/mscham/sm-htt/ml
    # if [ "emb" = $m ] ; then
    # 	ln -sfn 2017_tt_mc 2017_tt
    # 	ln -sf 2017_tt_training_mc.yaml 2017_tt_training.yaml
    # elif [ "mc" = $m ]; then
    # 	ln -sfn 2017_tt_emb 2017_tt
    # 	ln -sf 2017_tt_training_emb.yaml 2017_tt_training.yaml
    # else
    # 	echo "#####\nError switching links!"
    # 	exit 1
    # fi
    # ls -l 2017_tt 2017_tt_training.yaml
    # cd -
}

function overridePar() {
    file=$1
    arg=$2
    val=$3
    sed -E -r "s@(\s--$arg)(\s+|=)\w+@\1\2$val@" $file
}
function getPar() {
    file=$1
    arg=$2
    grep "$2=" $file | sed -E "s@.*$arg(\s+|=)(\w+)@\2@"
}

### produce datacard from era_shapes.root and run the statistical training_z_estimation_method
### plain text resultst to  "$outdir/$METHOD-$STXS_SIGNALS-$STXS_FIT.txt"
function runana() {
    echo "analysis for:"
    echo '$METHOD $STXS_SIGNALS $STXS_FIT $ERA $CATEGORIES $JETFAKES $EMBEDDING $CHANNELS'
    echo "$METHOD $STXS_SIGNALS $STXS_FIT $ERA $CATEGORIES $JETFAKES $EMBEDDING $CHANNELS"
    if [[ $PROD_NEW_DATACARDS == 1 ]]; then
        echo "Prodcing datacard:"
        ## one could produce a datacard for stage1p1 and then just select the right one upon produce_workspace :)
        ./datacards/produce_datacard.sh $ERA $STXS_SIGNALS $CATEGORIES $JETFAKES $EMBEDDING $CHANNELS > /dev/null
    fi
    ./datacards/produce_workspace.sh $ERA $STXS_FIT > /dev/null
    echo "writing to $outdir/$METHOD-$STXS_SIGNALS-$STXS_FIT.txt"
    temp_file=$(mktemp)
    ./combine/signal_strength.sh $ERA $STXS_FIT > $temp_file
    cat $temp_file | sed -n -e '/ --- MultiDimFit ---/,$p'| sed  "/Printing Message Summary/q" | head -n -2 | grep -v INFO: | tee "$outdir/$METHOD-$STXS_SIGNALS-$STXS_FIT.txt"

    ### add more analysis scripts here

    PROD_NEW_DATACARDS=0
}

function exportForApplication {
    ERA=$1
    CHANNEL=$2
    METHOD=$3
    bash -x "
    source utils/setup_cvmfs_sft.sh
    source utils/setup_python.sh
    python htt-ml/application/export_keras_to_json.py  ml/${ERA}_${CHANNEL}_training.yaml ml/${ERA}_${CHANNEL}_application.yaml"
    ./ml/translate_models.sh $ERA $CHANNEL
    ./ml/export_lwtnn.sh $ERA $CHANNEL

    #statements
}


### run the analysis for mc and emb and all stages
function runStages() {
    for m in "mc" "emb"; do
        METHOD=$m
        setmethod $METHOD
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

###
function compareSignRes {
    cd $outdir
    for mcfile in mc-stxs_stage*txt; do
        embfile=$( echo $mcfile | sed 's@mc@emb@')
        inlinediff.py <(echo $mcfile; cat $mcfile ) <(echo $embfile; cat $embfile) | sort
    done
}

function main() {
    if [[ $anaSSStep < 1]]; then
        for m in "mc" "emb"; do
            setmethod

            if [[ ! $( getPar completedMilestones ${m}_create_training_dataset ) == 1  ]]; then
                ./ml/create_training_dataset.sh $ERA
                overridePar completedMilestones ${m}_ds 1
            fi

            if [[ ! $( getPar completedMilestones ${m}_sum_training_weights ) == 1  ]]; then
                ./ml/sum_training_weights.sh $ERA
                overridePar completedMilestones ${m}_sum_training_weights 1
            fi

            if [[ ! $( getPar completedMilestones ${m}_training  ) == 1  ]]; then
                ./ml/run_training.sh $ERA $CHANNEL
                overridePar completedMilestones ${m}_training 1
                ## not needed
                #./ml/run_testing.sh $ERA $CHANNEL
            fi

            if [[ ! $( getPar completedMilestones ${m}_NNApplication_started  ) == 1  ]]; then
                ## NNScore Friend Tree Production on the etp
                ./ml/export_for_application.sh $ERA $CHANNEL
                ~/ownAnaScripts/batchrunNNApplication.sh "$ERA" "" "submit"
                #./ml/run_application.sh $ERA $CHANNEL
                overridePar completedMilestones ${m}_NNApplication_started 1
                exit 0
            fi
            if [[ ! $( getPar completedMilestones ${m}_NNApplication_ended  ) == 1  ]]; then
                ~/ownAnaScripts/batchrunNNApplication.sh "$ERA" "" "check"
                if [[ durchgelaufen ]]; then
                    ~/ownAnaScripts/batchrunNNApplication.sh "$ERA" "" "collect"
                    overridePar completedMilestones ${m}_NNApplication_ended 1
                else
                    exit 0
                fi
            fi
        done
        overridePar completedMilestones anaSSStep 1
        anaSSStep=1
    fi
    if [[ $anaSSStep < 2 ]]; then
        runStages
        overridePar completedMilestones anaSSStep 2
        anaSSStep=2
    fi
    if [[ $anaSSStep < 3 ]]; then
        compareSignRes
        read -p "Run finished. Start new run? y/[n]" yn
        if [[ yn = "y" ]]; then
            sed -E -r "s@(\w+)(\s+|=)\w+@\1\20@" completedMilestones
            echo ""
        fi
    fi
}

main
