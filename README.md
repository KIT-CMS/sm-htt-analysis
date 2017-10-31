# Standard Model Higgs boson to two tau leptons analysis

## Convention of process names
Signals: ggH, qqH, WH, ZH, total: HTT
Backgrounds: W, QCD, TTT, TTJ (only TT in emu), ZL, ZJ, ZT

## Train and apply machine learning methods

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

## Run analysis

The script `run_analysis.sh` in the top-level directory of this repository guides through all steps. The analysis ntuples need to be annotated with the ML method's response first with the workflow shown above.

```bash
./run_analysis.sh
```
