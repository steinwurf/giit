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

    def clone(self, repository, directory, cwd):

        # os.makedirs(self.directory)
        shutil.copytree(src=self.directory, dst=directory)


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

        return factory


def mkdir_project(directory):
    project_dir = directory.copy_dir(directory='test/data/test_project')
    project_dir.run(['git', 'init'])
    project_dir.run(['git', 'add', '.'])
    project_dir.run(['git', '-c', 'user.name=John', '-c',
                     'user.email=doe@email.org', 'commit', '-m', 'oki'])
    project_dir.run(['git', 'tag', '3.1.2'])
    project_dir.run(['git', 'tag', '3.2.0'])
    project_dir.run(['git', 'tag', '3.3.0'])
    project_dir.run(['git', 'tag', '3.3.1'])

    return project_dir


def test_project(testdirectory, caplog):

    caplog.set_level(logging.DEBUG)

    project_dir = mkdir_project(testdirectory)
    build_dir = testdirectory.mkdir('build')
    giit_dir = testdirectory.mkdir('giit')

    build = FakeBuild(directory=project_dir.path(),
                      step='docs', repository=project_dir.path(),
                      build_path=build_dir.path(), data_path=giit_dir.path())

    build.run()

    build = FakeBuild(directory=project_dir.path(),
                      step='landing_page', repository=project_dir.path(),
                      build_path=build_dir.path(), data_path=giit_dir.path())

    build.run()

    build = FakeBuild(directory=project_dir.path(),
                      step='publish', repository=project_dir.path(),
                      build_path=build_dir.path(), data_path=giit_dir.path())

    build.run()

    build.sftp.connect.assert_called_once_with(
        hostname="files.build.com", username="giit")

    local_path = os.path.join(build_dir.path(), u'docs')
    remote_path = u'/tmp/www/docs/'
    exclude_patterns = [build_dir.path() + u'/workingtree/*']

    build.sftp.transfer.assert_called_once_with(
        local_path=local_path, remote_path=remote_path,
        exclude_patterns=exclude_patterns)

    # cmd = ['giit', 'docs', project_dir.path(),
    #        '--build_path', build_dir.path(),
    #        '--data_path', giit_dir.path(),
    #        '--source_branch', 'origin/add-docs']

    # testdirectory.run(cmd)

    # cmd = ['giit', 'landing_page', url,
    #        '--build_path', build_dir.path(),
    #        '--data_path', giit_dir.path(),
    #        '--json_config', config_file,
    #        '--source_branch', 'origin/add-docs']

    # testdirectory.run(cmd)
