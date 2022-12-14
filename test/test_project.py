#!/usr/bin/env python
# encoding: utf-8

import logging
import mock

import giit.build
import giit.git


class FakeGit(giit.git.Git):
    def __init__(self, fake_git_repository, fake_git_branch, **kwargs):
        """Fakes running git

        :param fake_git_repository: This is a path to a local fake git
            repository.
        :param fake_git_branch: The branch we should say we are on.
        """

        super(FakeGit, self).__init__(**kwargs)

        self.fake_git_repository = fake_git_repository
        self.fake_git_branch = fake_git_branch

    def remote_origin_url(self, cwd):
        return "https://github.com/fake/fake.git"

    def remote_branches(self, cwd):
        return [self.fake_git_branch]

    def clone(self, repository, directory, cwd):
        """Fake the clone command.

        :param repository: The clone URL in this case it is the
            https://github.com.../fake.git URL returned by
            the remote_origin_function

        :param directory: This is the directory where the repository
            should be cloned.
        """

        assert repository == "https://github.com/fake/fake.git"

        super(FakeGit, self).clone(
            repository=self.fake_git_repository,
            directory=directory,
            cwd=self.fake_git_repository,
        )

        # Emulate that we cloned from a URL
        super(FakeGit, self).checkout(branch="master", cwd=directory)
        # self.git.clone(
        #     repository=self.directory,
        #     directory=directory, cwd=self.directory)


def require_fake_git(factory):

    prompt = factory.require(name="prompt")
    git_binary = factory.require(name="git_binary")
    log = logging.getLogger(name="giit.git")
    fake_git_repository = factory.require(name="fake_git_repository")
    fake_git_branch = factory.require(name="fake_git_branch")

    return FakeGit(
        git_binary=git_binary,
        prompt=prompt,
        log=log,
        fake_git_branch=fake_git_branch,
        fake_git_repository=fake_git_repository,
    )


class FakeBuild(giit.build.Build):
    def __init__(self, fake_git_repository, fake_git_branch, **kwargs):

        super(FakeBuild, self).__init__(**kwargs)

        self.fake_git_branch = fake_git_branch
        self.fake_git_repository = fake_git_repository

    def resolve_factory(self):

        factory = super(FakeBuild, self).resolve_factory()

        factory.provide_value(
            name="fake_git_repository", value=self.fake_git_repository
        )

        factory.provide_value(name="fake_git_branch", value=self.fake_git_branch)

        factory.provide_function(name="git", function=require_fake_git, override=True)

        return factory

    def build_factory(self, build_type):

        factory = super(FakeBuild, self).build_factory(build_type)

        if build_type == "push":

            def push_config(factory):
                config = factory.require(name="config")
                config["git_url"] = self.fake_git_repository

                return giit.push_config.PushConfig.from_dict(config=config)

            factory.provide_function(
                name="command_config", function=push_config, override=True
            )

        return factory


def commit_file(directory, filename, content):
    directory.write_text(filename, content, encoding="utf-8")
    directory.run(["git", "add", "."])
    directory.run(
        [
            "git",
            "-c",
            "user.name=John",
            "-c",
            "user.email=doe@email.org",
            "commit",
            "-m",
            "oki",
        ]
    )


def mkdir_project(directory, giit_branch):

    project_dir = directory.mkdir("test_project")

    project_dir.run(["git", "init"])

    commit_file(directory=project_dir, filename="ok.txt", content="hello world")

    project_dir.copy_dir(directory="test/data/test_project/docs")
    project_dir.copy_dir(directory="test/data/test_project/landing_page")

    project_dir.run(["git", "add", "."])
    project_dir.run(
        [
            "git",
            "-c",
            "user.name=John",
            "-c",
            "user.email=doe@email.org",
            "commit",
            "-m",
            "oki",
        ]
    )
    project_dir.run(["git", "tag", "2.1.2"])
    project_dir.run(["git", "tag", "3.1.2"])
    project_dir.run(["git", "tag", "3.2.0"])
    project_dir.run(["git", "tag", "3.3.0"])
    project_dir.run(["git", "tag", "3.3.1"])

    # We add the giit.json on a branch but this should work
    # since we build with giit passing a path to the directory
    # where this branch is currently checkout out. It should
    # become the source branch
    if giit_branch:
        project_dir.run(["git", "checkout", "-b", giit_branch])
    project_dir.copy_file(filename="test/data/test_project/giit.json")
    project_dir.run(["git", "add", "."])
    project_dir.run(
        [
            "git",
            "-c",
            "user.name=John",
            "-c",
            "user.email=doe@email.org",
            "commit",
            "-m",
            "oki",
        ]
    )

    return project_dir


