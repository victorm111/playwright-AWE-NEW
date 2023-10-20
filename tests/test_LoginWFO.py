from playwright.sync_api import expect, Page
import logging
import pytest
import sys
import os
import json
from dotenv import load_dotenv

# from pages.search import DuckDuckGoSearchPage
# from pages.login_result import DuckDuckGoResultPage
from pages.login import WFOLoginPage
from pages.login_result import WFOLoginResultPage

import time as time
from datetime import date

# load env variables from .env in root dir
load_dotenv()

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



@pytest.mark.skip(reason="no way of currently testing this")
def test_login(page: Page, test_read_config_file) -> None:

    LOGGER.debug('test_login: start ...')
    # Start tracing before navigating a page.
    page.context.tracing.start(screenshots=True, snapshots=True, sources=True)
    login_page = WFOLoginPage(page, test_read_config_file)
    #search_page = DuckDuckGoSearchPage(page, test_read_config_file)
    LOGGER.debug('test_login: print search page')
    print(repr(login_page))
    #result_page = DuckDuckGoResultPage(page)

    # Given the WFO home page is displayed
    LOGGER.debug('test_login: load()')
    login_page.load()

    # attempt user login
    LOGGER.debug('test_login: login()')
    login_page.login()

    # retrieve login_result
    login_page_result = WFOLoginResultPage(page)

    LOGGER.debug('test_login: expect user to be visible in top right')


    # check username matches user configured in config.yml
    assert(login_page_result.username_loggedIn.text_content() == test_read_config_file['logon']['USERNAME_TA'])
    # And the logged in page title is correct
    LOGGER.debug('test_login: assert logged in page title correct')
    assert(login_page_result.result_login_title() == 'Workforce Engagement - Dashboards')

    # store authentication info for other tests
    # Save storage state and store as an env variable
    storage = page.context.storage_state()
    os.environ["STORAGE"] = json.dumps(storage)


    # Stop tracing and export it into a zip archive.
    # view trace at trace.playwright.dev
    page.context.tracing.stop(path = "./output/context-trace-LOGIN.zip")
    page.close()


