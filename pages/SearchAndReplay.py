# separate class declared for each page
import logging
import os
import sys
import time as time
from datetime import date

import playwright
from dotenv import load_dotenv
from playwright.sync_api import Browser, Playwright

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
        self.context='null'
        self.context = browser.new_context(storage_state=load_context, no_viewport=True)
        assert(load_context != 'null')
        self.page = self.context.new_page()

        # add custom locator 'tabid' for 'Search' submenu
        Playwright.selectors.set_test_id_attribute("tabid")
        #playwright.sync_api.Selectors.set_test_id_attribute("tabid")
        self.title = 'WFO search and replay page'
        self.author = 'VW'
        self.URL = test_read_config_file['urls']['AWE_dash']
        self.dropDownArrow = self.page.locator('#as-navdrawer-arrow-btnInnerEl')
        self.Interactions = self.page.locator('#INTERACTION')
        self.Search = self.page.get_by_test_id('INTERACTION->interactions_tab->search_tab')

        def __repr__(self):
            class_name = type(self).__name__
            return f"{class_name}(title={self.title!r}, author={self.author!r})"

        def __str__(self):
            return self.title

    def set_context(self, load_context) -> None:
        self.page.context = self.page.context.browser.new_context(storage_state=load_context)
        return


    def load(self) -> None:
        LOGGER.info('WFOSearchAndReplayPage: load method, open search and replay page')
        self.page.goto(self.URL)
        self.dropDownArrow.click()
        self.Interactions.wait_for()
        self.Interactions.click()
        self.Search.wait_for()
        return

    def searchMenuFound(self) -> bool:
        return self.Search.is_visible()
