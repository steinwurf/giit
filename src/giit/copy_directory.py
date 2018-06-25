import os
import shutil

import giit.filelist


class CopyDirectory(object):

    def copy(self, from_path, to_path, exclude_patterns):

        filelist = giit.filelist.FileList(
            local_path=from_path,
            remote_path=to_path,
            exclude_patterns=exclude_patterns)

        self.copy_filelist(filelist=filelist)

    def copy_filelist(self, filelist):

        for fileinfo in filelist:
            self._copy_file(from_file=fileinfo.local_file,
                            to_file=fileinfo.remote_file)

    def _copy_file(self, from_file, to_file):

        to_path, _ = os.path.split(to_file)

        if not os.path.isdir(to_path):
            os.makedirs(to_path)

        shutil.copyfile(src=from_file, dst=to_file)
