def test_urllib3(testdirectory):

    config_file = testdirectory.copy_file('test/data/urllib3_giit.json')

    url = 'https://github.com/urllib3/urllib3.git'

    cmd = ['giit', 'docs', url,
           '--json_config', config_file]

    print(testdirectory.run(cmd))
