import glob
import os
import typing

import pandas as pd

from config import input_dir, mapping_dir, results_dir


class DataManipulator:

    def __init__(self, year: str = '2007'):
        """
        Creates a  DataManipulator instance for shared functionality.

        Args:
            year (str): The year to read. If None all years will be checked. Default is None.
        """

        self.year: str = year

        start_dir = input_dir

        if self.year is not None:
            start_dir += self.year+'/*.csv'
        else:
            start_dir += '**/*.csv'

        # Identify the  considered files
        self.considered_files: typing.List = []
        for filename in glob.iglob(start_dir, recursive=True):
            self.considered_files.append(filename)

        # Load mapper
        self.ticker_to_sec_mapper: pd.DataFrame = pd.read_csv(mapping_dir)

        # Create results dir
        os.makedirs(results_dir, exist_ok=True)
