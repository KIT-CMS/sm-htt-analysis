#!/bin/bash
function overridePar() {
    file=$1
    arg=$2
    val=$3
    if [[ "" = $( grep -e "$arg" $file ) ]]; then
        logerror $arg is not in $file
        exit 2
    fi
    if [[ $( grep -e "(^|\s|--)$arg" $file | grep -c . ) >1 ]]; then
        logerror $arg appears multiple times in $file, aborting.
        exit 2
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
        exit 2
    fi
    if [[ $nlines >1 ]]; then
        logerror $arg appears multiple times in $file, aborting.
        exit 2
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
        [[ -f $target ]]  && rm $target
        ln -s $source $target
    else
        logerror "Invalid source: $source"
        exit 1
    fi

}

function recommendCPUs() {
    freecpus=$(top -bn1 | grep "Cpu(s)" | sed -E "s/.* ([0-9.]+)(%| )id.*/\1/" )
    ncpus=$(($(grep 'cpu' /proc/stat | wc -l)-1))
    echo $freecpus $ncpus | awk '{print int($1/100*$2*.7)}'
}


function loginfo {
    echo -e "\e[46m[INFO]\e[0m" $( date +"%y-%m-%d %R" ): $@
}
function logwarn {
    echo -e "\e[45m[WARN]\e[0m" $( date +"%y-%m-%d %R" ): $@
}
function logerror {
    echo -e "\e[41m[ERROR]\e[0m" $( date +"%y-%m-%d %R" ): $@
}
function logandrun() {
    echo -e "\e[43m[RUN]\e[0m" $( date +"%y-%m-%d %R" ): $@
    $@
    exit_code=$?
    if [[ $exit_code == 0 ]]; then
        echo -e "\e[42m[COMPLETE]\e[0m" $( date +"%y-%m-%d %R" ): $@
    else
        logerror $@
    fi
    [[ $sourced ]] || exit $exit_code
}