#!/bin/bash

#########################################################
#########################################################
# NAME 
#       custom_condor_run.sh - run scripts on HTCondor cluster
#SYNOPSIS
#       custom_condor_run.sh COMMANDS [OPTIONS]
#DESCRIPTION
#       Run single or multiple COMMANDS on available HTCondor cluster.
#       stdout and stderr are streamed to and recorded in the directory that was created at startup of the script
#       that directory is renamed to the id of the job AFTER completion
#       Files that should be transfered onto or off the cluster must be specified using the following options
#   -i [FILES]
#       Copy given FILES into the cluster with the same directory structure as originally
#       Only relative paths can be used. Wildcards can be used.
#       Example: -i this/path/data.dat this/path/*.txt ...
#   -o [FILES]
#       Copy given FILES from the cluster to the local directories, keeping the structure as originally
#       Only relative paths can be used. Wildcards can be used by using single quotation marks around the file.
#       Example: -o this/path/data.dat 'this/path/*.txt' ...
#   -s [FILE]
#       Use given HTCondor submission FILE instead of default file (custom_condor_default_submission.jdl)
#       Only the first given file will be used
#   -c [FILE]
#       Use given config FILE to get the information of th options i, o and s
#       The proper syntax for this config file is:
#       "@@input:" followed by the FILES of i
#       "@@output:" followed by the FILES of o, in this case wildcards DON'T need quotation marks
#       "@@submission_file:" followed by the FILE of s
#       The config file is only valid if all three exist, but they don't need entries
#
#       Example:
#           @@input:
#           @@output:
#           Hello_World_config.txt
#           @@submission_file:
#           custom_condor_scripts/custom_condor_default_submission.jdl
#   -q
#       Run the skript in quiet mode, only showing the script that is run, the timer and a message when the job is completed
#       instead of repeating input, outputs, config and submission files and displaying the resulting stdout and stderr
#   -t
#       Run the skript without a timer. This prevents the script from displaying the time since the submission of the script.
#       The actual times can still be found in the log files
#
#EXAMPLE
#   custom_condor_scripts/custom_condor_run.sh 'echo "Hello World" > Hello_World.txt' -o Hello_World.txt -s custom_condor_scripts/custom_condor_default_submission.jdl
#
#   This will start a job on the HTCondor cluster, that creates a file named "Hello_World.txt" that contains the words "Hello World".
#   The file is then transfered back to the directory in which the script was started from
#
#   Equivalent to:
#   custom_condor_scripts/custom_condor_run.sh 'echo "Hello World" > Hello_World.txt' -c custom_condor_scripts/Hello_World_config.txt
#
#AUTHOR
#       Tim Voigtländer
#########################################################
#########################################################

###Function to parse given inputs 
#inputs: all inputs of script
#outputs: None (saved internally as ..._arg)
function parse_arguments() {
    arguments=("$@")
    # Go through all given inputs
    for arg in "${arguments[@]}"; do
        # If input is option (a "-" fllowed by a letter) 
        if [[ $(echo "${arg}" | grep "^-.$") ]]; then
            # Evaluate last list of arguments for last given option
            evaluate_opt "${last_opt}" "${last_arg_list[@]}"
            # reset argument list
            last_arg_list=()
            # Set new option 
            last_opt=$(echo "${arg}" | sed "s/^-\(.\)$/\1/g")
        else
            # Add argument to current argument list 
            last_arg_list+=("${arg}")
        fi
    done;
    # Evaluate final list of arguments for final option
    evaluate_opt "${last_opt}" "${last_arg_list[@]}"
}

