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

# Create prefit and postfit shapes
./combine/prefit_postfit_shapes.sh

# Prefit plots
./plotting/plot_shapes.py -i datacard_shapes_prefit.root -f FOLDERS

# Postfit plots (signal plus background)
./plotting/plot_shapes.py -i datacard_shapes_postfit_sb.root -f FOLDERS

# Postfit plots (background only)
./plotting/plot_shapes.py -i datacard_shapes_postfit_b.root -f FOLDERS
```
