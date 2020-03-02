# Standard Model Higgs boson to two tau leptons analysis

## Train and apply machine learning methods

```bash
ERA="2016"
CHANNEL="tt"
./ml/create_training_dataset.sh $ERA $CHANNEL
./ml/run_training.sh $ERA $CHANNEL
./ml/run_testing.sh $ERA $CHANNEL
./ml/run_application.sh $ERA $CHANNEL
```

## Run analysis

```bash
# Check utils/setup_samples.sh for correct paths
ERA="2016"
CHANNELS="et mt tt"
./run_analysis.sh $ERA $CHANNELS
```
## Run GOF tests
First the equi-populated binning used in the GOF tests needs to be calculated. 
```bash
ERA=2016
bash gof/create_binning.sh $ERA
```
Afterwards the output directory and the submit scripts are created using the following command.
```bash
OUTPUTDIR=/some/output/directory
bash gof/create_jdl.sh $ERA $OUTPUTDIR
```
Then the directory created in the previous step is linked into the output folder.
```bash
ln -s $OUTPUTDIR output
```
Finally the jobs can be submitted using HTCondor.
```bash
pushd $OUTPUTDIR
condor_submit job.jdl
popd
```
