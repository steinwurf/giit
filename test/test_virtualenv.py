#!/usr/bin/env python
# encoding: utf-8

import mock
import os
import sys
import pytest

import giit.virtualenv as virtualenv


@pytest.mark.skipif(
    sys.version_info >= (3, 10), reason="not supported by python3.10 or higher"
)
def test_virtualenv_from_git(testdirectory):

    git = mock.Mock()
    log = mock.Mock()
    clone_path = testdirectory.path()

    virtual_environment = virtualenv.VirtualEnv.from_git(
        git=git, clone_path=clone_path, log=log
    )

    # The following directory should be in the PYTHONPATH of the virtualenv
    # prompt
    virtualenv_path = os.path.join(clone_path, virtualenv.VERSION)

    assert virtual_environment.prompt.env["PYTHONPATH"] == virtualenv_path


@pytest.mark.skipif(
    sys.version_info >= (3, 10), reason="not supported by python3.10 or higher"
)
def test_virtualenv(testdirectory):

    prompt = mock.Mock()
    log = mock.Mock()
    path = os.path.join(testdirectory.path(), "virtualenv")

    virtual_environment = virtualenv.VirtualEnv(prompt=prompt, log=log)

    env = virtual_environment.create_environment(path=path)

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
