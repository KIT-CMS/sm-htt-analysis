# script that can be used to check if there are any condor_job errors, required options are
# tag - the tag of the analysis
# path to the workdir
# additional option --resubmit can be given, so the jobs are resubmitted with grid control
TAG=$1
WORKDIR=$2
RESUBMIT=$3
go=$WORKDIR/condor_jobs/grid-control/go.py
for ERA in "2016" "2017" "2018"; do
    for CHANNEL in "et" "mt" "tt" "em"; do
    echo "Checking $TAG: $ERA-$CHANNEL"
    zgrep "Error" $WORKDIR/output/condor_jobs_wd/$TAG/$ERA/$CHANNEL/*/output/*/job.stdout.gz | uniq 
    if [[ $RESUBMIT == "--resubmit" ]]; then
    zgrep -l "Error" $WORKDIR/output/condor_jobs_wd/$TAG/$ERA/$CHANNEL/*/output/*/job.stdout.gz | while read -r line ; do
        echo "Resubmitting $TAG: $ERA-$CHANNEL jobs.... "
	    jobidtemp=$(dirname ${line})
	    jobidtemp2=${jobidtemp: -10}
	    jobid=${jobidtemp2//[!0-9]/}
	    if [[ $jobidtemp == *"bkg"* ]]; then
		echo "Background job"
		$go ${WORKDIR}/output/condor_jobs_wd/$TAG/$ERA/$CHANNEL/shapes_${ERA}_${CHANNEL}_${TAG}_bkg.conf --reset ${jobid}
	    else
	    	$go ${WORKDIR}/output/condor_jobs_wd/$TAG/$ERA/$CHANNEL/shapes_${ERA}_${CHANNEL}_${TAG}.conf --reset ${jobid}
	    fi
	done
    fi
    done
done
