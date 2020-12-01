#!/usr/bin/env python
# encoding: utf-8

import mock

import giit.git
import giit.prompt


def test_git(testdirectory):

    log = mock.Mock()

    git = giit.git.Git(
        git_binary='git', prompt=giit.prompt.Prompt(), log=log)

    print(git.version())
