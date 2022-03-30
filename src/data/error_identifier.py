import json

import pandas as pd
from loguru import logger
from tqdm import tqdm

from config import results_dir
from src.data import DataManipulator


class ErrorIdentifier(DataManipulator):

    def __init__(self, year: str = None):
        """

        Args:
            year(str): The year to fix. If None all years are fixed. Default is None.
        """

        super().__init__(year)

        self.problematic_indices = {}

    def identify_errors(self, export: bool = True):
        """
        Identify the problematic indices in the considered files.

        Args:
            export(bool): Flag about exporting the problematic indices to a JSON file.

        Returns:

        """
        logger.info('Identifying errors.')
        for filename in tqdm(self.considered_files):
            to_remove_indices = self._identify_filename_errors(filename)
            self.problematic_indices[filename] = list(to_remove_indices)

        if export:
            json.dump(self.problematic_indices, open(f'{results_dir}problematic_indices.json', 'w'))

    def _identify_filename_errors(self, filename: str) -> pd.core.indexes.numeric.Int64Index:
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
        daily_data = daily_data[daily_data.Ticker.isin(daily_mapper)]
        daily_data['IsValid'] = daily_data.apply(
            lambda row: True if row.Ticker in daily_mapper and daily_mapper[row.Ticker] == row.SecId else False, axis=1)

        return daily_data[daily_data['IsValid'] == False].index
