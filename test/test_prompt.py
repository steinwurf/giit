#!/usr/bin/env python
# encoding: utf-8

import giit.prompt


def test_run(testdirectory):

    prompt = giit.prompt.Prompt()
    prompt.run("python --version", cwd=testdirectory.path())
