#!/usr/bin/env python
# encoding: utf-8

from giit.cache import Cache


def test_cache(testdirectory):

    testdir = testdirectory.mkdir("testdir")

    with Cache(cache_path=testdirectory.path(), unique_name="std-932") as c:
        c.update(sha1="32423", path=testdir.path())
