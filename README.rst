============
Introduction
============

|PyPi| |Waf Python Tests| |Black| |Flake8| |Pip Install|

.. |PyPi| image:: https://badge.fury.io/py/giit.svg
    :target: https://badge.fury.io/py/giit

.. |Waf Python Tests| image:: https://github.com/steinwurf/giit/actions/workflows/waf.yml/badge.svg
   :target: https://github.com/steinwurf/giit/actions/workflows/waf.yml

.. |Flake8| image:: https://github.com/steinwurf/giit/actions/workflows/flake8.yml/badge.svg
    :target: https://github.com/steinwurf/giit/actions/workflows/flake8.yml

.. |Black| image:: https://github.com/steinwurf/giit/actions/workflows/black.yml/badge.svg
      :target: https://github.com/steinwurf/giit/actions/workflows/black.yml

.. |Pip Install| image:: https://github.com/steinwurf/giit/actions/workflows/pip.yml/badge.svg
      :target: https://github.com/steinwurf/giit/actions/workflows/pip.yml


The Git Iterator ``giit`` is a small tool for running commands on
branches and tags of a git repository.

It's original purpose was to allow Sphinx documentation to be easily
generated for all available tags of a bunch of different repositories. However,
should you find a different use for it - you should also be able to adapt it
to other scenarios.

.. contents:: Table of Contents:
   :local:

Quick Start
===========

To use ``giit`` you define a ``giit.json`` file which contains the steps
you want ``giit`` to be able to run. Note, the ``giit.json`` file can
live in the root of the repository.

Let's say we want to generate the Sphinx documentation for a specific
repository.

Installation
------------

``giit`` is a Python package so you can ``pip install`` it. If you just want to
try it out use a virtualenv or similar::

    $ virtualenv giit
    $ source giit/bin/activate

Now install the ``giit`` package::

    $ pip install giit


Example: C++ project documentation ``endian``
---------------------------------------------

``giit`` uses a ``giit.json`` file to describe the different steps::

    {
        "docs": {
            "branches.regex.filters": [
                "origin/master"
            ],
            "scripts": [
                "sphinx-build -b html . ${build_path}"
            ],
            "cwd": "${source_path}/docs",
            "requirements": "${source_path}/docs/requirements.txt"
        }
    }

