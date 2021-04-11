import sys
import traceback
import importlib

import click
from colorama import Fore as FgColour


class ModuleType(click.ParamType):
    name = 'module'

    def convert(self, value, param, ctx):
        parts = value.split(':')

        try:
            if len(parts) == 1:
                parts.append('main')

            assert len(parts) == 2

            sys.path.insert(0, '')
            module = importlib.import_module(parts[0])
            group = getattr(module, parts[1])
            return module, group

        except ModuleNotFoundError as e:
            if e.name == parts[0]:
                hint = "Perhaps you need to remove '.py'." \
                    if parts[0].endswith('.py') else ''

                return self.fail(
                    ' '.join([
                        f"Could not find module '{parts[0]}'.",
                        hint,
                    ]),
                    param,
                    ctx,
                )

            traceback.print_exc()
            print(' '.join([
                f'{FgColour.RED}ERROR:{FgColour.RESET}',
                'Received ModuleNotFoundError while importing',
                f"'{parts[0]}':",
                e.msg,
            ]))
            sys.exit(1)

        except AttributeError:
            self.fail(
                f"Module '{parts[0]}' has no function '{parts[1]}'.",
                param,
                ctx,
            )
            return None
