# separate class declared for each page

from playwright.sync_api import expect, Page, BrowserContext, Browser
import logging
import pytest
import sys
import os

# from pages.search import DuckDuckGoSearchPage
# from pages.login_result import DuckDuckGoResultPage
from pages.SearchAndReplay import WFOSearchAndReplayPage
from pages.SearchAndReplay_result import WFOSearchReplayResultsPage

import time as time
from datetime import date

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

# getting the name of the directory
current = os.path.dirname(os.path.realpath(__file__))

# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)
# adding the parent directory to
# the sys.path.
sys.path.append(parent)

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)


#@pytest.mark.skip(reason="no way of currently testing this")
def test_SearchReplay(browser: Browser, test_read_config_file, load_context, playwright) -> None:


    LOGGER.debug('test_SearchReplay: start ...')
    # Start tracing before navigating a page.
    # browser.start_tracing()

    # page.context.tracing.start(page: Page, screenshots=True, snapshots=True, sources=True)
    #browser.start_tracing(screenshots=True, path='./output/browserTraceSearchReplay.zip')
    # create new page object class
    SearchReplay_page = WFOSearchAndReplayPage(browser,  test_read_config_file, load_context, playwright)

    # set browser context from saved login
    LOGGER.debug('test_SearchReplay: load previous context')
    #assert(load_context != 'null')
    #SearchReplay_page.set_context(load_context)
    LOGGER.debug('test_SearchReplay: load()')
    SearchReplay_page.load()
    # assert search menu found
    LOGGER.debug('test_SearchReplay: assert search submenu found')
    assert(SearchReplay_page.searchMenuFound())
    # search page access portion finished, now search and replay access
    LOGGER.debug('test_SearchReplay: close search page context')
    # gracefully close up everything
    SearchReplay_page.page.close()
    SearchReplay_page.context.close()
    #SearchReplay_page.context.browser.close()


    LOGGER.debug('test_SearchReplay: new searchandreplay context')
    SearchReplayResults_page = WFOSearchReplayResultsPage(browser, test_read_config_file, load_context, playwright)
    # expect calls found
    LOGGER.debug('test_SearchReplay: load results page')
    SearchReplayResults_page.load()
    # test for 1 day of calls
    SearchReplayResults_page.populate_searchTextBox('1')
    SearchReplayResults_page.clickSearch()
    # stop tracing
    # browser.stop_tracing()

    assert('Retrieved' in SearchReplayResults_page.check_recordings_found())

    LOGGER.debug('test_SearchReplay: calls found: ' + SearchReplayResults_page.check_recordings_found())
    assert (SearchReplayResults_page.check_no_recordings_found() == False)


    LOGGER.debug('test_SearchReplay: test finished')

