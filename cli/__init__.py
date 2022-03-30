import click

from src.data.error_fixer import ErrorFixer
from src.data.error_identifier import ErrorIdentifier


@click.group()
def cli():
    """
        \b
            _   _          ___          _     ___ _        _     _____        _
           /_\ | |__ _ ___/ __| ___ ___| |__ | __(_)_ _ __| |_  |_   _|_ _ __| |__
          / _ \| / _` / _ \__ \/ -_) -_) / / | _|| | '_(_-<  _|   | |/ _` (_-< / /
         /_/ \_\_\__, \___/___/\___\___|_\_\ |_| |_|_| /__/\__|   |_|\__,_/__/_\_\ \b
                 |___/

    """
    pass


@cli.command()
@click.option('--year', '-y', default=None, help='The year to fix. Use None for all the years.', type=click.STRING)
@click.option('--export', '-e', default=True, help='Export the identified lines as a JSON file.', type=click.BOOL)
def identify_errors(year: str = None, export: bool = True):
    """
    Identify the errors of the input files.
    The output is provided at results/identified with the same format.

    \b
    Arguments:
        export (bool): Export the lines with errors.
        year (str): The year to check for errors. If not specified all years are used. Default is None.
    """
    ErrorIdentifier(year).identify_errors(export)


@cli.command()
@click.option('--year', '-y', default=None, help='The year to fix. Use None for all the years.', type=click.STRING)
def fix_errors(year: str = None):
    """
    Fix the errors of the input files.
    The output is provided at results/fixed/ with the same format.

    \b
    Arguments:
        year (str): The year to check for errors. If not specified all years are used. Default is None.
    """
    ErrorFixer(year).fix_errors()
