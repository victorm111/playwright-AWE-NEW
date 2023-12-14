# login.py
# The login.py file will contain the AWE login object classe
from playwright.sync_api import expect,Page
import logging
import os
import sys
import time as time
from datetime import date
import pytest
import pytest_playwright

from datetime import datetime
from dotenv import load_dotenv

# load env variables from .env in root dir
load_dotenv()

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

# import Playwright's Page class
from playwright.sync_api import Page

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
class WFOLoginPage():

    def __init__(self, page: Page, test_read_config_file) -> None:
        LOGGER.info('WFOLoginPage: init class')
        self.page = page
        self.title = 'WFO login page'
        self.author = 'VW'
        self.URL = test_read_config_file['urls']['AWE']
        self.username = test_read_config_file['logon']['USERNAME_TA']
        self.password = test_read_config_file['logon']['PASSWORD_TA']
        self.login_button = page.locator('#kc-login')
        self.login_button_selector = '#kc-login'
        self.username_field_first = page.locator('#username')
        self.username_field_first_selector = '#username'
        self.username_field_second = page.locator('#username')
        self.username_field_second_selector = '#username'
        self.password_field_second = page.locator('#password')
        self.signIn_button = page.locator('.loginButtonLabel')
        self.signIn_button_selector = '.loginButtonLabel'
        return


        def __repr__(self):
            class_name = type(self).__name__
            return f"{class_name}(title={self.title!r}, author={self.author!r})"

        def __str__(self):
            return self.title

    def load(self) -> None:
        LOGGER.info('WFOLoginPage: load method, open URL')
        self.page.goto(self.URL)
        self.page.once("load", lambda: LOGGER.debug('WFOLoginPage: URL loaded successfully'))
        self.page.screenshot(path="output/screenshot-WFOLoginPageLoaded.png")
        return

    def login(self) -> None:
        LOGGER.info('WFOLoginPage: login method')
        self.page.wait_for_selector(self.username_field_first_selector)
        self.username_field_first.fill(self.username)
        #self.page.wait_for_selector(self.signIn_button_selector)
        self.signIn_button.click()
        self.page.screenshot(path="output/screenshot-secondLogin.png")
        self.page.wait_for_selector(self.username_field_second_selector)
        self.username_field_second.fill(self.username)
        self.password_field_second.fill(self.password)
        #self.page.wait_for_selector(self.login_button_selector)
        self.login_button.click()
        self.page.screenshot(path="output/screenshot-loggedIn.png")
        return
