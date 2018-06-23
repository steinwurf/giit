import os
import mock
import giit.python_config


def test_python_config():

    config_in = {
        'type': 'python',
        'scripts': [
            'python test.py'
        ]
    }

    config_out = giit.python_config.PythonConfig.from_dict(
        config=config_in)

    assert config_out.type == 'python'
    assert len(config_out.scripts) == 1
    assert config_out.scripts[0] == 'python test.py'
    assert config_out.cwd == os.getcwd()
    assert config_out.requirements == None
    assert config_out.variables == ''
    assert config_out.allow_failure == False
    assert config_out.scope == ['source_branch']
