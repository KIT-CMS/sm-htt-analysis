#!/usr/bin/env python

import argparse
import logging
logger = logging.getLogger("yamlmerge")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

### YAML + ORDERED DICT MAGIC
from collections import OrderedDict
import yaml
from yaml import Loader, Dumper
from yaml.representer import SafeRepresenter

def dict_representer(dumper, data):
   return dumper.represent_dict(data.iteritems())
Dumper.add_representer(OrderedDict, dict_representer)

def dict_constructor(loader, node):
    return OrderedDict(loader.construct_pairs(node))
Loader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, dict_constructor)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Sum training weights of classes in training dataset.")
    parser.add_argument("--era", required=True, help="Experiment era")
    parser.add_argument("--channel", required=True, help="Analysis channel")
    parser.add_argument("--dataset-config-file", type=str,required=False, help="Specifies the config file created by ml/create_training_dataset.sh calling ml/write_dataset_config.py")
    parser.add_argument("--training-template", type=str,required=False, help="Specifies the config file setting the model, used variables...")
    parser.add_argument("--testing-template", type=str,required=False)
    parser.add_argument("--application-template", type=str,required=False)
    return parser.parse_args()


def dictToString(exdict):
    return str(["{} : {}".format(key, value) for key, value in sorted(exdict.items(), key=lambda x: x[1])])

def main(args):


    if args.dataset_config_file == None:
        args.dataset_config_file= "ml/out/{}_{}/dataset_config.yaml".format(args.era, args.channel)
    dsConfDict=yaml.load(open(args.dataset_config_file, "r"))
    # logger.info("From {} load : {}".format( args.dataset_config_file,dictToString(dsConfDict)))

    classes = set([dsConfDict["processes"][key]["class"] for key in dsConfDict["processes"].keys()])


    if args.training_template == None:
        args.training_template= "ml/templates/{}_{}_training.yaml".format(args.era, args.channel)
    trainingTemplateDict=yaml.load(open(args.training_template, "r"))
    # logger.info("From {} load : {}", args.training_template,dictToString(trainingTemplateDict))

    # if args.testing_template == None:
    #     args.testing_template= "ml/templates/{}_{}_testing.yaml".format(args.era, args.channel)
    # testingTemplateDict=yaml.load(open(args.testing_template, "r"))
    # # logger.info("From {} load : {}", args.testing_template,dictToString(testingTemplateDict))

    # if args.application_template == None:
    #     args.application_template= "ml/templates/{}_{}_application.yaml".format(args.era, args.channel)
    # applicationTemplateDict=yaml.load(open(args.application_template, "r"))
    # # logger.info("From {} load : {}", args.application_template,dictToString(applicationTemplateDict))
    if "classes" in trainingTemplateDict.keys():
        if set(trainingTemplateDict["classes"])!=set(classes):
            logger.warn("Training classes in {} and {} differ".format(args.dataset_config_file,args.training_template))
        #exit 1

    mergeddict=OrderedDict({})
    mergeddict["classes"]=[]
    ## Sort the clases, so testing plots/... are easierer to compare
    priolist=["qqh","ggh","emb","ztt","tt","db","misc","zll","w","noniso","ss","ff"]
    for prioclass in priolist:
        if prioclass in classes:
            mergeddict["classes"].append(prioclass)
    ## add classes that are not in the priolist at the end
    for cl in classes:
        if cl not in mergeddict["classes"]:
            mergeddict["classes"].append(cl)

    for d in [dsConfDict, trainingTemplateDict]:
        for key in d:
            if key not in ["classes", "processes"]:
                if key in mergeddict and mergeddict[key]!=d[key]:
                    logger.fatal("Key overlap for key {}, {} should overwrite {}".format(key,d[key],mergeddict[key]))
                mergeddict[key]=d[key]
    mergeddict["processes"]=dsConfDict["processes"]
    # with open(mergeddict["output_path"]+"/runconf.yaml","w") as f:
    with open(mergeddict["output_path"]+"/dataset_config.yaml","w") as f:
        yaml.dump(mergeddict, f,Dumper=Dumper, default_flow_style=False)

    logger.info( "{}-{}: Dict after merge: without processes".format(args.era, args.channel))
    print(dictToString({key: value for key, value in mergeddict.items() if key != "processes"}))

if __name__ == "__main__":
    args = parse_arguments()
    main(args)
