#!/usr/bin/env python
# encoding: utf-8

import os

import giit.fileinfo
import giit.filelist
import giit.copy_directory


def test_copydirectory(testdirectory):

    from_dir = testdirectory.mkdir("from")
    to_dir = testdirectory.mkdir("to")

    mkdir_layout(from_dir)

    directory = giit.copy_directory.CopyDirectory()

    excludes = [
        os.path.join(from_dir.path(), "c", "d", "*"),
        os.path.join(from_dir.path(), "a", "*"),
    ]

    directory.copy(
        from_path=from_dir.path(), to_path=to_dir.path(), exclude_patterns=excludes
    )

    # Get the files
    files = []

    for root, _, filenames in os.walk(to_dir.path()):
        for filename in filenames:
            files.append(os.path.join(root, filename))

    assert len(files) == 4

    file1 = os.path.join(to_dir.path(), "b", "b.txt")
    file2 = os.path.join(to_dir.path(), "b", "c", "b_c.txt")
    file3 = os.path.join(to_dir.path(), "c", "c.txt")
    file4 = os.path.join(to_dir.path(), "d", "d.txt")

    assert file1 in files
    assert file2 in files
    assert file3 in files
    assert file4 in files


def mkdir_layout(parent_dir):

    a_dir = parent_dir.mkdir("a")
    b_dir = parent_dir.mkdir("b")
    c_dir = parent_dir.mkdir("c")
    d_dir = parent_dir.mkdir("d")

    a_dir.write_text(filename="a.txt", data="a", encoding="utf-8")
    b_dir.write_text(filename="b.txt", data="b", encoding="utf-8")
    c_dir.write_text(filename="c.txt", data="c", encoding="utf-8")
    d_dir.write_text(filename="d.txt", data="d", encoding="utf-8")

    a_a_dir = a_dir.mkdir("a")
    a_b_dir = a_dir.mkdir("b")
    b_c_dir = b_dir.mkdir("c")
    c_d_dir = c_dir.mkdir("d")

    a_a_dir.write_text(filename="a_a.txt", data="a", encoding="utf-8")
    a_b_dir.write_text(filename="a_b.txt", data="b", encoding="utf-8")
    b_c_dir.write_text(filename="b_c.txt", data="c", encoding="utf-8")
    c_d_dir.write_text(filename="c_d.txt", data="d", encoding="utf-8")

    #     .
    # ├── a
    # │   ├── a
    # │   │   └── a_a.txt
    # │   ├── a.txt
    # │   └── b
    # │       └── a_b.txt
    # ├── b
    # │   ├── b.txt
    # │   └── c
    # │       └── b_c.txt
    # ├── c
    # │   ├── c.txt
    # │   └── d
    # │       └── c_d.txt
    # └── d
    #     └── d.txt

    # 8 directories, 8 files


def test_filelist(testdirectory):

    mkdir_layout(parent_dir=testdirectory)

    excludes = [
        os.path.join(testdirectory.path(), "c", "d", "*"),
        os.path.join(testdirectory.path(), "a", "*"),
    ]

    filelist = giit.filelist.FileMapper(
        local_path=testdirectory.path(),
        remote_path=os.path.join(os.path.sep, "var", "www"),
        exclude_patterns=excludes,
    )

    result = list(filelist)

    local_result = [f.local_file for f in result]
    remote_result = [f.remote_file for f in result]

    # There should be 4 files
    assert len(local_result) == 4
    assert len(remote_result) == 4

    file1 = os.path.join(testdirectory.path(), "b", "b.txt")
    file2 = os.path.join(testdirectory.path(), "b", "c", "b_c.txt")
    file3 = os.path.join(testdirectory.path(), "c", "c.txt")
    file4 = os.path.join(testdirectory.path(), "d", "d.txt")

    assert file1 in local_result
    assert file2 in local_result
    assert file3 in local_result
    assert file4 in local_result

    file1 = os.path.join(os.path.sep, "var", "www", "b", "b.txt")
    file2 = os.path.join(os.path.sep, "var", "www", "b", "c", "b_c.txt")
    file3 = os.path.join(os.path.sep, "var", "www", "c", "c.txt")
    file4 = os.path.join(os.path.sep, "var", "www", "d", "d.txt")

    assert file1 in remote_result
    assert file2 in remote_result
    assert file3 in remote_result
    assert file4 in remote_result


def test_filelist_excludes_config(testdirectory):
    # When the excludes come from the giit.json they will not have
    # been nicely joined by os.path.join. We have to work with them anyway

    mkdir_layout(parent_dir=testdirectory)

    excludes = [testdirectory.path() + "/c/d/*", testdirectory.path() + "/a/*"]

    filelist = giit.filelist.FileMapper(
        local_path=testdirectory.path(),
        remote_path=os.path.join(os.path.sep, "var", "www"),
        exclude_patterns=excludes,
    )

    result = list(filelist)

    local_result = [f.local_file for f in result]
    remote_result = [f.remote_file for f in result]

    # There should be 4 files
    assert len(local_result) == 4
    assert len(remote_result) == 4

    file1 = os.path.join(testdirectory.path(), "b", "b.txt")
    file2 = os.path.join(testdirectory.path(), "b", "c", "b_c.txt")
    file3 = os.path.join(testdirectory.path(), "c", "c.txt")
    file4 = os.path.join(testdirectory.path(), "d", "d.txt")

    assert file1 in local_result
    assert file2 in local_result
    assert file3 in local_result
    assert file4 in local_result

    file1 = os.path.join(os.path.sep, "var", "www", "b", "b.txt")
    file2 = os.path.join(os.path.sep, "var", "www", "b", "c", "b_c.txt")
    file3 = os.path.join(os.path.sep, "var", "www", "c", "c.txt")
    file4 = os.path.join(os.path.sep, "var", "www", "d", "d.txt")

    assert file1 in remote_result
    assert file2 in remote_result
    assert file3 in remote_result
    assert file4 in remote_result


def test_filelist(testdirectory):
    a_dir = testdirectory.mkdir("a")
    a_dir.write_text(filename="a.txt", data="a", encoding="utf-8")

    filelist = giit.filelist.FileList(
        from_path=testdirectory.path(), exclude_patterns=[]
    )

    result = list(filelist)

    assert len(result) == 1

    assert os.path.join("a", "a.txt") == result[0]
