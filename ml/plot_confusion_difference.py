#!/usr/bin/env python

import logging
logger = logging.getLogger("plot_recall_precision")

import matplotlib as mpl
mpl.use('Agg')
mpl.rcParams['font.size'] = 16

import argparse
import yaml
import os
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import cm


def parse_arguments():
    logger.debug("Parse arguments.")
    parser = argparse.ArgumentParser(
        description="Train machine Keras models for Htt analyses")
    parser.add_argument('config_train', help='path to config train that contains classes in order')
    parser.add_argument("path_1", help="First path to confusion matrices")
    parser.add_argument("path_2", help="Second path to confusion matrices")
    parser.add_argument("fold", help="What fold")
    return parser.parse_args()


def parse_yaml(filename):
    logger.debug("Parse file {}".format(filename))
    return yaml.load(open(filename, "r"))


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

def plot_confusion(confusion, classes, filename, label, markup='{:.2f}'):
    logger.debug("Write plot to %s.", filename)
    plt.figure(figsize=(2.5 * confusion.shape[0], 2.0 * confusion.shape[1]))
    axis = plt.gca()
    for i in range(confusion.shape[0]):
        for j in range(confusion.shape[1]):
            axis.text(
                i + 0.5,
                j + 0.5,
                markup.format(confusion[i, -1 - j]),
                ha='center',
                va='center',
                fontsize=24)
    q = plt.pcolormesh(np.transpose(confusion)[::-1], cmap=cm.coolwarm_r, vmax=0.05, vmin=-0.05)
    cbar = plt.colorbar(q)
    cbar.set_label(label, rotation=270, labelpad=50, fontsize=28)
    cbar.ax.tick_params(labelsize=24)
    plt.xticks(
        np.array(range(len(classes))) + 0.5, classes, rotation='vertical', fontsize=24)
    plt.yticks(
        np.array(range(len(classes))) + 0.5,
        classes[::-1],
        rotation='horizontal', fontsize=24)
    plt.xlim(0, len(classes))
    plt.ylim(0, len(classes))
    plt.ylabel('Predicted class', fontsize=28)
    plt.xlabel('True class', fontsize=28)
    plt.savefig(filename+".png", bbox_inches='tight')
    plt.savefig(filename+".pdf", bbox_inches='tight')

    d = {}
    for i1, c1 in enumerate(classes):
        d[c1] = {}
        for i2, c2 in enumerate(classes):
            d[c1][c2] = float(confusion[i1, i2])
    f = open(filename+".yaml", "w")
    yaml.dump(d, f)


def main(args, path_1, path_2, config_train):
    efficiency_yaml_1 = os.path.join(path_1, "fold{}_keras_confusion_efficiency_cw2.yaml".format(args.fold))
    efficiency_yaml_2 = os.path.join(path_2, "fold{}_keras_confusion_efficiency_cw2.yaml".format(args.fold))
    efficiency_dic_1 = parse_yaml(efficiency_yaml_1)
    efficiency_dic_2 = parse_yaml(efficiency_yaml_2)
    config = parse_yaml(config_train)
    classes = config['classes']
    difference = np.zeros(
        (len(classes), len(classes)),
        dtype=np.float)
    for i_class, class_ in enumerate(classes):
        dict_1 = efficiency_dic_1[class_]
        dict_2 = efficiency_dic_2[class_]
        for j_class, class_2 in enumerate(classes):
            value_1 = dict_1[class_2]
            value_2 = dict_2[class_2]
            difference[i_class][j_class] = value_1 - value_2
    filename = 'fold{}_difference_efficiency'.format(args.fold)
    plot_confusion(difference, classes, filename, 'Difference of Efficiency', markup='{:.2f}')


    purity_yaml_1 = os.path.join(path_1, "fold{}_keras_confusion_purity_cw2.yaml".format(args.fold))
    purity_yaml_2 = os.path.join(path_2, "fold{}_keras_confusion_purity_cw2.yaml".format(args.fold))
    purity_dic_1 = parse_yaml(purity_yaml_1)
    purity_dic_2 = parse_yaml(purity_yaml_2)
    config = parse_yaml(config_train)
    classes = config['classes']
    difference_purity = np.zeros(
        (len(classes), len(classes)),
        dtype=np.float)
    for i_class, class_ in enumerate(classes):
        dict_1 = purity_dic_1[class_]
        dict_2 = purity_dic_2[class_]
        for j_class, class_2 in enumerate(classes):
            value_1 = dict_1[class_2]
            value_2 = dict_2[class_2]
            difference_purity[i_class][j_class] = value_1 - value_2
    filename = 'fold{}_difference_purity'.format(args.fold)
    plot_confusion(difference_purity, classes, filename, 'Difference of Purity', markup='{:.2f}')


if __name__ == "__main__":
    setup_logging(logging.DEBUG)
    args = parse_arguments()
    path_1 = args.path_1
    path_2 = args.path_2
    main(args, path_1, path_2, args.config_train)
