import glob
from typing import List


def get_considered_files(start_dir: str, year: str = None) -> List:
    """
    Get the filenames according to the preferences.

    Args:
        start_dir (str): The start directory to search.
        year (str): The year to use. Default is None.

    Returns:

    """
    if year is not None:
        start_dir += year + '/*.csv'
    else:
        start_dir += '**/*.csv'

    considered_files = []
    for filename in glob.iglob(start_dir, recursive=True):
        considered_files.append(filename)

    return considered_files
