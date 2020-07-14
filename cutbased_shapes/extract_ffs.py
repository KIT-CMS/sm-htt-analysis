#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser
ROOT.gErrorIgnoreLevel = ROOT.kError
import glob
import os

input_dirs = {
    "2016" : {
        "et" : "/ceph/htautau/deeptau_04-27/2016/friends/FakeFactors_final_v5/",
        "mt" : "/ceph/jbechtel/friend-tree-workdirs/auto_v8/2016/mt/FakeFactors_workdir/FakeFactors_collected/",
        "tt" : "/ceph/htautau/deeptau_04-27/2016/friends/FakeFactors_final_v5/"
    },
    "2017" : {
        "et" : "/ceph/jbechtel/friend-tree-workdirs/auto_v8/FakeFactors_workdir/FakeFactors_collected/",
        "mt" : "/ceph/jbechtel/friend-tree-workdirs/auto_v8/FakeFactors_workdir/FakeFactors_collected/",
        "tt" : "/ceph/htautau/deeptau_04-27/2017/friends/FakeFactors_final_v5/"
    },
    "2018" : {
        "et" : "/ceph/jbechtel/friend-tree-workdirs/auto_v8/2018/et/FakeFactors_workdir/FakeFactors_collected/",
        "mt" : "/ceph/htautau/deeptau_04-27/2018/friends/FakeFactors_final_v5/",
        "tt" : "/ceph/htautau/deeptau_04-27/2018/friends/FakeFactors_final_v5/"
    },
}

output_dirs = {
    "2016" : "/ceph/akhmet/merged_legacy_ntuples/cutbased_analysis/2016/friends/FakeFactors/",
    "2017" : "/ceph/akhmet/merged_legacy_ntuples/cutbased_analysis/2017/friends/FakeFactors/",
    "2018" : "/ceph/akhmet/merged_legacy_ntuples/cutbased_analysis/2018/friends/FakeFactors/",
}


for era in input_dirs:
    print "Processing era %s"%era
    nicks = set()
    for ch in input_dirs[era]:
        nicks.update([os.path.basename(p).replace(".root","") for p in [path for path in glob.glob(os.path.join(input_dirs[era][ch],"*/*.root")) if not ("HToTauTau" in path or "HToWW" in path)]])

    for nick in nicks:
        print "\tProcessing sample %s"%nick
        outputdir = os.path.join(output_dirs[era],nick)
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)
        output = ROOT.TFile.Open(os.path.join(outputdir,nick+".root"),"recreate")
        input_files = {}
        for ch in input_dirs[era]:
            input_files[ch] = ROOT.TFile.Open(os.path.join(input_dirs[era][ch],nick,nick+".root"),"read")
            dirs = [k.GetName() for k in input_files[ch].GetListOfKeys() if ch+"_" in k.GetName()]
            for d in dirs:
                output.cd()
                output.mkdir(d)
                output.cd(d)
                treename = "ntuple"
                t = input_files[ch].Get(os.path.join(d,treename))
                newt = t.CloneTree(-1, "fast")
                newt.Write(treename)
            input_files[ch].Close()
        output.Close()
