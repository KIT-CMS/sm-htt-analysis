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
./ml/run_application.sh CHANNEL
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
# Install CMSSW:
bash init_cmssw.sh

# Software stack:
source setup_cmssw.sh

# Python modules:
source setup_python.sh
```

```bash
python produce_datacard.py
```

## Run statistical inference

```bash
# Software stack:
source setup_cmssw.sh
```

```bash
# Signal strength:
combine -M MaxLikelihoodFit -m 125 datacard.txt

# Significance:
combine -M ProfileLikelihood -t -1 --expectSignal 1 --toysFrequentist --significance -m 125 datacard.txt

# Nuisance impacts:
text2workspace.py -m 125 datacard.txt -o workspace.root
combineTool.py -M Impacts -m 125 -d workspace.root --doInitialFit
combineTool.py -M Impacts -m 125 -d workspace.root --doFits --parallel 10
combineTool.py -M Impacts -m 125 -d workspace.root --output impacts.json
plotImpacts.py -i impacts.json -o impacts
```
