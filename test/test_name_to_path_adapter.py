#!/usr/bin/env python
# encoding: utf-8

import mock
import os

import giit.name_to_path_adapter as name_to_path_adapter


def test_venv_name_to_path_adapter(testdirectory):

    virtual_environment = mock.Mock()
    root_path = testdirectory.path()

    adapter = name_to_path_adapter.NameToPathAdapter(
        env=virtual_environment, root_path=root_path
    )

    adapter.create_environment(name="ok")

    expected_path = os.path.join(root_path, "ok")

    virtual_environment.create_environment.assert_called_once_with(path=expected_path)
