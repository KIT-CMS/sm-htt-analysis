import ROOT as r
import json
import math

f = r.TFile.Open("HiggsAnalysis/KITHiggsToTauTau/data/root/recoilMet/Type1_PFMET_2017.root","read")

funcs = [k.GetName() for k in f.GetListOfKeys() if isinstance(f.Get(k.GetName()),r.TF1)]

variable_dict = {
    "recoilZPerp" : "metPerpToZ",
    "recoilZParal" : "metParToZ",
}

category_dict = {
    "NJet0Pt0to10"    : "mm_njets_bin_0_vs_ptvis_bin_0",
    "NJet0Pt10to20"   : "mm_njets_bin_0_vs_ptvis_bin_1",
    "NJet0Pt20to30"   : "mm_njets_bin_0_vs_ptvis_bin_2",
    "NJet0Pt30to50"   : "mm_njets_bin_0_vs_ptvis_bin_3",
    "NJet0PtGt50"     : "mm_njets_bin_0_vs_ptvis_bin_4",
    "NJet1Pt0to10"    : "mm_njets_bin_1_vs_ptvis_bin_0",
    "NJet1Pt10to20"   : "mm_njets_bin_1_vs_ptvis_bin_1",
    "NJet1Pt20to30"   : "mm_njets_bin_1_vs_ptvis_bin_2",
    "NJet1Pt30to50"   : "mm_njets_bin_1_vs_ptvis_bin_3",
    "NJet1PtGt50"     : "mm_njets_bin_1_vs_ptvis_bin_4",
    "NJetGe2Pt0to10"  : "mm_njets_bin_2_vs_ptvis_bin_0",
    "NJetGe2Pt10to20" : "mm_njets_bin_2_vs_ptvis_bin_1",
    "NJetGe2Pt20to30" : "mm_njets_bin_2_vs_ptvis_bin_2",
    "NJetGe2Pt30to50" : "mm_njets_bin_2_vs_ptvis_bin_3",
    "NJetGe2PtGt50"   : "mm_njets_bin_2_vs_ptvis_bin_4",
}

outdict = {}

for func in funcs:
    info = func.split("_")
    var = info[0]
    cat = info[1]
    datatype = info[2]
    outdict.setdefault(variable_dict[var],{})
    outdict[variable_dict[var]].setdefault(category_dict[cat],{})
    F = f.Get(func)
    outdict[variable_dict[var]][category_dict[cat]][datatype] =  {"mean" : F.Mean(-180.0,180.0), "resolution" : math.sqrt(F.CentralMoment(2,-180.0,180.0))}

with open("recoil.json","w") as jsonout:
    jsonout.write(json.dumps(outdict, sort_keys=True, indent=2))
    jsonout.close()
