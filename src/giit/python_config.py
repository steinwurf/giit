import os
import schema
import six
import copy
import collections


def expand_key(keys, value):

    if len(keys) == 0:
        return value
    else:
        return {keys[0]: expand_key(keys[1:], value)}


def update_dict(d, u):
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            d[k] = update_dict(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def expand_dict(input_dict):

    output_dict = {}

    for key in input_dict.keys():

        subkeys = key.split('.')
        value = input_dict[key]

        if isinstance(value, dict):
            value = expand_dict(value)

        result = {subkeys[0]: expand_key(subkeys[1:], value)}

        update_dict(output_dict, result)

        # if subkeys[0] in output_dict and isinstance(result, dict):
        #    update_dict(output_dict[subkeys[0]].update(result)
        # else:
        #    output_dict[subkeys[0]] = result

    return output_dict


class PythonConfig(object):

    def __init__(self, config):
        """ Initialize the config.

        :param config: Dict with all the config values initialized.
        """
        self.config = config

    def __getattr__(self, attribute):
        """ Allow config.attribute access.

        :return: The value of the attribute
        """
        return self[attribute]

    def __getitem__(self, key):
        """ Allow config.key access.

        :return: The value of the attribute
        """
        if not key in self.config:
            raise AttributeError("{} not found, keys are {}".format(
                key, self.config.keys()))

        return self.config[key]

    def __contains__(self, attribute):
        """ Checks if the attribute is available.
        :return: True if the attribute is available otherwise False
        """
        return attribute in self.config

    @staticmethod
    def from_dict(config):

        # Make sure we do not modify the original dict.
        config = copy.deepcopy(config)
        config = expand_dict(config)

        default_branches = {'regex': {'filters': []},
                            'source_branch': False}
        default_tags = {
            'regex': {'filters': []},
            'semver': {'filters': [], 'relaxed': False}
        }

        config_schema = schema.Schema({
            'scripts': list,
            schema.Optional('variables', default=[]): list,
            schema.Optional('requirements', default=None): six.text_type,
            schema.Optional('cwd', default=os.getcwd()): six.text_type,
            schema.Optional('python_path', default=None): six.text_type,
            schema.Optional('branches', default=default_branches): {
                schema.Optional("regex", default=default_branches["regex"]): {"filters": list},
                schema.Optional("source_branch", default=default_branches["source_branch"]): bool},
            schema.Optional('workingtree', default=False): bool,
            schema.Optional('allow_failure', default=False): bool,
            schema.Optional('pip_packages', default=None): list,
            schema.Optional('tags', default=default_tags): {
                schema.Optional("regex", default=default_tags["regex"]): {
                    "filters": list
                },
                schema.Optional("semver", default=default_tags["semver"]): {
                    "filters": list,
                    schema.Optional(
                        "relaxed", default=default_tags["semver"]["relaxed"]): bool
                }
            }
        })

        config = config_schema.validate(config)

        # At least one of the filters should be specified.
        filters = ["workingtree", "tags", "branches"]

        in_config = set(filters) & set(config.keys())

        if len(in_config) == 0:
            raise RuntimeError("You must specify at least one of the "
                               "following filters in your giit.json: {}".format(filters))

        return PythonConfig(config=config)
