#!/usr/bin/env python
# encoding: utf-8

import mock
import os
import sys

import giit.virtualenv as venv


def test_virtualenv_from_git(testdirectory):

    git = mock.Mock()
    log = mock.Mock()
    clone_path = testdirectory.path()

    virtualenv = venv.VirtualEnv.from_git(git=git, clone_path=clone_path, log=log)

    # The following directory should be in the PYTHONPATH of the virtualenv
    # prompt
    virtualenv_path = os.path.join(clone_path, venv.VERSION)

    assert virtualenv.prompt.env["PYTHONPATH"] == virtualenv_path


def test_virtualenv(testdirectory):

    prompt = mock.Mock()
    log = mock.Mock()
    path = os.path.join(testdirectory.path(), "venv")

    virtualenv = venv.VirtualEnv(prompt=prompt, log=log)

    env = virtualenv.create_environment(path=path)

    prompt.run.assert_called_once_with(
        command=["python", "-m", "virtualenv", path, "--no-site-packages"]
    )

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
