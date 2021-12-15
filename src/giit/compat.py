#!/usr/bin/env python
# encoding: utf-8

import sys

IS_PY2 = sys.version_info[0] == 2

if IS_PY2:
    string_type = basestring  # noqa: F821
else:
    string_type = str
