import json
import argparse
import os 

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Merge nmssm limit json files")
    parser.add_argument(
        "--input", "-i", nargs="+", help="list of files")
    parser.add_argument(
        "--output", "-o", help="list of files")
    return parser.parse_args()

def main(args):
    output_dict = {}
    for file_ in args.input:
        if not ".json" in file_:
            print "Expect json file as input!"
            exit()
        if not os.path.exists(file_):
            print "WARNING: Skipping mass point for {}".format(file_)
            continue
        with open(file_,"r") as f:
            in_dict = json.load(f)
        output_dict.update(in_dict)
    with open(args.output,"w") as f:
        json.dump(output_dict, f)
if __name__ == "__main__":
    args = parse_arguments()
    main(args)