### Function to evaluate option and it's arguments
#inputs: 1. option parameter
#        2. any number of arguments for option
#outputs: None (saved internally as ..._arg)
function evaluate_opt() {
    #Get option
    option_para=$1
    #Get arguments for option
    arg_para=("${@: 2}")
    #Continue depending on choosen option
    case "${option_para}" in
        #No option given (arguments before first given option):
        '')
            # At least one argument mandatory
            if [[ -z "${arg_para}" ]]; then
                echo "At least 1 command expected, but none were given."
            else
                #all given arguments are added to list of commands  
                command_arg=("${arg_para[@]}")
            fi
            ;;
        #Option "-i" given:
        i)
            # At least one argument mandatory
            if [[ -z "${arg_para}" ]]; then
                echo "Option ${option_para} expected at least 1 argument, but none were given."
            else
                #all given arguments are added to list of input files  
                input_arg=("${arg_para[@]}")
            fi
            ;;
        #Option "-o" given:
        o)
            # At least one argument mandatory
            if [[ -z "${arg_para}" ]]; then
                echo "Option ${option_para} expected at least 1 argument, but none were given."
            else
                #all given arguments are added to list of output files  
                output_arg=("'${arg_para[@]}'")
            fi
            ;;
        #Option "-s" given:
        s)
            # Exactly one argument mandatory, further arguments are ignored
            if [[ -z "${arg_para}" ]]; then
                echo "Option ${option_para} expected 1 argument, but none were given."
            else
                #argument is set as submission file
                submission_arg="${arg_para[0]}"
                if [[ ${#arg_para[@]} -gt 1 ]]; then
                    echo "Only the first given submission file (${arg_para[0]}) will be used."
                fi        
            fi
            ;;
        #Option "-c" given:
        c)
            # Exactly one argument mandatory, further arguments are ignored
            if [[ -z "${arg_para}" ]]; then
                echo "Option ${option_para} expected 1 argument, but none were given."
            else
                #argument is set as config file
                config_arg="${arg_para[0]}"
                if [[ ${#arg_para[@]} -gt 1 ]]; then
                    echo "Only the first given config file (${arg_para[0]}) will be used."
                fi
            fi
            ;;
        #Option "-d" given:
        d)
            # Exactly one argument mandatory, further arguments are ignored
            if [[ -z "${arg_para}" ]]; then
                echo "Option ${option_para} expected 1 argument, but none were given."
            else
                #argument is set as config file
                dir_arg="${arg_para[0]}"
                if [[ ${#arg_para[@]} -gt 1 ]]; then
                    echo "Only the first given config file (${arg_para[0]}) will be used."
                fi
            fi
            ;;
        #Option "-q" given:
        q)
            # Exactly zero arguments are mandatory
            if [[ ! -z "${arg_para}" ]]; then
                echo "Option ${option_para} expected no arguments, but some were given."
            else
                #Quiet flag is set
                set_quiet=1
            fi
            ;;
        #Option "-t" given:
        t)
            # Exactly zero arguments are mandatory
            if [[ ! -z "${arg_para}" ]]; then
                echo "Option ${option_para} expected no arguments, but some were given."
            else
                #Quiet flag is set
                no_timer=1
            fi
            ;;
        #Any other option is given
        *)
            echo "option not recognized"
            ;;
    esac
}

### Function to parse arguments of i, o and s from file given in option f
#inputs: config file
#outputs: None (saved internally as ..._arg)
function parse_from_file(){
    #Read lines of file given in f into parse_line
    while IFS="" read -r parse_line || [ -n "$parse_line" ]
    do
        case ${parse_line} in
            #If line begins with a "#" it is ignored
            "#"*)
                ;;
            #If line begins is "@@input:" the following lines are marked as input arguments
            "@@input:")
                input_flag=1
                output_flag=0
                submission_flag=0
                ;;
            #If line begins is "@@input:" the following lines are marked as output arguments
            "@@output:")
                input_flag=0
                output_flag=1
                submission_flag=0
                ;;
            #If line begins is "@@input:" the following lines are marked as the submission argument
            "@@submission_file:")
                input_flag=0
                output_flag=0
                submission_flag=1
                ;;
            *)
            #Else the lines are saved into the corresponding args
            if [[ ${input_flag} -eq 1 ]]; then
                input_arg+=(${parse_line})
            elif [[ ${output_flag} -eq 1 ]]; then
                output_arg+=("${parse_line}")
            elif [[ ${submission_flag} -eq 1 ]]; then
                submission_arg=${parse_line}
            fi
            ;;
        esac
    done < $1;
}

