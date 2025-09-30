import re
import argparse

import pandas as pd
from playwright.sync_api import sync_playwright, expect, TimeoutError

DEFAULT_INPUT_PATH = 'London Stock Exchange task - input.csv'
DEFAULT_OUTPUT_PATH = 'London Stock Exchange task - output.csv'
URL_BASE = r'https://www.londonstockexchange.com/stock/{}/{}/company-page'


class CStockValuesRetriever:

    def __init__(self):
        self.input_file = None
        self.output_file = None
        self.df_in = None
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def _setup(self, input_path):
        """
        Reads input CSV file and changes timestamp column type from dtype to string to avoid type errors
        :param input_path: path to input file
        :return (bool): True if file read properly
        """
        print(f'Reading input data file {input_path}\n')
        try:
            self.df_in = pd.read_csv(input_path)
        except FileNotFoundError:
            print(f'File {input_path} not found')
            return False
        except pd.errors.EmptyDataError:
            print(f'File {input_path} is empty')
            return False

        self.df_in['timestamp'] = self.df_in['timestamp'].astype('string')
        return True

    def _verify_page(self, response, company_url, company_name):
        """
        Verifies if the loaded page is th correct stock page
        :param response: open page response
        :param company_url: URL to company stock page
        :param company_name: company name
        :return (bool): True if page is opened correctly
        """
        if response is None:
            print(f'No response for {company_url}')
            return False

        if response.status != 200:
            print(f'Bad status: {response.status} {response.status_text}')
            return False

        try:
            expect(self.page.get_by_role('link', name='Company page')).to_be_visible(timeout=5000)
        except AssertionError:
            print('Company page landmark not found, wrong page opened.')
            return False

        try:
            heading = self.page.get_by_role("heading", name=re.compile(company_name + '$', re.I))
            expect(heading).to_be_visible(timeout=5000)
        except AssertionError:
            print(f'Company heading does not match the expected company name: {company_name}')
            return False

        return True

    def _get_stock_value(self):
        """
        Reads page to obtain stock price value
        :return (str): stock price value or False
        """
        try:
            price_element = self.page.locator('span.price-tag').first
            raw_price = (price_element.text_content() or '').strip()
            raw_price = raw_price if ',' not in raw_price else raw_price.replace(',', '')
        except TimeoutError:
            print('Failed to find the latest stock price value')
            raw_price = False

        return raw_price

    def _get_last_update_timestamp(self):
        """
        Reads page to obtain last price update timestamp
        :return (str): last stock update timestamp or False
        """
        try:
            timestamp = self.page.locator('div.ticker-item.delay span.bold-font-weight').first
            raw_time = (timestamp.text_content() or "").strip()
        except TimeoutError:
            print('Failed to find the last stock update timestamp')
            raw_time = False

        return raw_time

    def start(self):
        """
        Starts playwright session
        """
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        self.context = self.browser.new_context(
            user_agent='Mozilla/5.0',
            locale='en-GB'
        )
        self.page = self.context.new_page()

    def stop(self):
        """
        Stops playwright session
        """
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def get_stock_values_csv(self, input_path, output_path):
        """
        Retrieve stock values with timestamp for companies defined in input_path and save the data in output_path
        :param input_path: input CSV file path with target companies
        :param output_path: output CSV file path where data is saved
        """
        if not self._setup(input_path):
            raise RuntimeError(f'Failed to read the input CSV file {input_path}')

        for idx, row in self.df_in.iterrows():
            # extract company name and stock code
            company_name = row['company name']
            stock_code = row['stock code']
            print(f'Looking for latest stock price value for {company_name}')

            # prepare URL to company page
            name_converted = company_name.lower().replace(' ', '-')
            company_url = URL_BASE.format(stock_code, name_converted)

            # navigate to company page
            print(f'Loading company stock page: {company_url}')
            response = self.page.goto(company_url, wait_until='domcontentloaded')

            if not self._verify_page(response, company_url, company_name):
                print(f'Failed to correctly load company stock page\nContinue to next company\n')
                continue
            print('Stock page loaded successfully')

            print('Retrieving latest stock price value and last update timestamp')
            stock_value = self._get_stock_value()
            timestamp = self._get_last_update_timestamp()

            if stock_value:
                self.df_in.at[idx, 'value'] = float(stock_value)
            if timestamp:
                self.df_in.at[idx, 'timestamp'] = timestamp

            print()

        self.df_in.to_csv(output_path, index=False)
        print(f'Data saved in {output_path}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Retrieve stock prices from London Stock Exchange'
    )
    parser.add_argument(
        '--input',
        '-i',
        default=DEFAULT_INPUT_PATH,
        type=str,
        help='Path to input CSV file with company names and codes'
    )
    parser.add_argument(
        '--output',
        '-o',
        default=DEFAULT_OUTPUT_PATH,
        type=str,
        help='Path to output CSV file where to save data'
    )
    args = parser.parse_args()
    # request
    stock_value_retrieve = CStockValuesRetriever()
    try:
        stock_value_retrieve.start()
        stock_value_retrieve.get_stock_values_csv(args.input, args.output)
    finally:
        stock_value_retrieve.stop()
