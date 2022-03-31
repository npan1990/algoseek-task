import json
from multiprocessing import Queue
from queue import Empty

from loguru import logger

from config import input_dir, results_dir
from src.data.error_fixer import ErrorFixer
from src.data.error_identifier import ErrorIdentifier
from src.utils import get_considered_files


class ProcessWrapper:

    def __init__(self, year: str = None, export: bool = True, workers: int = 4):
        """
        Create a process wrapper.

        Args:
            year (str): The year to handle. Default is None.
            export (bool): Export the JSON output. Default is True.
            workers (int): The number of workers to use. Default is 4.
        """
        self.year = year
        self.export = export
        self.workers = workers
        self.tasks_queue = Queue()
        self.indices_queue = Queue()
        self.secid_queue = Queue()

        start_dir = input_dir

        self.considered_files = get_considered_files(start_dir, self.year)

        for filename in self.considered_files:
            self.tasks_queue.put(filename)

    def identify_errors(self):
        error_identifiers = []
        for i in range(self.workers):
            error_identifiers.append(ErrorIdentifier(self.year, self.export,
                                                     self.tasks_queue, self.indices_queue, self.secid_queue))

        for error_identifier in error_identifiers:
            error_identifier.daemon = True
            error_identifier.start()

        # Start reading from results queue
        problematic_indices = []
        problematic_sec_ids = []
        while len(problematic_indices) < self.workers:
            problematic_indices.append(self.indices_queue.get())

        while len(problematic_sec_ids) < self.workers:
            problematic_sec_ids.append(self.secid_queue.get())

        for error_identifier in error_identifiers:
            error_identifier.join()

        if self.export:
            logger.info('Exporting.')
            # Combine the data  and export

            while not self.indices_queue.empty():
                try:
                    problematic_indices.append(self.indices_queue.get(timeout=1))
                except Empty as e:
                    break

            while not self.secid_queue.empty():
                try:
                    problematic_sec_ids.append(self.secid_queue.get(timeout=1))
                except Empty as e:
                    break

            logger.info('Writing files.')
            # Combine dictionaries to a single dictionary
            problematic_indices_dict = {str(k): v for d in problematic_indices for k, v in d.items()}
            problematic_sec_ids_dict = {str(k): v for d in problematic_sec_ids for k, v in d.items()}
            json.dump(problematic_indices_dict, open(f'{results_dir}problematic_indices.json', 'w'))
            json.dump(problematic_sec_ids_dict, open(f'{results_dir}problematic_sec_ids.json', 'w'))

    def error_fixer(self):
        error_fixers = []
        for i in range(self.workers):
            error_fixers.append(ErrorFixer(self.year, self.tasks_queue, self.indices_queue, self.secid_queue))

        for error_fixer in error_fixers:
            error_fixer.daemon = True
            error_fixer.start()

        for error_fixer in error_fixers:
            error_fixer.join()
