import logging
import shutil
import os
import mock

import giit.build
import giit.git


class FakeGit(giit.git.Git):

    def __init__(self, directory, **kwargs):

        super(FakeGit, self).__init__(**kwargs)

        self.directory = directory

    def remote_origin_url(self, cwd):
        return "https://github.com/fake/fake.git"

    # def clone(self, repository, directory, cwd):

    #     # os.makedirs(self.directory)
    #     #shutil.copytree(src=self.directory, dst=directory)

    #     print("repository={} directory={}".format(self.directory,
    #                                               directory))

    #     super(FakeGit, self).clone(repository=self.directory,
    #                                directory=directory, cwd=self.directory)

    #     # Emulate that we cloned from a URL
    #     super(FakeGit, self).checkout(branch='master', cwd=directory)
    #     # self.git.clone(
    #     #     repository=self.directory,
    #     #     directory=directory, cwd=self.directory)


def require_fake_git(factory):

    prompt = factory.require(name='prompt')
    git_binary = factory.require(name='git_binary')
    fake_project_path = factory.require(name='fake_project_path')

    return FakeGit(git_binary=git_binary, prompt=prompt,
                   directory=fake_project_path)


class FakeBuild(giit.build.Build):

    def __init__(self, directory, **kwargs):

        super(FakeBuild, self).__init__(**kwargs)

        self.directory = directory

    def resolve_factory(self):

        factory = super(FakeBuild, self).resolve_factory()

        factory.provide_value(name='fake_project_path', value=self.directory)

        factory.provide_function(
            name='git', function=require_fake_git, override=True)

        return factory

    def build_factory(self, build_type):

        factory = super(FakeBuild, self).build_factory(build_type)

        if build_type == 'sftp':
            self.sftp = mock.Mock()
            factory.provide_value(name='sftp', value=self.sftp, override=True)

        if build_type == 'push':

            def push_config(factory):
                config = factory.require(name='config')
                config['git_url'] = self.directory

                return giit.push_config.PushConfig.from_dict(
                    config=config)

            factory.provide_function(
                name='command_config', function=push_config,
                override=True)

        return factory


def commit_file(directory, filename, content):
    directory.write_text(filename, content, encoding='utf-8')
    directory.run(['git', 'add', '.'])
    directory.run(['git', '-c', 'user.name=John', '-c',
                   'user.email=doe@email.org', 'commit', '-m', 'oki'])


def mkdir_project(directory, giit_branch):

    project_dir = directory.mkdir('test_project')

    project_dir.run(['git', 'init'])

    commit_file(directory=project_dir, filename='ok.txt',
                content=u'hello world')

    project_dir.copy_dir(directory='test/data/test_project/docs')
    project_dir.copy_dir(directory='test/data/test_project/landing_page')

    project_dir.run(['git', 'add', '.'])
    project_dir.run(['git', '-c', 'user.name=John', '-c',
                     'user.email=doe@email.org', 'commit', '-m', 'oki'])
    project_dir.run(['git', 'tag', '2.1.2'])
    project_dir.run(['git', 'tag', '3.1.2'])
    project_dir.run(['git', 'tag', '3.2.0'])
    project_dir.run(['git', 'tag', '3.3.0'])
    project_dir.run(['git', 'tag', '3.3.1'])

    # We add the giit.json on a branch but this should work
    # since we build with giit passing a path to the directory
    # where this branch is currently checkout out. It should
    # become the source branch
    if giit_branch:
        project_dir.run(['git', 'checkout', '-b', giit_branch])
    project_dir.copy_file(filename='test/data/test_project/giit.json')
    project_dir.run(['git', 'add', '.'])
    project_dir.run(['git', '-c', 'user.name=John', '-c',
                     'user.email=doe@email.org', 'commit', '-m', 'oki'])

    return project_dir


