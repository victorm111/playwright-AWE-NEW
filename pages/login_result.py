# login_result.py
# The search.py and login_result.py modules will contain the search and
# result page object classes respectively.

from playwright.sync_api import Page


# Add a class definition for the results page object
class WFOLoginResultPage:

    def __init__(self, page: Page) -> None:
        self.page = page
        self.username_loggedIn = page.locator('#prefButton-btnInnerEl')
        self.dropDownArrow = page.locator('#as-navdrawer-arrow-btnInnerEl')
        self.user_details = self.username_loggedIn.text_content()
        self.loggedInTitle = self.page.title()
        return

    def result_login_user(self) -> str:  # return username shown after logged in OK
        # wait for blue arrow button to be visible
        self.dropDownArrow.wait_for(timeout=0)
        # check for username field
        self.username_loggedIn.wait_for()
        return self.username_loggedIn.text_content()

    def result_login_title(self) -> str:        # return get page title
        return self.loggedInTitle
