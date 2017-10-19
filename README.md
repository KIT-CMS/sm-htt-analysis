# Standard Model Higgs boson to two tau leptons analysis

## Apply machine learning methods

```bash
# Software stack:
source setup_cvmfs_sft.sh
```

### Create training dataset

```bash
./ml/create_training_dataset.sh CHANNEL
```

### Training

```bash
./ml/run_training.sh CHANNEL
```

### Application

```bash
# TODO
```

## Create shapes of systematics

```bash
# Software stack:
source setup_cvmfs_sft.sh
# Python modules:
source setup_python.sh
```

```bash
python produce_shapes.py
```

## Build datacards

```bash
# Software stack:
# Source CMSSW_7_4_7 for CombineHarvester python bindings
# Python modules:
source setup_python.sh
```

```bash
python produce_datacard.py
```

## Run statistical inference

```bash
# Software stack:
# Source CMSSW_7_4_7 for combine
```

```bash
# TODO: add combine calls on datacards to extract signal strenght, significance, ...
```
