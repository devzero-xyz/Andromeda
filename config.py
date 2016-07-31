from collections import OrderedDict
import json

def load(config_file):
    with open(config_file) as conf:
        return json.load(conf, object_pairs_hook=OrderedDict)

def save(config_file, config):
    with open(config_file, "w") as conf:
        json.dump(config, conf, indent=4)
        conf.write("\n")
