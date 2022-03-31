import os
import typing
from multiprocessing import Process, Queue

import pandas as pd

from config import input_dir, mapping_dir, results_dir
from src.utils import get_considered_files


class DataManipulator(Process):

    def __init__(self, year: str = '2007',
                 tasks_queue: Queue = None, indices_queue: Queue = None, secid_queue: Queue = None):
        """
        Creates a  DataManipulator instance for shared functionality.

        Args:
            year (str): The year to read. If None all years will be checked. Default is None.
            tasks_queue (Queue): The shared queue. If None single process behaviour is followed. Default is None.
            indices_queue (Queue): The shared indices queue. If None single process behaviour is followed.
             Default is None.
            secid_queue (Queue): The shared secid queue. If None single process behaviour is followed. Default is None.
        """

        # Call process
        super().__init__()

        self.year: str = year

        start_dir = input_dir

        # Load mapper
        self.ticker_to_sec_mapper: pd.DataFrame = pd.read_csv(mapping_dir)

        # Create results dir
        os.makedirs(results_dir, exist_ok=True)

        # Set workers
        self.tasks_queue = tasks_queue
        self.indices_queue = indices_queue
        self.secid_queue = secid_queue

        self.considered_files = []
        if self.tasks_queue is None:
            # Not multiprocessing  all the files are considered

            # Identify the  considered files
            self.considered_files: typing.List = get_considered_files(start_dir, year)



