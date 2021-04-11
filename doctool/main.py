
import click

from doctool.cli_documentation import document_cli
from doctool.api_documentation import document_api


@click.group()
def main():
    pass


main.add_command(document_cli)
main.add_command(document_api)


if __name__ == '__main__':
    main()
