ERA=$1
CHANNEL=$2
ANALYSIS_NAME=$3
echo $TAG
source utils/setup_cvmfs_sft.sh
python ml/create_combined_config.py  --tag $ANALYSIS_NAME --channel $CHANNEL --output_dir output/ml/${ANALYSIS_NAME}/${ERA}_${CHANNEL}

