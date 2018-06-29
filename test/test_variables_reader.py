import mock
import pytest

import giit.variables_reader


def test_variables():

    variables = {
        'source_branch:master:out': 'yoyo',
        'source_branch:out': 'yiyi',
        'tag:out': 'yuyu ${boing} ${build_path}',
        'tag:1.0.0:boing': 'hip ${boo}',
        'tag:boing': 'hop ${boo}',
        'tag:boo': 'hap'
    }

    context = {
        'scope': 'tag',
        'checkout': '1.0.0',
        'build_path': '/tmp/build',
        'source_path': '/tmp/clone'
    }

    v = giit.variables_reader.VariablesReader(
        variables=variables, context=context)

    r = v.expand(element='$out likes')
    assert r == 'yuyu hip hap /tmp/build likes'


def test_variables_not_found():

    variables = {
        'source_branch:master:out': 'yoyo',
        'source_branch:out': 'yiyi',
        'tag:out': 'yuyu ${boing} ${build_path}',
        'tag:boo': 'hap'
    }

    context = {
        'scope': 'tag',
        'checkout': '1.0.0',
        'build_path': '/tmp/build',
        'source_path': '/tmp/clone'
    }

    v = giit.variables_reader.VariablesReader(
        variables=variables, context=context)

    with pytest.raises(AttributeError):
        r = v.expand(element='$out likes')


def test_variables_empty():

    variables = ''

    context = {
        'scope': 'tag',
        'checkout': '1.0.0',
        'build_path': '/tmp/build',
        'source_path': '/tmp/clone'
    }

    v = giit.variables_reader.VariablesReader(
        variables=variables, context=context)

    r = v.expand(element='$build_path')
    assert r == '/tmp/build'
