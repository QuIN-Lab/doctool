import re
import shutil
from pathlib import Path


class Example:
    def __init__(self, args, name, help=None, creates_image=False):
        self.args = args
        self.help = help
        self.name = name
        self.creates_image = creates_image

    def format_commandline(self, command, ctx):
        """
        Get the full command including `python main.py` that could be
        copy/pasted into a terminal
        """
        args = map(str, self.args)

        # Replace /home/marcel and similar with `~`
        home = str(Path.home()).replace('/', r'\/')
        args = [re.sub(rf'^{home}', '~', a) for a in args]

        args = [
            f'"{x}"' if ' ' in x else x
            for x in args
        ]
        return ' '.join([ctx.info_name, command.name, *args])

    def run(self, command, ctx, output_dir):
        """
        Run the example and generate the output image
        """
        with ctx.scope():
            command.parse_args(ctx, self.args)
            external_filename = ctx.invoke(command, **ctx.params)

        try:
            external_filename = Path(external_filename)
        except TypeError as e:
            raise SystemExit(' '.join([
                f'The value returned from command `{command.name}` is not a path.',
                'Expected str, bytes or os.PathLike,',
                f'received `{type(external_filename)}`.',
                'Commands must return a path to an image',
                'when using an image example.',
            ])) from e


        internal_filename = output_dir / \
            f'{command.name}_{external_filename.name}'

        shutil.copy(external_filename, internal_filename)

        return internal_filename


def example(help, args, name='', creates_image=False):
    def wrapper(func):
        if not hasattr(func, '__doctool_examples__'):
            func.__doctool_examples__ = []
        func.__doctool_examples__.append(Example(
            help=help,
            creates_image=creates_image,
            args=args,
            name=name,
        ))

        return func
    return wrapper
