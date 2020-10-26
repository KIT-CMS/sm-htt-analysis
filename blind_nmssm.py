import ROOT
import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=
        "")
    parser.add_argument("input", type=str, help="")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    file_ = ROOT.TFile(args.input,"UPDATE")
    for key in file_.GetListOfKeys():
        cat = [int(x) for x in key.GetName().split("_") if x.isdigit()][0]
        if cat>4:
            file_.cd(key.GetName())
            data_hist = file_.Get(key.GetName()+"/data_obs")
            for i in range(data_hist.GetNbinsX()+1):
                if data_hist.GetBinLowEdge(i+1)>0.4 or i==(data_hist.GetNbinsX()):
                    print "Setting content of bin {} to zero".format(i)
                    data_hist.SetBinContent(i,-1.0)
                    data_hist.SetBinError(i,0.0)

            data_hist.Write()

    file_.Write()
    file_.Close()
