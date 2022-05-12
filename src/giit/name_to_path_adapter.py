#!/usr/bin/env python
# encoding: utf-8

import os


class NameToPathAdapter(object):
    def __init__(self, env, root_path):
        self.env = env
        self.root_path = root_path

    def create_environment(self, name):

        path = os.path.join(self.root_path, name)

        return self.env.create_environment(path=path)
