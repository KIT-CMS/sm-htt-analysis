#!/usr/bin/env python

import logging
logger = logging.getLogger("history_plotter")

import argparse
import yaml
import os
import pickle


def parse_arguments():
    logger.debug("Parse arguments.")
    parser = argparse.ArgumentParser(
        description="Train machine Keras models for Htt analyses")
    parser.add_argument("config", help="Path to training config file")
    parser.add_argument("fold", type=int, help="Select the fold to be trained")
    return parser.parse_args()


def parse_config(filename):
    logger.debug("Parse config.")
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

def main(args, config):
    history_path = os.path.join(config["output_path"],
                              "fold{}_keras_model_history.pkl".format(args.fold))

    with open(history_path, 'r') as history_file:
        logger.info("Opened input history pickle file")
        history = pickle.load(history_file)

        import matplotlib.pyplot as plt
        plt.plot(history["loss"])
        plt.plot(history["val_loss"])
        plt.title("Model Loss")
        plt.ylabel("Loss")
        plt.xlabel("epoch")
        plt.legend(['train', 'validation'], loc='upper right')
        # Uncomment the line below for interactive figure handling
        #plt.show()

        plt_basepath = os.path.join(config["output_path"],
                              "fold{}_keras_model_loss".format(args.fold))
        plt.savefig(plt_basepath + '.png', bbox_inches='tight')
        plt.savefig(plt_basepath + '.pdf', bbox_inches='tight')

if __name__ == "__main__":
    setup_logging(logging.DEBUG)
    args = parse_arguments()
    config = parse_config(args.config)
    main(args, config)
