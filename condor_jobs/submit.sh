###############################
# Submit shape jobs to condor #
###############################
# create folder if it doesn't exit
dir=output/log/condorShapes/
[[ -d $dir ]] || mkdir -p $dir
# jobs will be submitted directly from this repository, so the logfiles created by the job will be updated.
if [[ ! -z $1 && ! -z $2 ]]; then
    IFS=',' read -r -a eras <<< $1
    IFS=',' read -r -a channels <<< $2
    if [[ -z $3 ]]; then
        tags="default"
    else
        IFS=',' read -r -a tags <<< $3
    fi
    for tag in ${tags[@]}; do
        for era in ${eras[@]}; do
            for channel in ${channels[@]}; do
                    echo "$era $channel $tag $(pwd -P)"
            done
        done
    done > condor_jobs/arguments.txt
fi
## source LCG Stack and submit the job
if uname -a | grep -E 'el7' -q
then
    condor_submit condor_jobs/produce_shapes_cc7.jdl
elif uname -a | grep -E 'el6' -q
then
    condor_submit condor_jobs/produce_shapes_slc6.jdl
else
    echo "Maschine unknown, i don't know what to do !"
    exit 1
fi
