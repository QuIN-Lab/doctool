
# Usage
```
Usage: python -m doctool.main [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  document-api  Generate API documentation using [pdoc3](https://pdoc3.github.io/pdoc/).
  document-cli  Generate usage documentation for a click command-line application for...
```

## `document-api`

Generate API documentation using [pdoc3](https://pdoc3.github.io/pdoc/).


```
Usage: python -m doctool.main document-api [OPTIONS]

Options:
  --help  Show this message and exit.

```

## `document-cli`

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


```
Usage: python -m doctool.main document-cli [OPTIONS] MODULE

Options:
  --output-format [markdown|latex]
                                  Type of documentation to generate
  --output-file TEXT              File to write usage to (`usage.md` for markdown, `usage.tex` for latex)
  --section-depth INTEGER         Depth of top-level section. Will prepend all `\section` with this many `sub`
  --print-tex-template            Print a minimal LaTeX template for use with `--output-format=latex` and exit
  --help                          Show this message and exit.

```
