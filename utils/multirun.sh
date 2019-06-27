set -e

function waitForAll() {
    echo "pidList: $@"
    #set +o xtrace
    export someRunning=1
    while [[ $someRunning == 1 ]]; do
        someRunning=0
        for process in $@; do
            if [[ -d /proc/$process ]]; then
                someRunning=1
                #echo "Pid $process ist still running, cannot exit"
            fi
        done
        sleep .3
    done
}

function multirun() {
	run=$1
    shift
	tmpFileL=""
	pidL=""

    for (( j = 0; j < $i; j++ )); do
        if [[ $PARALLEL != 1 ]]; then
            $run $1 $2
        else
            tmpFile=$(mktemp tmpFile-$1-$2.XXXX)
            tmpFileL+=" $tmpFile"
            $run $1 $2 &> $tmpFile &
            # Test correct behaviour
            #a=$(( ( RANDOM % 25 )  + 1 ))
            #( echo $a; sleep $a; echo $a ) &>$tmpFile &
            #trap "rm $tmpFile; kill $!" INT
            pidL+=" $!"
        fi
        shift 2
    done

    if [[ $PARALLEL = 1 ]]; then
    #set -o xtrace
    #trap "rm $tmpFileL; kill $(ps -s $$ -o pid=)" INT
    ### if the process dies, kill the children and remove the tempfiles
    trap "kill 0; rm $tmpFileL" INT EXIT TERM
    waitForAll $pidL &
    lasttmpFile=""
	tail -f $tmpFileL --pid $!
    fi
}
