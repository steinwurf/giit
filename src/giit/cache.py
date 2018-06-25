import json
import os
import shutil
import hashlib
import sys

from . import run_error


class Cache(object):

    def __init__(self, cache_path, unique_name):
        """ Open or create a new cache

        :param cache_path: The path to the cache directory as a string. The
            cache directory is where the cache files (json) which contains
            information about the different builds will be stored.
        :param unique_name: The unique name of the repository as a string
        """

        # Read the "cache" from json
        filename = 'cache-' + unique_name + '.json'
        cache_path = os.path.abspath(os.path.expanduser(cache_path))

        self.filepath = os.path.join(cache_path, filename)

        # Dict which will hold the cached values
        self.cache = None

    def __enter__(self):

        if os.path.isfile(self.filepath):

            with open(self.filepath, 'r') as json_file:
                self.cache = json.load(json_file)

        else:
            self.cache = {}

        return self

    def __exit__(self, *args):

        with open(self.filepath, 'w') as json_file:

            json.dump(self.cache, json_file, indent=2, sort_keys=True,
                      separators=(',', ': '))

    def match(self, sha1):

        if sha1 in self.cache:
            path = self.cache[sha1]

            return os.path.isdir(path)

        return False

    def update(self, sha1, path):

        assert os.path.isdir(path)

        self.cache[sha1] = path


#
