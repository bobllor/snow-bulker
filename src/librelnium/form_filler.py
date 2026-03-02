from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from .driver import Driver
import time

class FormFiller(Driver):
    def __init__(self, driver):
        super().__init__(driver)
    
    def fill_fields(self, values_info: list[tuple[str, str, str]], *, sleep_time: float | int = 0) -> None:
        '''Fill the fields of a given page. The driver assumes it is already on the page.

        This method **does not** submit an entry, invoke the `submit` method instead.
        
        Errors on the user creation page are not handled in this method. 
        Use the method `check_errors` instead.
        
        Parameters
        ----------
            values_info: list[tuple[str, str, str]]
                A list of tuples that are in order of (VALUE, HTML_ELEMENT, LOCATOR) where the
                VALUE will be inserted into the HTML_ELEMENT by searching the LOCATOR.
                For example: ('USER_EMAIL', 'user.email', By.ID), will insert
                'USER_EMAIL' at the HTML element with the ID 'user.email'.

            sleep_time: float | int
                Time used to delay each key insertion to the DOM element. By default it has
                no delay.
        '''
        # tup[0] is the value, tup[1] is the HTML value, tup[2] is the locator strategy. 
        for tup in values_info:
            element: WebElement = self.find_element(tup[2], tup[1])
            
            element.send_keys(tup[0])

            time.sleep(sleep_time)

    def submit(self, submit_element: str, *, locator: str | By = By.ID) -> None:
        '''Presses the submit button on the form entry page.
        
        Parameters
        ----------
            submit_element: str
                The HTML of the element that represents the save/submit button to
                insert the user into the database.

            by: str | By
                The locator used to find the element. By default it is By.ID.
        '''
        submit_element: WebElement = self.find_element(locator, submit_element)

        submit_element.click()

    def check_errors(self, error_elements: list[tuple[str, str]]) -> list[str]:
        '''Checks the page for errors and return a list of strings representing
        the text of the error messages.
        
        Parameters
        ----------
            error_html_elements: list[tuple[str, str]]
                A list of tuples that contain (HTML_ELEMENT, LOCATOR) used to locate and extract
                information from the errors in the DOM.
        '''
        errors = []

        for tup in error_elements:
            # find_elements work better at the cost of readability and complexity
            # up for debate to be honest. also the O(m * n) complexity. i probably have brain worms.
            error_elements: list[WebElement] = self.driver.find_elements(tup[1], tup[0])

            if len(error_elements) > 0:
                for element in error_elements:
                    errors.append(element.text)

        return errors