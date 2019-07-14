source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

ERA=$1

python zptm_reweighting/compute_zptm_weights.py counts_zptm_${ERA}.root
