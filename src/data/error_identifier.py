import json
from queue import Empty
from typing import Tuple, Dict
from multiprocessing import Queue

import pandas as pd
from loguru import logger
from tqdm import tqdm

from config import results_dir
from src.data import DataManipulator


class ErrorIdentifier(DataManipulator):

    def __init__(self, year: str = None, export: bool = True,
                 tasks_queue: Queue = None, indices_queue: Queue = None, secid_queue: Queue = None):
        """

        Args:
            year(str): The year to fix. If None all years are fixed. Default is None.
            export(bool): Flag about exporting the problematic indices to a JSON file.
            tasks_queue (Queue): The shared tasks queue. If None single process behaviour is followed.
             Default is None.
            indices_queue (Queue): The shared indices queue. If None single process behaviour is followed.
             Default is None.
            secid_queue (Queue): The shared secid queue. If None single process behaviour is followed. Default is None.
        """

        super().__init__(year, tasks_queue, indices_queue, secid_queue)

        self.export = export

        self.problematic_indices = {}
        self.problematic_sec_ids = []

    def identify_errors(self):
        """
        Identify the problematic indices in the considered files.

        Args:


        Returns:

        """
        logger.info('Identifying errors.')
        for filename in tqdm(self.considered_files):
            to_remove_indices, sec_ids_errors = self._identify_filename_errors(filename)
            self.problematic_indices[filename] = list(to_remove_indices)
            self.problematic_sec_ids.append(sec_ids_errors)
        if self.export:
            json.dump({str(k): v for d in self.problematic_sec_ids for k, v in d.items()}, open(
                f'{results_dir}problematic_sec_ids.json', 'w'))
            json.dump(self.problematic_indices, open(f'{results_dir}problematic_indices.json', 'w'))

    def _identify_filename_errors(self, filename: str) -> Tuple[pd.core.indexes.numeric.Int64Index, Dict]:
        """
        Fixes the filename provides. The general idea is the following:
            1) Load the  data.
            2) Create a ticker index (Daily Mapper) for this day for O(1) lookup.
            3) Remove rows not present in the Daily Mapper.
            4) From the remaining identify the problematic rows.

        Args:
            filename(str): The filename to fix.

        Returns:
            pandas.core.indexes.numeric.Int64Index: The data frame indices that must be removed.
        """

        # 1) Load data
        daily_data = pd.read_csv(filename)

        # 2) Create the ticker index
        daily_ticker_df = self.ticker_to_sec_mapper[
            (self.ticker_to_sec_mapper.StartDate <= daily_data.TradeDate.iloc[0]) &
            (self.ticker_to_sec_mapper.EndDate >= daily_data.TradeDate.iloc[0])]

        # Sanity check: Each day the daily mapper should  have at most 1 SecId per Security
        max_ticker_appearances = daily_ticker_df.groupby(['Ticker']).size().sort_values(ascending=False)[0]
        if max_ticker_appearances != 1:
            logger.error(f'Problem on {filename}. The same ticker appears multiple times on daily mapper.')
        daily_mapper = dict(zip(daily_ticker_df.Ticker, daily_ticker_df.SecId))

        # 3) and 4) Identify problematic rows as rows not present on daily mapper or with problematic SedId

        # Out of range sec_ids
        out_of_range_sec_ids = daily_data[~daily_data.Ticker.isin(daily_mapper)]['SecId'].astype(int).unique().tolist()

        daily_data = daily_data[daily_data.Ticker.isin(daily_mapper)]
        daily_data['IsValid'] = daily_data.apply(
            lambda row: True if row.Ticker in daily_mapper and daily_mapper[row.Ticker] == row.SecId else False, axis=1)

        # Invalid sec_ids
        invalid_sec_ids = daily_data[daily_data['IsValid'] == False]['SecId'].unique().tolist()

        sec_ids_errors = {daily_data.TradeDate.iloc[0]: {
            'invalid': invalid_sec_ids,
            'out_of_range': out_of_range_sec_ids
        }}

        return daily_data[daily_data['IsValid'] == False].index, sec_ids_errors

    def run(self) -> None:
        """
        Process behaviour if multiple workers are used.
        Warning this increased the memory required.

        Returns:
            None
        """
        logger.info('Starting new process.')
        while True:
            try:
                filename = self.tasks_queue.get(timeout=1)
                # Process the filename
                to_remove_indices, sec_ids_errors = self._identify_filename_errors(filename)
                self.problematic_indices[filename] = list(to_remove_indices)
                self.problematic_sec_ids.append(sec_ids_errors)
                self.considered_files.append(filename)
            except Empty as e:
                logger.info('Process completed.')
                if self.export:
                    # Copy the results to the indices, sec_id queue
                    self.indices_queue.put(self.problematic_indices)
                    self.secid_queue.put({str(k): v for d in self.problematic_sec_ids for k, v in d.items()})
                break
        logger.info('Process exit.')
