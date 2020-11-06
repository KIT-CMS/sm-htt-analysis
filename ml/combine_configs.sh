ERA=$1
CHANNEL=$2
TAG=$3
echo $TAG
source utils/setup_cvmfs_sft.sh
python ml/create_combined_config.py  --tag $TAG --channel $CHANNEL --output_dir output/ml/${ERA}_${CHANNEL}_${TAG}

