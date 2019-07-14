source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

ERA=$1

python recoil_corrections/determine_recoil_corrections.py $ERA recoil_measurements_$ERA
