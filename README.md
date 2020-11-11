
# NMSSM H->h(tautau)h'(bb) analysis

## Train and apply machine learning methods

```bash
ERA="all" # all three years (2016,2017,2018) are trained in one go
CHANNEL="tt" # other possibilities: mt, et
./run_ml.sh $ERA $CHANNEL
```

## Produce analysis histograms

```bash
# Check utils/setup_samples.sh for correct paths
ERA="2016" # other possibilities: 2017, 2018
CHANNELS="tt" # other possibilities: mt, et
./shapes/produce_nmssm_shapes.sh $ERA $CHANNEL ${CHANNEL}_max_score
```

# NMSSM H->h(tautau)h'(bb) analysis

The workflow of the analysis consists of multiple steps: 

0. Skimming the official CMS data (miniAOD format) to create our own KIT internal format ("Kappa"). This step is neglected for now as it will very likely not need to be redone anytime soon.
1. Creation of flat ntuples from the skimmed CMS data and simulation. During the creation of ntuple, the data is filtered and the releveant physical variables (e.g. invariant masses of tau-pairs, ...) are calculated.
2. Production of "friend trees" for the ntuples created in step 1. Friend trees are additional ntuples with a 1:1 correspondence with the ntuples of step 1. Friend trees contain further information about the event, usually things which are often updated, and thus the calculation of friend trees is faster. Three friend trees need to be created here: HHKinFit (kinematic fit of the bb$\tau\tau$ mass), SVFit (likelihood fit of the $\tau\tau$ mass, FakeFactors (event-by-event probability of a tau_h being a misidentified jet)
3. Training of the machine learning model. 
4. Application of the model for each event in the ntuples --> Another friend tree "NNScore" needs to be created containing the neural network score for each event. 
5. "Shape production": Histograms are now calculated from the event lists in the flat ntuples.
6. Statistical treatment of the histograms and calculation of the results, which are in this case exclusion limits.

The different steps usually uses different software, which will be explained below. All software has been tested on `portal1`, and should also work on `bms1` and `bms3`.


## Creation of ntuples

**You probably do not need to produce new ntuple currently** and can use the ones I used for the analysis. They are located in 
```
/ceph/jbechtel/nmssm/ntuples/201?/?t/
```
in which `201?` can be 2016, 2017 or 2018 and stands for the CMS run period the sample describes, and `?t` stands for the final state of the di-tau pair: et, mt or tt.

In each folder lies a collection of root files, one for each physical process which is of interest for the analysis.
To create ntuples, we use https://github.com/KIT-CMS/KITHiggsToTauTau/. To set up the code, use the checkout script:
```bash
wget https://raw.githubusercontent.com/KIT-CMS/KITHiggsToTauTau/reduced_trigger_objects/scripts/checkout_packages_CMSSW102X.sh
chmod u+x checkout_packages_CMSSW102X.sh
./checkout_packages_CMSSW102X.sh
```
The default branch is `reduced_trigger_objects` and works for all analyses we do, so also the NMSSM analysis. 
After the checkout and compilation is complete, you can set up the software by these commands. This needs to be done in every new shell, so best create a script of an alias. Also change `/PATH/TO/` to the path where you cloned the repository. For the last two commands you will need a valid grid certificate and voms-proxy, necessary for grid submission. If you don't have this (yet) you can still use the software locally.
```bash
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh
cd /PATH/TO/CMSSW_10_2_18/src/
source /cvmfs/grid.cern.ch/emi3ui-latest/etc/profile.d/setup-ui-example.sh
cmsenv
export PATH=$PATH:$CMSSW_BASE/src/grid-control
export PATH=$PATH:$CMSSW_BASE/src/grid-control/scripts
source ${CMSSW_BASE}/src/HiggsAnalysis/KITHiggsToTauTau/scripts/ini_KITHiggsToTauTauAnalysis.sh
export X509_USER_PROXY=/home/${USER}/.globus/x509up
voms-proxy-init --voms cms:/cms/dcms --valid 192:00 --out ${X509_USER_PROXY}
```
Afterwards, you can create an example ntuple from a skimmed file:
```bash
cd HiggsAnalysis/KITHiggsToTauTau/
HiggsToTauTauAnalysis.py -a legacy --nmssm -c tt -i data/Samples/Run2Legacy_bjetRegression/Run2018/Tau_Run2018A_17Sep2018v1_13TeV_MINIAOD.txt  -f 1
```
The option `-a legacy` is used for all legacy analyses on Run2 data. `--nmssm` is needed for the NMSSM analysis to apply a cut on the number of b-jets and to write out additional information. `-c tt` specifies that only the `tt` final state will be considered. `-i ` specifies the input file, for a complete set of ntuples, all files in the lists in `data/Samples/Run2Legacy_bjetRegression` need to be used. `-f 1` just tells the program to stop after one file (for testing).
The command creates an output file called `output.root`. You can see the content of the file via 
```
root -l output.root 
.ls # to see the content directly in the command line
TBrowser g
```
Opening the `TBrowser` is  a nice way of seeing the file content, however not recommended for remote file access. Another way of seeing the file content is 
```
rootls -t output.root:tt_nominal/ntuple
```
The most important TTree in each file is located in the folder `?t_nominal`, where `?t` is again mt, et or tt depending on the final state. 
The names of the variables can be cryptic, they correspond to event information such as pT of the particles, invariant masses, correction factors, etc. To actually see the data in some distribution, you can also do
```
root -l output.root 
.ls # to see the content directly in the command line
tt_nominal->cd()
ntuple->Draw("m_vis") # Creates a histogram of the visible di-tau mass 
```
As you can see, only very few events are in the file. To produce the events, we require a CPU batch system to parallelize the tasks.
```
HiggsToTauTauAnalysis.py -a legacy --pipelines auto --nmssm -i data/Samples/Run2Legacy_bjetRegression/SAMPLES_TO_PRODUCE  -b etp7 --dry-run --files-per-job 10 -c tt -w ${PWD}/workbase --se-path srm://cmssrm-kit.gridka.de:8443/srm/managerv2?SFN=/pnfs/gridka.de/cms/disk-only/store/user/${USER}/ntuple_testing/
```
`-b etp7` specifies that we will use the CentOS7 batch system of the ETP. `-w` specifies the working directory where grid control stores the job information. It is important that an absolute path is used here. 
`--se-path ` specifies the remote disk where the output is written to. 
Note that now also the option ` --pipelines auto` is used. In simulated samples, these create additional folders in the root file, in which systematic variations are propagated through  the analysis. An example is the folder `tt_btagEffDown`, in which the b-tagging efficiency is lowered within its uncertainty, and the effect on the analysis evaluated. These additional folders only exists for simulated or embedded events.

After running the command above, you will get a command of the form `go.py ...` returned. By running this command, the task is sent to the batch system via the tool grid-control.
After the task is complete, you will need to merge the outputs of the individual jobs using 
```
artusMergeOutputs.py /storage/gridka-nrg/${USER}/ntuple_testing/ --output-dir
```


This part can alternatively be very conveniently be run on the NAF cluster at DESY, which is where I always did it. The advantages are that usually many CPU cores are available, and the files will be stored on a mount with local read access.

The code can be set up the same way on the NAF, by logging in using `ssh USER@naf-cms-el7.desy.de`.
The command to 
```
HiggsToTauTauAnalysis.py -a legacy --pipelines auto --nmssm -i data/Samples/Run2Legacy_bjetRegression/SAMPLES_TO_PRODUCE  -b naf7 --dry-run --files-per-job 10 -c tt 
```
Note that you do not need to set the workdir and the se-path anymore. These will be automatically set to the disks mounted at `/nfs/dust/cms/user/`. 
After the task is complete, you can merge on NAF using the command
```
artusMergeOutputs.py -b naf7 /nfs/dust/cms/user/PATH/TO/WORKDIR/
```
and then again submitting the grid-control command that is output from the command line. 




## Create friends trees

Friend trees need to be created for the FakeFactors, SVFit and HHKinFit. For this we use https://github.com/KIT-CMS/friend-tree-producer.

In this case I had to create a separate branch as the treatment of the FakeFactors is a bit different from the other analyses we do. The branch is not the default branch and is called `nmssm_analysis`.
There also exists a checkout script:
```bash
wget https://raw.githubusercontent.com/KIT-CMS/friend-tree-producer/nmssm_analysis/scripts/checkout.sh
chmod u+x checkout.sh
./checkout.sh
```
To set up the code in a new shell, use
```bash
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh
cd /PATH/TO/CMSSW_10_2_14/src/
cmsenv
export PATH=$PATH:$CMSSW_BASE/src/grid-control
export PATH=$PATH:$CMSSW_BASE/src/grid-control/scripts
export X509_USER_PROXY=/home/${USER}/.globus/x509up
voms-proxy-info
voms-proxy-init --voms cms:/cms/dcms --valid 192:00 --out ${X509_USER_PROXY}
```
To set up a task of producing new friend trees, you first need the ntuples from the previous step. An example command is then
```
job_management.py --command submit --executable HHKinFit --custom_workdir_path /ceph/${USER}/nmssm/friends/tt  --input_ntuples_directory /ceph/jbechtel/nmssm/ntuples/tt/   --batch_cluster etp7 --events_per_job 20000 --cores 24 --restrict_to_channels tt
```
The executable can be either `HHKinFit`, `SVFit`, `FakeFactors` or (later)  `NNScore`. The four executables have very different run times. I usually set 20,000 events per job for HHKinFit, 5000 for SVFit and 100,000 for NNScore and FakeFactors, but this is up to you. Usually jobs with take on average ~15 minutes are very manageable.

Again, after running the command above, you will get a command of the form `go.py ...` returned. By running this command, the task is sent to the batch system.

When the command is complete, run the command from above again, only change `--command submit` to `--command collect`. This will merge the outputs of the individual tasks to single files.

## Train and apply machine learning methods

```bash
ERA="all" # all three years (2016,2017,2018) are trained in one go
CHANNEL="tt" # other possibilities: mt, et
./run_ml.sh $ERA $CHANNEL
```

## Produce analysis histograms

```bash
# Check utils/setup_samples.sh for correct paths
ERA="2016" # other possibilities: 2017, 2018
CHANNELS="tt" # other possibilities: mt, et
./shapes/produce_nmssm_shapes.sh $ERA $CHANNEL ${CHANNEL}_max_score
```



