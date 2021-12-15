#!/usr/bin/env python
# encoding: utf-8

import os
import schema
import six
import copy
from collections.abc import Mapping

import giit.variables_reader


def _expand_key(keys, value):
    """Expands a list of keys and a value into a nested
    dictionary where the last dictionary contains the value.
    """

    if len(keys) == 0:
        return value
    else:
        return {keys[0]: _expand_key(keys[1:], value)}


def _update_dict(dst, src):
    """Takes the dictionary src and merges its keys into
    dst.
    """
    for key, value in src.items():

        if isinstance(value, Mapping):
            # If the value is a dictionary recursively take
            # key of dst and src and continue the process
            dst[key] = _update_dict(dst.get(key, {}), value)

        else:
            # This process should not overwrite any values
            assert key not in dst
            dst[key] = value

    return dst


def _expand_dict(input):
    """Takes an input dictionary and expands all dot keys
    into nested dictionaries
    """

    output_dict = {}

    for key in input.keys():

        subkeys = key.split(".")
        value = input[key]

        if isinstance(value, dict):
            value = _expand_dict(value)

        result = {subkeys[0]: _expand_key(subkeys[1:], value)}

        _update_dict(output_dict, result)

    return output_dict


def validate_config(config):
    """Takes as input a config object and validates it against
    the giit schema
    """

    # Make sure we do not modify the original dict.
    config = copy.deepcopy(config)

    # The config is a Python dictionary were we allow
    # a compressed notation where keys may contain
    # dots - see README. Lets expand this to a fully nested
    # dictionary
    config = _expand_dict(config)

    # Check whether we have any git steps - if not we mark
    # this config a no_git. The task generator will use this
    # information and generate a single task for just running
    # the script.
    no_git = not any(key in config for key in ["branches", "tags", "workingtree"])

    # Lets validate the config
    default_branches = {"regex": {"filters": []}, "source_branch": False}
    default_tags = {
        "regex": {"filters": []},
        "semver": {"filters": [], "relaxed": False},
    }

    config_schema = schema.Schema(
        {
            "scripts": list,
            schema.Optional("variables", default={}): dict,
            schema.Optional("requirements", default=None): six.text_type,
            schema.Optional("cwd", default=os.getcwd()): six.text_type,
            schema.Optional("python_path", default=None): six.text_type,
            schema.Optional("branches", default=default_branches): {
                schema.Optional("regex", default=default_branches["regex"]): {
                    "filters": list
                },
                schema.Optional(
                    "source_branch", default=default_branches["source_branch"]
                ): bool,
            },
            schema.Optional("workingtree", default=False): bool,
            schema.Optional("allow_failure", default=False): bool,
            schema.Optional("pip_packages", default=None): list,
            schema.Optional("tags", default=default_tags): {
                schema.Optional("regex", default=default_tags["regex"]): {
                    "filters": list
                },
                schema.Optional("semver", default=default_tags["semver"]): {
                    "filters": list,
                    schema.Optional(
                        "relaxed", default=default_tags["semver"]["relaxed"]
                    ): bool,
                },
            },
        }
    )

    config = config_schema.validate(config)

    # Inject the no_git configuration values
    config["no_git"] = no_git

    return config


def fill_dict(context, config):
    """Visit all the values in the dict and expand the string"""

    # Make sure we do not modify the original dicts.
    config = copy.deepcopy(config)
    context = copy.deepcopy(context)

    variables = giit.variables_reader.VariablesReader(
        variables=config["variables"], context=context
    )

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
