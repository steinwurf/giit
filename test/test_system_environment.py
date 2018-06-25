import mock
import os

import giit


class SystemEnvironment(object):

    def create_environment(self):
        return dict(os.environ)


def test_python_environment(testdirectory):

    system_environment = SystemEnvironment()

    env = system_environment.create_environment()

    assert dict(os.environ) == env
