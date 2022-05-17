#!/usr/bin/env python
# encoding: utf-8

import mock
import os
import sys

import giit.virtualenv as virtualenv


def test_virtualenv(testdirectory):

    prompt = mock.Mock()
    log = mock.Mock()
    path = os.path.join(testdirectory.path(), "virtualenv")

    virtual_environment = virtualenv.VirtualEnv(prompt=prompt, log=log)

    env = virtual_environment.create_environment(path=path)

    prompt.run.assert_called_once_with(command=["python", "-m", "virtualenv", path])

    # Depending on our platform the path should be modified
    if sys.platform == "win32":
        expected_path = os.path.join(path, "Scripts")
    else:
        expected_path = os.path.join(path, "bin")

    # We should be first in the PATH environment variable
    assert env["PATH"].startswith(expected_path)
