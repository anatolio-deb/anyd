import subprocess
from sockets_framework.cli import Structure
from multiprocessing import Process


def test_case01(tmp_path):
    p = subprocess.run([
        'python', './sockets_framework/cli.py', 'new', 'test_project', tmp_path
    ],
                       capture_output=True)
    p.check_returncode()
    s = Structure(path=tmp_path, arg_name='test_project')
    assert p.stdout.decode().lstrip().rstrip() == s.msg
    for path in s.paths:
        assert path.exists() is True
        if path in s.paths[:3]:
            assert path.read_text() == s.content[s.paths.index(path)]
    p = subprocess.run(['poetry', 'build'], capture_output=True)
    p.check_returncode()
    out = p.stdout.decode().split('\n')[-1]
    for o in out.split(' '):
        if '.whl' in o:
            p = subprocess.run(['pip', 'install', f'./dist/{o}'])
    p.check_returncode()
    p = Process(target=subprocess.run,
                args=(['python', s.paths[0], 'runserver']))
    p.start()
    assert p.is_alive() is True
    p.kill()
