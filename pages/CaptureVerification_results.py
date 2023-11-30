import logging
import os
import sys
import time as time
from datetime import date
import re

import pytest
from bs4 import BeautifulSoup
# generate random integers
import random
from pytest_html_reporter import attach

import playwright
from dotenv import load_dotenv
from playwright.sync_api import Browser, TimeoutError as PlaywrightTimeoutError, expect

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
        self.context.set_default_timeout(timeout=30000)         # default timeout for locators
        self.page = self.context.new_page()  # first tab page in context
        Playwright.selectors.set_test_id_attribute("class")

        self.leftMenu = self.page.get_by_text("OrganizationTime FrameData SourcesSeverityIssues")
        self.time_frame_select = self.page.get_by_test_id("MuiButtonBase-root MuiIconButton-root icon-time-picker verint-icon-button verint-icon-medium") # lhs menu
        self.time_frame_pin = self.page.get_by_label("Pin Filter Pane")
        self.time_frame_unpin = self.page.get_by_label("Pin Filter Pane").get_by_test_id('MuiButtonBase-root MuiIconButton-root icon-unpin verint-icon-button verint-icon-small')
        #self.time_select = self.page.get_by_role("heading", name = "Time Frame")
        # iframe locator for set time lhs menu, used 'last' radio button selector

        self.time_radio_last = self.page.get_by_role("radio", name="timeFrameLastDateTimeRadio", exact=True)
        self.time_radio_last_2 = self.page.get_by_test_id("verint-regular-label last-label")    # to set
        #self.time_radio_last_3 = self.page.get_by_label(text='mui-component-select-timeFrameLastDateTimeSelect')  # to read if disabled, aria-disabled=true

        self.time_radio_from = self.page.get_by_role("radio", name="timeFrameRangeDateTimeRadio", exact=True)
        self.time_radio_from_2 = self.page.get_by_test_id("verint-regular-label datetime-label").get_by_text(text='From')

        self.time_config_box = self.page.get_by_test_id("MuiInputBase-input MuiInput-input")    # time box hours or days
        self.time_dropDown_select = self.page.get_by_test_id("MuiSelect-root MuiSelect-select MuiSelect-selectMenu MuiInputBase-input MuiInput-input")

        self.dropDownHoursSelect = self.page.get_by_test_id("MuiButtonBase-root MuiListItem-root MuiMenuItem-root Mui-selected MuiMenuItem-gutters MuiListItem-gutters MuiListItem-button Mui-selected")
        self.dropDownDaysSelect = self.page.locator("xpath=//ul/*[@name='timeFrameLastDateTimeSelectDays' and @data-value='day']")
        self.dropDownSelected = self.page.locator("xpath=//ul/*[@role='option' and @aria-selected='true']")
        self.time_apply_enabled = self.page.get_by_test_id("MuiButtonBase-root MuiButton-root MuiButton-text verint-btn-primary")
        self.time_apply_disabled = self.page.get_by_test_id("MuiButtonBase-root MuiButton-root MuiButton-text verint-btn-primary Mui-disabled Mui-disabled")
        self.TimeFrame_bothRadioButtonFalse = self.page.locator("xpath=//span/*[@type='radio' and @value='false']")
        self.TimeFrame_bothRadioButtonTrue = self.page.locator("xpath=//span/*[@type='radio' and @value='true']")

        self.lastRadio_disabled = self.page.locator("xpath=//div/*[@class='MuiSelect-root MuiSelect-select MuiSelect-selectMenu MuiInputBase-input MuiInput-input Mui-disabled Mui-disabled Mui-disabled' and @role='button']")
        self.fromRadio_disabled = self.page.locator("xpath=//div/*[@class='MuiInputBase-input MuiOutlinedInput-input Mui-disabled Mui-disabled MuiInputBase-inputAdornedEnd MuiOutlinedInput-inputAdornedEnd' and @name='timeFrameFromDateInput']")
        self.LastOrFromTimeRadio = self.page.locator("xpath=//div/*[(@class='MuiInputBase-input MuiOutlinedInput-input Mui-disabled Mui-disabled MuiInputBase-inputAdornedEnd MuiOutlinedInput-inputAdornedEnd' and @name='timeFrameFromDateInput') or (@class='MuiSelect-root MuiSelect-select MuiSelect-selectMenu MuiInputBase-input MuiInput-input Mui-disabled Mui-disabled Mui-disabled' and @role='button'])")

        self.activeRadioTimeFrame = 'null'
        self.activeRadioTimeRange = 'timeFrameRangeDateTimeRadio'
        self.activeRadioTimeLast = 'mui-component-select-timeFrameLastDateTimeSelect'
        self.dropDownHoursDays_1 = self.page.locator("xpath=//div/*[@role='button' and @aria-haspopup='listbox']")
        self.dropDownHoursDays_2 = self.page.locator("xpath=//div/*[@name='timeFrameLastDateTimeSelect' and @placeholder='select']")

        self.checkForApplyActive = self.page.get_by_test_id("MuiButtonBase-root MuiButton-root MuiButton-text verint-btn-primary")
        self.IssuesTable = self.page.get_by_test_id('avpRowContainer issuesTableRow')
        self.IssuesTableLoaded = self.page.locator("xpath=//div/*[@class='avTableContainer']")

        self.returnedIssuesEmpty = self.page.get_by_text("To display call issues, apply a broader filter.")
        self.returnedIssuesNotEmpty = self.page.get_by_test_id("callIssuesTotal")
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
        self.dropDownArrow.click()
        self.CaptVerif.wait_for()
        self.CaptVerif.click()
        self.Issues.wait_for()
        self.Issues.click()
        LOGGER.debug('WFOCaptureVerificationResultsPage: load method:: wait issue table to load if available')
        #expect((self.IssuesTableLoaded).first.or_(self.returnedIssuesEmpty)).to_be_visible(timeout=15000)
        LOGGER.info('WFOCaptureVerificationResultsPage: load method finished')
        return


    def pinTimeFrameMenu(self) -> bool:

        """attempt to pin the lhs time frame selection to 24 hours"""
        LOGGER.info(
            'WFOCaptureVerificationResultsPage: pinTimeFrame():: start')
        tf_pinned = False
        tf_pin_count = 0
        while not tf_pinned and tf_pin_count < 3:

            self.time_frame_select.wait_for(timeout=25000, state='visible')
            self.time_frame_select.click()

            try:
                self.time_frame_pin.wait_for(timeout=25000, state='visible')
                self.time_frame_pin.click(timeout=25000)

            except PlaywrightTimeoutError:

                tf_pin_count = +1
                LOGGER.exception(
                    'WFOCaptureVerificationResultsPage: pinTimeFrame:: time menu not pinned, reselect time menu')
                print(
                    f'WFOCaptureVerificationResultsPage: pinTimeFrame:: time frame pin error::  count , status: {tf_pin_count} {tf_pinned}')
                continue  # continue while loop

            else:
                tf_pinned = True
                LOGGER.debug('WFOCaptureVerificationResultsPage: pinTimeFrame:: time menu pinned successfully')

                print(
                    f'WFOCaptureVerificationResultsPage: pinTimeFrame:: time frame pin success::  count , status: {tf_pin_count} {tf_pinned}')
        LOGGER.info(
            'WFOCaptureVerificationResultsPage: pinTimeFrame():: end')
        return tf_pinned


    def checkLeftMenuAvailable(self) -> str:


        """confirm left hand side menu available including org, datasource etc., also init time setting """

        LOGGER.info('WFOCaptureVerificationResultsPage: checkLeftMenuAvailable method start')
        self.leftMenu.wait_for()
        LOGGER.info('WFOCaptureVerificationResultsPage: checkLeftMenuAvailable method finished')

        return self.page.content()

    def checkIssueTable(self) -> tuple[str | bool, str | bool]:
        """waits until issue table is stable, checks if issues listed or is empty"""

        LOGGER.info('WFOCaptureVerificationResultsPage: checkIssueTable() called')

        emptyConfirmed = 'null'
        issues_listed = 'null'

        try:
            #expect(self.IssuesTableLoaded).to_be_visible(timeout=25000).or_expect(self.returnedIssuesEmpty).to_be_visible(timeout=10000)
            #expect(self.IssuesTableLoaded).or_(self.returnedIssuesEmpty).to_be_visible(timeout=25000)
            self.IssuesTableLoaded.wait_for(timeout=25000, state='visible')
            issues_listed = self.IssuesTableLoaded.is_visible(timeout=25000)
            ####expect((self.IssuesTableLoaded).first.or_(self.returnedIssuesEmpty)).to_be_visible(timeout=25000)
            # expect((self.IssuesTableLoaded).first.or_(self.returnedIssuesEmpty)).to_be_visible(timeout=15000)

        except PlaywrightTimeoutError:      # if issues list locator not found, confirm empty table
            LOGGER.exception('WFOCaptureVerificationResultsPage: checkIssueTable:: timeout error retrieving capt verif table, check for empty table')
            print(
                f'WFOCaptureVerificationResultsPage: checkIssueTable:: no calls returned: {issues_listed}')
            try:
                self.returnedIssuesEmpty.wait_for(timeout=10000, state='visible')
                expect(self.returnedIssuesEmpty).to_be_visible(timeout=5000)
            except PlaywrightTimeoutError:
                LOGGER.exception(
                    'WFOCaptureVerificationResultsPage: checkIssueTable:: timeout error retrieving capt verif table, nothing returned')
            else:
                self.returnedIssuesEmpty.wait_for(timeout=10000, state='visible')
                emptyConfirmed = self.returnedIssuesEmpty.is_visible()
                if not emptyConfirmed:
                    LOGGER.debug('WFOCaptureVerificationResultsPage: checkIssueTable:: confirmed issues table empty')
                    print(
                        f'WFOCaptureVerificationResultsPage: checkIssueTable:: confirmed issues table empty: {emptyConfirmed}')

                else:
                    # if issues_listed = False then no issues in table container, confirm empty table
                    LOGGER.debug('WFOCaptureVerificationResultsPage: checkIssueTable:: confirmed issues table no calls, confirm empty')
                    print(
                    f'WFOCaptureVerificationResultsPage: checkIssueTable:: confirmed issues table no calls, confirm empty: {issues_listed}')
                    if not issues_listed or issues_listed == 'null':
                        try:
                            expect(self.returnedIssuesEmpty).to_be_visible(timeout=5000)
                        except PlaywrightTimeoutError:
                            LOGGER.exception(
                        'WFOCaptureVerificationResultsPage: checkIssueTable:: timeout error retrieving capt verif table locators')
                        else:
                            emptyConfirmed = self.returnedIssuesEmpty.is_visible()
                            if emptyConfirmed:
                                LOGGER.debug('WFOCaptureVerificationResultsPage: checkIssueTable:: confirmed issues table empty')
                            print(
                                f'WFOCaptureVerificationResultsPage: checkIssueTable:: confirmed issues table empty: {emptyConfirmed}')
                    else:
                        LOGGER.error('WFOCaptureVerificationResultsPage: checkIssueTable:: issue table query invalid response')
                        pytest.fail()

        LOGGER.info('WFOCaptureVerificationResultsPage: checkIssueTable():: finished')
        return emptyConfirmed, issues_listed



    def config_timeInterval(self) -> None:
        """configure and inject 24hour time interval"""
        LOGGER.info('WFOCaptureVerificationResultsPage: config_timeInterval method start')
        page_content = self.page.content()
        html = BeautifulSoup(page_content, 'html.parser')
        #left_timeframe_menu_last_radio=html.find('input', attrs = {'name': 'timeFrameLastDateTimeRadio'})

            # re-select time menu, inject last 24hr time interval
            # self.time_frame_select.click()
            # read name from radio buttons
            #name_active_radio = self.TimeFrame_bothRadioButtonTrue
            # which button, find name of active button
            # check true radio button, need run is_checked() routine to determine active radio
            # true or false identifies two radio search options, but does not mark radio button status !!
            # need is_checked() routine on the locator

            # select time frame menu not available

            # wait for time select menu to be available, page will load issues automatically and take over !

            # confirm issue table loaded
            # LOGGER.debug('WFOCaptureVerificationResultsPage: config_timeInterval:: wait issue table to load if available')
            #expect(self.IssuesTableLoaded.or_(self.returnedIssuesEmpty).first).to_be_visible(timeout=10000)
        LOGGER.debug('WFOCaptureVerificationResultsPage: config_timeInterval:: confirm issues table loaded')
        emptyConfirmed, issues_listed = self.checkIssueTable()
        print(f'WFOCaptureVerificationResultsPage: config_timeInterval:: random hours issues table loaded, emptyConfirmed, issues_loaded: {emptyConfirmed} , {issues_listed}')


        # emptyConfirmed = 'null'
        # issues_listed = 'null'
        #
        #
        # try:
        #     #expect(self.IssuesTableLoaded).to_be_visible(timeout=25000).or_expect(self.returnedIssuesEmpty).to_be_visible(timeout=10000)
        #     #expect(self.IssuesTableLoaded).or_(self.returnedIssuesEmpty).to_be_visible(timeout=25000)
        #     self.IssuesTableLoaded.wait_for(timeout=25000, state='visible')         # wait until visible, waits for issues to load !!!
        #     issues_listed = self.IssuesTableLoaded.is_visible(timeout=25000)
        #         ####expect((self.IssuesTableLoaded).first.or_(self.returnedIssuesEmpty)).to_be_visible(timeout=25000)
        #         # expect((self.IssuesTableLoaded).first.or_(self.returnedIssuesEmpty)).to_be_visible(timeout=15000)
        #
        # except PlaywrightTimeoutError:      # if issues list locator not found, confirm empty table
        #     LOGGER.exception('WFOCaptureVerificationResultsPage: config_timeInterval:: timeout error issues container locator not found, now confirm empty table')
        #     try:
        #         expect(self.returnedIssuesEmpty).to_be_visible(timeout=5000)
        #     except PlaywrightTimeoutError:
        #         LOGGER.exception(
        #             'WFOCaptureVerificationResultsPage: config_timeInterval:: timeout error retrieving capt verif table, nothing returned')
        #     else:
        #         emptyConfirmed = self.returnedIssuesEmpty.is_visible()
        #         if not emptyConfirmed:
        #             LOGGER.debug('WFOCaptureVerificationResultsPage: config_timeInterval:: confirmed issues table empty')
        #             print(
        #                 f'WFOCaptureVerificationResultsPage: config_timeInterval:: confirmed issues table empty: {emptyConfirmed}')
        #
        #         else:
        #             # if issues_listed = False then no issues in table container, confirm empty table
        #             LOGGER.debug('WFOCaptureVerificationResultsPage: config_timeInterval:: confirmed issues table no calls, confirm empty')
        #             print(
        #                 f'WFOCaptureVerificationResultsPage: config_timeInterval:: confirmed issues table no calls, confirm empty: {issues_listed}')
        #             if not issues_listed:
        #                 try:
        #                     expect(self.returnedIssuesEmpty).to_be_visible(timeout=5000)
        #                 except PlaywrightTimeoutError:
        #                     LOGGER.exception(
        #                     'WFOCaptureVerificationResultsPage: config_timeInterval:: timeout error retrieving capt verif table locators')
        #                     pytest.fail('error retrieving capture verification table')
        #                 else:
        #                     emptyConfirmed = self.returnedIssuesEmpty.is_visible()
        #                     if emptyConfirmed:
        #                         LOGGER.debug('WFOCaptureVerificationResultsPage: config_timeInterval:: confirmed issues table empty')
        #                         print(
        #                             f'WFOCaptureVerificationResultsPage: config_timeInterval:: confirmed issues table empty: {emptyConfirmed}')
        #                     else:
        #                         LOGGER.error('WFOCaptureVerificationResultsPage: config_timeInterval:: issue table has valid issues listed')
        #
        #


            # maybe put in new test to check if table populated??

            #expect((self.IssuesTableLoaded).first.or_(self.returnedIssuesEmpty)).to_be_visible(timeout=15000)
        LOGGER.debug('WFOCaptureVerificationResultsPage: config_timeInterval:: issue table loaded, select time menu')
        self.page.screenshot(path='./output/screenshot2.png')
        #attach('./output/screenshot2.png')

            #self.time_frame_pin.wait_for(timeout=5000)

            # end_time = datetime.now() + timedelta(seconds=25)   # 25s timeout for access time menu, enough time for any issues to load
            # LOGGER.debug('WFOCaptureVerificationResultsPage: config_timeInterval:: start time frame menu wait loop')
            # while not self.TimeFrame_bothRadioButtonFalse.is_visible():
            #     self.time_frame_select.wait_for(timeout=2000)
            #     self.time_frame_select.click()
            #     LOGGER.debug('WFOCaptureVerificationResultsPage: config_timeInterval:: time frame menu wait loop clicked time frame menu')
            #     if not self.time_frame_unpin.is_visible(timeout=2000):
            #         LOGGER.debug(
            #             'WFOCaptureVerificationResultsPage: config_timeInterval:: time frame menu wait loop unpin not visible, reselect time frame menu')
            #         self.time_frame_select.click()
            #         LOGGER.debug(
            #             'WFOCaptureVerificationResultsPage: config_timeInterval:: time frame menu wait loop clicked time frame menu ok')
            #         self.time_frame_pin.click(timeout=1000)
            #         LOGGER.debug('WFOCaptureVerificationResultsPage: config_timeInterval:: pinned time frame menu OK')
            #         break
            #     current_time = datetime.now()
            #     if current_time == end_time:
            #         LOGGER.error('WFOCaptureVerificationResultsPage: config_timeInterval method timeout time menu radio button access')
            #         break

            # record the active time interval radio button
            # if self.TimeFrame_bothRadioButtonTrue.is_checked(timeout=1000):
            #     self.activeRadioTimeFrame = self.TimeFrame_bothRadioButtonTrue.get_attribute('name')
            # else:
            #     self.activeRadioTimeFrame = self.TimeFrame_bothRadioButtonFalse.get_attribute('name')
            # LOGGER.debug('WFOCaptureVerificationResultsPage: config_timeInterval:: confirmed active radio button ')
            # print(f'WFOCaptureVerificationResultsPage: config_timeInterval:: confirmed active radio button: {self.activeRadioTimeFrame}')

    # 2nd go to collect active radio

        LOGGER.debug(
            'WFOCaptureVerificationResultsPage: config_timeInterval re-pin time frame after random hours table loaded')

        pin_status = self.pinTimeFrameMenu()
        print(
            f'WFOCaptureVerificationResultsPage: config_timeInterval:: previous time frame was last, inject random hours: {pin_status}')

    # query radio buttons
        try:
                 #expect(self.IssuesTableLoaded).to_be_visible(timeout=25000).or_expect(self.returnedIssuesEmpty).to_be_visible(timeout=10000)
                 #expect(self.IssuesTableLoaded).or_(self.returnedIssuesEmpty).to_be_visible(timeout=25000)
                 #self.lastRadio_disabled.is_disabled(timeout=10000)

                 #expect(self.lastRadio_disabled).to_be_disabled(timeout=25000).or_expect(
                     #self.fromRadio_disabled).to_be_visible(timeout=25000)

            self.lastRadio_disabled.wait_for(timeout=10000, state = 'visible')
            self.lastRadio_disabled.is_disabled(timeout=10000)

                 ####expect((self.IssuesTableLoaded).first.or_(self.returnedIssuesEmpty)).to_be_visible(timeout=25000)
                 # expect((self.IssuesTableLoaded).first.or_(self.returnedIssuesEmpty)).to_be_visible(timeout=15000)
        except PlaywrightTimeoutError:

            LOGGER.exception('WFOCaptureVerificationResultsPage: config_timeInterval:: timeout error retrieving last radio button status, check from status')

            try:
            #self.fromRadio_disabled.is_visible(timeout=10000)
                self.fromRadio_disabled.wait_for(timeout=10000, state = 'visible')
                expect(self.fromRadio_disabled).to_be_visible(timeout=10000)

            except PlaywrightTimeoutError:
                LOGGER.exception(
                         'WFOCaptureVerificationResultsPage: config_timeInterval:: timeout error retrieving from radio button status')
            else:

                self.activeRadioTimeFrame = 'last'
                LOGGER.debug('WFOCaptureVerificationResultsPage: config_timeInterval::  from Radio button status disabled')

        else:

            self.activeRadioTimeFrame = 'from'
            LOGGER.debug('WFOCaptureVerificationResultsPage: config_timeInterval:: last Radio button status disabled')

        finally:
            LOGGER.debug('WFOCaptureVerificationResultsPage: config_timeInterval:: radio button check complete')


            # try:
            #     self.lastRadio_disabled.is_disabled(timeout=1000)
            # except PlaywrightTimeoutError:
            #
            #     self.activeRadioTimeFrame = 'from'
            # else:
            #     self.activeRadioTimeFrame = 'last'
            # LOGGER.debug('WFOCaptureVerificationResultsPage: config_timeInterval:: confirmed active radio button ')
            print(f'WFOCaptureVerificationResultsPage: config_timeInterval:: confirmed active radio button: {self.activeRadioTimeFrame}')

            #self.time_frame_select.click()
            #self.time_frame_pin.click()

            #LOGGER.debug('WFOCaptureVerificationResultsPage: config_timeInterval:: time frame menu select OK')

        # if last not active set it
        if self.activeRadioTimeFrame != 'last':
            # 'from' was active, apply 'last' config
            LOGGER.debug('WFOCaptureVerificationResultsPage: config_timeInterval:: previous time frame was interval')
            self.time_radio_last_2.click()
            self.time_config_box.clear()
            self.time_config_box.fill("24")  # inject non 24 value
            self.dropDownHoursSelect.click()
            self.time_apply_enabled.click()  # hit apply button, activate from profile
             # confirm Issues table loaded

            LOGGER.debug('WFOCaptureVerificationResultsPage:: config_timeInterval: (previously interval) last 24hr time profile now applied')

            # scenario where 'last' was configured, need re-inject last 24hr time profile

        else:
            LOGGER.debug('WFOCaptureVerificationResultsPage: config_timeInterval:: previous time frame was last, start re-inject last 24hr')
            # if time config menu not visible re-enable
            self.time_radio_last_2.click()
            self.time_config_box.wait_for(timeout=5000)
            box_text = int(self.time_config_box.get_attribute('value'))  # number of hours
            print(f'WFOCaptureVerificationResultsPage: config_timeInterval:: re-inject 24hrs: {box_text} ')
            self.time_dropDown_select.click()  # enable drop down to prepare selection
            #  will select hours
            box_test_1 = self.time_dropDown_select.text_content()   # hours or days?
            self.dropDownHoursSelect.click()  # select hours

            print(f'WFOCaptureVerificationResultsPage: config_timeInterval:: previous time frame was last: {box_text} {box_test_1}')

            list_hours = list(range(1, 700))  # 720 is max value that can be applied
            new_list_hours = [el for el in list_hours if el != box_text]
            random_number = random.choice(new_list_hours)
            # if last enabled but equal to 24hours, need to change to random x hours then back to 24hours to
            # drive new 24hour profile

            # inject a random integer for number of hours not equal current number of hours

            print(f'WFOCaptureVerificationResultsPage: config_timeInterval:: previous time frame was last, inject random hours: {random_number}')
            # clear hours box
            self.time_config_box.clear()
            LOGGER.debug('WFOCaptureVerificationResultsPage: config_timeInterval previous time frame was last, inject random hours, cleared time box in prep')

            self.time_config_box.fill(str(random_number))  # inject random hours, needs string
            # apply the changes
            LOGGER.debug('WFOCaptureVerificationResultsPage: config_timeInterval previous time frame was last, inject random hours, filled time box in prep')

            self.time_apply_enabled.wait_for(timeout=10000)
            LOGGER.debug('WFOCaptureVerificationResultsPage: config_timeInterval previous time frame was last, inject random hours, apply button available to click')

            self.time_apply_enabled.click(timeout=10000)
            LOGGER.debug('WFOCaptureVerificationResultsPage: config_timeInterval previous time frame was last, inject random hours, apply clicked and completed ok')

            #self.time_apply_enabled.click()  # hit apply button
            #LOGGER.debug('WFOCaptureVerificationResultsPage: config_timeInterval previous time frame was last, inject random hours, random applied ok')
            # now inject 24 , hours already selected, pin time menu again

            # wait until results page loaded
            LOGGER.debug('WFOCaptureVerificationResultsPage: config_timeInterval wait random hours results loaded ok')

            emptyConfirmed = 'null'
            issues_listed = 'null'
            emptyConfirmed, issues_listed = self.checkIssueTable()
            print(f'WFOCaptureVerificationResultsPage: config_timeInterval:: random hours issues table loaded, emptyConfirmed, issues_loaded: {emptyConfirmed} , {issues_listed}')

            LOGGER.debug(
                    'WFOCaptureVerificationResultsPage: config_timeInterval re-pin time frame after random hours table loaded')

            pin_status = self.pinTimeFrameMenu()
            print(f'WFOCaptureVerificationResultsPage: config_timeInterval:: previous time frame was last, inject random hours: {pin_status}')

            LOGGER.debug(
                    'WFOCaptureVerificationResultsPage: config_timeInterval previous time frame was last, inject random hours completed and applied, pin time frame completed OK')


                #self.time_frame_select.wait_for(timeout=2000)
                #self.time_frame_select.click()

                # try:
                #     self.time_frame_pin.click()
                #
                # except PlaywrightTimeoutError:
                #     LOGGER.exception(
                #         'WFOCaptureVerificationResultsPage: config_timeInterval:: time menu not pinned, reselect time menu')
                #     self.time_frame_select.wait_for(timeout=2000)
                #     self.time_frame_pin.click()
                #
                # else:
                #     LOGGER.debug('WFOCaptureVerificationResultsPage: config_timeInterval:: time menu pinned successfully')

            #self.time_frame_select.click()
            self.time_config_box.clear()
            LOGGER.debug('WFOCaptureVerificationResultsPage: config_timeInterval previous time frame was last, inject random hours, cleared time box')

            self.time_config_box.fill("24")  # inject  24hr value
            LOGGER.debug(
                        'WFOCaptureVerificationResultsPage: config_timeInterval previous time frame was last, inject random hours, 24hrs injected ok, try hit apply')
            # apply the changes
            self.time_apply_enabled.wait_for(timeout=10000, state='visible')
            LOGGER.debug(
                        'WFOCaptureVerificationResultsPage: config_timeInterval previous time frame was last, inject random hours, 24 injected, apply button available')
            self.time_apply_enabled.click(timeout=10000)

            LOGGER.debug('WFOCaptureVerificationResultsPage: config_timeInterval:: previous time frame was last, re-inject random hrs then last 24hr completed OK')

            # confirm issue table loaded
            # expect(self.IssuesTableLoaded.or_(self.returnedIssuesEmpty).first).to_be_visible(timeout=10000)

        LOGGER.info('WFOCaptureVerificationResultsPage: config_timeInterval method finished')
        self.page.screenshot(path='./output/screenshot3.png')

        return

    def check_recordings_found(self, time_out) -> str:
        LOGGER.info('WFOCaptureVerificationResultsPage: check_recordings_found method start')

        """look for calls found with ACV issues"""
        return_value = 'none'

        # check issues list is stable
        self.checkIssueTable()

        try:
            #self.IssuesTable.wait_for()         # Issues table
            self.foundCalls.page.wait_for_load_state()
            self.foundCalls.wait_for(timeout=time_out, state='visible') # check if 'found' located
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
            self.page.screenshot(path='./output/screenshot4.png')
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

