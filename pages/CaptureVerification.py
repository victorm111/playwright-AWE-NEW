# separate class declared for each page
import logging
import os
import sys
import time as time
from datetime import date

import playwright
from dotenv import load_dotenv
from playwright.sync_api import expect, Browser, Page

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
class WFOCaptureVerificationPage():

    def __init__(self, browser: Browser, test_read_config_file: object, load_context: object, Playwright: playwright) -> None:

        LOGGER.debug('WFOCaptureVerificationPage: init class')
        #self.context = 'null'
        assert(load_context != 'null')
        self.context = browser.new_context(storage_state=load_context, no_viewport=True)
        self.context.set_default_timeout(timeout=60000)         # default timeout for locators

        self.page = self.context.new_page()
        # playwright used as fixture
        # add custom locator 'tabid' for 'Issues' submenu
        Playwright.selectors.set_test_id_attribute("tabid")

        self.title = 'WFO Capture Verification page'
        self.author = 'VW'
        self.URL = test_read_config_file['urls']['AWE_dash']
        self.dropDownArrow_selector = '#as-navdrawer-arrow-btnInnerEl'
        self.Issues_selector = "AVPlus_Module->AVPlus_Module_Menu->AVPlus_Module_Menu_Sub_Issues"

        self.CaptVerif_selector = 'Automated Verification'

        self.CaptVerif = self.page.get_by_label("Automated Verification")
        #self.CaptVerif = self.page.get_by_test_id(self.CaptVerif_selector)
        self.dropDownArrow = self.page.locator(self.dropDownArrow_selector)
        self.Issues = self.page.get_by_test_id(self.Issues_selector)
        #self.Issues = self.page.get_by_label("Issues")
        #self.Issues = self.page.get_by_text("Issues")

        def __repr__(self):
            class_name = type(self).__name__
            return f"{class_name}(title={self.title!r}, author={self.author!r})"

        def __str__(self):
            return self.title

    # def set_context(self, load_context) -> None:
    #     self.page.context = self.page.context.browser.new_context(storage_state=load_context)
    #     return


    def load(self) -> None:
        LOGGER.info('WFOCaptureVerificationPage: load method, open issues page')
        self.page.goto(self.URL)
        #self.__context.tracing.start(sources=True, screenshots=True, snapshots=True)
        #self.__context.browser.start_tracing(screenshots=True, path='./output/browserTraceCaptureVerification.zip')
        self.dropDownArrow.click()
        self.CaptVerif.wait_for()
        self.CaptVerif.click()
        self.Issues.wait_for()
        return

    def IssuesMenuFound(self) -> bool:
        self.Issues.wait_for()
        return self.Issues.is_visible()


