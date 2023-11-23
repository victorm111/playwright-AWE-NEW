import logging
import os
import sys
import time as time
from datetime import date
from typing import Tuple, Any

from bs4 import BeautifulSoup
import pandas as pd
import re




from dotenv import load_dotenv
from playwright.sync_api import Browser, TimeoutError as PlaywrightTimeoutError, Playwright

from pages.SearchAndReplay import WFOSearchAndReplayPage


# load env variables from .env in root dir
load_dotenv()

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

# import Playwright's Page class

# getting the name of the directory
current = os.path.dirname(os.path.realpath(__file__))

# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)
# adding the parent directory to
# the sys.path.
sys.path.append(parent)
# retrieve data and time for test run
today = str(date.today())
t = time.localtime()
current_time = time.strftime("%H_%M_%S", t)


# Add a class definition for the results page object
class WFOSearchReplayResultsPage(WFOSearchAndReplayPage):

    def __init__(self, browser: Browser, test_read_config_file, load_context, playwright: Playwright) -> None:

        LOGGER.debug('WFOSearchReplayResultsPage: init class')

        super(WFOSearchReplayResultsPage, self).__init__(browser, test_read_config_file, load_context, playwright)
        assert(load_context != 'null')
        self.context = browser.new_context(storage_state=load_context, no_viewport=True)
        self.context.set_default_timeout(timeout=60000)         # default timeout for locators

        self.callsRetrieved = self.page.get_by_text('Retrieved')
        self.NoCallsRetrieved = self.page.get_by_text('No Results')
        self.SearchTextBox = self.page.get_by_role("textbox", name="From the Last:")
        self.SearchInit = self.page.get_by_label("Search", exact=True)
        self.SearchResults = self.page.locator('#qm_SearchResultsWorkspace-title')

    def load(self) -> None:
        LOGGER.info('WFOSearchAndReplayResultsPage: load method, open search and replay results page')
        self.page.goto(self.URL)
        self.dropDownArrow.click()
        self.Interactions.wait_for()
        self.Interactions.click()
        self.Search.wait_for()
        self.Search.click()
        # edit textbox to change to 1d search
        self.SearchTextBox.wait_for()
        return

    def populate_searchTextBox(self, days) -> None:
        # edit textbox to change to 1d search
        self.SearchTextBox.fill(days)
        LOGGER.debug('WFOSearchAndReplayResultsPage: populate_searchTextBox() finished')
        return


    def clickSearch(self) -> None:
        # click search icon with updated 1d search window
        self.SearchInit.click()
        LOGGER.debug('WFOSearchAndReplayResultsPage: clickSearch() finished')
        return


    def check_recordings_found(self) -> tuple[str | Any, BeautifulSoup, Any | str]:
        """checks recordings are available, returns soup"""

        LOGGER.debug('WFOSearchAndReplayResultsPage: check_recordings_found() start')
        result = 'none'
        soup = 'null'
        number_calls = 'null'

        #regex = re.compile('.*x-grid-item*.')

        try:
            self.SearchResults.wait_for(timeout=10000)
        except PlaywrightTimeoutError:
            result = 'null'
        else:
            result = self.callsRetrieved.text_content()
            # dump to beautiful soup
            page_content = self.page.content()
            #soup = 'null'
            soup = BeautifulSoup(page_content, 'html.parser')
            #LOGGER.debug('+++++++++ WFOSearchAndReplayResultsPage: clickSearch() BS table start +++++++++++++++')
            #print(soup.prettify(formatter='html'))
            #LOGGER.debug('+++++++++ WFOSearchAndReplayResultsPage: clickSearch() BS table end +++++++++++++++')
            #table = soup.find('table', attrs={'class': 'subs noBorders evenRows'}, recursive=True)

            #create empty dataframe to store calls
            df_allCalls = pd.DataFrame()
            df_dropDupAllCalls = pd.DataFrame()
            df = pd.DataFrame()

            LOGGER.debug('WFOSearchAndReplayResultsPage: check_recordings_found(), start create df')
            number_calls = re.search(r'\d+', result).group()
            counted_calls = 0       # calls counted scrolling through viewport
            while counted_calls < int(number_calls):
                # pull each row, each row is a separate table
                LOGGER.debug('WFOSearchAndReplayResultsPage: check_recordings_found(), pull soup')
                tables = soup.find_all('table', class_='x-grid-item', role='presentation')
                for table in tables:
                    #print(table.tbody.tr.td['data-columnid'])
                    df = pd.read_html(str(table))
                    if table.tbody.tr['class'] == ['x-grid-row']:     # write to csv if search and replay row
                        #df.drop([1])    # drop unreq
                        # append call to all calls df
                        LOGGER.debug('WFOSearchAndReplayResultsPage: check_recordings_found(), store table to df')
                        df_allCalls = pd.concat([df_allCalls, df[0]])
                        df_dropDupAllCalls = df_allCalls.drop_duplicates()  # drop duplicates as scrolls down page
                        #counted_calls = len(df_dropDupAllCalls)
                        counted_calls = df_dropDupAllCalls.shape[0]

                LOGGER.debug('WFOSearchAndReplayResultsPage: check_recordings_found(), df construct page down')

                self.page.keyboard.press('PageDown')           # drop down page
                        # pull table column headers
                        # col_header = table.tbody.tr.td['data-columnid']


            df_dropDupAllCalls.to_csv('./output/SearchReplay-CallsFound.csv', mode='a')

        finally:
            self.page.screenshot(path='./output/screenshot5.png')

            LOGGER.debug('WFOSearchAndReplayResultsPage: check_recordings_found() finished')
            return result, soup, number_calls

    def check_no_recordings_found(self) -> bool:

        """looking for no calls found"""

        LOGGER.debug('WFOSearchAndReplayResultsPage: check_no_recordings_found()')
        result = 'null'

        try:
            self.NoCallsRetrieved.wait_for(timeout=30000)
        except PlaywrightTimeoutError:
            result = False
            LOGGER.exception('WFOSearchAndReplayResultsPage: check_no_recordings_found() timeout')
        else:
            result = True
            LOGGER.debug('WFOSearchAndReplayResultsPage: check_no_recordings_found() finished result')
        finally:
            LOGGER.debug('WFOSearchAndReplayResultsPage: check_no_recordings_found() finished result')
            print(
                f'WFOSearchAndReplayResultsPage: check_no_recordings_found() finished result {result}')
            return result
