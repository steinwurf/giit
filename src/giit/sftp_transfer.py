import os
import paramiko

import giit.filelist


class SFTPTransfer(object):

    def __init__(self, ssh):
        """ Create a new instance

        :param ssh: A paramiko.SSHClient object
        """

        self.ssh = ssh

    def connect(self, username, hostname):
        """ Connect to the remote server.

        :param username: The username as a string
        :param hostname: The hostname as a string
        """

        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname=hostname,
                         username=username)

    def transfer(self, local_path, remote_path, exclude_patterns):
        """ Start a transfer.

        :param local_path: A local directory to be transferred.
        :param remote_path: The remote location where the files should be
            copied.
        :param exclude_patterns: A list of path patterns which should not
            be copied.
        """

        filelist = giit.filelist.FileList(
            local_path=local_path,
            remote_path=remote_path,
            exclude_patterns=exclude_patterns)

        self.transfer_filelist(filelist=filelist)

    def transfer_filelist(self, filelist):
        """ Start a transfer.

        :param filelist: A FileList object.
        """

        with self.ssh.open_sftp() as sftp:

            for fileinfo in filelist:
                self._transfer_file(sftp=sftp,
                                    local_file=fileinfo.local_file,
                                    remote_file=fileinfo.remote_file)

    def _transfer_file(self, sftp, local_file, remote_file):
        """ Transfer a file.

        :param sftp: The SFTP client ot use.
        :param local_file: The path to the local file
        :param remote_file: The path to the remote file.
        """

        remote_path, remote_file = self._path_split(remote_file=remote_file)

        for path in remote_path:

            try:
                # http://docs.paramiko.org/en/2.4/api/sftp.html
                sftp.chdir(path=path)
            except IOError:
                sftp.mkdir(path=path)
                sftp.chdir(path=path)

        sftp.put(localpath=local_file, remotepath=remote_file)

    @staticmethod
    def _path_split(remote_file):
        """ Split a path into a list of directories and a filename.

        : param remote_file: An absolute remote file path as a string.
        : return: 2-tuple where the first element is a list of directories and
            the second element is the filename.
        """

        assert remote_file.startswith('/'), "must be absolute %s" % remote_file

        path = remote_file
        path_split = []

        while True:
            path, leaf = os.path.split(path)
            if leaf:
                # Adds one element, at the beginning of the list
                path_split = [leaf] + path_split
            else:
                path_split = [path] + path_split
                break

        return path_split[:-1], path_split[-1]
