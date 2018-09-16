import mock
import logging

import giit.factory


def _test_git_repository(testdirectory, caplog):

    caplog.set_level(logging.INFO)

    giit_dir = testdirectory.mkdir('giit')
    repo_dir = testdirectory.mkdir('repo')
    repo_dir.run('git init')

    factory = giit.factory.resolve_factory(
        giit_path=giit_dir.path(), repository=repo_dir.path())

    git = mock.Mock()
    git.version.return_value = (1, 2, 3)
    git.remote_origin_url.return_value = "git@github.com:steinwurf/giit.git"

    factory.provide_value(name='git', value=git, override=True)

    git_repository = factory.build()

    git_repository.clone()

    # Add some tests
    # assert 0


def test_git_checkout(testdirectory, caplog):

    giit_dir = testdirectory.mkdir('giit')
    repo_dir = testdirectory.mkdir('repo')

    remotes = ["origin/add-prune",
               "origin/fix-checkout-in-variables",
               "origin/improvements-v2",
               "origin/initial-push",
               "origin/master",
               "origin/modify-scopes"]

    factory = giit.factory.resolve_factory(
        giit_path=giit_dir.path(), repository=repo_dir.path())

    git = mock.Mock()
    git.version.remote_branches = remotes

    factory.provide_value(name='git', value=git, override=True)

    git_repository = factory.build()

    git_repository.checkout_branch(checkout="master")
