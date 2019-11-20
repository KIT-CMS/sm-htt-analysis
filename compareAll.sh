#!/usr/bin/env bash
### Skript to compare the training with embedding and mc samples in it's effect on the signal strength

## Detect if the script is being sourced
#mklement0 https://stackoverflow.com/questions/2683279/how-to-detect-if-a-script-is-being-sourced
([[ -n $ZSH_EVAL_CONTEXT && $ZSH_EVAL_CONTEXT =~ :file$ ]] ||
 [[ -n $KSH_VERSION && $(cd "$(dirname -- "$0")" &&
    printf '%s' "${PWD%/}/")$(basename -- "$0") != "${.sh.file}" ]] ||
 [[ -n $BASH_VERSION ]] && (return 0 2>/dev/null)) && export sourced=1 || export sourced=0

[[ $sourced != 1 ]] && set -e
#set -uo pipefail

unset PYTHONPATH
unset PYTHONUSERBASE
shopt -s checkjobs # wait for all jobs before exiting
export PARALLEL=1
export USE_BATCH_SYSTEM=1
export cluster=naf #lxplus7 # etp7 # lxplus7 # #
export sm_htt_analysis_dir=$( pwd ) ### local sm-htt repo !
export cmssw_src_local="/portal/ekpbms3/home/${USER}/CMSSW_10_2_14/src" ### local CMSSW !
export batch_out_local=${sm_htt_analysis_dir}/output/friend_trees
source utils/bashFunctionCollection.sh


if [[ $USE_BATCH_SYSTEM == "1" ]]; then
    if [[ $cluster == "etp7" ]]; then
        export batch_out=$batch_out_local
    elif [[ $cluster == "lxplus7" ]]; then
        export batch_out="/afs/cern.ch/work/${USER::1}/${USER}/batch-out"
        export cmssw_src_dir="/afs/cern.ch/user/${USER::1}/${USER}/CMSSW_10_2_14/src" ## Remote CMSSW!
        export remote="cern"
    elif [[ $cluster == "naf" ]]; then
        export remote="naf"
        export cmssw_src_dir="/afs/desy.de/user/m/mscham/CMSSW_10_2_14/src"
        export batch_out="/nfs/dust/cms/user/mscham/NNScoreApp"
    else
        logerror No such cluster: $cluster
        exit 1
    fi
fi

########### Argument handling and Tests ##################
IFS=',' read -r -a eras <<< $1
IFS=',' read -r -a channels <<< $2
IFS=',' read -r -a tags <<< $3
erasarg=$1
channelsarg=$2
tagsarg=$3

[[ "" = $( echo ${eras} ) ]] && eras=("2016" "2017" "2018") erasarg="2016,2017,2018"
[[ "" = $( echo ${channels} ) ]] && channels=("em" "et" "tt" "mt") channelsarg="em,et,mt,tt"
[[ "" = $( echo ${tags} ) ]] && tags=("default") tagsarg="default"

loginfo Eras: ${erasarg}  Channels: ${channelsarg}   Training Dataset Generation tag: ${tagsarg} Sourced: $sourced

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
    if [[ ! "em et tt mt" =~ ${channel} ]]; then
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




