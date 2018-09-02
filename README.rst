Introduction
============

.. image:: https://ci.appveyor.com/api/projects/status/mld0fa79ox939fex/branch/master?svg=true
    :target: https://ci.appveyor.com/project/SteinwurfApS/giit

.. image:: https://travis-ci.org/steinwurf/giit.svg?branch=master
    :target: https://travis-ci.org/steinwurf/giit

The Git Iterator ``giit`` is a small tool for running commands on
branches and tags of a git repository.

It's original purpose was to allow Sphinx documentation to be easily
generated for all available tags of a bunch of different repositories. However,
should you find a different use for it - you should also be able to adapt it
to other scenarios.

Quick Start
===========

To use ``giit`` you define a ``giit.json`` file which contains the steps
you want ``giit`` to be able to run. Note, the ``giit.json`` file can
live in the root of the repository.

Let's say we want to generate the Sphinx documentation for a specific
repository.

Example: ``urllib3``
--------------------

``giit`` uses a ``giit.json`` file to describe the different steps::

    {
        "docs": {
            "type": "python",
            "scripts": [
                "sphinx-build -b html . ${build_path}"
            ],
            "python_path": "${source_path}/src",
            "cwd": "${source_path}/docs",
            "requirements": "${source_path}/docs/requirements.txt"
        }
    }

