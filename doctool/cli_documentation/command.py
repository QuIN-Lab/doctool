import shutil
import textwrap
from io import StringIO
from pathlib import Path
from functools import partial
from contextlib import redirect_stdout, redirect_stderr

import click
from tqdm import tqdm
from timer import timer
from pathos.multiprocessing import ProcessingPool as Pool

from doctool.lib.module_type import ModuleType
from doctool.console import console
from .formatters import MarkdownFormatter, LatexFormatter


def get_usage(command, ctx):
    """
    Click usage without docstring. Docstring is added separately
    (outside of code block)
    """

    formatter = ctx.make_formatter()
    command.format_usage(ctx, formatter)
    command.format_options(ctx, formatter)

    return formatter.getvalue()


def print_tex_template(ctx, _param, value):
    if not value or ctx.resilient_parsing:
        return

    with open(Path(__file__).parent / 'example.tex', 'r',
              encoding='utf-8') as f:
        print(f.read())
    ctx.exit()


def tap(f, iterable):
    """
    Apply a function to each item of an iterable and yield the item
    """
    for item in iterable:
        f(item)
        yield item


def generate_for_command(command_name, ctx, group, formatter, output_dir,
                         output_file):
    """
    Generate markdown docs for a single command
    :returns: StringIO
    """

    try:
        with timer() as t, \
                open('/dev/null', 'w', encoding='utf-8') as devnull, \
                redirect_stdout(devnull), redirect_stderr(devnull):

            s = StringIO()

            command = group.get_command(ctx, command_name)
            child_ctx = click.Context(
                command=command,
                parent=ctx,
                info_name=command.name,
            )
            s.write(formatter.format_command(
                command_name=command_name,
                command_description=textwrap.dedent(command.__doc__ or ''),
                command_help=get_usage(command, child_ctx),
            ))

            for i, example in enumerate(reversed(getattr(
                command.callback,
                '__doctool_examples__',
                [],
            ))):
                s.write(formatter.format_command_example(
                    example_number=i + 1,
                    name=example.name,
                    cmd=example.format_commandline(ctx=ctx, command=command),
                    help=textwrap.dedent(example.help),
                    image_path=example.run(
                        ctx=child_ctx,
                        output_dir=output_dir,
                        command=command,
                    ).relative_to(output_file.parent)
                    if example.creates_image else None,
                ))

            return command_name, t.elapse, s
    except:  # pylint: disable=bare-except
        console.print('[red][DOCTOOL ERROR]:[/red] '
                      f'Error when processing command `{command_name}`')
        console.print_exception()
        return command_name, 0, StringIO()


def iter_commands(multiprocessing, commands, **kwargs):
    """
    Iterate through the commands and call `generate_for_command` on each one,
    passing kwargs.
    Use multiprocessing if allowed, otherwise use a simple serial loop.
    """
    if multiprocessing:
        with Pool() as p:
            yield from p.imap(
                partial(generate_for_command, **kwargs),
                commands,
            )
    else:
        for command in commands:
            yield generate_for_command(command, **kwargs)


@click.command()
@click.argument('module', type=ModuleType())
@click.option(
    '--output-format',
    type=click.Choice(('markdown', 'latex')),
    default='markdown',
    help='Type of documentation to generate',
)
@click.option(
    '--output-file',
    default=None,
    help='File to write usage to '
    '(`usage.md` for markdown, `usage.tex` for latex)'
)
@click.option(
    '--section-depth',
    help='Depth of top-level section. ' +
    r'Will prepend all `\section` with this many `sub`',
    type=int,
)
@click.option(
    '--print-tex-template',
    is_flag=True,
    callback=print_tex_template,
    expose_value=False,
    is_eager=True,
    help='Print a minimal LaTeX template for use with `--output-format=latex` '
    'and exit'
)
@click.option(
    '--output-dir',
    default=None,
    type=click.Path(),
    help='Where to save images output by examples that generate figures.'
)
@click.option(
    '--multiprocessing/--no-multiprocessing',
    default=True,
    is_flag=True,
    type=bool,
    help='Whether to process the commands in parallel. '
    'This is faster, but can make it difficult to track down issues.'
)
@click.option(
    '--progress/--no-progress',
    'should_print_progress',
    default=True,
    is_flag=True,
    help='Whether to print a progress bar. Can get in the way of debugging.',
)
def document_cli(module, output_format, output_file, output_dir, multiprocessing,
        should_print_progress, section_depth=None):
    r"""
    Generate usage documentation for a click command-line application
    for `MODULE`, where module is `path.to.python.module:group`.

    The following click group should have the `MODULE` of `main:main`.
    ```python
    # main.py
    @click.group()
    def main():
        pass
    ```

    If the output format is LaTeX, then the output will be
    an embeddable `.tex` document.
    This file is intended to be included in a larger LaTeX guide
    using `\input`.
    You must include `minted` and `csquotes` packages.
    If using figures as examples, you must use the `graphicx`
    and set the `\graphicspath{}` option to find your figures.
    A template is available with the `--print-tex-template` option.
    """

    module, group = module

    # TODO: Actually, this could prepend extra `#`
    if output_format == 'markdown' and section_depth is not None:
        console.print(' '.join([
            '[yellow][DOCTOOL WARNING]:[/yellow]',
            '`--section-depth` does nothing with markdown output',
        ]))

    if section_depth is None:
        section_depth = 0

    if output_file is None:
        output_file = {
            'markdown': 'USAGE.md',
            'latex': 'usage.tex',
        }[output_format]

    output_file = Path(output_file)

    output_dir = output_file.parent / 'examples' if output_dir is None \
            else output_dir
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    ctx = click.Context(
        group,
        info_name=f'python -m {module.__name__}',
        terminal_width=110,
        max_content_width=110,
    )
    formatter = {
        'markdown': MarkdownFormatter(),
        'latex': LatexFormatter(section_depth=section_depth),
    }[output_format]

    def print_progress(args):
        command_name, time, _ = args
        tqdm.write(f'Finished {command_name} in {time:.2f}s')

    with ctx.scope(), open(output_file, 'w', encoding='utf-8') as f:

        # Print main usage
        f.write(formatter.format_usage(group.get_help(ctx)))

        commands = group.list_commands(ctx)

        iterator = iter_commands(
            commands=commands,
            multiprocessing=multiprocessing,
            ctx=ctx,
            group=group,
            formatter=formatter,
            output_dir=output_dir,
            output_file=output_file,
        )
        iterator = tqdm(tap(print_progress, iterator), total=len(commands)) \
            if should_print_progress else iterator

        results = [s for *_, s in iterator]

        for s in results:
            s.seek(0)
            shutil.copyfileobj(s, f)
