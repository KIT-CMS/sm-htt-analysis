ERA=$1
CHANNEL=$2
ANALYSIS_NAME=$3
TAG=$4
echo $TAG
source utils/setup_cvmfs_sft.sh
python ml/create_combined_config.py  --tag $TAG --channel $CHANNEL --output_dir output/ml/${ANALYSIS_NAME}/${ERA}_${CHANNEL}_${TAG} --analysis_name ${ANALYSIS_NAME}

