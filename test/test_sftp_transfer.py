#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import fnmatch
import mock
import shutil

import giit.fileinfo
import giit.filelist
import giit.sftp_transfer
import giit.copy_directory


def test_filetransfer(testdirectory):

    a_dir = testdirectory.mkdir('a')

    a_file = a_dir.write_text(filename='helloworld.txt',
                              data=u'hello', encoding='utf-8')
    b_dir = a_dir.mkdir('b')

    b_file = b_dir.write_text(filename='helloworld.txt',
                              data=u'hello', encoding='utf-8')

    ssh = mock.Mock()
    sftp = mock.Mock()
    ctx = mock.Mock()
    ctx.__enter__ = mock.Mock(side_effect=lambda: sftp)
    ctx.__exit__ = mock.Mock()

    ssh.open_sftp.side_effect = lambda: ctx

    filetransfer = giit.sftp_transfer.SFTPTransfer(ssh=ssh)
    filetransfer.connect(hostname='buildbot.steinwurf.dk', username='buildbot')

    ssh.connect.assert_called_once_with(
        hostname='buildbot.steinwurf.dk', username='buildbot')

    filetransfer.transfer(local_path=testdirectory.path(),
                          remote_path='/tmp',
                          exclude_patterns=[])

    sftp.chdir.assert_has_calls([
        mock.call(path='/'),
        mock.call(path='tmp'),
        mock.call(path='a'),
        mock.call(path='/'),
        mock.call(path='tmp'),
        mock.call(path='a'),
        mock.call(path='b')
    ])

    sftp.put.assert_has_calls([
        mock.call(localpath=a_file, remotepath="helloworld.txt"),
        mock.call(localpath=b_file, remotepath="helloworld.txt")
    ])


def test_filetransfer_path_split():

    path, filename = giit.sftp_transfer.SFTPTransfer._path_split(
        remote_file='/www/var/file.txt')

    assert path == ['/', 'www', 'var']
    assert filename == 'file.txt'
