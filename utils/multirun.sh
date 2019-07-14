source utils/bashFunctionCollection.sh
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
			tmpFile=$(mktemp tmp-$1-$2.XXXX)
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
	trap "kill 0; rm $tmpFileL" INT TERM
	trap "rm $tmpFileL" EXIT
	waitForAll $pidL &
	lasttmpFile=""
	tail -f $tmpFileL --pid $! | grep --color -E "==> [a-Z0-9\.\-]+ <==|$"
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
	shift

	IFS=',' read -r -a eras <<< $1
	IFS=',' read -r -a channels <<< $2
	echo ${eras[@]} ${channels[@]}

	if [[ ! "" = $3 ]]; then
	    logerror only takes 3 arguments, seperate multiple eras and channels by comma eg: 2016,2018 mt,em   or \"\" em
	    exit 1
	fi
	for era in ${eras[@]}; do
	    if [[ ! "  2016 2017 2018" =~ $era ]]; then
	        logerror $era is not a valid era.
			exit 1
	    fi
	done
	for channel in ${channels[@]}; do
	    if [[ ! "  em et tt mt" =~ $channel ]]; then
	        logerror $channel is not a valid channel.
			exit 1
	    fi
	done

	channels=$(if [[ -z "${channels[@]}" ]]; then echo "tt" "mt" "et" "em"; else echo "${channels[@]}"; fi)
	eras=$(if [[ -z "${eras[@]}" ]]; then echo "2016" "2017" "2018"; else echo "${eras[@]}"; fi)
	i=0 ## how many sets of arguments
	unset argslist
	for era in $eras; do
		for channel in $channels;do
			argslist[$i]=" $era $channel"
			i=$(($i+1))
		done
	done
	loginfo "multirun $run_procedure ${argslist[@]}"
	multirun $run_procedure ${argslist[@]}
}
