import argparse
import pathlib

parser = argparse.ArgumentParser(prog="socket-framework",
                                 description="Socket Framework")
subprasers = parser.add_subparsers(dest='command')
new = subprasers.add_parser('new', help='Start a new project.')
new.add_argument('name', type=str, help='The name of a project.')
new.add_argument('-p',
                 '--path',
                 help='Path for a new project.',
                 type=str,
                 default=None)
args = parser.parse_args()
if args.command == "new":
    if args.path:
        path = pathlib.Path(args.path)
        if not path.exists():
            raise FileNotFoundError(path.as_posix())
    else:
        path = pathlib.Path().cwd() / str(args.name)
        if path.exists():
            raise FileExistsError(path.as_posix())
        path.mkdir()
    structure = ("settings.py", str(args.name).replace('-', '_'),
                 '.'.join([str(args.name).replace('-', '_'),
                           'py']), '__init__.py')
    for name in structure:
        if name is structure[0]:
            target = path / name
        elif name is structure[1]:
            target = path / name
            target.mkdir()
        else:
            target = path / structure[1] / name
        if name is not structure[1]:
            target.touch()
        if not target.exists():
            raise FileNotFoundError(target.as_posix())
    with open(path / structure[1] / structure[2], 'w') as core:
        core.write(
            '# Implement your functions here.\n# Return any pickable value.\n')
    print("Created package {} in {}".format(structure[1], path.as_posix()))
