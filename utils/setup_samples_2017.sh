#!/bin/bash
# general corrections applied: MetFilters, 2016 BTag efficiencies & Fall17 V1 CSV used from btag corrections

ARTUS_OUTPUTS=/storage/b/akhmet/merged_files_from_nrg/artusjobs_Data_and_MC_17NovRereco_Fall17MC_15_05_2018/ # available weights: puweights, preliminary trigger SF's, lepton -> tau fake rate SF's
#ARTUS_OUTPUTS=/storage/b/akhmet/merged_files_from_nrg/artusjobs_Data_and_MC_17NovRereco_Fall17MC_16_05_2018/ # available weights: puweights, preliminary trigger SF's, lepton -> tau fake rate SF's; also tau ES corr. applied
#ARTUS_OUTPUTS=/storage/b/akhmet/merged_files_from_nrg/artusjobs_Data_and_MC_17NovRereco_Fall17MC_17_05_2018/ # available weights: puweights, preliminary trigger SF's, lepton -> tau fake rate SF's, KIT trigger, id, iso weights, mu & e tracking/reco weights; also tau ES corr. applied


KAPPA_DATABASE=/portal/ekpbms1/home/akhmet/workdir/SkimmingMain/CMSSW_9_4_6_patch1/src/Kappa/Skimming/data/datasets.json
