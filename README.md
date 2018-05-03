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
