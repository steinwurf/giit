News for giit
=============

This file lists the major changes between versions. For a more detailed list of
every change, see the Git log.

Latest
------
* tbd

2.0.0
-----
* Major: Remove source_branch scope for a more general branch scope
* Minor: Add a branches attribute to allow certain branches to
  always run.
* Patch: Add a --clean_build option to remove the build directory
  before building.

1.0.3
-----
* Patch: Add support for writing a .nojekyll file in the push step.

1.0.2
-----
* Patch: Simplify exception handling logic in PythonCommand.
* Patch: If building from a workingtree (local directory), then
  read from config from there.

1.0.1
-----
* Patch: Fix the handling of the source branch. The behavior now is
  to ensure we switch to the source branch before we read the config
  file.

1.0.0
-----
* Initial release
