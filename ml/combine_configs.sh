ERA=$1
CHANNEL=$2
source utils/setup_cvmfs_sft.sh
python ml/create_combined_config.py  --channel $CHANNEL --output_dir output/ml/${ERA}_${CHANNEL}