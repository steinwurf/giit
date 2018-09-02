import mock
import os

import giit.python_environment


def test_python_environment(testdirectory):

    prompt = mock.Mock()
    virtualenv = mock.Mock()
    log = mock.Mock()
    requirements = testdirectory.write_text(
        filename='requirements.txt', data=u'sphinx', encoding='utf-8')

    env = {'PATH': '/oki/doki'}
    virtualenv.create_environment.side_effect = lambda name: env

    python_environment = giit.python_environment.PythonEnvironment(
        prompt=prompt, virtualenv=virtualenv, log=log)

    venv = python_environment.from_requirements(requirements=requirements,
                                                pip_packages=None)

    assert venv == env

    command = 'python -m pip install -U -r {}'.format(
        os.path.join(testdirectory.path(), 'requirements.txt'))
    prompt.run.assert_called_once_with(command=command, env=env)
