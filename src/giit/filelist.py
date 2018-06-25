import os
import fnmatch

import giit.fileinfo


class FileList(object):

    def __init__(self, local_path, remote_path, exclude_patterns=[]):
        self.local_path = local_path
        self.remote_path = remote_path
        self.exclude_patterns = exclude_patterns

    def __iter__(self):
        for root, dirs, files in os.walk(self.local_path, topdown=True):

            for f in files:
                local_file = os.path.join(root, f)

                if not self._exclude(filename=local_file):

                    relative_path = os.path.relpath(
                        local_file, self.local_path)

                    remote_file = os.path.join(self.remote_path, relative_path)

                    yield giit.fileinfo.FileInfo(
                        local_file=local_file,
                        remote_file=remote_file)

    def _exclude(self, filename):

        for e in self.exclude_patterns:

            if fnmatch.fnmatch(filename, e):
                return True

        return False