Lets build the ``urllib3`` Sphinx documentation
(https://urllib3.readthedocs.io/en/latest/) by running ``giit``::

    giit docs https://github.com/urllib3/urllib3.git --json_config ./giit.json

You should now seem something like::

    Lets go!
    Using git repository: https://github.com/urllib3/urllib3.git
    Running: git clone in /tmp/giit/data/clones/urllib3-b1919a
    Building into: /tmp/giit/build/urllib3-b1919a
    Python: sphinx-build -b html . /tmp/giit/build/urllib3-b1919a

If you visit ``/tmp/giit/build/urllib3-b1919a`` with your web browser
you should be able to see the ``urllib3`` Sphinx documentation.

Command-line arguments
----------------------

Whn invoking ``giit`` there are two mandatory arguments::

    giit STEP REPOSITORY

* ``STEP`` selects the step defined in the ``giit.json`` to execute.
* ``REPOSITORY`` is a repository URL or a path on the file system to a
   repository

In addition to the two mandatory arguments there are a number of optional
options that can customize the ``giit``'s behavior.

* ``--build_path`` this option controls where in the file system the should
  be produced. This option is passed to the ``giit`` steps such that Python
  commands etc. can respect it (notice how it was used to control the build
  output of the ``urllib3`` example).

* ``--giit_path`` this option controls where ``giit`` will store all it's
  state. Clones of repositories, meta data etc.

* ``--json_config`` this option allows the path to the ``giit.json`` file to
  be specified.

* ``-v`` / ``--verbose`` allows the verbosity level of the tool to be increased
  generating more debug information on the command line.

``giit.json``
=============

The ``giit.json`` is where the different steps are defined. Let's
walk though the different attributes which can be used.

Location
--------

Since the content of the ``giit.json`` file fully determines the steps taken
by ``giit`` understanding how the ``giit.json`` file is found is quite
important.

The following outlines the rules:

1. Passing a path using ``--json_config``.
2. If using a path to the repository when calling ``giit`` e.g.::

       git docs ../path/to/repo

   We will try to find the ``giit.json`` in ``../path/to/repo/giit.json``

3. In


Defining steps
--------------

The different steps define the behavior we can invoke, in
the following ``giit.json`` we define three steps::

    {
        "docs": {
            ...
        },
        "landing_page": {
            ...
        },
        "publish": {
            ...
        }
    }

Step type
----------

Each step will have a type. The type defines the behavior and
attributes available in the step.

Currently supported are ``python``, ``sftp`` and ``push``.

Step scope
----------

If enabled a step will run in a number of different "scopes":

* ``workingtree``:
  * If a user passes a path to the ``giit`` command e.g.
    ``giit docs ../dev/project/docs`` then the ``workingtree`` scope will
    be enabled.
  * The step will run once with the variable ``source_path`` set to
    local path.
  * This allows a user to run steps without having to first
    push to the remote git repository.
* ``branch``:
  * The source branch scope will default to ``master``.
  * If a user passes a path to ``giit`` the source branch will be whatever
    branch the local repository is on.
  * The source branch can also be selected by the user when passing
    a git URL to the ``giit`` command.
* ``tag``:
  * A default ``giit`` will run the step for each tag on the repository
    in this scope.

As a default all steps default to only run in the ``branch``
scope. This can be change with the ``scope`` step attribute.

Step built-in variables
-----------------------

When defining a step ``giit`` makes a number of variables available.

As an example in the following we can customize the output location
of ``sphinx-build`` like this::

    {
        "docs": {
            "type": "python",
            "scripts": [
                "sphinx-build -b html . ${build_path}"
            ]
            ...
        }
        ...
    }

In the above ``${build_path}`` will be substituted for the default
``giit`` build path or a user specified one.

The following built-in variables are available:

* ``build_path``: The path where the produced output should go.
* ``source_path``: The path to the repository
* ``name``: Identifier depending on the scope e.g. branch name or
   tag name.
* ``scope``: The scope we are in.

Step user variables
--------------------

The user can define variables using the ``variables`` attribute.
User variables are define using the following syntax::

    scope:remote_branch:variable_name

Where ``scope`` and ``remote_branch`` are optional.

This can be used to customize e.g. the ``build_path``. Consider
the following example::

    {
        "sphinx": {
            "type": "python",
            "scripts": [
                "sphinx-build -b html . ${output_path}"
            ],
            ...
            "variables": {
                "branch:origin/master:output_path": "${build_path}/docs/latest",
                "branch:output_path": "${build_path}/sphinx/${name}",
                "tag:output_path": "${build_path}/docs/${name}",
                "workingtree:output_path": "${build_path}/workingtree/sphinx"
            }
        }
    }

When calling ``sphinx-build`` we use the user defined ``output_path``
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
    Tag 1.0.0 -----------> /tmp/project/docs/2.0.0
    Tag 1.0.0 -----------> /tmp/project/docs/2.1.0
    Tag 1.0.0 -----------> /tmp/project/docs/3.0.0
    Branch master -------> /tmp/project/docs/latest
    Branch trying_new ---> /tmp/project/sphinx/trying_new
    Branch new_idea -----> /tmp/project/sphinx/new_idea
    Workingtree ---------> /tmp/project/workingtree

``clean`` step
..............

The ``clean`` step just remove the ``build_path``.

``python`` step
...............

The ``python`` step supports the following attributes:

* Mandatory ``scripts``: A list of commands to execute
* Optional ``cwd``: The path where commands will be executed
* Optional ``requirements``: Path to a ``pip`` requirements file containing
  dependencies to be installed. If specified a virtualenv will
  created.
* Optional ``pip_packages``: A list of ``pip`` packages to install. If
  specified a virtualenv will created.
* Optional ``scope``: A list of ``scope`` names for which the step will run.
* Optional ``allow_failure``: A boolean indicating whether we
  allow the scripts to fail.
* Optional ``python_path``: Setting the python path before running the
  scripts.

``giit`` command line arguments
===============================

The ``giit`` tool takes two mandatory arguments and a number of options::

    giit STEP REPOSITORY [--options]

Argument: ``STEP``
-----------------

Selects the step in the ``giit.json`` file to run.

Argument: ``REPOSITORY``
------------------------

The URL or path to the git repository.

Option: ``--build_path``
-----------------------

Sets the build path (i.e. where the output artifacts/data) will be generated/
built. This argument is available in the ``giit.json`` as the ``${build_path}``
variable.

Option: ``--data_path``
-----------------------

This path is where the ``giit`` tool will store configurations, virtualenvs
clones created while running the tool. It also serves as a cache, to speed up
builds.

Option: ``--remote_branch``
---------------------------

Specifies the source branch to use. The default is ``origin/master``, however if you
need to build a different branch this is one way of doing it.

Option: ``--json_config``
-------------------------

Sets the path to where the ``giit.json`` file.




Factories and Dependency Injection
----------------------------------

Testability is a key feature of any modern software library and one of the key
techniques for writing testable code is dependency injection (DI).

In Python DI is relatively simple to implement due to the dynamic nature of the
language.

Git branches
------------


