import os
from multiprocessing import Queue

import pandas as pd
from loguru import logger
from tqdm import tqdm

from config import results_dir, input_dir
from src.data.error_identifier import ErrorIdentifier


class ErrorFixer(ErrorIdentifier):

    def __init__(self, year: str = None,
                 tasks_queue: Queue = None, indices_queue: Queue = None, secid_queue: Queue = None):
        """
        Creates an ErrorFixed object.

        Args:
            year(str): The year to fix. If None all years are fixed. Default is None.
            tasks_queue (Queue): The shared tasks queue. If None single process behaviour is followed.
             Default is None.
            indices_queue (Queue): The shared indices queue. If None single process behaviour is followed.
             Default is None.
            secid_queue (Queue): The shared secid queue. If None single process behaviour is followed. Default is None.
        """

        super().__init__(year, False, tasks_queue, indices_queue, secid_queue)

        # Create results directories
        for filename in self.considered_files:
            tokens = os.path.split(filename)
            head = tokens[0]
            folder = head.replace(input_dir, results_dir)
            os.makedirs(folder, exist_ok=True)

    def fix_errors(self) -> None:
        """
        Fixes the errors of all the considered files. The results are stored in results folder.

        Returns:
            None

        """
        if len(self.problematic_indices) == 0:
            self.identify_errors(False)

        logger.info('Fixing errors and storing files.')
        for filename in tqdm(self.considered_files):
            updated_data = self._fix_filename(filename)
            filename.replace(input_dir, results_dir)
            updated_data.to_csv(filename.replace(input_dir, results_dir), index=False)

    def _fix_filename(self, filename: str) -> pd.DataFrame():
        """
        Fixes the filename using the indices provided from the ErrorIdentifier.

        Args:
            filename(str): The filename to fix.

        Raises:
            ValueError: If the error indices are not available for the filename.

        Returns:
            pd.DataFrame: The fixed data frame.
        """

        if filename not in self.problematic_indices:
            raise ValueError('The indices are not calculated for this file. Did you run this method in a  custom code?'
                             ' Consider using identify_errors().')

        # Load data. Second loading into memory since we can not afford to keep all data in memory.
        daily_data = pd.read_csv(filename)
        return daily_data[~daily_data.index.isin(self.problematic_indices[filename])]

    def run(self) -> None:
        """
        Process behaviour for fixer.

        Returns:
            None
        """

        # Identify errors
        logger.info('Identifying errors.')
        super().run()

        # Fix all errors
        logger.info('Writing all files.')
        for filename in self.considered_files:
            updated_daily = self._fix_filename(filename)
            filename.replace(input_dir, results_dir)
            updated_daily.to_csv(filename.replace(input_dir, results_dir), index=False)
