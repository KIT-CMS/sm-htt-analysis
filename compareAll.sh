#!/usr/bin/env bash
### Skript to compare the training with embedding and mc samples in it's effect on the signal strength

## Detect if the script is being sourced
#mklement0 https://stackoverflow.com/questions/2683279/how-to-detect-if-a-script-is-being-sourced
([[ -n $ZSH_EVAL_CONTEXT && $ZSH_EVAL_CONTEXT =~ :file$ ]] ||
[[ -n $KSH_VERSION && $(cd "$(dirname -- "$0")" &&
printf '%s' "${PWD%/}/")$(basename -- "$0") != "${.sh.file}" ]] ||
[[ -n $BASH_VERSION ]] && (return 0 2>/dev/null)) && export sourced=1 || export sourced=0

if [[ $sourced == 0 ]]; then
    echo "This is a function library, not a script."
    exit 1
fi
set -o pipefail

source utils/bashFunctionCollection.sh

## make sure all the output directories are there
ensureoutdirs

## set the user specific paths (cluster, remote, batch_out, cmssw_src)
source .userconfig

########### Argument handling and Tests ##################
if [[ "bash" =~ $0 ]]; then
    shopt -s checkjobs # wait for all jobs before exiting
    #set -u # disallow using unused variables
    IFS=',' read -r -a eras <<< $1
    IFS=',' read -r -a channels <<< $2
    IFS=',' read -r -a tags <<< $3
else #zsh
    setopt sh_word_split
    # IFS=',' eras=("${(@f)$1}")
    setopt monitor # wait for all jobs before exiting
    IFS=',' eras=($1)
    IFS=',' channels=($2)
    IFS=',' tags=($3)
    IFS=' '
fi

erasarg=$1
channelsarg=$2
tagsarg=$3

if [[ $erasarg == "all" ]]; then
    loginfo CONDITIONAL_TRAINING is on
    CONDITIONAL_TRAINING=1
    eras=""
else
    CONDITIONAL_TRAINING=0
fi

[[ " " =~ ${eras[*]} ]] && eras=("2016" "2017" "2018") erasarg="2016,2017,2018"
[[ " " =~ ${channels[*]} ]] && channels=("em" "et" "tt" "mt") channelsarg="em,et,mt,tt"
[[ " " =~ ${tags[*]} ]] && tags=("default") tagsarg="default"

loginfo Eras: ${erasarg}  Channels: ${channelsarg} Tag: ${tagsarg}
loginfo Following functions are provided: $( grep -E  '^function .*{' compareAll.sh | sed "s@function \(\w\+\).*@\1@" | tr "\n" " " )



if [[ ! -z ${4:-} ]]; then
    logerror only takes 3 arguments, seperate multiple eras and channels by comma eg: 2016,2018 mt,em   or \"\" em
    [[ $sourced != 1 ]] && exit 1
fi
for era in ${eras[@]}; do
    if [[ ! "2016 2017 2018" =~ ${era} ]]; then
        logerror ${era} is not a valid era.
        [[ $sourced != 1 ]] && exit 1
    fi
done
for channel in ${channels[@]}; do
    if [[ ! "em et tt mt cmb all" =~ ${channel} ]]; then
        logerror ${channel} is not a valid channel.
        [[ $sourced != 1 ]] && exit 1
    fi
done

for DIRECTORY in shapes datacards combine plotting utils
do
    if [ ! -d "$DIRECTORY" ]; then
        logerror "Directory $DIRECTORY not found, you are not in the top-level directory of the analysis repository?"
        [[ $sourced != 1 ]] && exit 1
    fi
done
############################################
############# Ensure all folders and files are available for mc and emb
function ensuremldirs() {
    for tag in ${tags[@]}; do
        for era in ${eras[@]}; do
            for channel in ${channels[@]}; do
                mldir=output/ml/${era}_${channel}_${tag}
                if [[ ! -d $mldir ]]; then
                    mkdir $mldir
                    loginfo "Creating $mldir"
                fi
            done
        done
    done
}


function compenv()(
    set +u
    eval echo $(echo `cat compareAll.sh | grep -E "\w+=" | sed -E "s@^\s+@@" | grep -v -E "^#" | sed -E "s#.*( |^)(\w+)=.*#\2 = \\\${\2\[@\]}#" | sort -u | tr "\n" "#"`) | tr "#" "\n"
)

