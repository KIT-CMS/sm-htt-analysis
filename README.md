# Standard Model Higgs boson to two tau leptons analysis

## Apply machine learning methods

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
./shapes/produce_shapes.sh
```

## Build datacards

```bash
# Install CMSSW:
bash init_cmssw.sh
```

```bash
./datacards/produce_datacard.sh
```

## Run statistical inference

```bash
# Signal strength:
./combine/signal_strength.sh

# Significance:
./combine/significance.sh

# Nuisance impacts:
./combine/nuisance_impacts.sh
```

## Plotting

```bash
# Software stack:
# TODO: CMSSW_7_4_7 with HarryPlotter
```

```bash
# Plot categories with statistical uncertainties only from nominal shapes
# created using the shape-producer module
./plotting/plot_nominal.py -v VARIABLES -c CATEGORIES

# Prefit plots
PostFitShapes -m 125 -d datacard.txt -o datacard_shapes_prefit.root
./plotting/plot_shapes.py -i datacard_shapes_prefit.root -f mt_inclusive_prefit

# Postfit plots
combine -M MaxLikelihoodFit -m 125 datacard.txt

PostFitShapes -m 125 -d datacard.txt -o datacard_shapes_postfit_sb.root -f mlfit.root:fit_s --postfit
./plotting/plot_shapes.py -i datacard_shapes_postfit_sb.root -f mt_inclusive_postfit
```
