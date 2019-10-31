## Package for MET Recoil corrections and uncertainties

### Preparations

At first, you will need the n-tuples without MET recoil corrections applied, but with `Z(p_T, mass)` weights produced. In order to obtain these ntuples, please have a look at [instructions](https://github.com/KIT-CMS/sm-htt-analysis/tree/master/zptm_reweighting) for this reweighting procedure.
Make sure, that the recent workspaces including the `Z(p_T, mass)` weights are used within the [KITHiggsToTauTau configuration](https://github.com/KIT-CMS/KITHiggsToTauTau/blob/reduced_trigger_objects/python/data/ArtusConfigs/Run2LegacyAnalysis_base.py#L133-L135).
Please note, that you can re-use the data samples from the previously produced n-tuples (without the reweighting).

### Control plots with `Z(p_T, mass)` weights

Following [these](https://github.com/KIT-CMS/sm-htt-analysis/tree/master/zptm_reweighting#having-a-look-at-control-plots) instructions, you can again produce control plots. For that round, please make sure that `Z(p_T, mass)` reweighting is now **enabled**.
Don't forget to adapt the [samples](https://github.com/KIT-CMS/sm-htt-analysis/blob/master/utils/setup_samples.sh) setttings.

### Determine histograms for MET recoil corrections

Using the same n-tuples as above, you can now determine the histograms of MET projections needed as inputs for MET recoil corrections. To compute these histograms (and fit gaussians to them), execute please the following command:

```bash
for year in 2016 2017 2018;
do
    ./recoil_corrections/produce_recoilcorr_shapes.sh ${year}
    ./recoil_corrections/determine_recoil_corrections.sh ${year}
done
```

After performing this, folders with names `recoil_measurements_${year}` will be created. They will contain plots of the MET projection distributions (with fitted gaussians) and input files for MET recoil corrections. These input files are:

 * `Type1_PFMET_${year}.root`
 * `Type1_PuppiMET_${year}.root`

These files need to be committed to the [RecoilCorrections](https://github.com/KIT-CMS/RecoilCorrections/tree/master/data) repository.
This repo needs to be updated in the [KITHiggsToTauTau](https://github.com/KIT-CMS/KITHiggsToTauTau/blob/reduced_trigger_objects/scripts/checkout_packages_CMSSW102X.sh#L49) setup and the corresponding configuration for [PF MET](https://github.com/KIT-CMS/KITHiggsToTauTau/blob/reduced_trigger_objects/python/data/ArtusConfigs/Run2LegacyAnalysis_base.py#L138-L140) and [Puppi MET](https://github.com/KIT-CMS/KITHiggsToTauTau/blob/reduced_trigger_objects/python/data/ArtusConfigs/Run2LegacyAnalysis_base.py#L145-L147) needs also an update.

### Prepare histograms for MET recoil uncertainties

Another step, which needs to be run is the preparation of MET recoil uncertainties based on n-tuples without MET recoil corrections applied. To obtain these inputs, please run:


```bash
for year in 2016 2017 2018;
do
    ./recoil_corrections/produce_recoilunc_shapes.sh ${year}
    ./recoil_corrections/prepare_recoil_uncertainties.sh ${year} prefit
done
```
This command will create root files containing the hadronic recoil component parallel to Z direction devided by generator Z boson `p_T`, $`- H_{\parallel}/p_T^{gen}(Z)`$ and prefit uncertainties on its scale and resolution of 10%. The files are named as:

 * `PFMETSys_${year}.root`
 * `PuppiMETSys_${year}.root`

Make sure, that you put these files into the corresponding [folder](https://github.com/KIT-CMS/RecoilCorrections/tree/master/data) of your analysis setup and update the configuration for [PF MET](https://github.com/KIT-CMS/KITHiggsToTauTau/blob/reduced_trigger_objects/python/data/ArtusConfigs/Run2LegacyAnalysis_base.py#L141-L143) and [Puppi MET](https://github.com/KIT-CMS/KITHiggsToTauTau/blob/reduced_trigger_objects/python/data/ArtusConfigs/Run2LegacyAnalysis_base.py#L148-L150).

### Constrain MET recoil uncertainties

With the inputs for corrections and initial uncertainties explained above, please create n-tuples with MET recoil corrections applied and the corresponding uncertainty shifts. This is only needed for the MC samples, so you can re-use again the data n-tuples produced before.
To do this, please execute the following command after making sure, that the MET recoil corrections and uncertainty shifts are **enabled**:

```bash
HiggsToTauTauAnalysis.py -i <collection_with_background_mc>.txt -a HiggsAnalysis/KITHiggsToTauTau/python/data/ArtusConfigs/Run2LegacyAnalysis_base.py --no-run -b naf --wall-time 03:00:00 --memory 2000 --files-per-job 15 --se-path srm://cmssrm-kit.gridka.de:8443/srm/managerv2?SFN=/pnfs/gridka.de/cms/disk-only/store/user/<dCacheUserName>/31-07-2019_MetRecoil_QMHist -c mm --pipelines nominal METrecoil_shifts
```

The currently supported correction method is [quantile mapping with histograms](https://github.com/KIT-CMS/KITHiggsToTauTau/blob/reduced_trigger_objects/python/data/ArtusConfigs/Run2LegacyAnalysis_base.py#L152), but feel free to test the other ones, which use the fitted functions.

After updating the [samples](https://github.com/KIT-CMS/sm-htt-analysis/blob/master/utils/setup_samples.sh) for `mm` channel, you can produce shapes for control plots as explained for `Z(p_T, mass)` [reweighting](https://github.com/KIT-CMS/sm-htt-analysis/tree/master/zptm_reweighting#having-a-look-at-control-plots) and prepare shapes for the fit. The latter step is performed by the following command:

```bash
for year in 2016 2017 2018;
do
    ./recoil_corrections/produce_fit_shapes.sh ${year}
done
```

After this step, the output files should be converted into a format suitable for CombineHarvester:

```bash
for year in 2016 2017 2018;
do
    for var in metParToZ puppimetParToZ;
    do
        ./recoil_corrections/convert_to_synced_shapes.sh ${year} ${var}
    done
done
```

In order to perform the fit, please follow the instructions for [fitting](https://github.com/KIT-CMS/FitMETRecoilUnc). From these instructions you will need the following outputs:

 * `output_*metParToZ/Run201?/postfit_shapes.root`: files with prefit and postfit shapes for plotting
 * `output_*metParToZ/Run201?/uncertainties.json`: files containing the total constrained uncertainties

### Plot prefit-postfit shapes

In order to see, how the fit of the MET recoil uncertainties behaves, you can use the following command to plot the postfit and prefit shapes:

```bash
for var in metParToZ puppimetParToZ;
do
    for year in 2016 2017 2018;
    do
        ./recoil_corrections/plot_shapes.sh ${year} ${var} output_${var}/Run${year}/
    done
done
```

### Update inputs for final MET recoil uncertainties

Finally, you can create MET recoil uncertainty inputs with constrained uncertainties by providing the corresponding .json files to the `prepare_recoil_uncertainties.sh` script:

```bash
for year in 2016 2017 2018;
do
    ./recoil_corrections/prepare_recoil_uncertainties.sh ${year} output_metParToZ/Run${year}/uncertainties.json
done
```

Please note, that the script automatically replaces `metParToZ` with `puppimetParToZ`. Make also sure, that you are **still** using the uncertainty inputs `shapes_mm_recoilunc_${year}.root` produced from n-tuples **without** MET recoil corrections.
These files should then be updated and commited to [this folder](https://github.com/KIT-CMS/RecoilCorrections/tree/master/data)
