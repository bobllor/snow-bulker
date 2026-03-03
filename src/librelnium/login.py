from .driver import Driver
from getpass import getpass
from typing import TypedDict, get_args
from .support.types import Locator
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys

class LoginElements(TypedDict):
    '''Type to hold the login WebElements. 
    
    These are expected to be the properties of DOM elements, 
    such as `classes`, `IDs`, or `CSS selectors`.

    The button element is optional. If omitted, then the WebDriver will
    hit the enter key instead of hitting the button.

    Example: `#user_fmt` - ID of an HTML element 
    '''
    user_element: str
    password_element: str
    button_element: str | None

class Login(Driver):
    def __init__(self, driver):
        '''Class used to login.
        Parameters
        ----------
            driver: WebDriver
                Any WebDriver.
        '''
        super().__init__(driver)
    
    def login(self,
        elements: LoginElements,
        *,
        locators: list[Locator] = [],
        multi_page: bool = False,
        frame: str = None,
        username: str = None,
        password: str = None,
        show_username: bool = False,
        ):
        '''
        Starts the login process. This does not handle MFA or additional pages after a login.

        Parameters
        ----------
            elements: LoginElements
                A dictionary containing the DOM element properties for LoginElements. The DOM element
                for the button is not required.
            
            locators: list[Locator]
                A list of locators used for the DOM element attribute. The list is expected to have these in values
                in order: username locator, password locator, and button locator. The list is expected
                to be the same length as `elements`. If the list is less than `elements` or the list has invalid
                Locator values, then it will fill the values with `css selector`. If the list is greater than
                `elements`, then only the first three elements are used.
            
            multi_page: bool
                Indicates if the login is a multi-page/step login. Used if the username and password are on separate
                pages rather than all on one page.

            frame: str
                An attribute of the DOM element of a frame on the page. If a value is given, the driver 
                will switch to the frame.

            username: str, default `None`
                Default is `None` which prompts a manual input if no value is passed.
        
            password: str
                Default is `None` which prompts a manual input if no value is passed. 
                The input for `password` is hidden.
            
            show_username: bool
                If true, the username will be visible in the terminal. By default this is false.
                This only applies if username is `None`.
        '''
        if username is None:
            if show_username:
                username = getpass('Enter your username: ')
            else:
                username = input("Enter your username: ")
        if password is None:
            password = getpass('Enter your password: ')

        if frame is not None:
            self.switch_frames(frame)
        
        if len(locators) > 3:
            locators = locators[0:2]
        elif len(locators) < 3:
            for _ in range(3 - len(locators)):
                locators.append("css selector")
        temp: list[Locator] = []
        for loc in locators:
            loc_t: Locator = loc.lower()

            if loc_t in {base_loc for base_loc in get_args(Locator)}:
                temp.append(loc_t)
            else:
                temp.append("css selector")
        locators = temp

        user_element: WebElement = self.find_element(locators[0], elements["user_element"])
        self.send_keys(username, element=user_element, pause=.7)

        if multi_page:
            self.send_keys(Keys.ENTER, pause=1)

        pw_element: WebElement | None = self.find_element(locators[1], elements["password_element"], return_none=True)

        if pw_element is not None:
            self.send_keys(password, element=pw_element, pause=.7)
        
        # locators[2] only matters if button is not None
        found_button: bool = False
        if elements.get("button_element") is not None:
            button_element: WebElement | None = self.find_element(locators[-1], elements["button_element"], return_none=True)

            if button_element is not None:
                button_element.click()
                found_button = True

        if not found_button:
            self.send_keys(Keys.ENTER, pause=0.5)