def test_project(testdirectory, caplog):

    caplog.set_level(logging.DEBUG)

    project_dir = mkdir_project(testdirectory, giit_branch='add-giit')
    build_dir = testdirectory.mkdir('build')
    giit_dir = testdirectory.mkdir('giit')

    # Run the "docs" step

    build = FakeBuild(
        directory=project_dir.path(),
        step='docs', repository=project_dir.path(),
        build_path=build_dir.path(), data_path=giit_dir.path())

    build.run()

    # The project is on the "add-giit" branch

    assert build_dir.contains_file('sphinx/add-giit/docs.txt')
    # We have a tag filter that whould remove this tag
    assert not build_dir.contains_file('docs/2.1.2/docs.txt')
    assert build_dir.contains_file('docs/3.1.2/docs.txt')
    assert build_dir.contains_file('docs/3.2.0/docs.txt')
    assert build_dir.contains_file('docs/3.3.0/docs.txt')
    assert build_dir.contains_file('docs/3.3.1/docs.txt')
    assert build_dir.contains_file('workingtree/sphinx/docs.txt')

    # Run the "landing_page" step

    build = FakeBuild(
        directory=project_dir.path(),
        step='landing_page', repository=project_dir.path(),
        build_path=build_dir.path(), data_path=giit_dir.path())

    build.run()

    assert build_dir.contains_file('landing_page/add-giit/landing.txt')
    assert build_dir.contains_file('workingtree/landingpage/landing.txt')

    # Run the "publish" step

    build = FakeBuild(
        directory=project_dir.path(),
        step='publish', repository=project_dir.path(),
        build_path=build_dir.path(), data_path=giit_dir.path())

    build.run()

    build.sftp.connect.assert_called_once_with(
        hostname="files.build.com", username="giit")

    # We don't use os.path.join here since this is not what the
    # variable substitution would do when taking the value from
    # giit.json
    #
    # Note, to future testing geeks. It would probably be better
    # to mock out at the paramiko.SSHClient() point instead.
    # Since, then we would include a bit more of our own functionality
    # in this integration test
    local_path = build_dir.path() + u'/docs'
    remote_path = u'/tmp/www/docs/'
    exclude_patterns = [build_dir.path() + u'/workingtree/*']

    build.sftp.transfer.assert_called_once_with(
        local_path=local_path, remote_path=remote_path,
        exclude_patterns=exclude_patterns)

    # Run the "gh_pages" step

    build = FakeBuild(directory=project_dir.path(),
                      step='gh_pages', repository=project_dir.path(),
                      build_path=build_dir.path(), data_path=giit_dir.path())

    build.run()

    # Switch to the brach where we have push'ed the files
    project_dir.run(['git', 'checkout', 'gh-pages'])

    #assert project_dir.contains_file('docs/latest/docs.txt')
    assert project_dir.contains_file('docs/3.1.2/docs.txt')
    assert project_dir.contains_file('docs/3.2.0/docs.txt')
    assert project_dir.contains_file('docs/3.3.0/docs.txt')
    assert project_dir.contains_file('docs/3.3.1/docs.txt')
    #assert project_dir.contains_file('docs/landing.txt')


def test_project_master(testdirectory, caplog):
    # When building the master branch the output locations
    # of the different pieces change

    caplog.set_level(logging.DEBUG)

    project_dir = mkdir_project(testdirectory, giit_branch=None)
    build_dir = testdirectory.mkdir('build')
    giit_dir = testdirectory.mkdir('giit')

    # Run the "docs" step

    build = FakeBuild(source_branch='master',
                      directory=project_dir.path(),
                      step='docs', repository=project_dir.path(),
                      build_path=build_dir.path(), data_path=giit_dir.path())

    build.run()

    # The project is on the "add-giit" branch

    assert build_dir.contains_file('docs/latest/docs.txt')
    # We have a tag filter that would remove this tag
    assert not build_dir.contains_file('docs/2.1.2/docs.txt')
    assert build_dir.contains_file('docs/3.1.2/docs.txt')
    assert build_dir.contains_file('docs/3.2.0/docs.txt')
    assert build_dir.contains_file('docs/3.3.0/docs.txt')
    assert build_dir.contains_file('docs/3.3.1/docs.txt')
    assert build_dir.contains_file('workingtree/sphinx/docs.txt')

    # Run the "landing_page" step

    build = FakeBuild(source_branch='master',
                      directory=project_dir.path(),
                      step='landing_page', repository=project_dir.path(),
                      build_path=build_dir.path(), data_path=giit_dir.path())

    build.run()

    assert build_dir.contains_file('docs/landing.txt')
    assert build_dir.contains_file('workingtree/landingpage/landing.txt')

    build = FakeBuild(directory=project_dir.path(),
                      step='gh_pages', repository=project_dir.path(),
                      build_path=build_dir.path(), data_path=giit_dir.path())

    build.run()

    # Switch to the brach where we have push'ed the files
    project_dir.run(['git', 'checkout', 'gh-pages'])

    assert project_dir.contains_file('docs/latest/docs.txt')
    assert project_dir.contains_file('docs/3.1.2/docs.txt')
    assert project_dir.contains_file('docs/3.2.0/docs.txt')
    assert project_dir.contains_file('docs/3.3.0/docs.txt')
    assert project_dir.contains_file('docs/3.3.1/docs.txt')
    assert project_dir.contains_file('docs/landing.txt')
    assert project_dir.contains_file('.nojekyll')
