import logging
import os
import sys
import time as time
from datetime import date
from typing import Tuple, Any
import pytest
from pytest_html_reporter import attach

from bs4 import BeautifulSoup
import pandas as pd
import re
import playwright

from dotenv import load_dotenv
from playwright.sync_api import Browser, TimeoutError as PlaywrightTimeoutError, expect

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

    def __init__(self, browser: Browser, test_read_config_file, load_context, Playwright: playwright) -> None:

        LOGGER.debug('WFOSearchReplayResultsPage: init class')

        super(WFOSearchReplayResultsPage, self).__init__(browser, test_read_config_file, load_context, Playwright)
        self.context.close()
        assert(load_context != 'null')
        self.context = browser.new_context(storage_state=load_context, no_viewport=True)
        self.context.set_default_timeout(timeout=30000)  # default timeout for locators
        self.page = self.context.new_page()  # first tab page in context
        Playwright.selectors.set_test_id_attribute("tabid")

        self.callsRetrieved = self.page.get_by_text('Retrieved')
        self.NoCallsRetrieved = self.page.get_by_text('No Results')
        self.SearchTextBox = self.page.get_by_role("textbox", name="From the Last:")
        self.SearchInit = self.page.get_by_label("Search", exact=True)
        self.SearchResults = self.page.locator('#qm_SearchResultsWorkspace-title')
        self.firstCell = self.page.locator("xpath=//tr/*[@class='x-grid-cell x-grid-td x-grid-cell-duration x-unselectable']")


        # update parent locator
        self.dropDownArrow = self.page.locator(self.dropDownArrow_selector)
        self.Interactions = self.page.locator(self.Interactions_selector)
        self.Search = self.page.get_by_test_id(self.Search_selector)

    def load(self) -> None:
        LOGGER.info('WFOSearchAndReplayResultsPage: load method, open search and replay results page')
        self.page.goto(self.URL)
        self.dropDownArrow.wait_for(timeout=45000, state='visible')
        self.dropDownArrow.click()
        self.Interactions.wait_for(timeout=45000, state='visible')
        self.Interactions.click()
        self.Search.wait_for(timeout=45000, state='visible')
        self.Search.click()
        # edit textbox to change to 1d search
        self.SearchTextBox.wait_for(timeout=45000, state='visible')
        return

    def populate_searchTextBox(self, days) -> None:
        # edit textbox to change to 1d search
        self.SearchTextBox.fill(days)
        LOGGER.debug('WFOSearchAndReplayResultsPage: populate_searchTextBox() finished')
        return


    def clickSearch(self) -> None:
        # click search icon with updated 1d search window
        self.SearchInit.wait_for(timeout=25000, state='visible')
        self.SearchInit.click()
        LOGGER.debug('WFOSearchAndReplayResultsPage: clickSearch() finished')
        return


    def check_recordings_found(self) -> tuple[str | Any, Any , Any | str]:
        """checks recordings are available, returns df and output csv"""

        result = 'null'
        soup = 'null'
        number_calls = 'null'

        LOGGER.debug('WFOSearchAndReplayResultsPage: check_recordings_found() start')

        # create empty dataframe to store calls
        df_allCalls = pd.DataFrame()
        df_dropDupAllCalls = pd.DataFrame()
        df = pd.DataFrame()

        try:
            LOGGER.debug('WFOSearchAndReplayResultsPage: check_recordings_found(), attempt to find results')
            self.SearchResults.wait_for(timeout=10000, state='visible')      # check on results page
            self.callsRetrieved.wait_for(timeout=25000, state='visible')
            result = self.callsRetrieved.text_content(timeout=10000)
        except PlaywrightTimeoutError:
            LOGGER.exception('WFOSearchAndReplayResultsPage: check_recordings_found(), results element search timeout')
            result = 'null'
        else:
            LOGGER.debug('WFOSearchAndReplayResultsPage: check_recordings_found() dump csv, results found')
            # dump to beautiful soup
            page_content = self.page.content()

            soup = BeautifulSoup(page_content, 'html.parser')

            LOGGER.debug('WFOSearchAndReplayResultsPage: check_recordings_found(), start create df')
            number_calls = re.search(r'\d+', result).group()
            counted_calls = 0       # calls counted scrolling through viewport
            count = 0
            page_scrolled = 0
            column_names = list()       # store search and replay column names
            no_columns = 0              # number of search and replay columns
            columns_collected = 0       # confirm column names collected, saves re-looping

            while counted_calls < int(number_calls):
                # pull each row, each row is a separate table
                LOGGER.debug('WFOSearchAndReplayResultsPage: check_recordings_found(), pull soup')
                print(f'counted_calls while loop, counted_calls, number_calls: {counted_calls}, {number_calls}')
                tables = soup.find_all('table', class_='x-grid-item', role='presentation')

                for table in tables:
                    count+=1
                    #print(f'table for loop, table, tables: {table}, {tables}')

                    df = pd.read_html(str(table))
                    if table.tbody.tr['class'] == ['x-grid-row']:     # write to csv if search and replay row
                        LOGGER.debug('WFOSearchAndReplayResultsPage: check_recordings_found(), store table to df')
                        df_allCalls = pd.concat([df_allCalls, df[0].iloc[[0]]])
                        df_allCalls = df_allCalls.drop_duplicates()
                        counted_calls = len(df_allCalls)

                        # collect column names if not already done
                        if not columns_collected:

                            # get number of columns
                            #no_columns = len(df_allCalls.columns)
                            # pull headers
                            script_tags = table.find_all('td')
                            no_columns = len(script_tags)
                            for i in range(no_columns) :
                                #column_names[i] = table.tbody.tr.td['data-columnid']
                                #column_names.append(table.tbody.tr.td['data-columnid'])
                                try:
                                    column_names.append(script_tags[i]['data-columnid'])
                                    print(f'script tags i, data-columnid, {i}, {script_tags[i]['data-columnid']}')
                                except KeyError:
                                    column_names.append('img')

                            # remove the img, was causing trouble as counted as two headers
                            column_names.remove('img')
                            LOGGER.debug(
                                'WFOSearchAndReplayResultsPage: check_recordings_found(), column names retrieved')
                            print(
                                f'WFOSearchAndReplayResultsPage: check_recordings_found(), add df column names:  {column_names}')
                            columns_collected = 1

                LOGGER.debug('WFOSearchAndReplayResultsPage: check_recordings_found(), for table loop finished')
                count=0             # reset count for new page
                page_scrolled+=1
                LOGGER.debug('WFOSearchAndReplayResultsPage: check_recordings_found(), attempt firstCell focus')

                try:
                    self.firstCell.first.focus(timeout=25000)              # select first instance in time column , required before page down
                except PlaywrightTimeoutError:
                    LOGGER.exception(
                        'WFOSearchAndReplayResultsPage: check_recordings_found(), attempt first cell focus fail, timeout')
                except:
                    LOGGER.exception('WFOSearchAndReplayResultsPage: check_recordings_found(), attempt first cell focus fail')
                else:
                    LOGGER.debug('WFOSearchAndReplayResultsPage: check_recordings_found(), attempt first page down')
                    self.page.keyboard.press('PageDown')
                    LOGGER.debug('WFOSearchAndReplayResultsPage: check_recordings_found(), attempt second page down')
                    self.page.keyboard.press('PageDown')

                    LOGGER.debug('WFOSearchAndReplayResultsPage: check_recordings_found(), page down finished, construct new soup')
                    # re-dump to beautiful soup after page down
                    page_content = self.page.content()
                    # soup = 'null'
                    soup = BeautifulSoup(page_content, 'html.parser')

            LOGGER.debug('WFOSearchAndReplayResultsPage: check_recordings_found(), counted_calls while loop finished, attach col names')
            # assign df column names
            df_allCalls.columns = column_names
            LOGGER.debug('WFOSearchAndReplayResultsPage: check_recordings_found(), dump duplicates')
            df_dropDupAllCalls = df_allCalls.drop_duplicates()  # drop duplicates as scrolls down page
            LOGGER.debug('WFOSearchAndReplayResultsPage: check_recordings_found() dump csv')
            df_dropDupAllCalls.to_csv('./output/SR/SearchReplay-CallsFound.csv', mode='a')
            LOGGER.debug('WFOSearchAndReplayResultsPage: check_recordings_found() dumped csv')

        finally:
            self.page.screenshot(path='./output/screenshot5.png')

            print(f'WFOSearchAndReplayResultsPage: check_recordings_found(), *** results:  {result} {number_calls}')
            LOGGER.info('WFOSearchAndReplayResultsPage: check_recordings_found() finished')
            return result, df_dropDupAllCalls, number_calls

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
