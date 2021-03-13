import subprocess
from sockets_framework.cli import Structure
from multiprocessing import Process
import pathlib


def test_case01(tmp_path: pathlib.Path):
    p = subprocess.run([
        'python',
        (pathlib.Path().cwd() / './sockets_framework/cli.py').as_posix(),
        'new', 'test_project'
    ],
                       capture_output=True,
                       cwd=tmp_path.as_posix(),
                       check=True)
    assert (tmp_path / 'test_project').exists() is True
    s = Structure(path=tmp_path, arg_name='test_project')
    assert p.stdout.decode().strip() == s.msg
    for path in s.paths:
        assert path.exists() is True
        if path in s.paths[:3]:
            assert path.read_text() == s.content[s.paths.index(path)]
    p = subprocess.run(['poetry', 'build'], capture_output=True, check=True)
    out = p.stdout.decode().split('\n')[-1]
    for o in out.split(' '):
        if '.whl' in o:
            subprocess.run(['pip', 'install', f'./dist/{o}'], check=True)
    p = Process(target=subprocess.run,
                kwargs={
                    "args": ['python', s.paths[0], 'runserver'],
                    "check": True
                })
    p.start()
    assert p.is_alive() is True
    p.kill()
