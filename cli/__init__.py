import click

from src.data.error_fixer import ErrorFixer
from src.data.error_identifier import ErrorIdentifier
from src.wrapper.wrapper import ProcessWrapper


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
@click.option('--workers', '-w', default=1, help='The number of workers.', type=click.IntRange(1, 10))
def identify_errors(year: str = None, export: bool = True, workers: int = 1):
    """
    Identify the errors of the input files.
    The output is provided at results/identified with the same format.

    \b
    Arguments:
        export (bool): Export the lines with errors.
        year (str): The year to check for errors. If not specified all years are used. Default is None.
        workers (int): How many workers to use. Default 1.
    """
    if workers == 1:
        ErrorIdentifier(year, export).identify_errors()
    else:
        ProcessWrapper(year, export, workers).identify_errors()


@cli.command()
@click.option('--year', '-y', default=None, help='The year to fix. Use None for all the years.', type=click.STRING)
@click.option('--workers', '-w', default=1, help='The number of workers.', type=click.IntRange(1, 10))
def fix_errors(year: str = None, workers: int = 1):
    """
    Fix the errors of the input files.
    The output is provided at results/fixed/ with the same format.

    \b
    Arguments:
        year (str): The year to check for errors. If not specified all years are used. Default is None.
        workers (int): How many workers to use. Default 1.
    """
    if workers == 1:
        ErrorFixer(year).fix_errors()
    else:
        ProcessWrapper(year, False, workers).error_fixer()