Lets build the ``endian`` Sphinx documentation
(https://steinwurf-endian.netlify.app/latest/) by running ``giit``::

    giit docs https://github.com/steinwurf/endian.git --config_path ./giit.json

You should now seem something like::

    Lets go: docs
    Building into: /tmp/giit/data/build/endian-30a816
    Using git version: 2.34.1
    Using git repository: https://github.com/steinwurf/endian.git
    Running: git clone into /tmp/giit/data/clones/endian-30a816
    Using giit.json from path /tmp/giit_cwd/giit.json
    Tasks generated 1
    Running task [1/1]: scope 'branch' name 'master' checkout 'origin/master'
    Python: sphinx-build -b html . /tmp/giit/data/build/endian-30a816

If you visit ``/tmp/giit/data/build/endian-30a816`` with your web browser
you should be able to see the ``endian`` Sphinx documentation.

``giit.json`` location
======================

Since the content of the ``giit.json`` file fully determines the steps
taken by ``giit`` understanding how the ``giit.json`` file is found is
quite important.

The following outlines the rules:

1. Passing a path using ``--config_path`` or passing a branch
   using ``--config_branch``.

2. If no config path or branch is passed by the user and ``giit`` is
   invoked with an URL (like in the ``endian`` example).

   Example::

        giit docs https://github.com/endian/endian.git

   In this case ``giit`` will look at the root of the repository in
   ``origin/master`` branch for a ``giit.json``.

3. If no config path or branch is passed by the user and ``giit`` is
   invoked with a path::

       git docs ../path/to/repo

   In this case ``giit`` will try to find a ``giit.json`` at
   ``../path/to/repo/giit.json``.

Filters and tasks
=================

As we saw in the ``endian`` example a single task is generated for building
the ``origin/master`` branch. We can generate more tasks by setting up more
filters.

As a quick note it is also possible to not specify any filters. In that case
a single task for running the specified scripts will be gererated (with a
limited context - see below).

To specify the different filters here are the available options:

``branches.regex.filters``
--------------------------

This is a list of regular expressions that will be matched against the branch
name. If the regular expression matches a task will be generated.

For example (in ``giit.json``)::

        "branches.regex.filters": [
            "origin/master",
            "(\d+\.\d+.\d+)-LTS"
        ]


``branches.source_branch``
--------------------------

When invoking ``giit`` with a path to a repository e.g.:
``giit docs ../path/repo``. ``giit`` can be instructed to build the
remote tracking branch currently checkout out in ``../path/repo``.

This is useful in continuous integration systems.

For example (in ``giit.json``)::

        "branches.source_branch": true

``tags.regex.filters``
--------------------------

This is a list of regular expressions that will be matched against
the tag name. If the regular expression matches a task will be
generated.

For example (in ``giit.json``)::

        "tags.regex.filters": [
            "(\d+\.\d+.\d+)"
        ]

``tags.semver.filters``
------------------------

If a project uses sematic versioning the semver filter can be used.

For example (in ``giit.json``)::

        "tags.semver.filters": [
            ">=0.1.1", "<0.3.0"
        ]

We use https://python-semanticversion.readthedocs.io/en/latest/ you
can find more examples of requirement specifications there.

``tags.semver.relaxed``
-----------------------

If a project uses "kind-of" semver, such as ``1.20``, you can set the
semver filter in relaxed mode and still use the filters.

For example (in ``giit.json``)::

    "tags.semver.relaxed": true

``workingtree``
---------------

The ``workingtree`` filter is useful for quickly iterating on stuff.
It is similar to the ``source_branch`` filter. In that if ``giit`` is
invoked with a path, then that path will be the ``workingtree`` this
allows you to run ``giit`` without commit'ing pushing changes.

For example (in ``giit.json``)::

    "workingtree": true

No filter
---------

If you pass no filter e.g. ``tags``, ``branches`` or ``workingtree``, then


Context and variables
=====================

In the ``endian`` example you may have noticed what we used the
``${build_path}`` and ``${source_path}`` in the ``json`` configuration.

These denote variables that will be substituted when running the
tasks. The following variables are always available:

* ``build_path``: This points to the directory where the command
  is expected to output any artifacts produced by the command. It is
  up to the ``giit.json`` author to ensure this happens.

* ``source_path``: This is the path to where the current git
  repository is checked out.

* ``checkout``: This is the checkout of that was used.

* ``name``: This is a shorter version of checkout. E.g. for branches
  if the checkout is ``origin/master`` the name will be ``master``.
  Also if the ``checkout`` contains ``/`` that may result in
  unwanted sub-directories. In the ``name`` we replace ``/`` with ``_``.
  So if a branch is called ``origin/bug/543`` the name will be ``bug_543``.

* ``scope``: This can be one of three values. Either ``tag``,
  ``branch`` or ``workingtree``.

Note, only the ``${build_path}`` variable is available when running without
any filters.

Example
-------

Here we will use the ``${name}`` variable to output documentation
for the different tags to different folders::

    {
        "docs": {
            "branches.regex.filters": [
                "origin/master"
            ],
            "tags.semver.filters": [
                ">=1.20"
            ],
            "tags.semver.relaxed": true,
            "scripts": [
                "sphinx-build -b html . ${build_path}/${name}"
            ],
            "python_path": "${source_path}/src",
            "cwd": "${source_path}/docs",
            "requirements": "${source_path}/docs/requirements.txt"
        }
    }

User variables
--------------

In some cases we want to define our own variables according to some
simple rules.

This is done either using the ``variables`` attribute in the json or by using
the ``--variable [name] [value]`` command line argument.

User variables are define using the following syntax::

    scope:remote_branch:variable_name

Where ``scope`` and ``remote_branch`` are optional.

This can be used to customize e.g. the output of a command. Consider
the following example::

    {
        "docs": {
            ...
            "scripts": [
                "sphinx-build -b html . ${output_path}"
            ],
            "variables": {
                "branch:origin/master:output_path": "${build_path}/docs/latest",
                "branch:output_path": "${build_path}/sphinx/${name}",
                "tag:output_path": "${build_path}/docs/${name}",
                "workingtree:output_path": "${build_path}/workingtree/sphinx"
            }
        }
    }

When calling ``giit docs ...`` we use the user defined ``output_path``
variable.

Let walk though the different values ``output_path`` can take.

* If scope is ``branch`` and the branch is ``origin/master`` then
  ``output_path`` will be ``${build_path}/docs/latest``.
* For all other branches ``output_path`` will be
  ``${build_path}/sphinx/${name}`` where ``${name}`` will be the
  branch name.
* For the tags ``output_path`` will be ``${build_path}/docs/${name}``
  where name is the tag value e.g. ``1.0.0`` etc.
* Finally if we are in the ``workingtree`` scope the ``output_path``
  variable will be ``${build_path}/workingtree/sphinx``

Lets see how this could look (``build_path`` is ``/tmp/project``)::

    Tag 1.0.0 -----------> /tmp/project/docs/1.0.0
    Tag 2.0.0 -----------> /tmp/project/docs/2.0.0
    Tag 2.1.0 -----------> /tmp/project/docs/2.1.0
    Tag 3.0.0 -----------> /tmp/project/docs/3.0.0
    Branch master -------> /tmp/project/docs/latest
    Branch trying_new ---> /tmp/project/sphinx/trying_new
    Branch new_idea -----> /tmp/project/sphinx/new_idea
    Workingtree ---------> /tmp/project/workingtree


Optional Variables
==================
In some cases you may want to have optional variables. These can be specified
in a similar way as with non optional variables, the only difference is that you
need to use the ``£`` character instead of the ``$`` character.
If the variable doesn't exists it simply be removed.


Escaping Variable Replacements
==============================
If you want to use either ``$`` or ``£`` as characters in the giit configuration
file, you need to escape them.
This is done using ``$$`` or ``££`` respectively.


``giit`` command line arguments
===============================

The ``giit`` tool takes two mandatory arguments and a number of options::

    giit STEP REPOSITORY [--options]

Argument: ``STEP``
------------------

Selects the step in the ``giit.json`` file to run.

Argument: ``REPOSITORY``
------------------------

The URL or path to the git repository.

Option: ``--build_path``
------------------------

Sets the build path (i.e. where the output artifacts/data) will be generated/
built. This argument is available in the ``giit.json`` as the ``${build_path}``
variable.

Option: ``--giit_path``
-----------------------

This path is where the ``giit`` tool will store configurations, virtualenvs
clones created while running the tool. It also serves as a cache, to speed up
builds.

Option: ``--config_branch``
---------------------------

Specifies the a branch where the ``giit.json`` file will be take from.

Option: ``--config_path``
-------------------------

Sets the path to where the ``giit.json`` file.

Option ``--variable``
---------------------

Extends the variables set for each step.

Option ``-v`` / ``--verbose``
------------------------------

Allows the verbosity level of the tool to be increased
generating more debug information on the command line.


The ``clean`` step
==================

This step is always defined, in addition to the steps defined in
the ``giit.json`` file. The ``clean`` step just remove the
``build_path``.
