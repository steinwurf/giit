
import giit.prompt


def test_run(testdirectory):

    prompt = giit.prompt.Prompt()
    prompt.run('python --version', cwd=testdirectory.path())
