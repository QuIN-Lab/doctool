import sys
import shutil
from pathlib import Path

import click
from colorama import Fore as FgColour


class DoctoolCommand(click.Command):
    def __init__(self, *args, example=None, example_help='', **kwargs):
        super().__init__(*args, **kwargs)
        self._example_args = example
        self.example_help = example_help

    def get_example_command(self, ctx):
        args = [f'"{x}"' if ' ' in x else x for x in self._example_args]
        return ' '.join([ctx.info_name, self.name, *args])

    def get_example(self, ctx, output_dir):
        with ctx.scope():
            self.parse_args(ctx, self._example_args)
            external_filename = ctx.invoke(self, **ctx.params)

        try:
            external_filename = Path(external_filename)
        except TypeError:
            print(' '.join([
                f'{FgColour.RED}ERROR:{FgColour.RESET}',
                f'The value returned from command {self.name} is not a path.',
                'Expected str, bytes or os.PathLike,',
                f'recived {type(external_filename)}.',
                'Commands must return a path to an image',
                'when using an image example.',
            ]))
            sys.exit(1)


        internal_filename = output_dir / \
            f'{self.name}_{external_filename.name}'

        shutil.copy(external_filename, internal_filename)

        return internal_filename
