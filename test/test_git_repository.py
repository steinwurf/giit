#!/usr/bin/env python
# encoding: utf-8

import mock

import giit.factory


def fake_git():
    """Create an return a fake git object we can use for testing."""

    git = mock.Mock()
    git.version.return_value = (1, 2, 3)
    git.remote_origin_url.return_value = "git@github.com:steinwurf/giit.git"

    git.remote_branches.return_value = [
        "origin/add-prune",
        "origin/improvements-v2",
        "origin/initial-push",
        "origin/master",
    ]

    git.tags.return_value = [
        "1.0.0",
        "1.0.1",
        "1.0.2",
        "1.0.3",
        "2.0.0",
        "2.1.0",
        "3.0.0",
    ]

    return git


def test_git_source_branch_url(testdirectory, caplog):
    """Test we have no source branch when the repository is an URL"""

    giit_dir = testdirectory.mkdir("giit")

    factory = giit.factory.resolve_factory(
        giit_path=giit_dir.path(), repository="https://github.com"
    )

    git = fake_git()

    factory.provide_value(name="git", value=git, override=True)

    git_repository = factory.build()

    assert git_repository.source_branch() == None


def test_git_source_branch_no_current(testdirectory, caplog):
    """Test that we have no source branch when the current branch is not
    in the list of remote branches
    """

    giit_dir = testdirectory.mkdir("giit")
    repo_dir = testdirectory.mkdir("repo")

    factory = giit.factory.resolve_factory(
        giit_path=giit_dir.path(), repository=repo_dir.path()
    )

    git = fake_git()
    git.current_branch.return_value = "this-branch-does-not-exist"

    factory.provide_value(name="git", value=git, override=True)

    git_repository = factory.build()

    assert git_repository.source_branch() == None


def test_git_source_branch(testdirectory, caplog):
    """Test that we get the source branch when the current branch is in the
    list of remote branches
    """

    giit_dir = testdirectory.mkdir("giit")
    repo_dir = testdirectory.mkdir("repo")

    factory = giit.factory.resolve_factory(
        giit_path=giit_dir.path(), repository=repo_dir.path()
    )

    git = fake_git()
    git.current_branch.return_value = "master"

    factory.provide_value(name="git", value=git, override=True)

    git_repository = factory.build()

    assert git_repository.source_branch() == "origin/master"
