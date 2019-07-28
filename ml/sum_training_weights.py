#!/usr/bin/env python

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

import argparse
import yaml
import logging
logger = logging.getLogger("write_dataset_config")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Sum training weights of classes in training dataset.")
    parser.add_argument("--era", required=True, help="Experiment era")
    parser.add_argument("--channel", required=True, help="Analysis channel")
    parser.add_argument("--dataset", type=str,required=True, help="Training dataset.")
    parser.add_argument("--dataset-config-file", type=str,required=True, help="Specifies the config file created by ml/create_training_dataset.sh calling ml/write_dataset_config.py")
    parser.add_argument("--write-weights", type=bool, default=False, help="Overwrite inverse weights to ml/$era_$channel_training.yaml")
    parser.add_argument( "--weight-branch", default="training_weight", type=str, help="Branch with weights.")
    return parser.parse_args()



def readclasses(filename):
    logger.debug("Parse config.")
    confdict= yaml.load(open(filename, "r"))
    return set([confdict["processes"][key]["class"] for key in confdict["processes"].keys()])

def dictToString(exdict):
    return str(["{} : {}".format(key, value) for key, value in sorted(exdict.items(), key=lambda x: x[1])])

def main(args):
    logger.info("Process training dataset %s.", args.dataset)
    f = ROOT.TFile(args.dataset)
    classes=readclasses(args.dataset_config_file)

    ### Weight Calculation
    counts = []
    sum_all = 0.0
    for name in classes:
        logger.debug("Process class %s.", name)
        sum_ = 0.0
        tree = f.Get(name)
        if tree == None:
            logger.fatal("Tree %s does not exist in file.", name)
            raise Exception
        for event in tree:
            sum_ += getattr(event, args.weight_branch)
        sum_all += sum_
        counts.append(sum_)

    ### Weight printing
    for i, name in enumerate(classes):
        logger.info(
            "Class {} (sum, fraction, inverse): {:g}, {:g}, {:g}".format(
                name, counts[i], counts[i] / sum_all, sum_all / counts[i]))

    ### Writing calculated weight to "ml/{}_{}_training.yaml"
    if args.write_weights:
        training_config_filename="ml/{}_{}_training.yaml".format(args.era, args.channel)
        training_config_dict=yaml.load(open(training_config_filename, "r"))

        logger.info( "{}-{}: Class weights before update: {}".format(args.era, args.channel,dictToString(training_config_dict["class_weights"])))

    newWeightsDict={}
    for i, name in enumerate(classes):
        newWeightsDict[name]=sum_all / counts[i]

    if set(training_config_dict["class_weights"].keys())==set(newWeightsDict.keys()):
        ### Warning for big changes
        for i, name in enumerate(classes):
            oldweight=training_config_dict["class_weights"][name]
            newweight=newWeightsDict[name]
            if newweight/oldweight > 2 or newweight/oldweight < .5:
                    logger.warning( "{}-{}: Class weights for {} changing by more than a factor of 2".format(args.era, args.channel,name))
    else:
        logger.warn("Training classes in {} and {} differ".format(args.dataset_config_file,training_config_filename))

    dsConfDict=yaml.load(open(args.dataset_config_file, "r"))
    dsConfDict["classes"]=newWeightsDict.keys()
    dsConfDict["class_weights"]=newWeightsDict
    with open(args.dataset_config_file,"w") as f:
        yaml.dump(dsConfDict, f, default_flow_style=False)


    logger.info( "{}-{}: Class weights after update: {}".format(args.era, args.channel,dictToString(training_config_dict["class_weights"])))

if __name__ == "__main__":
    args = parse_arguments()
    main(args)
