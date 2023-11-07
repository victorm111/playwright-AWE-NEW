import logging
import os
import sys
import time as time
from datetime import date
import re
from bs4 import BeautifulSoup

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

        self.context.close()    # from parent
        assert(load_context != 'null')
        self.context = browser.new_context(storage_state=load_context, no_viewport=True)
        self.context.set_default_timeout(timeout=40000)         # default timeout for locators
        self.page = self.context.new_page()  # first tab page in context
        Playwright.selectors.set_test_id_attribute("class")

        self.leftMenu = self.page.get_by_text("OrganizationTime FrameData SourcesSeverityIssues")
        self.time_frame_select = self.page.get_by_test_id("MuiButtonBase-root MuiIconButton-root icon-time-picker verint-icon-button verint-icon-medium") # lhs menu
        #self.time_select = self.page.get_by_role("heading", name = "Time Frame")
        # iframe locator for set time lhs menu, used 'last' radio button selector

        self.time_radio_last = self.page.get_by_role("radio", name="timeFrameLastDateTimeRadio", exact=True)
        self.time_radio_last_2 = self.page.get_by_test_id("verint-regular-label last-label")    # to set
        #self.time_radio_last_3 = self.page.get_by_label(text='mui-component-select-timeFrameLastDateTimeSelect')  # to read if disabled, aria-disabled=true

        self.time_radio_from = self.page.get_by_role("radio", name="timeFrameRangeDateTimeRadio", exact=True)
        self.time_radio_from_2 = self.page.get_by_test_id("verint-regular-label datetime-label").get_by_text(text='From')

        self.time_config_box = self.page.get_by_test_id("MuiInputBase-input MuiInput-input")    # time box hours or days
        #self.time_hours = self.page.get_by_label("mui-component-select-timeFrameLastDateTimeSelect")    # hours box
        self.time_dropDown = self.page.get_by_test_id("MuiSelect-root MuiSelect-select MuiSelect-selectMenu MuiInputBase-input MuiInput-input")     # hours/days dropdown, before select

        self.time_dropDown_select = self.page.get_by_test_id(
            "MuiButtonBase-root MuiListItem-root MuiMenuItem-root MuiMenuItem-gutters MuiListItem-gutters MuiListItem-button")

        #self.time_apply = self.page.get_by_role("button", name="Apply")
        self.time_apply_enabled = self.page.get_by_test_id("MuiButtonBase-root MuiButton-root MuiButton-text verint-btn-primary")
        self.time_apply_disabled = self.page.get_by_test_id("MuiButtonBase-root MuiButton-root MuiButton-text verint-btn-primary Mui-disabled Mui-disabled")

        self.IssuesTable = self.page.get_by_test_id('avpRowContainer issuesTableRow')

        self.NoCallsRetrieved = self.page.get_by_text('No call issues to display')
        self.foundCalls = self.page.get_by_text(re.compile(r'Found\s\d+\scalls'))
        self.DownloadCSV = self.page.get_by_text("Export to CSV", exact=True)


        self.NoCallsRetrieved = self.page.get_by_text('No call issues to display')
        self.foundCalls = self.page.get_by_text(re.compile(r'Found\s\d+\scalls'))
        self.DownloadCSV = self.page.get_by_text("Export to CSV", exact=True)

# update parent locators

        self.Issues = self.page.get_by_text("Issues")
        #self.Issues = self.page.get_by_text(self.Issues_selector)
        #self.Issues =  self.page.locator(self.Issues_selector_1).filter(has=self.page.get_by_label(self.Issues_selector))
        self.dropDownArrow = self.page.locator(self.dropDownArrow_selector)

        self.CaptVerif = self.page.get_by_label(self.CaptVerif_selector)

    def load(self) -> None:
        """load the capture verification results page"""
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

    def checkLeftMenuAvailable(self) -> str:
        """confirm left hand side menu available including org, datasource etc. """
        self.leftMenu.wait_for()
        return self.page.content()

    def config_timeInterval(self) -> None:
        """configure time interval"""
        # steps select 'time frame' in lhs menu
        # select 'last'
        # select 24 hours
        # hit apply
        # check which radio button is active, turns out non-selected button has 'checked' in the element

        # query radio buttons


        page_content = self.page.content()
        html = BeautifulSoup(page_content, 'html.parser')
        left_timeframe_menu_last_radio=html.find('input', attrs = {'name':'timeFrameLastDateTimeRadio'})
        # select and check the 'last' radio button
        # check if checked
        self.time_frame_select.click()
        # check if 'from-to' section disabled
        from_disabled=self.time_radio_from_2.get_attribute(name='aria-disabled', timeout=1000)
        #check if 'last' section enabled
        last_disabled=self.time_radio_last_2.get_attribute(name='aria-disabled', timeout=1000)

        # click both buttons, check if apply available for click
        self.time_radio_from_2.click()
        # check if apply button disabled, can determine which radio button active
        from_disabled = self.time_apply_disabled.is_disabled()
        self.time_radio_last_2.click()
        last_disabled=self.time_apply_disabled.is_disabled()
        # if from_disabled then continue with 24 hours in time box
        # otherwise need to toggle


        # assert and verify the checked state
        #self.time_radio.is_checked() is True
        #self.time_radio.wait_for()
        #self.time_radio.click()
        #self.time_config_box.wait_for()        # clear input
        # read text content of text box
        box_text = self.time_config_box.get_attribute('value')

        self.time_dropDown.click()      # enable drop down to prepare selection
        # toggle between hours and days to activate 'apply' button
        box_test_1 = self.time_dropDown_select.get_attribute('value')
        if box_test_1 == 'Hours':
            self.time_dropDown_select.select_option("Days")
        elif box_test_1 == 'Days':
            self.time_dropDown_select.select_option("Hours")
        self.time_apply.click()     # hit apply button
        self.time_config_box.clear()
        self.time_config_box.fill("24")  # inject 24 hours
            
        return

    def check_recordings_found(self, time_out) -> str:
        """look for calls found"""
        return_value = 'none'

        try:
            self.IssuesTable.wait_for()         # Issues table
            self.foundCalls.page.wait_for_load_state()
            self.foundCalls.wait_for(timeout=time_out) # check if 'found' located
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
        """download results csv"""
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

