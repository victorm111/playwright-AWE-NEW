# conftest.py
import logging

import datetime
import os
import sys
import json

import time as time
from datetime import date
from dotenv import load_dotenv

import pytest

import platform
import src.__init__     # contains sw version
import pytest_html
import yaml
import pandas as pd
from pytest_html_reporter import attach

from playwright.sync_api import expect, Page
from pages.login import WFOLoginPage
from pages.login_result import WFOLoginResultPage

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


# set expect timeout global
expect.set_options(timeout=10_000)

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)


@pytest.fixture(scope="function")
def test_read_config_file():

    LOGGER.debug('conftest:: test_read_config_file() start')
    cfgfile_parse_error = 0
    # create an Empty DataFrame object
    df_config = pd.DataFrame()

    try:
        with open("./config/config.yml", 'r') as file:
            test_config = yaml.safe_load(file)
            cfgfile_parse_error = 0

    except yaml.YAMLError as exc:
        print("!!! test_read_config_file(): Error in configuration file loading:", exc)
        cfgfile_parse_error = 1
        if hasattr(exc, 'problem_mark'):
            mark = exc.problem_mark
            print("**config.yaml file Error position: (%s:%s)" % (mark.line + 1, mark.column + 1))
    else:
        # Convert the YAML data to a Pandas DataFrame
        df_config = pd.DataFrame.from_dict(test_config)
        output_prefix_path = df_config['output_files']['output_prefix_path']

        # create env variable tracking home dir
        os.environ['home_dir'] = str(df_config['dirs']['working'])

    finally:
        # check config file read ok
        assert cfgfile_parse_error == 0, 'assert error test_read_config_file: yaml cfg file not read'  # if cfgfile_parse_error = 1
        print("test_read_config_file(): read finished OK")
        python_version = str(platform.python_version())
        pytest_version = str(pytest.__version__)
        testcode_version = str(src.__init__.__version__)
        LOGGER.debug(f'conftest:: python version: {python_version}')
        LOGGER.debug(f'conftest:: pytest version: , {pytest_version}')
        LOGGER.debug(f'conftest:: test code version: {testcode_version}')
        LOGGER.debug('conftest:: test_read_config_file() finished')

    yield df_config

@pytest.fixture(scope="function")
def load_context(page: Page, test_read_config_file) -> None:

    LOGGER.debug('conftest:: load_context: start ...')
    # load env variables from .env in root dir
    load_dotenv()
    # reset the storage env location
    os.environ["STORAGE"] = 'null'
    storage_state = 'null'

    # login to WFO with T0 credentials as per config.yml
    # first load the login page
    login_page = WFOLoginPage(page, test_read_config_file)
    # load the page
    login_page.load()
    # now login
    login_page.login()

    # retrieve login_result
    login_page_result = WFOLoginResultPage(page)

    # check username matches user configured in config.yml
    assert (login_page_result.username_loggedIn.text_content() == test_read_config_file['logon']['USERNAME_TA'])
    # store authentication info for other tests
    # Save storage state and store as an env variable
    storage = page.context.storage_state()
    os.environ["STORAGE"] = json.dumps(storage)
    storage_state = json.loads(os.environ["STORAGE"])
    assert os.environ["STORAGE"] != 'null'
    assert storage_state != 'null'

    page.close()
    page.context.close()
    LOGGER.debug('conftest:: load_context: yield storage_state ...')
    yield storage_state

# To create one log file for each worker with pytest-xdist,
# you can leverage PYTEST_XDIST_WORKER to generate a unique filename
# for each worker.
def pytest_configure(config):
    worker_id = os.environ.get("PYTEST_XDIST_WORKER")
    if worker_id is not None:
        logging.basicConfig(
            format=config.getini("log_file_format"),
            filename=f"tests_{worker_id}.log",
            level=config.getini("log_file_level"),
        )

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    extras = getattr(report, "extras", [])
    if report.when == "call":
        # always add url to report
        extras.append(pytest_html.extras.url("http://www.example.com/"))
        xfail = hasattr(report, "wasxfail")
        if (report.skipped and xfail) or (report.failed and not xfail):
            # only add additional html on failure
            extras.append(pytest_html.extras.html("<div>Additional HTML</div>"))
        report.extras = extras