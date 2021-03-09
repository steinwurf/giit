#!/usr/bin/env python
# encoding: utf-8

import os


def test_urllib3_main(testdirectory):

    config_file = testdirectory.copy_file('test/data/urllib3_main_giit.json')

    url = 'https://github.com/urllib3/urllib3.git'

    cmd = ['giit', 'clean', url,
           '--config_path', config_file]

    print(testdirectory.run(cmd))

    cmd = ['giit', 'docs', url,
           '--config_path', config_file, '-v']

    print(testdirectory.run(cmd))


def test_urllib3_tags(testdirectory):

    config_file = testdirectory.copy_file('test/data/urllib3_tags_giit.json')

    url = 'https://github.com/urllib3/urllib3.git'

    cmd = ['giit', 'clean', url,
           '--config_path', config_file]

    print(testdirectory.run(cmd))

    cmd = ['giit', 'docs', url,
           '--config_path', config_file, '-v']

    print(testdirectory.run(cmd))


def test_urllib3_workingtree(testdirectory):

    config_file = testdirectory.copy_file(
        'test/data/urllib3_source_branch_giit.json')

    url = 'https://github.com/urllib3/urllib3.git'

    cmd = ['git', 'clone', url]

    print(testdirectory.run(cmd))

    urllib_path = os.path.join(testdirectory.path(), 'urllib3')

    # Not working -> cmd = ['git', 'checkout', 'origin/bug/907']
    #cmd = ['git', 'checkout', 'bug/907']
    #cmd = ['git', 'checkout', 'v2']

    #print(testdirectory.run(cmd, cwd=urllib_path))

    cmd = ['giit', 'docs', urllib_path,
           '--config_path', config_file, '-v']

    print(testdirectory.run(cmd))

#     assert 0
