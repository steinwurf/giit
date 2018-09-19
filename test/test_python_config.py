import os
import mock
import json
import giit.python_config


def read_config(json_path, step):
    """ Small helper to read the configs """
    with open(json_path) as json_file:
        json_data = json.load(json_file)

    config = json_data[step]

    return giit.python_config.validate_dict(config=config)


def test_python_config_master(datarecorder):

    config = read_config(
        'test/data/urllib3_master_giit.json', step="docs")

    datarecorder.recording_path = 'test/data/recordings/urllib3_master_giit.json'
    datarecorder.record(data=config)


def test_python_config_master_upload(datarecorder):

    config = read_config(
        'test/data/urllib3_master_giit.json', step="upload")

    datarecorder.recording_path = 'test/data/recordings/urllib3_master_upload_giit.json'
    datarecorder.record(data=config)


def test_python_config_source(datarecorder):

    config = read_config(
        'test/data/urllib3_source_branch_giit.json', step="docs")

    datarecorder.recording_path = 'test/data/recordings/urllib3_source_branch_giit.json'
    datarecorder.record(data=config)


def test_python_config_tags(datarecorder):

    config = read_config(
        'test/data/urllib3_tags_giit.json', step="docs")

    datarecorder.recording_path = 'test/data/recordings/urllib3_tags_giit.json'
    datarecorder.record(data=config)


def test_python_config_tags_fill(datarecorder):

    config = read_config(
        'test/data/urllib3_tags_giit.json', step="docs")

    context = {
        'scope': 'tag',
        'name': '1.0.0',
        'checkout': '1.0.0',
        'build_path': '/tmp/build',
        'source_path': '/tmp/clone'
    }

    config = giit.python_config.fill_dict(context=context, config=config)

    datarecorder.recording_path = 'test/data/recordings/urllib3_tags_giit_fill.json'
    datarecorder.record(data=config)
