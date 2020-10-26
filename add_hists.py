import ROOT
import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=
        "")
    parser.add_argument("input", type=str, help="")
    parser.add_argument(
        "--input-hist",
        nargs="+",
        type=str,
        required=True, 
        default=None,
        help="Hists")
    parser.add_argument(
        "--output-hist",
        type=str,
        required=True, 
        default=None,
        help="Output hist")
    parser.add_argument(
        "--mode",
        type=str,
        required=False, 
        default="prefit",
        help="Output hist")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    file_ = ROOT.TFile(args.input,"UPDATE")
    if args.mode == "prefit":
        for key in file_.GetListOfKeys():
            file_.cd(key.GetName())
            temp_hist = file_.Get(key.GetName()+"/"+args.input_hist[0])
            output_hist = temp_hist.Clone()
            output_hist.SetTitle(args.output_hist)
            output_hist.SetName(args.output_hist)
            output_hist.Add(temp_hist,-1)
            del temp_hist
            for input_hist in args.input_hist:
                temp_hist = file_.Get(key.GetName()+"/"+input_hist)
                output_hist.Add(temp_hist)
                del temp_hist
            output_hist.Write()
    else:
        histnames = []
        for key in file_.GetListOfKeys():
            for input_hist in args.input_hist:
		if True:
                	if input_hist in key.GetName() and key.GetName()[-1] == "#":
                   		histnames.append(key.GetName())
                    		out_name = key.GetName().replace(input_hist,"HTT")
        temp_hist = file_.Get(histnames[0])
        output_hist = temp_hist.Clone()
        output_hist.SetTitle(out_name)
        output_hist.SetName(out_name)
        output_hist.Add(temp_hist,-1)
        del temp_hist
        for input_hist in histnames:
            temp_hist = file_.Get(input_hist)
            output_hist.Add(temp_hist)
            del temp_hist
        output_hist.Write()       
    file_.Write()
    file_.Close()
