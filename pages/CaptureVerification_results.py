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

        LOGGER.info('WFOCaptureVerificationResultsPage: init class start')

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

        self.timeDate_dropDown_listbox = self.page.get_by_test_id('MuiList-root MuiMenu-list MuiList-padding')
        #self.time_apply = self.page.get_by_role("button", name="Apply")
        self.dropDownHoursSelect = self.page.locator("xpath=//ul/*[@name='timeFrameLastDateTimeSelectHours' and @data-value='hour']")
        self.dropDownDaysSelect = self.page.locator("xpath=//ul/*[@name='timeFrameLastDateTimeSelectDays' and @data-value='day']")
        self.dropDownSelected = self.page.locator("xpath=//ul/*[@role='option' and @aria-selected='true']")



        self.time_apply_enabled = self.page.get_by_test_id("MuiButtonBase-root MuiButton-root MuiButton-text verint-btn-primary")
        self.time_apply_disabled = self.page.get_by_test_id("MuiButtonBase-root MuiButton-root MuiButton-text verint-btn-primary Mui-disabled Mui-disabled")
        self.TimeFrame_bothRadioButtonFalse = self.page.locator("xpath=//span/*[@type='radio' and @value='false']")
        self.TimeFrame_bothRadioButtonTrue = self.page.locator("xpath=//span/*[@type='radio' and @value='true']")
        self.activeRadioTimeFrame = 'null'
        self.activeRadioTimeRange = 'timeFrameRangeDateTimeRadio'
        self.activeRadioTimeLast = 'timeFrameLastDateTimeRadio'
        self.dropDownHoursDays_1 = self.page.locator("xpath=//div/*[@role='button' and @aria-haspopup='listbox']")
        self.dropDownHoursDays_2 = self.page.locator("xpath=//div/*[@name='timeFrameLastDateTimeSelect' and @placeholder='select']")

        self.checkForApplyActive = self.page.get_by_test_id("MuiButtonBase-root MuiButton-root MuiButton-text verint-btn-primary")
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
        LOGGER.info('WFOCaptureVerificationResultsPage: init class finished')


    def load(self) -> None:
        """load the capture verification results page"""
        LOGGER.info('WFOCaptureVerificationResultsPage: load method start')
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
        LOGGER.info('WFOCaptureVerificationResultsPage: load method finished')

        return

    def checkLeftMenuAvailable(self) -> str:
        """confirm left hand side menu available including org, datasource etc., also init time setting """
        LOGGER.info('WFOCaptureVerificationResultsPage: checkLeftMenuAvailable method start')
        self.leftMenu.wait_for()
        LOGGER.info('WFOCaptureVerificationResultsPage: checkLeftMenuAvailable method finished')
        return self.page.content()

    def config_timeInterval(self) -> None:
        """configure 24hour time interval"""
        LOGGER.info('WFOCaptureVerificationResultsPage: config_timeInterval method start')
        page_content = self.page.content()
        html = BeautifulSoup(page_content, 'html.parser')
        left_timeframe_menu_last_radio=html.find('input', attrs = {'name':'timeFrameLastDateTimeRadio'})

        # inject an initial configuration, was a bug where when checking interval/last radio
        # radio check was returning false for active radio after initial login
        #self.time_frame_select.click()
        #self.time_radio_from_2.click()  # select interval time radio button
        # check if apply button active after click from or last search profile, apply button will become active after
        # inactive button is selected
        #try:
        #    self.checkForApplyActive.wait_for(timeout=1000)
        #except PlaywrightTimeoutError:
        #    self.time_radio_last_2.click()  # now select 'last' option
        #finally:
        #    self.time_apply_enabled.click()  # hit apply button, activate prof time profile

        # re-select time menu, inject last 24hr time interval
        self.time_frame_select.click()
        # read name from radio buttons
        #name_active_radio = self.TimeFrame_bothRadioButtonTrue
        # which button, find name of active button
        # check true radio button, need run is_checked() routine to determine active radio
        # true or false identifies two radio search options, but does not mark radio button status !!
        # need is_checked() routine on the locator
        # check the True marked button first, pull name and mark as active radio
        if self.TimeFrame_bothRadioButtonTrue.is_checked(timeout=1000):
            self.activeRadioTimeFrame = self.TimeFrame_bothRadioButtonTrue.get_attribute('name')
        else:
            self.activeRadioTimeFrame = self.TimeFrame_bothRadioButtonFalse.get_attribute('name')

        # if last not active set it
        if self.activeRadioTimeFrame != self.activeRadioTimeLast:

            self.time_radio_last_2.click()
            self.time_apply_enabled.click()  # hit apply button, activate from profile
            self.time_frame_select.click()      # reselect tome menu on lhs
            #self.time_radio_last_2.click()      # now select 'last' option


        # handle case where 'from' was active  , click 'last' radio button and populate it
        #else:
         #   self.time_radio_last_2.click()

        # now continue to populate 'last hours and number of hours'
        box_text = self.time_config_box.get_attribute('value')  # number of hours
        self.time_dropDown.click()  # enable drop down to prepare selection
        #  will select hours
        box_test_1 = self.dropDownSelected.text_content()
        need_change = 'null'

        # if last enabled but equal to 24hours, need to change to 23hours then back to 24hours to
        # drive new 24hour profile

        if (self.activeRadioTimeFrame == self.activeRadioTimeLast) and (box_test_1 == 'Hours' and box_text == '24'):
                need_change = True

        self.dropDownHoursSelect.click()
        # if hours selected no need to change
        if self.dropDownSelected.get_attribute(name = 'name', timeout=1000) == self.dropDownDaysSelect.get_attribute(name='name'):
            self.dropDownHoursSelect.click()

#        if box_test_1 == 'Hours':
#            self.time_dropDown_select.select_option("Days")
#        elif box_test_1 == 'Days':
#            self.time_dropDown_select.select_option("Hours")

        # clear hours box
        self.time_config_box.clear()

        # check number of hours
        # if number already = 24, inject a non-24 value to drive new config, then inject 24 second time

        if need_change:
            self.time_config_box.fill("23")  # inject non 24 value
            #apply the changes
            self.time_apply_enabled.click()  # hit apply button

        # handle case where number hours was not 24
        else:
            self.time_config_box.fill("24")  # inject non 24 value
            #apply the changes
            self.time_apply_enabled.click()  # hit apply button


        LOGGER.info('WFOCaptureVerificationResultsPage: config_timeInterval method finished')

        return

    def check_recordings_found(self, time_out) -> str:
        LOGGER.info('WFOCaptureVerificationResultsPage: check_recordings_found method start')

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
            LOGGER.info('WFOCaptureVerificationResultsPage: check_recordings_found method finished')
            return return_value

    def downloadCSVStart(self) -> str:
        """download results csv"""
        LOGGER.debug('WFOCaptureVerificationResultsPage:: downloadCSVStart method start')
        download = 'False'
        # Start waiting for the download
        with self.page.expect_download() as download_info:
            # click download button
            LOGGER.debug('WFOCaptureVerificationResultsPage:: downloadCSVStart click')
            self.DownloadCSV.click()
        download = download_info.value
        # Wait for the download process to complete and save the downloaded file somewhere
        download.save_as("./output/CaptureVerification/" + download.suggested_filename)
        LOGGER.debug('WFOCaptureVerificationResultsPage:: downloadCSVStart method finished')
        return str(download)

