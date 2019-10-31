## Checking orthogonality to `H->WW` analysis

In the `mt`, `et` and `em` decay channels, we see a non-vanishing contribution of `H->WW` process (produced via gluon fusion and vector boson fusion) to our selection entering statistical inference.
Therefore, we need to check orthogonality to `H->WW` analysis (for now, only for 2017 data-taking period).

### Creating sample after final selection

Similarly to the procedure of creating training datasets for the ML classification, we create datasets for the following processes:

 * `data_obs`
 * `HWW`
 * `qqH125`
 * `ggH125`

In order to do this, please execute the following command:

```bash
for ch in mt et em;
do
    ./check_hww/create_training_dataset.sh 2017 ${ch}
done
```

### Comparing 2D distributions

In order to compare 2D distributions of `ggH125`, `qqH125` and `HWW` for a selected set of variables, please execute the following command:

```bash
for ch in mt et em;
do
    ./check_hww/plot_2D_comparisons.sh 2017 ${ch}
done
```

### Creating event list for data

Cleanest check of overlap is a brute-force method: create an event list of the final selection and compare with the other analysis. To create the list for our analysis, please execute the following command:

```bash
for ch in mt et em;
do
    ./check_hww/create_event_list.sh 2017 ${ch}
done
```

### Computing signal yield losses for several cuts

To compare signal yield losses for predifined cuts (marked as **new** and **old**), please use the following command:

```bash
./check_hww/produce_hwwcut_counts.sh 2017 mt et em
```
