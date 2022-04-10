import re
import textwrap
from pathlib import Path
from abc import ABC, abstractmethod


class Formatter(ABC):

    @abstractmethod
    def format_usage(self, usage):
        pass

    @abstractmethod
    def format_command(self, command_name, command_description, command_help):
        pass

    @abstractmethod
    def format_command_example(self, example_cmd, example_path, example_help):
        pass


class MarkdownFormatter(Formatter):

    @staticmethod
    def tex_to_gl_md(s):
        """
        Convert latex math blocks to GitLab KaTeX
        """

        return re.sub(r'\$([^\$]+)\$', r'$`\1`$', s)

    def format_usage(self, usage):
        return textwrap.dedent(r"""
            # Usage
            ```
            {usage}
            ```
        """).format(usage=usage)

    def format_command(self, command_name, command_description, command_help):
        return textwrap.dedent(r"""
            ## `{command_name}`
            {command_description}

            ```
            {command_help}
            ```
        """).format(
            command_name=command_name,
            command_description=self.tex_to_gl_md(command_description),
            command_help=self.tex_to_gl_md(command_help),
        )

    def format_command_example(self, example_number, name, cmd, help, image_path):
        image = '' if image_path is None else f'![]({image_path})'

        return textwrap.dedent(r"""
            ### Example {example_number}: {name}
            {help}

            `{cmd}`
            {image}
        """).format(
            name=name,
            cmd=cmd,
            image=image,
            help=self.tex_to_gl_md(help),
            example_number=example_number,
        )


class LatexFormatter(Formatter):

    def __init__(self, section_depth):
        self.section_depth = section_depth

    def section(self, n):
        # TODO: Support paragraph and such

        prefix = 'sub' * (n + self.section_depth)
        return rf'\{prefix}section'

    def format_usage(self, usage):
        return textwrap.dedent(r"""
            {section}{{Usage}}
            \begin{{minted}}[breaklines]{{text}}
            {usage}
            \end{{minted}}
        """).format(
            section=self.section(0),
            usage=usage,
        )

    def format_command(self, command_name, command_description, command_help):

        # Replace `` with inline code blocks
        command_description = re.sub(
            r'`([^`]+)`',
            r'\\mintinline{text}{\1}',
            command_description,
        )

        # Use textquote rather than ""
        command_description = re.sub(
            r'"([^"]+)"',
            r'\\textquote{\1}',
            command_description,
        )

        return textwrap.dedent(r"""
            {section}{{{command_name}}}
            {command_description}

            \begin{{minted}}[breaklines]{{text}}
            {command_help}
            \end{{minted}}
        """).format(
            section=self.section(1),
            command_name=command_name,
            command_description=command_description,
            command_help=command_help,
        )

    def format_command_example(self, name, cmd, path, image_path):
        image = '' if image_path is None else r"""
            \begin{{figure}}[H]
            \includegraphics[width=\linewidth]{{{image_path}}}
            \caption{{{example_help}}}
            \end{{figure}}
        """.format(image_path=Path(image_path).name)

        return textwrap.dedent(r"""
            {section}{{Example:}}
            \begin{{minted}}[breaklines]{{text}}
            {example_cmd}
            \end{{minted}}
            {image}
        """).format(
            section=self.section(2),
            example_cmd=example_cmd,
            example_help=example_help,
            image=image,
        )