###Function to scan HTCondor log file for Codes (3 digit numbers at the start of a new log entry)
#  looks for the next code starting with the line after $line or after an given line
#inputs: 1. log file of job
#        2. line where search in log file should start
#outputs: None (The variables line, EOF_reached, line_code, line_jobID and line_date can be used outside the function after it has been called)
function read_next_code() {
    #Get log file name
    log_file=$1
    #Exit if given log file does not exist 
    if [[ ! -f ${log_file} ]]; then
        echo "Given log file ${log_file} does not exist"
        exit 1
    fi
    #Get last file line
    EOF_line=$(wc -l ${log_file} | sed "s/^\([0-9]\+\).*/\1/g")
    #Use given line if possible
    if [[ ! -z $2 ]]; then
        line=$2
    fi
    #Reset EOF_reached token
    EOF_reached=0
    #Remember starting line in case of EOF
    previous_code_line=${line}
    #Prevent hit in starting line
    line_text=""
    #Loop over lines until a code is found or the EOF is reached
    until ( [[ ${line_text} =~ ^[0-9]{3} ]] || [[ ${line} -gt ${EOF_line} ]] ); do
        line=$((${line} + 1))
        line_text=$(sed -n "${line}{p;q}" ${log_file})
    done;
    #If EOF was reached:
    if [[ ${line} -gt ${EOF_line} ]]; then
        #Reset line variable to starting line and set EOF_reached token
        line=${previous_code_line}
        EOF_reached=1
    #If code was found:
    else
        #Copy code, jobID and date from line
        line_code=$(echo "${line_text}" | sed "s/^\([0-9]\{3\}\).*/\1/g")
        line_jobID=$(echo "${line_text}" | sed "s/.*(\([0-9]\+\).[0-9]\{3\}.[0-9]\{3\}).*/\1/g")
        line_date=$(echo "${line_text}" | sed "s@.* \([0-9]\{2\}/[0-9]\{2\} [0-9]\{2\}:[0-9]\{2\}:[0-9]\{2\}\) .*@\1@g")
    fi
}

###Function based on read_next_code() to search for codes of specific jobs
#inputs: 1. log file of job
#        2. id of job that should be monitored
#outputs: None (The variables line, EOF_reached, line_code, line_jobID and line_date can be used outside the function after it has been called
#               and line_jobID will be the job ID that was searched for)
function read_next_job_code() {
    #Get log file name 
    log_file=$1
    #Get job ID to be searched for
    job_ID=$2
    #Remember last line where code and job ID were found
    previous_job_code_line=${line}
    #Prevent hit in starting line
    line_jobID=""
    #Loop over found code lines until code line with matching job ID is found or EOF is reached
    until ( [[ ${line_jobID} -eq ${job_ID} ]] || [[ ${EOF_reached} -eq 1 ]] ); do
        read_next_code ${log_file}
    done;
    #If EOF was reached:
    if [[ ${EOF_reached} -eq 1 ]]; then
        #Return to last code with matching ID
        read_next_code ${log_file} $((previous_job_code_line -1 ))
        #Set seperate EOF token as this is only the last code in log for this job
        EOF_reached_for_job=1
    fi
}

###Function to skip to last code in log file
###If job ID was given jump to last code with matching job ID instead 
#inputs: 1. log file of job
#        2. id of job that should be monitored
#outputs: None (The variables line, EOF_reached, line_code, line_jobID and line_date can be used outside the function after it has been called
#               and line_jobID will be the job ID that was searched for)
function read_last_code() {
    #Get log file name 
    log_file=$1
    #If job ID was given:
    if [[ ! -z $2 ]]; then
        #Get job ID
        job_ID=$2
        #Loop over codes with matching job ID until EOF is reached
        until [[ ${EOF_reached_for_job} -eq 1 ]]; do
            read_next_job_code ${log_file} ${job_ID}
        done;
    #If job iD was not given:
    else
        #Loop over codes until EOF is reached
        until [[ ${EOF_reached} -eq 1 ]]; do
            read_next_code ${log_file} 
        done;
    fi
}

