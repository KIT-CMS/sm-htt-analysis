#!/usr/bin/env python

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

import argparse
import yaml
import logging
logger = logging.getLogger("sum_training_weights")
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
    parser.add_argument("--training-template", type=str,required=False, help="Specifies the config file setting the model, used variables...")
    parser.add_argument("--write-weights", type=bool, default=True, help="Overwrite inverse weights to ml/$era_$channel_training.yaml")
    parser.add_argument( "--weight-branch", default="training_weight", type=str, help="Branch with weights.")
    return parser.parse_args()


def dictToString(exdict):
    return str(["{} : {}".format(key, value) for key, value in sorted(exdict.items(), key=lambda x: x[1])])


def main(args):
    logger.info("Process training dataset %s.", args.dataset)
    f = ROOT.TFile(args.dataset)

    dsConfDict= yaml.load(open(args.dataset_config_file, "r"))
    ### use the classes that have processes mapped to them
    classes = set([dsConfDict["processes"][key]["class"] for key in dsConfDict["processes"].keys()])

    if args.training_template == None:
        args.training_template= "ml/templates/{}_{}_training.yaml".format(args.era, args.channel)
    trainingTemplateDict=yaml.load(open(args.training_template, "r"))

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

    logger.info( "{}-{}: Class weights before update: {}".format(args.era, args.channel,dictToString(trainingTemplateDict["class_weights"])))

    newWeightsDict={}
    for i, name in enumerate(classes):
        newWeightsDict[name]=sum_all / counts[i]

    if set(trainingTemplateDict["class_weights"].keys())==set(newWeightsDict.keys()):
        ### Warning for big changes
        for i, name in enumerate(classes):
            oldweight=trainingTemplateDict["class_weights"][name]
            newweight=newWeightsDict[name]
            if newweight/oldweight > 2 or newweight/oldweight < .5:
                    logger.warning( "{}-{}: Class weights for {} changing by more than a factor of 2".format(args.era, args.channel,name))
    else:
        logger.warn("Training classes in {} and {} differ".format(args.dataset_config_file,args.training_template))

    ## set the classes / classweights to the "new" dict
    dsConfDict["classes"]=newWeightsDict.keys()
    dsConfDict["class_weights"]=newWeightsDict

    ## check if the dataset_config.yaml is overwriting no permitted values in the template dict
    diffkeys=[key for key in trainingTemplateDict if key in dsConfDict and trainingTemplateDict[key]!=dsConfDict[key] and not key in ["classes", "class_weights","datasets"]  ]
    if len(diffkeys)>0:
        logger.fatal("Cannont merge configs in {} and {}: keys {} overlap".format(args.dataset_config_file,args.training_template,str(diffkeys)))
        raise Exception

    ## update the template dict with the values from the dataset_config dict + new generated classweight and classes
    for key in dsConfDict:
        if args.write_weights or key not in ["classes", "class_weights"]:
            if key in trainingTemplateDict and trainingTemplateDict[key]!=dsConfDict[key]:
                logger.warn("Overwriting template key {} with value {} with {}".format(key, str(trainingTemplateDict[key]),str(dsConfDict[key])))
            trainingTemplateDict[key]=dsConfDict[key]
    with open(args.dataset_config_file,"w") as f:
        yaml.dump(trainingTemplateDict, f, default_flow_style=False)


    logger.info( "{}-{}: Class weights after update: {}".format(args.era, args.channel,dictToString(trainingTemplateDict["class_weights"])))

if __name__ == "__main__":
    args = parse_arguments()
    main(args)
