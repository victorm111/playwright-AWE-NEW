import logging
import os
import sys
import time as time
from datetime import date


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
        return


    def clickSearch(self) -> None:
        # click search icon with updated 1d search window
        self.SearchInit.click()
        return


    def check_recordings_found(self) -> str:

        try:
            self.SearchResults.wait_for(timeout=30000)
        except PlaywrightTimeoutError:
            return 'null'
        else:
            return self.callsRetrieved.text_content()

    def check_no_recordings_found(self) -> bool:

        no_recordings = 'true'
        try:
            self.NoCallsRetrieved.wait_for(timeout=30000)
        except PlaywrightTimeoutError:
            return False
        else:
            return True
