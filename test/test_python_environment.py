#!/usr/bin/env python
# encoding: utf-8

import mock
import os
import giit.python_environment


def test_python_environment(testdirectory):

    prompt = mock.Mock()
    virtual_environment = mock.Mock()
    log = mock.Mock()
    requirements = testdirectory.write_text(
        filename="requirements.txt", data="sphinx", encoding="utf-8"
    )

    env = {"PATH": "/oki/doki"}
    virtual_environment.create_environment.side_effect = lambda name: env

    python_environment = giit.python_environment.PythonEnvironment(
        prompt=prompt, virtual_environment=virtual_environment, log=log
    )

    venv = python_environment.from_requirements(
        requirements=requirements, pip_packages=None
    )

    assert venv == env

    command = "python -m pip install -U -r {}".format(
        os.path.join(testdirectory.path(), "requirements.txt")
    )
    prompt.run.assert_called_once_with(command=command, env=env)
