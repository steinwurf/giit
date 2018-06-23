def test_build(testdirectory):

    build_dir = testdirectory.mkdir('build')
    giit_dir = testdirectory.mkdir('giit')
    config_file = testdirectory.copy_file('test/data/giit.json')

    url = 'git@github.com:steinwurf/stub.git'

    cmd = ['giit', 'sphinx', url,
           '--json_config', config_file,
           '--source_branch', 'origin/add-docs']

    testdirectory.run(cmd)

    cmd = ['giit', 'landing_page', url,
           '--json_config', config_file,
           '--source_branch', 'origin/add-docs']

    testdirectory.run(cmd)

    cmd = ['giit', 'publish', url,
           '--json_config', config_file]

    testdirectory.run(cmd)

    cmd = ['giit', 'gh_pages', url,
           '--json_config', config_file]

    testdirectory.run(cmd)
