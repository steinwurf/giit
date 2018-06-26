News for giit
=============

This file lists the major changes between versions. For a more detailed list of
every change, see the Git log.

Latest
------
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
