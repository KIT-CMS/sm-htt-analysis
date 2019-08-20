source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

for f in 2017_??_counts_for_soverb_jdeta.root;
do
    python cut_optimization/determine_best_cut.py ${f}
done