###Function to remove traces of script
###Removes job from HTC, clock subprocess and generated temporary files
#inputs: None (Takes information from existing variables)
#outputs: None
function shutdown(){
    #Removes .tar files
    rm -r ${data_dir}/*.tar
    #Remove job from HTC
    if [[ ! -z ${last_submitted_jobID} ]]; then
        condor_rm ${last_submitted_jobID}
    fi
    #Remove clock subprocess
    if [[ ! -z ${last_sub_ID} ]]; then
        kill ${last_sub_ID}; wait ${last_sub_ID} 2>/dev/null; echo ""
    fi
    #Disable extended globbing
    shopt -u extglob
}

###Function to run commands on HTC
#inputs: all inputs of script
#outputs: None (files are placed into corresponding folders and outputs are written into output/error files)
function custom_condor_run() {
    #Save startuptime (nanoseconds)
    t_init="$(date +%F-%H-%M-%S-%N)"
    #Initialize quiet flag to be False and no_timer to be False
    set_quiet=0
    no_timer=0
    
    #Parse additional options and arguments
    parse_arguments "$@"
    #Check for incompatible options
    if ( [[ ! -z ${config_arg} ]] && ( [[ ! -z ${input_arg} ]] || [[ ! -z ${output_arg} ]] || [[ ! -z ${submission_arg} ]] ) ); then
        echo "Option 'f' is incompatible with the options 'i', 'o' and 's' as they try to set the same variables, exiting."
        exit 1;
    fi    
    #Get config file if option f was set
    if [[ ! -z ${config_arg} ]]; then
        #Check if config file has proper formating
        if ( [[ ! $(cat ${config_arg} | grep '@@input:') ]] || 
                [[ ! $(cat ${config_arg} | grep '@@output:') ]] || 
                [[ ! $(cat ${config_arg} | grep '@@submission_file:') ]] );then
            echo "${config_arg} has incorrect formating, exiting."
            exit 1;
        else
            #parse arguments of i, o and s from file given in option f
            parse_from_file ${config_arg}
        fi
    fi

    #trap SIGINT (Ctr-c) to ensure proper exit
    trap "shutdown; exit 1" SIGINT
    if [[ ${dir_arg} ]]; then
        if [[ -d ${dir_arg} ]]; then
            rm -r ${dir_arg}
        fi
        mkdir -p ${dir_arg}
        data_dir="${dir_arg}"
    else
        #Create directory for temporary files and outpus logs if necessary
        if [[ ! -d "custom_condor_data_dir" ]]; then
            mkdir -p custom_condor_data_dir 2>/dev/null
        fi
        #Create file with maching startup time as singular step
        #This prevents two instances of the script from using the same directory
        while : ; do
            if mkdir "custom_condor_data_dir/${t_init}" 2>/dev/null; then
                break;
            fi
            #If the directory cannot be created (because it already exists) a "_0" is appended to the time
            #And it is tried again until it succeeds
            t_init="${t_init}_0"
        done;
        #The created directory is then set as the default location for this instance of the script
        data_dir="custom_condor_data_dir/${t_init}"
    fi

    #Create skript string
    #Go through all given command arguments
    for comm in "${command_arg[@]}"; do
        #Check if the given command is a bash script (.sh file). If yes:
        script_name=$(echo "${comm}" | sed 's@\(\(\x22[^\x22]*\x22\|\x27[^\x27]*\x27\|[^\x22\x27\x20]\+\)\+\).*@\1@' | grep ".sh[\"']\?$")
        if [[ ${script_name} ]]; then
            #Add './' to beginning of script string if needed
            if [[ ! $(echo ${script_name} | grep "/") ]]; then
                comm="./${comm}"
            fi
            #Add bash script to list of input files
            input_arg+=("${script_name}")
        fi
        #Append to collective command string
        skript_string="${skript_string}${comm}; "
    done;
    #Repeat command
    echo "Running '${skript_string}' on HTCondor"

    #Print config file
    if [[ ! -z ${config_arg} ]]; then
        if [[ ${set_quiet} -eq 0 ]]; then
            echo "Config file: ${config_arg}"
        fi
    fi

    #Print work directory
    if [[ ! -z ${dir_arg} ]]; then
        if [[ ${set_quiet} -eq 0 ]]; then
            echo "Log directory: ${dir_arg}"
        fi
    fi
    
    #Print input files
    if [[ ! -z ${input_arg} ]]; then
        if [[ ${set_quiet} -eq 0 ]]; then
            echo "Input files: ${input_arg[@]}"
        fi
    fi

    #Print output files
    if [[ ! -z ${output_arg} ]]; then
        if [[ ${set_quiet} -eq 0 ]]; then
            echo "Output files: ${output_arg[@]}"
        fi
    fi
    #Get submission file
    if [[ ! -z ${submission_arg} ]] ; then
        submission_file=${submission_arg}
    else
        #If no file was given, use default submission file
        submission_file="${path_to_script_dir}/custom_condor_default_submission.jdl"
    fi
    #Print submission file
    if [[ ${set_quiet} -eq 0 ]]; then
        echo "Submission file: ${submission_file}"
    fi

    # Create dummy file for input if needed
    if [[ -z ${input_arg[@]} ]]; then
        mkdir ${data_dir}/condor_in.dummy
        input_arg="${data_dir}/condor_in.dummy"
    fi
    #Pack input files
    tar -cf ${data_dir}/condor_input_files.tar "${input_arg[@]}"
    #(Optional) display files in tar
    # tar -tvf ${data_dir}/condor_input_files.tar
    # delete dummy file
    if [[ ${input_arg[@]} == "${data_dir}/condor_in.dummy" ]]; then
        rm -r ${data_dir}/condor_in.dummy
    fi

    #Write initial bash script 
    #Set name of script that will be created. 
    #Should match with the one specified in the submission .jdl file
    condor_script="${data_dir}/custom_condor_pre_script.sh"

    ##Following comments refer to functionality in container 

    echo "#!/bin/bash" > ${condor_script}

    if ( [[ ! -z ${input_arg} ]] || [[ ! -z ${output_arg} ]] ); then
        #Enable extended globbing
        echo 'shopt -s extglob' >> ${condor_script}
    fi
    #Get name of initial directory
    if ( [[ ! -z ${input_arg} ]] || [[ ! -z ${output_arg} ]] ); then
        echo 'starting_path=$_CONDOR_JOB_IWD' >> ${condor_script}
    fi
    #(Optional) Display all files in tmp
    # echo 'echo "in $(pwd):"' >> ${condor_script}
    # echo "ls -R" >> ${condor_script}
    #Change to tmp directory
    echo "cd tmp" >> ${condor_script}
    #Unpack files from condor_input_files.tar to tmp
    if [[ ! -z ${input_arg} ]]; then
        echo 'tar -xf ${starting_path}/condor_input_files.tar' >> ${condor_script}
    fi
    #Create directories that output files will be placed in
    if [[ ! -z ${output_arg} ]]; then
        for dir_name in $(dirname "${output_arg[@]//\'/}" | tr '\n' ' '); do
            if [[ ! "${dir_name}" == "." ]]; then
                echo 'mkdir -p '"${dir_name}" >> ${condor_script}
            fi
        done;
    fi
    #Run command
    echo "${skript_string}" >> ${condor_script}
    echo 'cd ${starting_path}/tmp' >> ${condor_script}
    if [[ ! -z "${output_arg}" ]]; then
        #Pack output files
        echo 'tar -cf ${starting_path}/condor_output_files.tar'" ${output_arg[@]//\'/}" >> ${condor_script}
    else
        # Create dummy file if needed
        echo 'mkdir condor_out.dummy' >> ${condor_script}
        echo 'tar -cf ${starting_path}/condor_output_files.tar condor_out.dummy' >> ${condor_script}
    fi
    #remove condor_input_files.tar file from initial directory to prevent it from beeing copied again
    if [[ ! -z ${input_arg} ]]; then
        echo 'rm ${starting_path}/condor_input_files.tar 1> /dev/null' >> ${condor_script}
    fi
    #Disable extended globbing
    if ( [[ ! -z ${input_arg} ]] || [[ ! -z ${output_arg} ]] ); then
        echo 'shopt -u extglob' >> ${condor_script}
    fi
    #remove docker_stderror from initial directory to prevent it from beeing copied back
    echo 'rm -f ${starting_path}/docker_stderror' >> ${condor_script}

    #Set user proxy
    # add_commands="x509userproxy=/tmp/x509up_u$(id -u) data_dir=${data_dir}"
    add_commands="data_dir=${data_dir}"

    # ###########################################################################
    # #Start monitored job with specified submission file and additional commands
    # ###########################################################################
    
    #Get name of log file from submission .jdl file
    log_file=$(grep "^Log" ${submission_file} | sed 's/Log \?= \?\(.*\)/\1/g;s@$(data_dir)@'"${data_dir}"'@')
    #Reset current line to 0 for the read functions
    line=0

    #Get additional submission commands
    if [[ ! -z ${add_commands} ]]; then
        for command in ${add_commands}; do
            add_command_string="${add_command_string}-append ${command} "
        done;
    fi

    # Change name of batch in cluster
    if [[ ! -z ${dir_arg} ]]; then
        batch_name_string="-batch-name ${dir_arg//\//}"
        batch_name_message="with the name ${dir_arg//\//} "
    fi

    #Send job submission and catch submission message
    submission_message=$(condor_submit ${submission_file} ${add_command_string} ${batch_name_string})
    #Get Job ID from submission message
    last_submitted_jobID=$(echo ${submission_message} | sed "s/.*submitted to cluster \([0-9]\+\)\.$/\1/g")
    #Get time at moment of submission in seconds

    if [[ ${no_timer} -eq 0 ]]; then
        submission_date=$(date +%s)
    fi
    echo "Submitting job to cluster ${last_submitted_jobID} ${batch_name_message}(Script started at ${t_init})"

    #Abort if HTCondor doesn't responde
    if [[ ! -f ${log_file} ]]; then
        timeout_counter=0
        until [[ -f ${log_file} ]]; do
            sleep 10
            timeout_counter=$((timeout_counter + 1))
            if [[ ! ${timeout_counter} -lt 6 ]]; then
                condor_rm  ${last_submitted_jobID}
                echo "HTCondor has not responded, aborting script."
                exit 1
            else
                echo "HTCondor has not responded, waiting."
            fi
        done;
    fi

    if [[ ${no_timer} -eq 0 ]]; then
        #Start clock in subprocess
        (
        while : ; do
        #Display time since submission_date in hh:mm:ss format in same line
        echo -ne "$(date -u --date @$(($(date +%s) - $submission_date)) +%H:%M:%S)\033[0K\r"
        sleep 1
        done;
        ) &
        #Get ID of clock subprocess
        last_sub_ID=$!
    fi
    #Reset end signal
    job_finished=0
    #Repeat until end signal is set:
    until [[ ${job_finished} -gt 0 ]] ; do
        #Wait
        sleep 10
        #Reset EOF_reached_for_job signal set by read_next_job_code
        EOF_reached_for_job=0
        #Until end of file is reached again or until end signal is set:
        until ( [[ ${EOF_reached_for_job} -eq 1 ]] || [[ ${job_finished} -gt 0 ]] ); do
            #Read next code entry with matching job ID in log file
            read_next_job_code ${log_file} ${last_submitted_jobID}
            #If a new code was found:
            if [[ ${EOF_reached_for_job} -eq 0 ]]; then
                #React depending on signal (Codes are explained at https://htcondor.readthedocs.io/en/v8_8/codes-other-values/job-event-log-codes.html)
                #Can be modified fairly easily
                case ${line_code} in
                    000)
                        echo -e "\nJob ${last_submitted_jobID} ${batch_name_message}sent"
                        ;;
                    001)
                        echo -e "\nJob ${last_submitted_jobID} ${batch_name_message}started"
                        ;;
                    005)
                        #On return code: Get return value and set end signl
                        return_value=$(sed -n "$((line + 1)){p;q}" ${log_file} | sed "s/.*(return value \([0-9]\+\))$/\1/g")
                        echo -e "\nJob ${last_submitted_jobID} ${batch_name_message}finished with return value ${return_value}"
                        job_finished=1
                        ;;
                    012)
                        #On held job code:
                        echo -e "\nJob ${last_submitted_jobID} ${batch_name_message}was held"
                        # Optional: remove held job
                        #condor_rm ${last_submitted_jobID}
                        # Optional: Set end signal
                        #job_finished=2
                        ;;
                esac
            fi
        done;
    done;
    if [[ ${no_timer} -eq 0 ]]; then
        #Stop clock subprocess
        kill ${last_sub_ID}; wait ${last_sub_ID} 2>/dev/null; echo ""
    fi
    #Print output/errors during command execution to terminal
    if [[ ${set_quiet} -eq 0 ]]; then
        echo "############"
        if [[ -f $(grep "^Output" ${submission_file} | sed 's/Output \?= \?\(.*\)/\1/g;s@$(data_dir)@'"${data_dir}"'@') ]]; then
            echo "## Output ##"
            cat $(grep "^Output" ${submission_file} | sed 's/Output \?= \?\(.*\)/\1/g;s@$(data_dir)@'"${data_dir}"'@')
            echo -e "\n############"
        fi
        if [[ -f $(grep "^Error" ${submission_file} | sed 's/Error \?= \?\(.*\)/\1/g;s@$(data_dir)@'"${data_dir}"'@') ]]; then
            echo "## Error ###"
            cat $(grep "^Error" ${submission_file} | sed 's/Error \?= \?\(.*\)/\1/g;s@$(data_dir)@'"${data_dir}"'@')
            echo "############"
        fi
    fi
    #Unpack output files on return
    if [[ ! -z ${output_arg} ]]; then
        #unpack .tar
        tar -xf "${data_dir}/condor_output_files.tar"
    fi
    #remove .tar locally
    rm "${data_dir}/condor_output_files.tar" "${data_dir}/condor_input_files.tar"
    #Move logs of finnished job to directory with job id prepended
    if [[ ! ${dir_arg} ]]; then
        mv ${data_dir} "custom_condor_data_dir/${last_submitted_jobID}_${t_init}"
    fi
}

###Function to copy the basic templates from the script directory to either the current directory or another directory
#inputs: target directory where templates should be copied to
#outputs: None (files are copied)
function get_templates() {
    # Get current or given path
    if [[ ! -z $1 ]]; then
        target_dir=$(cd "$1"; pwd)
    else
        target_dir=$(pwd)
    fi
    #Copy files
    echo "Copy templates custom_condor_default_config.txt and custom_condor_default_submission.jdl from ${path_to_script_dir} to ${target_dir}"
    cp ${path_to_script_dir}/custom_condor_default_config.txt ${path_to_script_dir}/custom_condor_default_submission.jdl ${target_dir}
}

####################################
#########Start of script############
####################################

#Enable extended globbing
shopt -s extglob

#Initialize paths
path_to_script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

#Set path to storage
storage_path="srm://cmssrm-kit.gridka.de:8443/srm/managerv2?SFN=/pnfs/gridka.de/cms/disk-only/store/user/${USER}/custom_condor_tmp_storage"

#Check if user proxy exists
# if ( [[ ! -f /tmp/x509up_u$(id -u) ]] || [[ $(voms-proxy-info | grep "timeleft  : 0:00:00") ]] ); then
#     echo "No valid proxy found. Creating a new one"
#     #Create user proxy valid for 8 days
#     voms-proxy-init -voms cms:/cms/dcms -rfc -b 2048 -valid 192:00
#     if ( [[ ! -f /tmp/x509up_u$(id -u) ]] || [[ $(voms-proxy-info | grep "timeleft  : 0:00:00") ]] ); then
#         echo "Still no valid proxy found. Exiting script now."
#         exit 1
#     fi
# fi
#Set Proxy path for current user
# export X509_USER_PROXY=/tmp/x509up_u$(id -u)
#start script if command is given
if [[ "$1" == "get" ]]; then
    #get templates if "get" is given as an option
    get_templates $2
else
    #Run command on HTC
    custom_condor_run "$@"
fi

#Disable extended globbing
shopt -u extglob