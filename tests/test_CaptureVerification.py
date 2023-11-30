# separate class declared for each page

import logging
import os
import sys
import time as time
from datetime import date
import pytest
import glob

from playwright.sync_api import Browser

# from pages.search import DuckDuckGoSearchPage
# from pages.login_result import DuckDuckGoResultPage
from pages.CaptureVerification import WFOCaptureVerificationPage
from pages.CaptureVerification_results import WFOCaptureVerificationResultsPage

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
def test_CaptureVerification(browser: Browser, test_read_config_file, load_context, playwright) -> None:

    LOGGER.debug('test_CaptureVerification: start ...')

    # browser tracing
    # browser.start_tracing(screenshots=True, path='./output/browserTraceCaptureVerification.zip')
    # create new page object class
    CaptVerif_page = WFOCaptureVerificationPage(browser,  test_read_config_file, load_context, playwright)
    CaptVerif_page.context.browser.start_tracing(screenshots=True, path='./output/browserTraceCaptureVerification.zip')
    # playwright tracing
    CaptVerif_page.context.tracing.start(sources=True, screenshots=True, snapshots=True)
    # set browser context from saved login
    LOGGER.debug('test_CaptureVerification: load previous context')
    #assert(load_context != 'null')
    # CaptVerif_page.set_context(load_context)
    LOGGER.debug('test_CaptureVerification: load()')
    CaptVerif_page.load()
    # assert Issues sub menu found
    LOGGER.debug('test_CaptureVerification: assert Issues submenu found')
    assert(CaptVerif_page.IssuesMenuFound())
    # search page access portion finished, now search and replay access
    LOGGER.debug('test_CaptureVerification: close Capture Verification page context')
    # gracefully close up everything
    CaptVerif_page.context.tracing.stop(path="./output/CaptureVerif.zip")
    CaptVerif_page.context.browser.stop_tracing()
    CaptVerif_page.page.close()
    CaptVerif_page.context.close()

    LOGGER.debug('test_CaptureVerification: new Capture Verification results context')
    CaptureVerificationResults_page = WFOCaptureVerificationResultsPage(browser, test_read_config_file, load_context, playwright)
    CaptureVerificationResults_page.context.browser.start_tracing(screenshots=True, path='./output/browserTraceCaptureVerificationResults.zip')
    #CaptureVerificationResults_page.context.tracing.start(sources=True, screenshots=True, snapshots=True)
    LOGGER.debug('test_CaptureVerification: load results page')
    CaptureVerificationResults_page.load()
    # Check side menu items are visible, indicates page loaded
    # need check for page selector
    dump_html = CaptureVerificationResults_page.checkLeftMenuAvailable()

    fname = './output/html_dump_beforeSetTimeInterval.html'
    #dump_html = CaptureVerificationResults_page.page.content()
    with open(fname, "w", encoding="utf-8") as f:
        f.write(dump_html)

    # configure time interval
    CaptureVerificationResults_page.config_timeInterval()
    call_issues = 'none'
    # if call issues found means call errors, flag as test fail
    call_issues = CaptureVerificationResults_page.check_recordings_found(time_out=10000)
    # null returned if timeout or exception retrieving issues table
    try:
        assert call_issues == 'null'    # call_issues = 'null' if no issues found

    except AssertionError:
        if call_issues != 'null':
            LOGGER.exception('test_CaptureVerification: call issues found, downloadCSV')
            CaptureVerificationResults_page.downloadCSVStart()
            LOGGER.exception('test_CaptureVerification: close Results page')
            #CaptureVerificationResults_page.context.tracing.stop(path="./output/CaptureVerifResults.zip")
            pytest.fail('call recording errors in Capture Verification')
    else:
        LOGGER.info('test_CaptureVerification *** : test finished, no call recording issues, test passed')
    finally:
        # stop tracing
        #CaptureVerificationResults_page.context.tracing.stop(path="./output/CaptureVerifResults.zip")
        CaptureVerificationResults_page.context.browser.stop_tracing()
        CaptureVerificationResults_page.page.close()
        CaptureVerificationResults_page.context.close()
        LOGGER.info('test_CaptureVerification *** : test finished, no call recording issues, test finished and wrap up complete')