function genTrainingDS() {
    ensuremldirs
    for tag in ${tags[@]}; do
        for channel in ${channels[@]}; do
            for era in ${eras[@]}; do
                logandrun ./ml/create_training_dataset.sh ${era} ${channel} ${tag}
            done
            condwait
        done
    done
    wait
    if [[ $ERA == *"all"* || ${#eras[@]} == 3 ]]; then
        genCombinedDSConfig
    fi
}
function genCombinedDSConfig() {
    ensuremldirs
    for tag in ${tags[@]}; do
        for channel in ${channels[@]}; do
            echo "Creating dataset config for conditional training"
            outdir=output/ml/all_eras_${channel}_${tag}
            [[ -d $outdir ]] || mkdir -p $outdir
            (
                source utils/setup_cvmfs_sft.sh
                logandrun python ml/create_combined_config.py \
                    --tag ${tag} \
                    --channel ${channel} \
                    --output_dir ${outdir}
            )
        done
    done
}

function mltrain() {
    ensuremldirs
    for tag in ${tags[@]}; do
        if [[ $CONDITIONAL_TRAINING == 1 ]]; then
            for channel in ${channels[@]}; do
                logandrun ./ml/run_training.sh all ${channel} ${tag}
            done
        else
            for era in ${eras[@]}; do
                for channel in ${channels[@]}; do
                    logandrun ./ml/run_training.sh ${era} ${channel} ${tag}
                done
                wait
            done
        fi
    done
}

function checkTrainings() {
    ensuremldirs
    for tag in ${tags[@]}; do
        for channel in ${channels[@]}; do
            for fold in 0 1 ; do
                if [[ $CONDITIONAL_TRAINING == 1 ]]; then
                    fn=output/log/logandrun/python-htt-ml-training-keras_training.py-output-ml-all_eras_${channel}_${tag}-dataset_config.yaml-${fold}.log
                    if [[ ! -f $fn || ! $( tail -n1 $fn ) =~ 'COMPLETE'   ]]; then
                        echo "$tag $channel $fold training not done"
                    fi
                else
                    for era in ${eras[@]}; do
                        fn=output/log/logandrun/python-htt-ml-training-keras_training.py-output-ml-${era}_${channel}_${tag}-dataset_config.yaml-${fold}.log
                        if [[ ! -f $fn || ! $( tail -n1 $fn ) =~ 'COMPLETE'   ]]; then
                            echo "$tag $era $channel $fold training not done"
                        fi
                    done
                fi
            done
        done
    done
}

function mltest() {
    ensuremldirs
    for tag in ${tags[@]}; do
        if [[ $CONDITIONAL_TRAINING == 1 ]]; then
            for era in ${eras[@]}; do
                for channel in ${channels[@]}; do
                    logandrun ./ml/run_testing_all_eras.sh ${era} ${channel} ${tag}
                done
            done
        else
            for era in ${eras[@]}; do
                for channel in ${channels[@]}; do
                    logandrun ./ml/run_testing.sh ${era} ${channel} ${tag}
                done
            done
        fi
    done
}

#### converts models to the form needed for submission to a batch system
function exportForApplication {
    for tag in ${tags[@]}; do
        if [[ $CONDITIONAL_TRAINING == 1 ]]; then
            for channel in ${channels[@]}; do
                (
                    set -e
                    logandrun ./ml/translate_models.sh all ${channel} ${tag}
                logandrun ./ml/export_lwtnn.sh all ${channel}  ${tag} ) &
                condwait
            done
        else
            for era in ${eras[@]}; do
                for channel in ${channels[@]}; do
                    (
                        set -e
                        logandrun ./ml/translate_models.sh ${era} ${channel} ${tag}
                    logandrun ./ml/export_lwtnn.sh ${era} ${channel}  ${tag} ) &
                    condwait
                done
            done
        fi
    done
    wait
}

function provideCluster() (
    set -e
    tag=$1
    era=$2
    llwtnndir=$cmssw_src_local/HiggsAnalysis/friend-tree-producer/data/inputs_lwtnn
    find $llwtnndir -type l -iname "fold*_lwtnn.json" -delete
    for channel in ${channels[@]}; do
        llwtnndir_sel=$llwtnndir/$tag/${era}/${channel}
        ### Supply the generated models in the hard-coded path in the friendProducer
        ### alogrsync $remote will dereference this symlink
        [[ ! -d $llwtnndir_sel ]] && mkdir -p $llwtnndir_sel
        for fold in 0 1;
        do
            updateSymlink $sm_htt_analysis_dir/output/ml/${era}_${channel}_${tag}/fold${fold}_lwtnn.json  $llwtnndir_sel/fold${fold}_lwtnn.json
        done
    done
    updateSymlink $sm_htt_analysis_dir/datasets/datasets.json $cmssw_src_local/HiggsAnalysis/friend-tree-producer/data/input_params/datasets.json
    if [[ ! $cluster =~ "etp"  ]]; then
        logandrun alogrsync $remote -rLPthz ${cmssw_src_local}/HiggsAnalysis/friend-tree-producer/data/ $remote:${cmssw_src}/HiggsAnalysis/friend-tree-producer/data
    fi
)

function applyOnCluster()(
    set -e
    for tag in ${tags[@]}; do
        export tag
        for era in ${eras[@]}; do
            if ! friendTreesExistLocal; then
                provideCluster $tag $era
                logandrun ./batchrunNNApplication.sh ${era} ${channelsarg} "submit" ${tag} $CONDITIONAL_TRAINING
                logandrun ./batchrunNNApplication.sh ${era} ${channelsarg} "rungc" ${tag} $CONDITIONAL_TRAINING
                logandrun ./batchrunNNApplication.sh ${era} ${channelsarg} "collect" ${tag} $CONDITIONAL_TRAINING
                copyFromCluster
                logandrun ./batchrunNNApplication.sh ${era} ${channelsarg} "delete" ${tag} $CONDITIONAL_TRAINING || return 1
            else
                loginfo "Skipping Application for $tag $era because friend tree exists"
            fi
        done
    done
)

function friendTreesExistLocal() {
    nnscorefolder=$batch_out_local/${era}/nnscore_friends/${tag}
    if [[ ! -d $nnscorefolder ]]; then
        return 1
    fi
    if [[ ! -f $nnscorefolder/friendTreeComplete.lock && $( du -bs $nnscorefolder | cut -f1 ) -gt 11812544 ]]; then
        touch $nnscorefolder/friendTreeComplete.lock
        loginfo "Marking $nnscorefolder as complete"
        return 0
    else
        if [[ -f $nnscorefolder/friendTreeComplete.lock ]];then
            return 0
        else
            return 1
        fi
    fi
}

function copyFromCluster()(
    set -e
    nnscorefolder=$batch_out_local/${era}/nnscore_friends/${tag}
    [[ ! -d $nnscorefolder  ]] && mkdir -p $nnscorefolder
    if [[ $cluster == etp7 ]]; then
        logandrun rsync -rLPthz $batch_out/${era}_${tag}/NNScore_workdir/NNScore_collected/ $nnscorefolder
    else
        logandrun alogrsync $remote -rLPthz --delete $remote:$batch_out/${era}_${tag}/NNScore_workdir/NNScore_collected/ $nnscorefolder
    fi
    if ! friendTreesExistLocal; then
        logerror Recieved NNScore Friend folder to small!
        return 1
    fi
)


function genShapes() {
    ensureoutdirs
    for tag in ${tags[@]}; do
        for era in ${eras[@]}; do
            for channel in ${channels[@]}; do
                fn=output/shapes/${era}-${tag}-${channel}-shapes.root
                if [[ ! -f $fn  ]]; then
                    logandrun ./shapes/produce_shapes.sh ${era} ${channel} ${tag} || return 1
                else
                    loginfo Skipping shape generation as $fn exists
                fi
            done
        done
    done
}

function submitBatchShapes()(
    source utils/setup_cvmfs_sft.sh
    source utils/setup_python.sh
    ensureoutdirs
    if [ -n "${X509_USER_PROXY+1}" ]; then
        echo "Using $X509_USER_PROXY as proxy"
    else
        export X509_USER_PROXY=/home/${USER}/.globus/x509up
        echo "Setting proxy path to $X509_USER_PROXY"
    fi
    logandrun python ./condor_jobs/construct_remote_submit.py --eras $erasarg --channels $channelsarg --tags $tagsarg --mode submit --gcmode optimal --workdir output/condor_jobs_wd
)

function mergeBatchShapes()(
    source utils/setup_cvmfs_sft.sh
    source utils/setup_python.sh
    logandrun python ./condor_jobs/construct_remote_submit.py --eras $erasarg --channels $channelsarg --tag $tagsarg --mode merge --gcmode optimal --workdir output/condor_jobs_wd
    condwait
)

function blindShapes() {
    for channel in ${channels[@]}; do
        for era in ${eras[@]}; do
            for tag in ${tags[@]}; do
               logandrun ./shapes/apply_blinding.sh ${era} ${channel} ${tag} "global" &
            done
            condwait
        done
    done
    wait
}



function syncShapes() {
    for channel in ${channels[@]}; do
        for era in ${eras[@]}; do
            for tag in ${tags[@]}; do
                fn=output/shapes/${era}-${tag}-${channel}-synced-ML.root
                #if [[ ! -f $fn  || $( stat -c%s $fn ) -le 2000 ]]; then
                logandrun ./shapes/convert_to_synced_shapes.sh ${era} ${channel} ${tag} &
                #else
                #    loginfo Skipping shape syncing as $fn exists
                #fi
            done
            condwait
        done
    done
    wait
}


export JETFAKES=1 EMBEDDING=1 CATEGORIES="stxs_stage1p1"
function genDatacards(){
    ensureoutdirs
    for era in ${eras[@]}; do
        for STXS_SIGNALS in "stxs_stage0" "stxs_stage1p1"; do
            for tag in ${tags[@]}; do
                if [[ $tag == *"stage0"* ]]; then
                    CATEGORIES="stxs_stage0"
                elif [[ $tag == *"inc"* ]]; then
                    CATEGORIES="inclusive"
                else
                    CATEGORIES="stxs_stage1p1"
                fi
                DATACARDDIR=output/datacards/${era}-${tag}-smhtt-ML/${STXS_SIGNALS}
                [ -d $DATACARDDIR ] || mkdir -p $DATACARDDIR
                logandrun ./datacards/produce_datacard.sh ${era} $STXS_SIGNALS $CATEGORIES $JETFAKES $EMBEDDING ${tag} ${channelsarg} &
            done
            condwait
        done
    done
    wait
}

function genWorkspaces(){
    ensureoutdirs
    for era in ${eras[@]}; do
        for STXS_FIT in "inclusive" "stxs_stage0" "stxs_stage1p1"; do
            for tag in ${tags[@]}; do
                if [[ $STXS_FIT == "inclusive" || $STXS_FIT == "stxs_stage0" ]]; then
                    STXS_SIGNALS=stxs_stage0
                elif [[ $STXS_FIT == "stxs_stage1p1" ]] ; then
                    STXS_SIGNALS=stxs_stage1p1
                fi
                fn="output/datacards/${era}-${tag}-smhtt-ML/${STXS_SIGNALS}/cmb/125/${era}-${STXS_FIT}-workspace.root"
                if [[ ! -f $fn ]]; then
                    logandrun ./datacards/produce_workspace.sh ${era} $STXS_FIT ${tag} &
                    condwait
                    #[[ $? == 0 ]] || return $?
                else
                    logwarn "skipping workspace creation, as  $fn exists"
                fi
            done
        done
    done
    wait
}

### Subroutine called by runstages
### do not run this parallel! it writes to fit.root in the main dir and is then moved
function runana() {
    ensureoutdirs
    for STXS_FIT in "inclusive" "stxs_stage0" "stxs_stage1p1"; do
        if [[ $STXS_FIT == "inclusive" || $STXS_FIT == "stxs_stage0" ]]; then
            STXS_SIGNALS=stxs_stage0
        elif [[ $STXS_FIT == "stxs_stage1p1" ]] ; then
            STXS_SIGNALS=stxs_stage1p1
        fi
        for era in ${eras[@]}; do
            for tag in ${tags[@]}; do
                if [[ ${#channels[@]} == 4 ]]; then
                    channelsPlusCmb=("${channels[@]}" "cmb")
                else
                    channelsPlusCmb=("${channels[@]}")
                fi
                for channel in ${channelsPlusCmb[@]}; do
                    DATACARDDIR=output/datacards/${era}-${tag}-smhtt-ML/${STXS_SIGNALS}/$channel/125
                    logandrun ./combine/signal_strength.sh ${era} $STXS_FIT $DATACARDDIR $channel ${tag} &
                    condwait
                done
            done
        done
    done
    wait
}

## methods for combining eras
function genCmbDatacards() {
    ensureoutdirs
    for tag in ${tags[@]}; do
        for STXS_SIGNALS in "stxs_stage0" "stxs_stage1p1"; do
            if [[ ${#channels[@]} == 4 ]]; then
                channelsPlusCmb=("${channels[@]}" "cmb")
            else
                channelsPlusCmb=("${channels[@]}")
            fi
            for channel in ${channelsPlusCmb[@]}; do
                ./datacards/combine_datacards.sh $erasarg $channel $tag $STXS_SIGNALS
            done
        done
    done
}
function genCmbWorkspaces(){
    ensureoutdirs
    for STXS_FIT in "inclusive" "stxs_stage0" "stxs_stage1p1"; do
        if [[ $STXS_FIT == "inclusive" || $STXS_FIT == "stxs_stage0" ]]; then
            STXS_SIGNALS=stxs_stage0
        elif [[ $STXS_FIT == "stxs_stage1p1" ]] ; then
            STXS_SIGNALS=stxs_stage1p1
        fi
        for tag in ${tags[@]}; do
            era=all
            fn="output/datacards/${era}-${tag}-smhtt-ML/${STXS_SIGNALS}/cmb/125/${era}-${STXS_FIT}-workspace.root"
            logandrun ./datacards/produce_workspace.sh ${era} $STXS_FIT ${tag} &
            condwait
        done
    done
    wait
}
function runCmbAna() {
    ensureoutdirs
    for tag in ${tags[@]}; do
        for STXS_FIT in "inclusive" "stxs_stage0" "stxs_stage1p1"; do
            if [[ $STXS_FIT == "inclusive" || $STXS_FIT == "stxs_stage0" ]]; then
                STXS_SIGNALS=stxs_stage0
            elif [[ $STXS_FIT == "stxs_stage1p1" ]] ; then
                STXS_SIGNALS=stxs_stage1p1
            fi
            era=all
            if [[ ${#channels[@]} == 4 ]]; then
                channelsPlusCmb=("${channels[@]}" "cmb")
            else
                channelsPlusCmb=("${channels[@]}")
            fi
            for channel in ${channelsPlusCmb[@]}; do
                DATACARDDIR=output/datacards/${era}-${tag}-smhtt-ML/${STXS_SIGNALS}/$channel/125
                logandrun ./combine/signal_strength.sh ${era} $STXS_FIT $DATACARDDIR $channel ${tag} &
                condwait
            done
        done
    done
    wait
}
function prepareBackgroundGofs() {
    # generate the needed datacards and workspaces
    ensureoutdirs
    # first generate Datacards
    genDatacards
    genCmbDatacards
    # generate workspaces, all with inclusive signal only
    STXS_FIT="inclusive"
    temperas=$eras
    temperas+=("all")
    for tag in ${tags[@]}; do
        if [[ $tag == *"stage0"* ]]; then
            STXS_SIGNALS=stxs_stage0
        else
            STXS_SIGNALS=stxs_stage1p1
        fi
        for era in ${temperas[@]}; do
            fn="output/datacards/${era}-${tag}-smhtt-ML/${STXS_SIGNALS}/cmb/125/${era}-${STXS_FIT}-workspace.root"
            logandrun ./datacards/produce_workspace.sh ${era} $STXS_FIT ${tag} &
            condwait
        done
    done
    wait
}

function prepareSignalGofs() {
    # generate all datacards and needed workspaces
    ensureoutdirs
    genDatacards
    genCmbDatacards 
    genCmbWorkspaces
    genWorkspaces
}

function runBackgroundGofs() {
    source gof/build_mask.sh
    mode=$1
    masksignals=false
    if [[ $tag == *"stage1p1"* ]]; then
    	trainingstype="15node"
    else
    	trainingstype=$mode
    fi
    echo "Running GoFs with settings:"
    echo "Tags:     ${tags}"
    echo "Eras:     ${eras}"
    echo "Channels: ${channels}"
    echo "Training: ${trainingstype}"
    if [[ $mode == "1" ]]; then
        echo "Mode:     ${mode} - All categories seperately"
        for tag in ${tags[@]}; do
            for era in ${eras[@]}; do
                for channel in ${channels[@]}; do
                    backlist=$(buildCategories $trainingstype $tag $era $channel "backgrounds")
                    for category in ${backlist[@]}; do
                        mask=$(buildMask ${trainingstype} $tag $era $channel $category)
                        ./gof/gof_categories_saturated.sh $mode $tag $era $channel $category $mask 1
                    done
                done
            done
        done
    elif [[ $mode == "2" ]]; then
        echo "Mode:     ${mode} - Combine channels"
        category="999"
        for tag in ${tags[@]}; do
            for era in ${eras[@]}; do
                for channel in ${channels[@]}; do
                    if [ "$masksignals" = true ] ; then
                        mask=$(buildMask ${trainingstype} $tag $era $channel $category)
                    else
                        mask=""
                    fi
                    ./gof/gof_categories_saturated.sh $mode $tag $era $channel $category $mask 1
                done
                #./gof/gof_categories_KSAD.sh $mode $tag $era $channel $category "AD"
                #./gof/gof_categories_KSAD.sh $mode $tag $era $channel $category "KS"
            done
        done

    elif [[ $mode == "3" ]]; then
        echo "Mode:     ${mode} - Combine eras"
        category="999"
        channel="cmb"
        for tag in ${tags[@]}; do
            for era in ${eras[@]}; do
                if [ "$masksignals" = true ] ; then
                    mask=$(buildMask ${trainingstype} $tag $era $channel $category)
                else
                    mask=""
                fi
                ./gof/gof_categories_saturated.sh $mode $tag $era $channel $category $mask 0
            done
        done

    elif [[ $mode == "4" ]]; then
        echo "Mode:     ${mode} - Combine everything"
        category="999"
        channel="cmb"
        era="all"
        for tag in ${tags[@]}; do
            if [ "$masksignals" = true ] ; then
                mask=$(buildMask ${trainingstype} $tag $era $channel $category)
            else
                mask=""
            fi
            ./gof/gof_categories_saturated.sh $mode $tag $era $channel $category $mask 0
        done
    else
        echo "GoF mode unknown, possible modes are:"
        echo "Mode 1: all background categories seperately"
        echo "Mode 2: Combine channels"
        echo "Mode 3: Combine eras"
        echo "Mode 4: Combine everything"
    fi
}


function runSignalGofs() {
    source gof/build_mask_signal.sh
    mode=$1
    for tag in ${tags[@]}; do
        if [[ $tag == *"1p1"* ]]; then
            trainingstype="15node"
            tagtype="stxs_stage1p1"
        else
            trainingstype=$mode
            tagtype="stxs_stage0"
        fi
        echo "Running GoFs with settings:"
        echo "Tags:     ${tags}"
        echo "Eras:     ${eras}"
        echo "Channels: ${channels}"
        echo "Training: ${trainingstype}"
        echo "Tagtype:  ${tagtype}"
        if [[ $mode == "1" ]]; then
            echo "Mode:     ${mode} - All categories seperately"
            for era in ${eras[@]}; do
                for channel in ${channels[@]}; do
                    backlist=$(buildCategories $trainingstype $tag $era $channel "backgrounds")
                    for category in ${backlist[@]}; do
                        mask=$(buildMask ${trainingstype} $tag $era $channel $category)
                        ./gof/gof_signal_saturated.sh $mode $tag $era $channel $category $mask $tagtype 1
                    done
                done
            done
        elif [[ $mode == "2" ]]; then
            echo "Mode:     ${mode} - Combine channels"
            category="999"
            for era in ${eras[@]}; do
                for channel in ${channels[@]}; do
                    mask="asdf"
                    ./gof/gof_signal_saturated.sh $mode $tag $era $channel $category $mask ${tagtype} 0
                    ./gof/gof_signal_KSAD.sh $mode $tag $era $channel $category ${tagtype} "AD"
                    ./gof/gof_signal_KSAD.sh $mode $tag $era $channel $category ${tagtype} "KS"
                done
            done
        elif [[ $mode == "3" ]]; then
            echo "Mode:     ${mode} - Combine eras"
            category="999"
            channel="cmb"
            for era in ${eras[@]}; do
                mask="asdf"
                ./gof/gof_signal_saturated.sh $mode $tag $era $channel $category $mask $tagtype 0
            done
        elif [[ $mode == "4" ]]; then
            echo "Mode:     ${mode} - Combine everything"
            category="999"
            channel="cmb"
            era="all"
            mask="asdf"
            ./gof/gof_signal_saturated.sh $mode $tag $era $channel $category $mask $tagtype 0
        else
            echo "GoF mode unknown, possible modes are:"
            echo "Mode 1: all background categories seperately"
            echo "Mode 2: Combine channels"
            echo "Mode 3: Combine eras"
            echo "Mode 4: Combine everything"
        fi
    done
}


function plotBackgroundGofSummary() {
    mode=$1
    echo $mode
    possible_modes=("1" "2" "3")
    if [[ ! " ${possible_modes[@]} " =~ " ${mode} " ]]; then
        echo "GoF Plot mode unknown, possible modes are:"
        echo "Mode 1: plot all results"
        echo "Mode 2: plot combined channel results"
        echo "Mode 3: plot all failing results"
    else
        if [[ ! -d output/gof_summary ]]
        then
            mkdir -p output/gof_summary
        fi
        tagstring=$( IFS=$','; echo "${tags[*]}" )
        erastring=$( IFS=$','; echo "${eras[*]}" )
        channelstring=$( IFS=$','; echo "${channels[*]}" )

        ./gof/plot_background_gof_summary.py --path output/gof \
                --tags ${tagstring} --eras ${erastring} --channels ${channelstring} \
                --outputpath output/gof_summary --mode $mode
    fi
    
}

function plotSignalGofSummary() {
    mode=$1
    echo $mode
    possible_modes=("1" "2" "3" "4")
    if [[ ! " ${possible_modes[@]} " =~ " ${mode} " ]]; then
        echo "GoF Plot mode unknown, possible modes are:"
        echo "Mode 1: plot all results"
        echo "Mode 2: plot combined channel results"
        echo "Mode 3: plot all failing results"
        echo "Mode 3: plot distribution of all category p-values"
    else
        if [[ ! -d output/gof_signal_summary ]]
        then
            mkdir -p output/gof_signal_summary
        fi
        tagstring=$( IFS=$','; echo "${tags[*]}" )
        erastring=$( IFS=$','; echo "${eras[*]}" )
        channelstring=$( IFS=$','; echo "${channels[*]}" )

        logandrun ./gof/plot_signal_gof_summary.py --path output/gof_signal \
                --tags ${tagstring} --eras ${erastring} --channels ${channelstring} \
                --outputpath output/gof_signal_summary --mode $mode
    fi
    
}

function plotBlindedPreFitShapes() (
    ensureoutdirs
    # set -e
    for tag in ${tags[@]}; do
        export tag
        for era in ${eras[@]}; do
            STXS_FIT="inclusive"
            STXS_SIGNALS="stxs_stage0"
            if [[ $tag == *"stage0"* ]]; then
                CATEGORIES="stxs_stage0"
            elif [[ $tag == *"stage1p1"* ]]; then
                CATEGORIES="stxs_stage1p1_15node"
            else
                CATEGORIES="stxs_stage1p1"
            fi
            for channel in ${channels[@]}; do
                DATACARDDIR=output/datacards/${era}-${tag}-smhtt-ML/${STXS_SIGNALS}/$channel/125
                WORKSPACE=$DATACARDDIR/${era}-${STXS_FIT}-workspace.root
                FILE="${DATACARDDIR}/prefitshape-${era}-${tag}-${STXS_FIT}.root"
                echo "Fitfile: $FILE"
                [[ -f $FILE ]] || 
                (
                    source utils/setup_cmssw.sh
                    logandrun PostFitShapesFromWorkspace \
                        -m 125 -w ${WORKSPACE} \
                        -d ${DATACARDDIR}/combined.txt.cmb \
                        -o ${FILE}
                )
                # plot the prefitshape
                (
                    source utils/setup_cvmfs_sft.sh
                    source utils/setup_python.sh
                    PLOTDIR=output/plots/all-${tag}-${channel}_shape-plots
                    [ -d $PLOTDIR ] || mkdir -p $PLOTDIR
                    logandrun ./plotting/plot_shapes.py -i $FILE \
                        -o $PLOTDIR -c ${channel} -e $era \
                        --categories $CATEGORIES --fake-factor \
                        --embedding --normalize-by-bin-width -l \
                        --train-ff True --train-emb True --blind-data
                )
            done
        done
    done
)

function plotBlindedPostFitShapes(){
    ensureoutdirs
    for tag in ${tags[@]}; do
        export tag
        era="all"
        STXS_SIGNALS="stxs_stage0"
        STXS_FIT="inclusive"
        channel="cmb"
        if [[ $tag == *"stage0"* ]]; then
            CATEGORIES="stxs_stage0"
        elif [[ $tag == *"stage1p1"* ]]; then
            CATEGORIES="stxs_stage1p1_15node"
        else
            CATEGORIES="stxs_stage1p1"
        fi
        DATACARDDIR=output/datacards/${era}-${tag}-smhtt-ML/${STXS_SIGNALS}/$channel/125
        # Generate the fitDiagnostics
        FITFILE=$DATACARDDIR/fitDiagnostics.hesse-${era}-${tag}-${channel}-${STXS_FIT}.MultiDimFit.mH125.root
        [[ -f $FITFILE ]] || 
        logandrun ./combine/signal_strength.sh ${era} $STXS_FIT $DATACARDDIR $channel ${tag} "bkg_robustHesse" 
        # generate the postfitshape
        FILE="${DATACARDDIR}/postfitshape-${era}-${tag}-${STXS_FIT}.root"
        [[ -f $FILE ]] || 
        (
            source utils/setup_cmssw.sh
            WORKSPACE=$DATACARDDIR/${era}-${STXS_FIT}-workspace.root
            logandrun PostFitShapesFromWorkspace \
                -m 125 -w ${WORKSPACE} \
                -d ${DATACARDDIR}/combined.txt.cmb \
                -o ${FILE} \
                -f ${FITFILE}:fit_b \
                --postfit --skip-prefit
        )
        for channel in ${channels[@]}; do
            ## plot the preditshape and postfitshape
            (
                source utils/setup_cvmfs_sft.sh
                source utils/setup_python.sh
                PLOTDIR=output/plots/${era}-${tag}-${channel}_shape-plots
                [ -d $PLOTDIR ] || mkdir -p $PLOTDIR
                for PLOTERA in "2016" "2017" "2018"
                do
                    logandrun ./plotting/plot_shapes.py -i $FILE -o $PLOTDIR \
                        -c ${channel} -e $PLOTERA $OPTION --categories $CATEGORIES \
                        --fake-factor --embedding --normalize-by-bin-width \
                        -l --train-ff True --train-emb True --blinded-shapes
                done
            )
        done
    done
}

### Subroutine called by runstages
### generate postfitshape
function plotPreFitShapes() (
    ensureoutdirs
    #set -e
    for tag in ${tags[@]}; do
        export tag
        for era in ${eras[@]}; do
            STXS_FIT="inclusive"
            STXS_SIGNALS="stxs_stage0"
            if [[ $tag == *"stage0"* ]]; then
                CATEGORIES="stxs_stage0"
            elif [[ $tag == *"stage1p1"* ]]; then
                CATEGORIES="stxs_stage1p1_15node"
            else
                CATEGORIES="stxs_stage1p1"
            fi
            for channel in ${channels[@]}; do
                DATACARDDIR=output/datacards/${era}-${tag}-smhtt-ML/${STXS_SIGNALS}/$channel/125
                WORKSPACE=$DATACARDDIR/${era}-${STXS_FIT}-workspace.root
                [ -f $WORKSPACE ] || logerror "No workspace to plot: $WORKSPACE" #; return 1
                [ -f ${DATACARDDIR}/combined.txt.cmb ] || logerror "No datacard to plot: ${DATACARDDIR}/combined.txt.cmb" #; return 1
                # generate the prefitshape
                FILE="${DATACARDDIR}/prefitshape-${era}-${tag}-${STXS_FIT}.root"
                [[ -f $FILE ]] || (
                    source utils/setup_cmssw.sh
                    logandrun PostFitShapesFromWorkspace \
                        -m 125 -w ${WORKSPACE} \
                        -d ${DATACARDDIR}/combined.txt.cmb \
                        -o ${FILE}
                )
                ## plot the prefitshape
                (
                    source utils/setup_cvmfs_sft.sh
                    source utils/setup_python.sh
                    PLOTDIR=output/plots/all-${tag}-${channel}_shape-plots
                    [ -d $PLOTDIR ] || mkdir -p $PLOTDIR
                    for OPTION in "--png" ""
                    do
                        logandrun ./plotting/plot_shapes.py -i $FILE \
                            -o $PLOTDIR -c ${channel} -e $era \
                            $OPTION --categories $CATEGORIES --fake-factor \
                            --embedding --normalize-by-bin-width -l \
                            --train-ff True --train-emb True
                    done
                )
            done
        done
    done
)

function plotPostFitShapes(){
    ensureoutdirs
    for tag in ${tags[@]}; do
        export tag
        era="all"
        STXS_SIGNALS="stxs_stage0"
        STXS_FIT="inclusive"
        channel="cmb"
        if [[ $tag == *"stage0"* ]]; then
            CATEGORIES="stxs_stage0"
            STXS_SIGNALS="stxs_stage0"
            STXS_FIT="stxs_stage0"
        elif [[ $tag == *"stage1p1"* ]]; then
            CATEGORIES="stxs_stage1p1_15node"
            STXS_SIGNALS="stxs_stage1p1"
            STXS_FIT="stxs_stage1p1"
        else
            CATEGORIES="stxs_stage1p1"
            STXS_SIGNALS="stxs_stage1p1"
            STXS_FIT="stxs_stage1p1"
        fi
        DATACARDDIR=output/datacards/${era}-${tag}-smhtt-ML/${STXS_SIGNALS}/$channel/125
        # Generate the fitDiagnostics
        FITFILE=$DATACARDDIR/fitDiagnostics.hesse-${era}-${tag}-${channel}-${STXS_FIT}.MultiDimFit.mH125.root
        [[ -f $FITFILE ]] || 
        logandrun ./combine/signal_strength.sh ${era} $STXS_FIT $DATACARDDIR $channel ${tag} "robustHesse" 
        # generate the postfitshape
        FILE="${DATACARDDIR}/postfitshape-${era}-${tag}-${STXS_FIT}.root"
        [[ -f $FILE ]] || 
        (
            source utils/setup_cmssw.sh
            WORKSPACE=$DATACARDDIR/${era}-${STXS_FIT}-workspace.root
            logandrun PostFitShapesFromWorkspace \
                -m 125 -w ${WORKSPACE} \
                -d ${DATACARDDIR}/combined.txt.cmb \
                -o ${FILE} \
                -f ${FITFILE}:fit_s \
                --postfit --skip-prefit
        )
        for channel in ${channels[@]}; do
            ## plot the preditshape and postfitshape
            (
                source utils/setup_cvmfs_sft.sh
                source utils/setup_python.sh
                PLOTDIR=output/plots/${era}-${tag}-${channel}_shape-plots_postfit
                [ -d $PLOTDIR ] || mkdir -p $PLOTDIR
                for PLOTERA in "2016" "2017" "2018"
                do
                    logandrun ./plotting/plot_shapes.py -i $FILE -o $PLOTDIR \
                        -c ${channel} -e $PLOTERA $OPTION --categories $CATEGORIES \
                        --fake-factor --embedding --normalize-by-bin-width \
                        -l --train-ff True --train-emb True
                done
            )
        done
    done
}



function plotMCprefitshapes(){
    ensureoutdirs
    JETFAKES=0 EMBEDDING=0 CATEGORIES="stxs_stage1p1"
    for tag in ${tags[@]}; do
        export tag
        for era in ${eras[@]}; do
            for STXS_SIGNALS in "stxs_stage0"; do
                DATACARDDIR=output/datacards/${era}-${tag}-smhtt-ML/${STXS_SIGNALS}
                [ -d $DATACARDDIR ] || mkdir -p $DATACARDDIR
                logandrun ./datacards/produce_datacard.sh ${era} $STXS_SIGNALS $CATEGORIES $JETFAKES $EMBEDDING ${tag} ${channelsarg}
            done
            for STXS_FIT in "stxs_stage0"; do
                fn="output/datacards/${era}-${tag}-smhtt-ML/${STXS_SIGNALS}/cmb/125/${era}-${STXS_FIT}-workspace.root"
                if [[ ! -f $fn ]]; then
                    logandrun ./datacards/produce_workspace.sh ${era} $STXS_FIT ${tag}
                    [[ $? == 0 ]] || return $?
                else
                    loginfo "skipping workspace creation, as  $fn exists"
                fi
            done
            STXS_FIT="stxs_stage0"
            DATACARDDIR=output/datacards/${era}-${tag}-smhtt-ML/${STXS_FIT}/cmb/125
            FILE="${DATACARDDIR}/prefitshape-${era}-${tag}-${STXS_FIT}.root"
            logandrun ./combine/prefit_postfit_shapes.sh ${era} ${STXS_FIT} ${DATACARDDIR} ${tag}

            OPTION="--png"
            (
                source utils/setup_cvmfs_sft.sh
                source utils/setup_python.sh
                if [[ $tag =~ "ff" ]]; then
                    TRAINFF=True
                else
                    TRAINFF=False
                fi
                if [[ $tag =~ "emb" ]]; then
                    TRAINEMB=True
                else
                    TRAINEMB=False
                fi
                PLOTDIR=output/plots/${era}-${tag}_prefit-plots
                mkdir -p $PLOTDIR
                logandrun ./plotting/plot_shapes.py -i $FILE -o $PLOTDIR -c ${channels[@]} -e $era $OPTION --categories $CATEGORIES --normalize-by-bin-width -l --train-ff $TRAINFF --train-emb $TRAINEMB
            )
        done
    done
}

### compares Signal strengths of the Samples classified on the training based on MCvsEMB dataset creation
function compareSignRes {
    for channel in ${channels[@]}; do
        for x in stage0-inclusive stage0-stxs_stage0 stage1p1-stxs_stage1p1; do
            echo signal-strength-${channel}-mc_{mc,ff}-stxs_$x.txt | xargs ls
        done
    done
    # for mcfile in mc-stxs_stage*txt; do
    #     embfile=$( echo $mcfile | sed 's@mc@emb@')
    #     ./utils/inlinediff.py <(echo $mcfile; cat $mcfile ) <(echo $embfile; cat $embfile) | sort
    # done
}
