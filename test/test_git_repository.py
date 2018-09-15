import mock
import logging

import giit.factory


def test_git_repository(testdirectory, caplog):

    caplog.set_level(logging.INFO)

    giit_dir = testdirectory.mkdir('giit')
    repo_dir = testdirectory.mkdir('repo')
    repo_dir.run('git init')

    factory = giit.factory.resolve_factory(
        giit_path=giit_dir.path(), repository=repo_dir.path())

    git_repository = factory.build()

    git_repository.clone()

    assert 0
