News for giit
=============

This file lists the major changes between versions. For a more detailed list of
every change, see the Git log.

Latest
------
* tbd

7.2.1
-----
* Patch: Added missing import.

7.2.0
-----
* Minor: Added support for using virtualenv as fallback for venv.

7.1.1
-----
* Patch: Fix task_filter incorrectly skipping all tasks.

7.1.0
-----
* Minor: Added task_filter argument for filtering tasks on the commandline.

7.0.0
-----
* Major: Added support for python 3.10.x, this required a switch from
  virtualenv to venv for virtual enviroment management.

6.1.0
-----
* Minor: Support other default branch names than master.
* Minor: Change the order of tasks so that working directory is always
  built first. Then branches, followed by tags in ascending order.
  Building the working directory first allows the giit run to fail quicker since
  most issues are in the working directory.
* Patch: Fix some spelling errors.

6.0.2
-----
* Patch: Really fix readme.

6.0.1
-----
* Patch: Fix readme.

6.0.0
-----
* Major: Remove SFTP feature.
* Major: Introduced optional variables. These work in a similar way as normal
  variables, execpt they will be removed if they doesn't exists and you need to
  use `£` instead of `$` to use them.
* Minor: Added support for extra variables provided as command line arguments.

5.0.0
-----
* Major: Make giit work for repositories without remotes

4.0.0
-----
* Major: Drop Python 3.4 support.
* Major: Added support for running scripts without a Git filter.
* Major: Rewrote steps and filters implementation.
* Patch: Fix using checkout in variable reader.
* Patch: Improve logging output.
* Minor: Added verbose flag to produce more logging on stdout
* Patch: Using absolute path for build_path, giit_path and config_path


3.0.0
-----
* Minor: Added a "clean" step which removes the build folder.
* Major: Support only building remote branches. I.e. you have to
  push your local changes to a remote before being able to build.
  You can always see your local changes with the workingtree build -
  if needed.

2.1.0
-----
* Minor: Better support build building local branches (which does
  not yet exist on the remote).
* Minor: Clone from path if available.
* Minor: Support publish_url for push type steps. This will print
  all index.html files pushed.

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
