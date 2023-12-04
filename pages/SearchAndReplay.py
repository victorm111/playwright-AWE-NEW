# separate class declared for each page
import logging
import os
import sys
import time as time
from datetime import date

import playwright
import playwright.async_api
from dotenv import load_dotenv
from playwright.sync_api import Browser, TimeoutError as PlaywrightTimeoutError, expect, Page


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

# Add a class definition for the WFO login page object
class WFOSearchAndReplayPage:

    def __init__(self, browser: Browser, test_read_config_file: object, load_context: object, Playwright: playwright) -> None:

        LOGGER.info('WFOSearchAndReplayPage: init class')

        assert(load_context != 'null')
        self.context = browser.new_context(storage_state=load_context, no_viewport=True)
        self.context.set_default_timeout(timeout=30000)         # default timeout for locators
        self.page = self.context.new_page()

        # add custom locator 'class' for 'Search' submenu
        Playwright.selectors.set_test_id_attribute("tabid")

        self.title = 'WFO search and replay page'
        self.author = 'VW'
        self.URL = test_read_config_file['urls']['AWE_dash']
        self.dropDownArrow = self.page.locator('#as-navdrawer-arrow-btnInnerEl')
        self.dropDownArrow_selector = '#as-navdrawer-arrow-btnInnerEl'
        self.Interactions = self.page.locator('#INTERACTION')
        self.Interactions_selector = '#INTERACTION'
        self.Search = self.page.get_by_test_id('INTERACTION->interactions_tab->search_tab')
        self.Search_selector = 'INTERACTION->interactions_tab->search_tab'

        def __repr__(self):
            class_name = type(self).__name__
            return f"{class_name}(title={self.title!r}, author={self.author!r})"

        def __str__(self):
            return self.title

    def load(self) -> None:
        LOGGER.info('WFOSearchAndReplayPage: load method, open search and replay page')
        self.page.goto(self.URL)
        self.dropDownArrow.wait_for(timeout=45000, state='visible')
        self.dropDownArrow.click()
        self.Interactions.wait_for(timeout=25000, state='visible')
        self.Interactions.click()
        self.Search.wait_for(timeout=25000, state='visible')
        return

    def searchMenuFound(self) -> bool:
        self.Search.wait_for(timeout=25000, state='visible')
        return self.Search.is_visible()
