#!/usr/bin/env python
# encoding: utf-8

import json
import giit.config


def _read_config(json_path, step):
    """ Small helper to read the configs """
    with open(json_path) as json_file:
        json_data = json.load(json_file)

    config = json_data[step]

    return giit.config.validate_config(config=config)


def test_python_config_default_branch(datarecorder):

    config = _read_config(
        'test/data/urllib3_main_giit.json', step="docs")
    datarecorder.record_data(
        data=config,
        recording_file='test/data/recordings/urllib3_main_giit.json')


def test_python_config_source(datarecorder):

    config = _read_config(
        'test/data/urllib3_source_branch_giit.json', step="docs")
    datarecorder.record_data(
        data=config,
        recording_file='test/data/recordings/urllib3_source_branch_giit.json')


def test_python_config_tags(datarecorder):

    config = _read_config(
        'test/data/urllib3_tags_giit.json', step="docs")

    datarecorder.record_data(
        data=config,
        recording_file='test/data/recordings/urllib3_tags_giit.json')


def test_python_config_tags_fill(datarecorder):

    config = _read_config(
        'test/data/urllib3_tags_giit.json', step="docs")

    context = {
        'scope': 'tag',
        'name': '1.0.0',
        'checkout': '1.0.0',
        'build_path': '/tmp/build',
        'source_path': '/tmp/clone'
    }

    config = giit.config.fill_dict(context=context, config=config)

    datarecorder.record_data(
        data=config,
        recording_file='test/data/recordings/urllib3_tags_giit_fill.json')


def test_expand_key():

    result = giit.config._expand_key(keys=['a', 'b', 'c'], value=True)
    expected = {'a': {'b': {'c': True}}}

    assert result == expected


def test_update_dict():

    dst = {'a': {'b': {'c': True}}}
    src = {'a': {'b': {'d': True}}}

    result = giit.config._update_dict(dst, src)
    expected = {'a': {'b': {'c': True, 'd': True}}}

    assert result == expected


def test_expand_dict():

    result = {
        "branch": {"regex": {"filter": ["origin/master"]}},
        "tag": {"semver": {"filter": [">=2.0.0"], "relaxed": True}},
        "other": {"value": {"check": {"this": True}}}
    }

    # Try some nested keys
    config = {
        "branch.regex.filter": ["origin/master"],
        "tag": {
            "semver.filter": [">=2.0.0"],
            "semver.relaxed": True
        },
        "other.value": {"check.this": True}
    }

    assert giit.config._expand_dict(config) == result

    # Try flat keys
    config = {
        "branch.regex.filter": ["origin/master"],
        "tag.semver.filter": [">=2.0.0"],
        "tag.semver.relaxed": True,
        "other.value": {"check.this": True}
    }

    print(giit.config._expand_dict(config))

    assert giit.config._expand_dict(config) == result
