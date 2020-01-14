#!/bin/bash
function overridePar() {
    file=$1
    arg=$2
    val=$3
    if [[ "" = $( grep -e "$arg" $file ) ]]; then
        logerror $arg is not in $file
        return 2
    fi
    if [[ $( grep -e "(^|\s|--)$arg" $file | grep -c . ) >1 ]]; then
        logerror $arg appears multiple times in $file, aborting.
        return 2
    fi
    sed -i -E "s@(^|\s|--)$arg(\s+|=)\w+@\1$arg\2$val@" $file
}
function getPar() {
    file=$1
    arg=$2
    lines=$( grep -E "(^|\s|--)$arg" $file  )
    nlines=$( echo $lines | grep -c . )

    if [[ $nlines == 0 ]]; then
        logerror $arg is not in $file
        return 2
    fi
    if [[ $nlines >1 ]]; then
        logerror $arg appears multiple times in $file, aborting.
        return 2
    fi
    echo $lines | sed -E "s@(^|\s|--)($arg)(\s+|=)(\w+).*@\4@"
}

function updateSymlink() {
    source=$1
    target=$2
    loginfo "Updating Link: $target -> $source"
    if [[ -d $source ]]; then
        [[ -L $target ]] && rm $target
        [[ -d $target ]] && rmdir $target
        ln -sn $source $target
    elif [[ -f $source ]]; then
        [[ -f $target || -L $target ]]  && rm $target
        ln -s $source $target
    else
        logerror "Invalid source: $source"
        return 1
    fi

}
function condwait(){
    if [[ $(jobs | wc -l ) -gt 15 ]]; then
        wait
    fi
}

function recommendCPUs() {
    avUsage=$(grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage}')
    ncpus=$(($(grep 'cpu' /proc/stat | wc -l)-1))
    echo $avUsage $ncpus | awk '{print int((1-$1/100)*$2*.7)}'
}


function loginfo {
    echo -e "\e[46m[INFO]\e[0m" $( date +"%y-%m-%d %R" ): $@ | tee -a $( pwd )/output/log/logutil.log
}
function logwarn {
    echo -e "\e[45m[WARN]\e[0m" $( date +"%y-%m-%d %R" ): $@ | tee -a $( pwd )/output/log/logutil.log
}
function logerror {
    echo -e "\e[41m[ERROR]\e[0m" $( date +"%y-%m-%d %R" ): $@ | tee -a $( pwd )/output/log/logutil.log
}
function logandrun() {
    # set bash to exit if as soon as a part of a pipe has a non-zero exit value
    set -o pipefail
    # set the name of the logfile based on the command
    logfile=$( pwd )/output/log/logandrun-$( echo "$@" | cut -d' ' -f1,2 | sed 's@\./@@' | sed -E "s@[/ ]@\-@g" ).log
    # print the startmessage and log it
    echo -e "\e[43m[RUN]\e[0m" $( date +"%y-%m-%d %R" ): $@ | tee -a $( pwd )/output/log/logutil.log | tee -a $logfile
    # evaluate the current date in seconds as the start date
    start=`date +%s`
    # execute the command and log it
    $@ | tee -a $logfile
    # capture the return code ( without  pipefail this would be the exit code of tee )
    return_code=$?
    end=`date +%s`
    # evaluate the end data
    # if the there was no error...
    if [[ $return_code == 0 ]]; then
        # print the message and log it
        echo -e "\e[42m[COMPLETE]\e[0m" $( date +"%y-%m-%d %R" ): $@ "     \e[104m{$((end-start))s}\e[0m" | tee -a $( pwd )/output/log/logutil.log | tee -a $logfile
    else
        # print a message with the return code
        logerror Error Code $return_code  $@ "     \e[104m{$((end-start))s}\e[0m"  | tee -a $( pwd )/output/log/logutil.log | tee -a $logfile
    fi
    # check if the script has been running for more than 2400s = 40 min AND
    # there is a script to notify the user
    if [[ $((end-start)) -gt 2400 ]] && hash sendmsg.py 2>/dev/null ; then
        #notify the user
        sendmsg.py "$( date +"%y-%m-%d %R" ) {$((end-start))s} $return_code: $@ " 2>/dev/null
    fi
    return $return_code
}
# this function makes sure all the output directories exit
function ensureoutdirs() {
    [[ -d output ]] || mkdir output
    pushd output  >/dev/null
    for folder in datacards  log  plots  shapes ml signalStrength; do
        [[ ! -d $folder ]] && mkdir $folder
    done
    [[ -d log/condorShapes ]] || mkdir log/condorShapes
    popd  >/dev/null
}
