from pathlib import Path

import click
import pdoc
from pdoc import text


@click.command()
@click.argument('module')
@click.option(
    '--output-file',
    default='usage.md',
    help='File to write usage to',
)
def document_api(module, output_file):
    """
    Generate API documentation using [pdoc3](https://pdoc3.github.io/pdoc/)
    for `MODULE`, where module is `path.to.python.module`.
    """

    pdoc.tpl_lookup.directories \
        .insert(0, str(Path(__file__).parent / 'templates'))

    result = text(module)

    with open(output_file, 'w') as f:
        f.write(result)
