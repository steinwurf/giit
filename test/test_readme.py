def test_urllib3(testdirectory):

    config_file = testdirectory.copy_file('test/data/urllib3_giit.json')

    url = 'https://github.com/urllib3/urllib3.git'

    cmd = ['giit', 'clean', url,
           '--config_path', config_file]

    print(testdirectory.run(cmd))

    cmd = ['giit', 'docs', url,
           '--config_path', config_file, '-v']

    print(testdirectory.run(cmd))

    assert 0
