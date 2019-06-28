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
	if [[ $PARALLEL != 1 ]]; then
		echo "Sequential execution, as \$PARALLEL !=1"
	else
		echo "Parallel execution, as \$PARALLEL =1"
	fi
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

containsElement () {
  local e match="$1"
  shift
  for e; do [[ "$e" == "$match" ]] && return 0; done
  return 1
}

function genArgsAndRun {
	run_procedure=$1
	ERA=$2
	CHANNEL=$3

	valideras=("" "2016" "2017" "2018")
	validchannels=("" "tt" "mt" "et" "em")

	if [[ ! " ${valideras[@]} " =~ $ERA ]]; then
	echo -e "$ERA is not a valid ERA! \n Valid ERAs are:  ${valideras[@]}"
	exit 1
	fi


	if [[ ! " ${validchannels[@]} " =~ $CHANNEL ]]; then
	echo -e "$CHANNEL is not a valid Channel! \n Valid Channels are: ${validchannels[@]}"
	exit 1
	fi

	CHANNELS=$(if [[ -z $CHANNEL ]]; then echo "tt" "mt" "et" "em"; else echo $CHANNEL; fi)
	ERAS=$(if [[ -z $ERA ]]; then echo "2016" "2017" "2018"; else echo $ERA; fi)

	i=0 ## how many sets of arguments
	unset argslist
	for era in $ERAS; do
			for channel in $CHANNELS;do
				argslist[$i]=" $era $channel"
			i=$(($i+1))
	done
	done

	multirun run_procedure ${argslist[@]}
}
