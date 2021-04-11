
import click

from doctool.cli_documentation import document_cli


@click.group()
def main():
    pass


main.add_command(document_cli)


if __name__ == '__main__':
    main()
