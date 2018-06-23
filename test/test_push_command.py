#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import mock
import tempfile

import giit.push_command


def test_push_command_to_path(testdirectory):

    assert os.path.join('/tmp', 'git') == giit.push_command.PushCommand._to_path(
        repository_path='/tmp', to_path='/git/')

    assert os.path.join('/tmp', 'git') == giit.push_command.PushCommand._to_path(
        repository_path='/tmp', to_path='./git/')

    assert os.path.join('/tmp', 'git') == giit.push_command.PushCommand._to_path(
        repository_path='/tmp', to_path='git')

    assert os.path.join('/tmp', 'git') == giit.push_command.PushCommand._to_path(
        repository_path='/tmp', to_path='git/')

    assert os.path.join('/tmp') == giit.push_command.PushCommand._to_path(
        repository_path='/tmp', to_path='.')

    assert os.path.join('/tmp') == giit.push_command.PushCommand._to_path(
        repository_path='/tmp', to_path='/')


def test_push_command(testdirectory):

    prompt = mock.Mock()
    config = {}
    log = mock.Mock()

    build_dir = testdirectory.mkdir('build')
    build_dir.write_text(
        filename='hello.txt', data=u'world', encoding='utf-8')

    config['to_path'] = '/'
    config['from_path'] = '${build_path}'
    config['variables'] = ''
    config['exclude_patterns'] = []
    config['git_url'] = 'git@github.com:org/project.git'
    config['target_branch'] = 'gh-pages'
    config['commit_name'] = 'Giit Bot'
    config['commit_email'] = 'deploy@giit.bot'

    command = giit.push_command.PushCommand(
        prompt=prompt, config=config, log=log)

    context = {
        'scope': 'tag',
        'name': '1.0.0',
        'build_path': build_dir.path()
    }

    command.run(context=context)

    cwd = os.path.join(tempfile.gettempdir(), 'giit_push')

    calls = [
        mock.call.run(command=["git", "init"], cwd=cwd),
        mock.call.run(command=["git", "add", "."], cwd=cwd),
        mock.call.run(
            command=["git", "-c", "user.name='Giit Bot'",
                     "-c", "user.email='deploy@giit.bot'",
                     "commit", "-m", "'giit push'"],
            cwd=cwd),
        mock.call.run(
            command=['git', 'push', '--force',
                     "git@github.com:org/project.git",
                     'master:gh-pages'],
            cwd=cwd)
    ]

    prompt.assert_has_calls(calls)
