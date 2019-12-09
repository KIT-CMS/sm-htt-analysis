import argparse
import os
import ROOT

exclusive_samples = {
        "et": ["EGamma","SingleElectron","ElTauFinalState"],
        "mt": ["SingleMuon","MuTauFinalState"],
        "tt": ["Tau_Run201","TauTauFinalState"],
        "em": ["MuonEG","ElMuFinalState"]
        }
all_channels = ["mt","et","tt","em"]

# Keep updated!
name_dict = {
	"jbechtel": "Janek",
	"sbrommer": "Sebastian",
	"swozniewski": "Sebastian",
	"akhmet": "Genosse Gottmann",
	"mburkart": "Max",
	"mscham": "Moritz",
	"ohlushch": "Olena",
	"wunsch": "Stefan"
	}

if os.environ["USER"] in name_dict:
	username = name_dict[os.environ["USER"]]
else:
	username = os.environ["USER"]

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Match friend trees to ntuples."
    )
    parser.add_argument("--friends", required=True, type=str, help="Path to friends")
    parser.add_argument("--ntuples", required=False, default="", type=str, help="Path to ntuples")
    return parser.parse_args()

def main(args):
    buggy_files = []
    for folder in os.listdir(args.friends):
        if os.path.exists(os.path.join(args.friends,folder,folder+".root")):
            friend_file = ROOT.TFile(os.path.join(args.friends,folder,folder+".root"))
        else:
            print "File {} not found.".format(os.path.exists(os.path.join(args.friends,folder,folder+".root")))
            continue
        if os.path.exists(os.path.join(args.ntuples,folder,folder+".root")):
            ntuple_file = ROOT.TFile(os.path.join(args.ntuples,folder,folder+".root"))
        else:
            print "Ntuple file {} not found.".format(os.path.exists(os.path.join(args.ntuples,folder,folder+".root")))
            print "\033[91m"+"This should exist - Please check!"+"\033[0m"
            exit(1)

        print "Matching friend file with ntuple:"
        print os.path.join(args.friends,folder,folder+".root")
        print os.path.join(args.ntuples,folder,folder+".root")
        channels = [x for x in all_channels]
        for ch in all_channels:
            for name in exclusive_samples[ch]:
                if name in folder:
                    channels = [ch]
                    break

        for ch in channels:
            friend_tree = friend_file.Get("{}_nominal/ntuple".format(ch))
            ntuple_tree = ntuple_file.Get("{}_nominal/ntuple".format(ch))
            if friend_tree.GetEntries() != ntuple_tree.GetEntries():
                print "Found {} entries for tree {}_nominal/ntuple in friend file {}".format(friend_tree.GetEntries(),ch,os.path.join(args.friends,folder,folder+".root"))
                print "But   {} entries for tree {}_nominal/ntuple in ntuple file {}".format(ntuple_tree.GetEntries(),ch,os.path.join(args.ntuples,folder,folder+".root"))
                print "\033[91m"+"Different event numbers detected in {} channel!".format(ch)+"\033[0m"
                buggy_files.append(os.path.join(args.friends,folder,folder+".root"))
            else:
                print "\033[92m"+"Same number of events in {} channel!".format(ch)+"\033[0m"
    print "\n"
    if len(buggy_files) == 0:
        print "\033[92m"+"All friend files look good. Well done {}!".format(username)+"\033[0m"
    else:
        print "\033[91m"+"These files are buggy :( :( :("+"\033[0m"
        for bfile in buggy_files:
            print bfile
if __name__ == "__main__":
    args = parse_arguments()
    if args.ntuples == "":
        if "friends/SVFit" in args.friends or "friends/FakeFactors" in args.friends or "friends/MELA" in args.friends:
            args.ntuples = args.friends.replace("friends/SVFit","ntuples").replace("friends/MELA","ntuples").replace("friends/FakeFactors","ntuples")
        else:
            print "Could not find ntuple path to these friend trees. Please set ntuple path explicitely as second argument."
            exit(1)
    main(args)
