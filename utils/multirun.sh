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
	fifoL=""
	pidL=""

    for (( j = 0; j < $i; j++ )); do
        if [[ ! $PARALLEL==1 ]]; then
            $run $1 $2 &> $fifo
        else
            fifo=$(mktemp fifo-$1-$2.XXXX)
            fifoL+=" $fifo"
            #$run $1 $2 &> $fifo &
            # Test correct behaviour
            a=$(( ( RANDOM % 25 )  + 1 ))
            ( echo $a; sleep $a; echo $a ) &>$fifo &
            #trap "rm $fifo; kill $!" INT
            pidL+=" $!"
        fi
        shift 2
    done

    if [[ $PARALLEL==1 ]]; then
    #set -o xtrace
    #trap "rm $fifoL; kill $(ps -s $$ -o pid=)" INT
    ### if the process
    #trap "rm -i $fifoL; kill 0" INT EXIT TERM
    trap "kill 0; rm $fifoL" INT EXIT TERM
    waitForAll $pidL &
    lastfifo=""
	tail -f $fifoL --pid $!
    fi
}
