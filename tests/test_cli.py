import subprocess
from sockets_framework.cli import Structure


def test_case01(tmp_path):
    p = subprocess.run([
        'python', './sockets_framework/cli.py', 'new', 'test_project', tmp_path
    ],
                       capture_output=True)
    assert p.returncode == 0
    s = Structure(path=tmp_path, arg_name='test_project')
    assert p.stdout.decode().lstrip().rstrip() == s.msg
    for path in s.paths:
        assert path.exists() is True
        if path in s.paths[:3]:
            assert path.read_text() == s.content[s.paths.index(path)]
