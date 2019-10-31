## Package for `Z(p_T, mass)` reweighting

### Preparations

At first you need the n-tuples for `mm` channel aligned with the `mt` selection for all Run II data-taking years. In order to obtain them, checkout the [KITHiggsToTauTau](https://github.com/KIT-CMS/KITHiggsToTauTau) software (use please this [script](https://github.com/KIT-CMS/KITHiggsToTauTau/blob/reduced_trigger_objects/scripts/checkout_packages_CMSSW102X.sh)), **adapt** the configuration and run the following command (here with NAF as example batch system):

```bash
HiggsToTauTauAnalysis.py -i <collection_with_background_mc>.txt HiggsAnalysis/KITHiggsToTauTau/data/Samples/Run201?/SingleMuon*.txt -a HiggsAnalysis/KITHiggsToTauTau/python/data/ArtusConfigs/Run2LegacyAnalysis_base.py --no-run -b naf --wall-time 03:00:00 --memory 2000 --files-per-job 15 --se-path srm://cmssrm-kit.gridka.de:8443/srm/managerv2?SFN=/pnfs/gridka.de/cms/disk-only/store/user/<dCacheUserName>/31-07-2019_NoMetRecoil -c mm --pipelines nominal
```
The following adaption with respect to the commited configuration is required:

Disable recoil corrections, so in particular, replace this line:

<https://github.com/KIT-CMS/KITHiggsToTauTau/blob/reduced_trigger_objects/python/data/ArtusConfigs/Run2LegacyAnalysis_base.py#L152>

with:

```python
config["MetCorrectionMethod"] = "none"
```

### Having a look at control plots
To check the general Data/Expectation agreement, it is useful to create control plots for the `mm` channel without `Z(p_T, mass)` reweighting and without MET recoil corrections

In order to create shapes, some modifications are needed:

 * Update `mm` ntuples for [2016](https://github.com/KIT-CMS/sm-htt-analysis/blob/master/utils/setup_samples.sh#L8), [2017](https://github.com/KIT-CMS/sm-htt-analysis/blob/master/utils/setup_samples.sh#L28) and [2018](https://github.com/KIT-CMS/sm-htt-analysis/blob/master/utils/setup_samples.sh#L43)
 * Disable `Z(p_T, mass)` reweighting for [2016](https://github.com/KIT-CMS/shape-producer/blob/master/shape_producer/estimation_methods_2016.py#L690), [2017](https://github.com/KIT-CMS/shape-producer/blob/master/shape_producer/estimation_methods_2017.py#L564) and [2018](https://github.com/KIT-CMS/shape-producer/blob/master/shape_producer/estimation_methods_2018.py#L545)
 * Choose appropriate set of interesting variables. This set should consist of:
   * `m_vis`, `ptvis`
   * `pt_1`, `pt_2`, `eta_1`, `eta_2`
   * `njets`, `jpt_1`, `jpt_2`, `jeta_1`, `jeta_2`
   * `met`, `metphi`, `pupppimet`, `puppimetphi`
   * `metParToZ`, `metPerpToZ`, `puppimetParToZ`, `puppimetPerpToZ`

After these adpations, the following command should executed:

```bash
for year in 2016 2017 2018;
do
    ./shapes/produce_control_shapes.sh ${year} mm
done
```

### Computing correction weights

This is a two-step procedure. With the configuration for control plots mentioned above, the following command should be executed to produce files with yields in different categories (`Z(p_T, mass)` bins) and then corresponding weights:

```bash
for year in 2016 2017 2018;
do
    zptm_reweighting/produce_zptm_reweighting_counts.sh ${year} # step 1: yield production
    zptm_reweighting/compute_zptm_weights.sh ${year} # step 2: computation of correction weights
done
```

This will create root files with 2D-histograms named `zptm_weights_${year}_kit.root` and corresponding plots. These files can then be integrated into a workspace which is used by the [ZPtReweightProducer](https://github.com/KIT-CMS/KITHiggsToTauTau/blob/reduced_trigger_objects/python/data/ArtusConfigs/Run2LegacyAnalysis_base.py#L133-L135). The corresponding translation software is [CorrectionsWorkspace](https://github.com/KIT-CMS/CorrectionsWorkspace).
