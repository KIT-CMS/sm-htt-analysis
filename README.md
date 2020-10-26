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