function compenv() {
    varnames=(era channel tag eras  channels  tags erasarg channelsarg tagsarg mldir trainingConfFile anaSSStep  llwtnndir temp_file PROD_NEW_DATACARDS redoConversion fn JETFAKES EMBEDDING CATEGORIES PROD_NEW_DATACARDS STXS_SIGNALS STXS_FIT USE_BATCH_SYSTEM)
    IFS='°' read -r -a vars <<< "${era[@]}"°"${channel[@]}"°"${tag[@]}"°"${eras[@]}"°"${channels[@]}"°"${tags[@]}"°"${erasarg[@]}"°"${channelsarg[@]}"°"${tagsarg[@]}"°"${mldir[@]}"°"${trainingConfFile[@]}"°"${anaSSStep[@]}"°"${llwtnndir[@]}"°"${temp_file[@]}"°"${PROD_NEW_DATACARDS[@]}"°"${redoConversion[@]}"°"${fn[@]}"°"${JETFAKES[@]}"°"${EMBEDDING[@]}"°"${CATEGORIES[@]}"°"${PROD_NEW_DATACARDS[@]}"°"${STXS_SIGNALS[@]}"°"${STXS_FIT[@]}"°$USE_BATCH_SYSTEM
    for (( i=0; i<${#vars[@]}; i++ )); do
        echo "${varnames[$i]}=${vars[$i]}"
    done
}

function create_training_dataset() {
    ensuremldirs
    for tag in ${tags[@]}; do
        logandrun ./ml/create_training_dataset.sh ${erasarg} ${channelsarg} ${tag}
    done
}

function mltrain() {
    ensuremldirs
    for tag in ${tags[@]}; do
    export tag
        for era in ${eras[@]}; do
            for channel in ${channels[@]}; do
                logandrun ./ml/run_training.sh ${era} ${channel} ${tag}
            done
        done
    done
}

function mltest() {
    ensuremldirs
    for tag in ${tags[@]}; do
    export tag
        for era in ${eras[@]}; do
            for channel in ${channels[@]}; do
                logandrun ./ml/run_testing.sh ${era} ${channel} ${tag}
            done
        done
    done
}

#### converts models to the form needed for submission to a batch system
function exportForApplication {
    for tag in ${tags[@]}; do
        export tag
        for era in ${eras[@]}; do
            for channel in ${channels[@]}; do
                (
                logandrun ./ml/translate_models.sh ${era} ${channel} ${tag}
                logandrun ./ml/export_lwtnn.sh ${era} ${channel}  ${tag} ) &
            done
        done
    done
    wait
}

function provideCluster() {
    tag=$1
    era=$2
    llwtnndir=$cmssw_src_local/HiggsAnalysis/friend-tree-producer/data/inputs_lwtnn
    find $llwtnndir -type l -iname "fold*_lwtnn.json" -delete
    # for era in ${eras[@]}; do
        for channel in ${channels[@]}; do
            ### Supply the generated models in the hard-coded path in the friendProducer
            ### alogrsync $remote will dereference this symlink
            [[ ! -d $llwtnndir/${era}/${channel} ]] && mkdir -p $llwtnndir/${era}/${channel}
            for fold in 0 1;
            do
                updateSymlink $sm_htt_analysis_dir/output/ml/${era}_${channel}_${tag}/fold${fold}_lwtnn.json  $llwtnndir/${era}/${channel}/fold${fold}_lwtnn.json
            done
        done
    # done
    updateSymlink $sm_htt_analysis_dir/datasets/datasets.json $cmssw_src_local/HiggsAnalysis/friend-tree-producer/data/input_params/datasets.json
    if [[ ! $cluster =~ "etp"  ]]; then
        logandrun alogrsync $remote -rLPthz ${cmssw_src_local}/HiggsAnalysis/friend-tree-producer/data/ $remote:${cmssw_src_dir}/HiggsAnalysis/friend-tree-producer/data
    fi
}

function runCluster(){
    set -e
    for tag in ${tags[@]}; do
        export tag
        for era in ${eras[@]}; do
            provideCluster $tag $era
            logandrun ./batchrunNNApplication.sh ${era} ${channelsarg} $cluster "submit" ${tag}
            [ $? ] && logandrun ./batchrunNNApplication.sh ${era} ${channelsarg} $cluster "rungc" ${tag}
            #[ $? ] && read -p " Collect? y/[n]" yn
            #[[ $yn == "y" ]]
            [ $? ] && logandrun ./batchrunNNApplication.sh ${era} ${channelsarg} $cluster "collect" ${tag}
            [ $? ] && copyFromCluster
            [ $? ] && logandrun ./batchrunNNApplication.sh ${era} ${channelsarg} $cluster "delete" ${tag} || return 1
        done
    done
}

function copyFromCluster() {
    # read -p "Sync files from $USER@lxplus.cern.ch:$batch_out/${era}_${tag} to $batch_out_local/${era}_${tag} now? y/[n]" yn
    # if [[ ! $yn == "y" ]]; then
    #     logerror "!=y \n aborting"
    #     [[ $sourced != 1 ]] && exit 0
    # fi
    nnscorefolder=$batch_out_local/${era}/nnscore_friends/${tag}
    [[ ! -d $nnscorefolder  ]] && mkdir -p $nnscorefolder
    if [[ $cluster == etp7 ]]; then
        logandrun rsync -rLPthz $batch_out/${era}_${tag}/NNScore_workdir/NNScore_collected/ $nnscorefolder
    else
        logandrun alogrsync $remote -rLPthz $remote:$batch_out/${era}_${tag}/NNScore_workdir/NNScore_collected/ $nnscorefolder
    fi
    if [[ $( du -bs $nnscorefolder | cut -f1 ) -lt 10000000000 ]]; then
        logerror Recieved NNScore Friend folder to small!
        return 1
    fi
}

export JETFAKES=1 EMBEDDING=1 CATEGORIES="stxs_stage1p1"

export redoConversion=0
function genshapes() {
    ensureoutdirs
    for tag in ${tags[@]}; do
        for era in ${eras[@]}; do
            export redoConversion=0
            if [[ ! -f output/shapes/${era}-${tag}-${channelsarg}-shapes.root  ]]; then
                logandrun ./shapes/produce_shapes.sh ${era} ${channelsarg} ${tag} || return 1
                redoConversion=1
            else
                loginfo Skipping shape generation as ${era}_${tag}_shapes.root exists
            fi
        done
    done
}

function subshapes(){
    ensureoutdirs
    for tag in ${tags[@]}; do
        for era in ${eras[@]}; do
            for channel in ${channels[@]}; do
                fn=output/shapes/${era}-${tag}-${channel}-shapes.root
                if [[ ! -f $fn || $( stat -c%s $fn ) -le 2000 ]]; then
                    echo "$era $channel $tag $(pwd -P)"
                    redoConversion=1
                fi
            done
        done
    done > condor_jobs/arguments.txt
    logandrun condor_jobs/submit.sh
}

function syncshapes() {
    for channel in ${channels[@]}; do
        for era in ${eras[@]}; do
            for tag in ${tags[@]}; do
		        fn=output/shapes/${era}-${tag}-${channel}-synced-ML.root
                if [[ $redoConversion == 1 || ! -f $fn  || $( stat -c%s $fn ) -le 2000 ]]; then
                    logandrun ./shapes/convert_to_synced_shapes.sh ${era} ${channel} ${tag} &
                else
                    loginfo Skipping shape syncing as $fn exists
                fi
            done
            wait
        done
    done
}



function gendatacards(){
    ensureoutdirs
    for era in ${eras[@]}; do
        for STXS_SIGNALS in "stxs_stage0" "stxs_stage1p1"; do
            for tag in ${tags[@]}; do
            export tag
                DATACARDDIR=output/datacards/${era}-${tag}-smhtt-ML/${STXS_SIGNALS}
                [ -d $DATACARDDIR ] || mkdir -p $DATACARDDIR
                logandrun ./datacards/produce_datacard.sh ${era} $STXS_SIGNALS $CATEGORIES $JETFAKES $EMBEDDING ${tag} ${channelsarg} &
            done
            wait
        done
    done
}

function genworkspaces(){
    ensureoutdirs
    for era in ${eras[@]}; do
        for STXS_FIT in "inclusive" "stxs_stage0" "stxs_stage1p1"; do
            for tag in ${tags[@]}; do
            export tag
                fn="output/datacards/${era}-${tag}-smhtt-ML/${STXS_SIGNALS}/cmb/125/${era}-${STXS_FIT}-workspace.root"
                if [[ ! -f $fn ]]; then
                    logandrun ./datacards/produce_workspace.sh ${era} $STXS_FIT ${tag} &
                    #[[ $? == 0 ]] || return $?
                else
                    loginfo "skipping workspace creation, as  $fn exists"
                fi
            done
            wait
        done
    done

}

export JETFAKES=1 EMBEDDING=1 CATEGORIES="stxs_stage1p1"

function genMCprefitshapes(){
    ensureoutdirs
    export JETFAKES=0 EMBEDDING=0 CATEGORIES="stxs_stage1p1"
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

### Subroutine called by runstages
### do not run this parallel! it writes to fit.root in the main dir and is then moved
function runana() {
    ensureoutdirs
    for STXS_FIT in "stxs_stage1p1"; do #"inclusive" "stxs_stage0";do #
        export tag
        for era in ${eras[@]}; do
            if [[ True ]]; then
                for tag in ${tags[@]}; do
                    if [[ $STXS_FIT == "inclusive" || $STXS_FIT == "stxs_stage0" ]]; then
                        STXS_SIGNALS=stxs_stage0
                    elif [[ $STXS_FIT == "stxs_stage1p1" ]] ; then
                        STXS_SIGNALS=stxs_stage1p1
                    fi
                    DATACARDDIR=output/datacards/${era}-${tag}-smhtt-ML/${STXS_SIGNALS}
                    for channel in ${channels[@]}; do
                         logandrun ./combine/signal_strength.sh ${era} $STXS_FIT $DATACARDDIR/$channel/125 $channel ${tag} &
                    done
                    wait
                    #logandrun ./combine/signal_strength.sh ${era} $STXS_FIT $DATACARDDIR/cmb/125 cmb ${tag} &
                done
            fi
        done
    done
}

### Subroutine called by runstages
### do not run this parallel! it writes to fit.root in the main dir and is then moved
function plot_shapes() {
    ensureoutdirs
    for tag in ${tags[@]}; do
        export tag
        for era in ${eras[@]}; do
            STXS_FIT="stxs_stage0"
            if [[ $STXS_FIT == "inclusive" || $STXS_FIT == "stxs_stage0" ]]; then
                STXS_SIGNALS=stxs_stage0
            elif [[ $STXS_FIT == "stxs_stage1p1" ]] ; then
                STXS_SIGNALS=stxs_stage1p1
            fi
            DATACARDDIR=output/datacards/${era}-${tag}-smhtt-ML/${STXS_FIT}/cmb/125
            FILE="${DATACARDDIR}/prefitshape-${era}-${tag}-${STXS_FIT}.root"
            [[ -f $FILE ]] || logandrun ./combine/prefit_postfit_shapes.sh ${era} ${STXS_FIT} ${DATACARDDIR} ${tag}

            # OPTION="--png"
            # (
            #     source utils/setup_cvmfs_sft.sh
            #     source utils/setup_python.sh
            #     if [[ $tag =~ "ff" ]]; then
            #         TRAINFF=True
            #     else
            #         TRAINFF=False
            #     fi
            #     if [[ $tag =~ "emb" ]]; then
            #         TRAINEMB=True
            #     else
            #         TRAINEMB=False
            #     fi
            #     PLOTDIR=output/plots/${era}-${tag}_prefit-plots
            #     [ -d $PLOTDIR ] || mkdir -p $PLOTDIR
            #     logandrun ./plotting/plot_shapes.py -i $FILE -o $PLOTDIR -c ${channels[@]} -e $era $OPTION --categories $CATEGORIES --fake-factor --embedding --normalize-by-bin-width -l --train-ff $TRAINFF --train-emb $TRAINEMB
            # )
            logandrun ./plotting/plot_shapes.sh $era $tag ${channelsarg} $STXS_SIGNALS $STXS_FIT $CATEGORIES $JETFAKES $EMBEDDING
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

#################################################################################################
### Main procedure. Ensures, no completed step is run again by sourcing completedMilestones
### in the beginning and overwriting variables upon completion of the step
#################################################################################################

function main() {
    read -p " Start new run? y/[n]" yn
    if [[ ! $yn == "y" ]]; then
        exit 0
    fi
    create_training_dataset
    mltrain
    mltest
    if [[ $USE_BATCH_SYSTEM == 1 ]]; then
        exportForApplication
        provideCluster
        submitCluster; exit
        resubmitCluster; exit
        collectCluster
        copyFromCluster
    else
        for era in ${eras[@]}; do
            for channel in ${channels[@]}; do
                ./ml/run_application ${era} ${channel}
            done
        done
    fi
    genshapes
    gendatacards
    genworkspaces
    runana
    compareSignRes
}

[[ $sourced == 1 ]] && [[ ! "bash" =~ $0 ]] && logerror "shell is sourced by another shell than bash, aborting" && exit 1
[[ $sourced == 0 ]] && main
echo