def _test_project(testdirectory, caplog):

    caplog.set_level(logging.DEBUG)

    giit_branch = "origin/add-giit"

    project_dir = mkdir_project(testdirectory, giit_branch=giit_branch)

    build_dir = testdirectory.mkdir("build")
    giit_dir = testdirectory.mkdir("giit")

    # Run the "docs" step

    build = FakeBuild(
        fake_git_repository=project_dir.path(),
        fake_git_branch=giit_branch,
        step="docs",
        repository=project_dir.path(),
        build_path=build_dir.path(),
        giit_path=giit_dir.path(),
    )

    build.run()

    # The project is on the "add-giit" branch

    assert build_dir.contains_file("sphinx/add-giit/docs.txt")
    # We have a tag filter that whould remove this tag
    assert not build_dir.contains_file("docs/2.1.2/docs.txt")
    assert build_dir.contains_file("docs/3.1.2/docs.txt")
    assert build_dir.contains_file("docs/3.2.0/docs.txt")
    assert build_dir.contains_file("docs/3.3.0/docs.txt")
    assert build_dir.contains_file("docs/3.3.1/docs.txt")
    assert build_dir.contains_file("workingtree/sphinx/docs.txt")

    # Run the "landing_page" step

    build = FakeBuild(
        fake_git_repository=project_dir.path(),
        fake_git_branch=giit_branch,
        step="landing_page",
        repository=project_dir.path(),
        build_path=build_dir.path(),
        giit_path=giit_dir.path(),
    )

    build.run()

    assert build_dir.contains_file("landing_page/add-giit/landing.txt")
    assert build_dir.contains_file("workingtree/landingpage/landing.txt")

    # Run the "gh_pages" step

    build = FakeBuild(
        fake_git_repository=project_dir.path(),
        fake_git_branch=giit_branch,
        step="gh_pages",
        repository=project_dir.path(),
        build_path=build_dir.path(),
        giit_path=giit_dir.path(),
    )

    build.run()

    # Switch to the brach where we have push'ed the files
    project_dir.run(["git", "checkout", "gh-pages"])

    # assert project_dir.contains_file('docs/latest/docs.txt')
    assert project_dir.contains_file("docs/3.1.2/docs.txt")
    assert project_dir.contains_file("docs/3.2.0/docs.txt")
    assert project_dir.contains_file("docs/3.3.0/docs.txt")
    assert project_dir.contains_file("docs/3.3.1/docs.txt")
    # assert project_dir.contains_file('docs/landing.txt')


def _test_project_master(testdirectory, caplog):

    # When building the master branch the output locations
    # of the different pieces change

    giit_branch = "origin/master"

    caplog.set_level(logging.DEBUG)

    project_dir = mkdir_project(testdirectory, giit_branch=giit_branch)

    build_dir = testdirectory.mkdir("build")
    giit_dir = testdirectory.mkdir("giit")

    # Run the "docs" step

    build = FakeBuild(
        fake_git_branch=giit_branch,
        fake_git_repository=project_dir.path(),
        step="docs",
        repository=project_dir.path(),
        build_path=build_dir.path(),
        giit_path=giit_dir.path(),
    )

    build.run()

    # The project is on the "add-giit" branch

    assert build_dir.contains_file("docs/latest/docs.txt")
    # We have a tag filter that would remove this tag
    assert not build_dir.contains_file("docs/2.1.2/docs.txt")
    assert build_dir.contains_file("docs/3.1.2/docs.txt")
    assert build_dir.contains_file("docs/3.2.0/docs.txt")
    assert build_dir.contains_file("docs/3.3.0/docs.txt")
    assert build_dir.contains_file("docs/3.3.1/docs.txt")
    assert build_dir.contains_file("workingtree/sphinx/docs.txt")

    # Run the "landing_page" step

    build = FakeBuild(
        fake_git_branch=giit_branch,
        fake_git_repository=project_dir.path(),
        step="landing_page",
        repository=project_dir.path(),
        build_path=build_dir.path(),
        giit_path=giit_dir.path(),
    )

    build.run()

    assert build_dir.contains_file("docs/landing.txt")
    assert build_dir.contains_file("workingtree/landingpage/landing.txt")

    build = FakeBuild(
        fake_git_branch=giit_branch,
        fake_git_repository=project_dir.path(),
        step="gh_pages",
        repository=project_dir.path(),
        build_path=build_dir.path(),
        giit_path=giit_dir.path(),
    )

    build.run()

    # Switch to the brach where we have push'ed the files
    project_dir.run(["git", "checkout", "gh-pages"])

    assert project_dir.contains_file("docs/latest/docs.txt")
    assert project_dir.contains_file("docs/3.1.2/docs.txt")
    assert project_dir.contains_file("docs/3.2.0/docs.txt")
    assert project_dir.contains_file("docs/3.3.0/docs.txt")
    assert project_dir.contains_file("docs/3.3.1/docs.txt")
    assert project_dir.contains_file("docs/landing.txt")
    assert project_dir.contains_file(".nojekyll")
