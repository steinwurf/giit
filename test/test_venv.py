#!/usr/bin/env python
# encoding: utf-8

import mock
import os
import sys

import giit.venv as venv


def test_virtualenv(testdirectory):

    prompt = mock.Mock()
    log = mock.Mock()
    path = os.path.join(testdirectory.path(), "venv")

    virtualenv = venv.VirtualEnv(prompt=prompt, log=log)

    env = virtualenv.create_environment(path=path)

    prompt.run.assert_called_once_with(command=["python", "-m", "venv", path])

    # Depending on our platform the path should be modified
    if sys.platform == "win32":
        expected_path = os.path.join(path, "Scripts")
    else:
        expected_path = os.path.join(path, "bin")

    # We should be first in the PATH environment variable
    assert env["PATH"].startswith(expected_path)


def test_virtualenv_name_to_path_adapter(testdirectory):

    virtualenv = mock.Mock()
    virtualenv_root_path = testdirectory.path()

    adapter = venv.NameToPathAdapter(
        virtualenv=virtualenv, virtualenv_root_path=virtualenv_root_path
    )

    adapter.create_environment(name="ok")

    virtualenv_path = os.path.join(virtualenv_root_path, "ok")

    virtualenv.create_environment.assert_called_once_with(path=virtualenv_path)
