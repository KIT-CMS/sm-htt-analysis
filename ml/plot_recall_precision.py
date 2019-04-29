#!/usr/bin/env python

import logging
logger = logging.getLogger("plot_recall_precision")

import argparse
import yaml
import os

def parse_arguments():
    logger.debug("Parse arguments.")
    parser = argparse.ArgumentParser(
        description="Train machine Keras models for Htt analyses")
    parser.add_argument("config_train", help="Path to training config file")
    parser.add_argument("fold", help="The fold to be evaluated")
    return parser.parse_args()


def parse_config(filename):
    logger.debug("Parse config.")
    return yaml.load(open(filename, "r"))

def parse_json(filename):
    import json
    logger.debug("Parse json-file")
    with open(filename, "r") as f:
        data = json.load(f)
    return data


def setup_logging(level, output_file=None):
    logger.setLevel(level)
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if not output_file == None:
        file_handler = logging.FileHandler(output_file, "w")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


def main(args, config_train, json_content):
    variables_list = []
    recall_list = []
    f1_score_list = []
    precision_list = []

    logger.info('Getting results...')
    for model in json_content["results"]:
        number_of_variables = model["number_of_variables"]
        variables_list.append(number_of_variables)
        #if number_of_variables == 20:
        #    all_variables = model["variables_used"]
        scores_by_class = model["scores_by_class"]
        for key, values in scores_by_class.items():
            if key == "Recall":
                recall_list.append(values)
            if key == "Precision":
                precision_list.append(values)
            if key == "F1-Score":
                f1_score_list.append(values)
    recall_dict = dict()
    f1_score_dict = dict()
    precision_dict = dict()
    for i_class, class_ in enumerate(config_train["classes"]):
        recall_dict[class_] = []
        f1_score_dict[class_] = []
        precision_dict[class_] = []
        for recall in recall_list:
            recall_dict[class_].append(recall[i_class])
        for precision in precision_list:
            precision_dict[class_].append(precision[i_class])
        for f1_score in f1_score_list:
            f1_score_dict[class_].append(f1_score[i_class])

    import matplotlib as mpl
    mpl.use('Agg')
    import matplotlib.pyplot as plt

    logger.info('Plotting scores...')

    all_variables = config_train['variables']

    fig = plt.figure(figsize=(15,5))
    ax = fig.add_subplot(111)

    for class_ in config_train["classes"]:
        value_list = recall_dict[class_]
        x_values, y_values = (list(t) for t in zip(*sorted(zip(variables_list, value_list))))

        ax.plot(x_values, y_values, lw=3, label="{}".format(class_))

    path_plot = os.path.join(config_train["output_path_json"],
                             "fold{}_{}_all".format(args.fold,"Recall"))
    ax.set_title("{} over # variables".format("Recall/Efficiency"))
    ax.set_xlabel("Number of variables"), plt.ylabel("Recall/Efficiency")
    ax.set_xticks(x_values)
    ax.set_xticklabels(all_variables)
    ax.legend()
    fig.savefig(path_plot + ".png", bbox_inches="tight")
    fig.savefig(path_plot + ".pdf", bbox_inches="tight")

    logger.info("Saved results to {}".format(path_plot))

    plt.clf()

    fig = plt.figure(figsize=(15,5))
    ax = fig.add_subplot(111)

    for class_ in config_train["classes"]:
        value_list = f1_score_dict[class_]
        x_values, y_values = (list(t) for t in zip(*sorted(zip(variables_list, value_list))))

        ax.plot(x_values, y_values, lw=3, label="{}".format(class_))

    path_plot = os.path.join(config_train["output_path_json"],
                             "fold{}_{}_all".format(args.fold, "F1_Score"))

    ax.set_title("{} over # variables".format("F1-Score"))
    ax.set_xlabel("Number of variables"), plt.ylabel("F1-Score")
    ax.set_xticks(x_values)
    ax.set_xticklabels(all_variables)
    ax.legend()
    fig.savefig(path_plot + ".png", bbox_inches="tight")
    fig.savefig(path_plot + ".pdf", bbox_inches="tight")

    logger.info("Saved results to {}".format(path_plot))

    plt.clf()

    fig = plt.figure(figsize=(15,5))
    ax = fig.add_subplot(111)

    for class_ in config_train["classes"]:
        value_list = precision_dict[class_]
        x_values, y_values = (list(t) for t in zip(*sorted(zip(variables_list, value_list))))

        ax.plot(x_values, y_values, lw=3, label="{}".format(class_))

    path_plot = os.path.join(config_train["output_path_json"],
                             "fold{}_{}_all".format(args.fold, "Precision"))
    ax.set_title("{} over # variables".format("Precision/Purity"))
    ax.set_xlabel("Number of variables"), plt.ylabel("Precision/Purity")
    ax.set_xticks(x_values)
    ax.set_xticklabels(all_variables)
    ax.legend()
    fig.savefig(path_plot + ".png", bbox_inches="tight")
    fig.savefig(path_plot + ".pdf", bbox_inches="tight")

    logger.info("Saved results to {}".format(path_plot))


if __name__ == "__main__":
    setup_logging(logging.DEBUG)
    args = parse_arguments()
    config = parse_config(args.config_train)
    json_path = os.path.join(config['output_path_json'], 'pruning_information_fold{}.json'.format(args.fold))
    json_content = parse_json(json_path)
    main(args, config, json_content)
