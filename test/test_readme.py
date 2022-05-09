#!/usr/bin/env python
# encoding: utf-8


def test_endian_master(testdirectory):

    config_file = testdirectory.copy_file("test/data/endian_master_giit.json")

    url = "https://github.com/steinwurf/endian.git"

    cmd = ["giit", "clean", url, "--config_path", config_file]

    print(testdirectory.run(cmd))

    cmd = ["giit", "docs", url, "--config_path", config_file, "-v"]

    print(testdirectory.run(cmd))


def test_endian_tags(testdirectory):

    config_file = testdirectory.copy_file("test/data/endian_tags_giit.json")

    url = "https://github.com/steinwurf/endian.git"

    cmd = ["giit", "clean", url, "--config_path", config_file]

    print(testdirectory.run(cmd))

    cmd = ["giit", "docs", url, "--config_path", config_file, "-v"]

    print(testdirectory.run(cmd))
