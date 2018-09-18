import os
import schema
import six
import copy
import collections

import giit.variables_reader


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

    return output_dict


def validate_dict(config):

    # Make sure we do not modify the original dict.
    config = copy.deepcopy(config)
    config = expand_dict(config)

    # These are useful when defining defaults in the schema
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

    return config


def fill_dict(context, config):
    """ Visit all the values in the dict and expand the string """

    variables = giit.variables_reader.VariablesReader(
        variables=config['variables'], context=context)

    def visit(data):

        if isinstance(data, dict):
            for k, v in data.items():
                data[k] = visit(v)

        elif isinstance(data, list):
            return [visit(v) for v in data]

        if isinstance(data, giit.compat.string_type):
            return variables.expand(element=data)

        else:
            return data

    config = visit(config)

    return config
