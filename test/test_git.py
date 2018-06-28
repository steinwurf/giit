import mock

import giit.git
import giit.prompt


def test_git(testdirectory):
    git = giit.git.Git(
        git_binary='git', prompt=giit.prompt.Prompt())

    print(git.version(cwd=testdirectory.path()))
