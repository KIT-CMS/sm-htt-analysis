source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

ERA=$1
UNC=$2 # provide as 'prefit' or a .json file with postfit uncertainties

python recoil_corrections/prepare_recoil_uncertainties.py $ERA recoil_measurements_$ERA $UNC
