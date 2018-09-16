import os
import mock
import logging

import giit.factory


def fake_git():
    """ Create an return a fake git object we can use for testing. """

    git = mock.Mock()
    git.version.return_value = (1, 2, 3)
    git.remote_origin_url.return_value = "git@github.com:steinwurf/giit.git"

    git.remote_branches.return_value = ["origin/add-prune",
                                        "origin/improvements-v2",
                                        "origin/initial-push",
                                        "origin/master", ]

    git.tags.return_value = ["1.0.0", "1.0.1", "1.0.2", "1.0.3",
                             "2.0.0", "2.1.0", "3.0.0"]

    return git


# def test_git_repository_clone(testdirectory, caplog):

#     caplog.set_level(logging.INFO)

#     giit_dir = testdirectory.mkdir('giit')
#     repo_dir = testdirectory.mkdir('repo')

#     factory = giit.factory.resolve_factory(
#         giit_path=giit_dir.path(), repository=repo_dir.path())

#     git = fake_git()

#     factory.provide_value(name='git', value=git, override=True)

#     git_repository = factory.build()

#     # The git repository has not yet been created so we should see a clone
#     assert not os.path.isdir(git_repository.giit_clone_path)

#     git_repository.clone()

#     git.clone.assert_called_once_with(
#         repository="git@github.com:steinwurf/giit.git",
#         directory=git_repository.giit_clone_path,
#         cwd=git_repository.clone_path)

#     git.fetch.assert_not_called()

#     # Reset call mocks

#     git.clone = mock.Mock()

#     os.makedirs(git_repository.giit_clone_path)

#     # The git repository now already exists so we should see a fetch
#     git_repository.clone()

#     git.clone.assert_not_called()
#     git.fetch.assert_called_once_with(
#         cwd=git_repository.giit_clone_path, all=True, prune=True)


# def test_git_checkout(testdirectory, caplog):

#     giit_dir = testdirectory.mkdir('giit')
#     repo_dir = testdirectory.mkdir('repo')

#     factory = giit.factory.resolve_factory(
#         giit_path=giit_dir.path(), repository=repo_dir.path())

#     git = fake_git()

#     factory.provide_value(name='git', value=git, override=True)

#     git_repository = factory.build()

#     git_repository.checkout_branch(checkout="improvements-v2")
#     git.reset.assert_called_once_with(
#         branch="origin/improvements-v2", hard=True, cwd=git_repository.giit_clone_path)

#     # Reset the mock
#     git.reset = mock.Mock()

#     git_repository.checkout_branch(checkout="origin/improvements-v2")
#     git.reset.assert_called_once_with(
#         branch="origin/improvements-v2", hard=True, cwd=git_repository.giit_clone_path)

def test_git_source_branch_url(testdirectory, caplog):
    """ Test we have no source branch when the repository is an URL """

    giit_dir = testdirectory.mkdir('giit')

    factory = giit.factory.resolve_factory(
        giit_path=giit_dir.path(), repository="https://github.com")

    git = fake_git()

    factory.provide_value(name='git', value=git, override=True)

    git_repository = factory.build()

    assert git_repository.source_branch() == None


def test_git_source_branch_no_current(testdirectory, caplog):
    """ Test that we have no source branch when the current branch is not
        in the list of remote branches
    """

    giit_dir = testdirectory.mkdir('giit')
    repo_dir = testdirectory.mkdir('repo')

    factory = giit.factory.resolve_factory(
        giit_path=giit_dir.path(), repository=repo_dir.path())

    git = fake_git()
    git.current_branch.return_value = "this-branch-does-not-exist"

    factory.provide_value(name='git', value=git, override=True)

    git_repository = factory.build()

    assert git_repository.source_branch() == None


def test_git_source_branch(testdirectory, caplog):
    """ Test that we get the source branch when the current branch is in the
        list of remote branches
    """

    giit_dir = testdirectory.mkdir('giit')
    repo_dir = testdirectory.mkdir('repo')

    factory = giit.factory.resolve_factory(
        giit_path=giit_dir.path(), repository=repo_dir.path())

    git = fake_git()
    git.current_branch.return_value = 'master'

    factory.provide_value(name='git', value=git, override=True)

    git_repository = factory.build()

    assert git_repository.source_branch() == "origin/master"
