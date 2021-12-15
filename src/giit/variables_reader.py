#!/usr/bin/env python
# encoding: utf-8

import string
from collections import ChainMap as _ChainMap


class PundTemplate(string.Template):
    delimiter = "£"

    # Copied from string.Template.safe_substitute (tag 3.6)
    def safe_substitute_to_none(*args, **kws):
        if not args:
            raise TypeError(
                "descriptor 'safe_substitute' of 'Template' object " "needs an argument"
            )
        self, *args = args  # allow the "self" keyword be passed
        if len(args) > 1:
            raise TypeError("Too many positional arguments")
        if not args:
            mapping = kws
        elif kws:
            mapping = _ChainMap(kws, args[0])
        else:
            mapping = args[0]

        # Helper function for .sub()
        def convert(mo):
            named = mo.group("named") or mo.group("braced")
            if named is not None:
                try:
                    return str(mapping[named])
                except KeyError:
                    # This line is what's changed.
                    return ""
            if mo.group("escaped") is not None:
                return self.delimiter
            if mo.group("invalid") is not None:
                return mo.group()
            raise ValueError("Unrecognized named group in pattern", self.pattern)

        return self.pattern.sub(convert, self.template)


class VariablesReader(object):
    def __init__(self, variables, context):
        self.variables = variables
        self.context = context

    def _find_item(self, key):

        scope = self.context["scope"]

        if "checkout" in self.context:
            checkout = self.context["checkout"]

            # We first look in the variables dict using the following order:
            #
            # 1. scope:checkout:variable
            # 2. scope:variable
            # 3. variable
            explicit = ":".join([scope, checkout, key])

            if explicit in self.variables:
                return self.variables[explicit]

        partial = ":".join([scope, key])

        if partial in self.variables:
            return self.variables[partial]

        if key in self.variables:
            return self.variables[key]

        # Check if the variable is defined in the context
        if key in self.context:
            return self.context[key]

        raise KeyError("Not found {}".format(key))

    def __getitem__(self, key):

        variable = self._find_item(key=key)
        return string.Template(variable).substitute(self)

    def expand(self, element):
        result = PundTemplate(element).safe_substitute_to_none(self)
        result = string.Template(result).substitute(self)
        return result
