import logging
import os
import sys
import time as time
from datetime import date
import re

import playwright
from dotenv import load_dotenv
from playwright.sync_api import Browser, Playwright, TimeoutError as PlaywrightTimeoutError

# import CaptureVerification class, outlines pre-results page
from pages.CaptureVerification import WFOCaptureVerificationPage

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
class WFOCaptureVerificationResultsPage(WFOCaptureVerificationPage):
    def __init__(self, browser: Browser, test_read_config_file, load_context, Playwright: playwright) -> None:

        LOGGER.info('WFOCaptureVerificationResultsPage: init class')

        super(WFOCaptureVerificationResultsPage, self).__init__(browser, test_read_config_file, load_context, Playwright)

        #self.context.close()    # from parent
        assert(load_context != 'null')
        self.context = browser.new_context(storage_state=load_context, no_viewport=True)

        self.page = self.context.new_page()     # first tab page in context

        self.resetDefault = self.page.get_by_text('Reset to default')
        self.NoCallsRetrieved = self.page.get_by_text('No call issues to display')
        self.foundCalls = self.page.get_by_text(re.compile(r'Found\s\d+\scalls'))
        self.DownloadCSV = self.page.get_by_text("Export to CSV", exact=True)

# update parent locators

        self.Issues = self.page.get_by_test_id(self.Issues_selector)
        self.dropDownArrow = self.page.locator(self.dropDownArrow_selector)
        self.CaptVerif = self.page.get_by_test_id(self.CaptVerif_selector)

    def load(self) -> None:
        LOGGER.info('WFOCaptureVerificationResultsPage: load method')

        self.page.goto(self.URL)
        self.context.tracing.start(sources=True, screenshots=True, snapshots=True)
        #self.context.tracing.start_chunk()
        #self.page.bring_to_front()
        self.dropDownArrow.click()
        self.CaptVerif.wait_for()
        self.CaptVerif.click()
        self.Issues.wait_for()
        self.Issues.click()
        #self.page.reload()  #  was trouble with table loading results even if issues were seen
        return

    def clickDefault(self) -> None:
        self.resetDefault.wait_for()
        self.resetDefault.click()
        return

    def check_recordings_found(self) -> str:

        return_value = 'none'

        try:
            self.foundCalls.page.wait_for_load_state()
            self.foundCalls.wait_for(timeout=24000) # check if 'found' located
        except PlaywrightTimeoutError:
            return_value= 'null'
        except:
            return_value = 'null'
        else:
            LOGGER.debug('WFOCaptureVerificationResultsPage:: check_recordings_found, calls found')
            return_value = self.foundCalls.text_content()
        finally:
            self.context.tracing.stop(path="./output/CaptureVerifResults.zip")
            return return_value

    def downloadCSVStart(self) -> str:

        LOGGER.debug('WFOCaptureVerificationResultsPage:: downloadCSVStart start')
        download = 'False'
        # Start waiting for the download
        with self.page.expect_download() as download_info:
            # click download button
            LOGGER.debug('WFOCaptureVerificationResultsPage:: downloadCSVStart click')
            self.DownloadCSV.click()
        download = download_info.value
        # Wait for the download process to complete and save the downloaded file somewhere
        download.save_as("./output/CaptureVerification/" + download.suggested_filename)
        LOGGER.debug('WFOCaptureVerificationResultsPage:: downloadCSVStart finished')
        return str(download)

