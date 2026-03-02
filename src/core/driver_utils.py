from src.librelnium.driver import Driver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
from src.support.types import Result
from typing import ParamSpec, TypeVar, Callable
import time

class DriverUtils:
    def __init__(self, driver: Driver):
        self.driver: Driver = driver

    def clear_field(self, element: WebElement) -> None:
        '''Used to clear fields from an HTML element.'''
        self.driver.action_driver.click(element).key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL)\
            .send_keys(Keys.BACKSPACE).pause(.5).perform()

    def get_element_css(self, value: str) -> WebElement:
        '''Get a WebElement from the DOM by using a CSS selector.'''
        return self.driver.find_element("css selector", value)
    
    def handle_dropdown(self,
            value: str | WebElement,
            *,
            key: str, 
            send_down: bool = False,
            send_enter: bool = False, 
            send_tab: bool = False,
            wait_time: int | float = .5) -> None:
        '''Handles the special dropdown menu with certain fields. It requires the element
        and the key to send to the element.

        The process is done by clicking on the element, then sending keys while the input is active.
        This bypasses the need to click additional elements.
        
        Parameters
        ----------
            value: str | WebElement
                The string or WebElement that represents an HTML element. This **must be in written 
                as a CSS selector** if a string is passed as an argument.
            
            key: str
                The key that is sent to the WebDriver as the value on the element.
            
            send_down: bool, default `False`
                Boolean that indicates whether or not to hit the down arrow key. By default it is False. If True,
                then send_enter will automatically be True.
                
            send_enter: bool, default `False`
                Boolean that indicates whether or not to hit the Enter key after sending the key to the field.
                By default it is False. It will be automatically True if send_down is True.
            
            send_tab: bool, default `False`
                Boolean that indicates whether or not to hit the Tab key after sending the key to the field.
                By default it is False.

            wait_time: int | float, default `.5`
                The wait time before the Enter key is submitted. It is recommended to keep this at a minimum 0.3 seconds
                to avoid raising an ElementIntercepted exception. By default it is 0.5 seconds.
        '''
        if isinstance(value, str):
            self.driver.find_element("css selector", value).click()
        elif isinstance(value, WebElement):
            value.click()
            
        self.driver.action_driver.send_keys(key).perform()

        if send_down:
            self.driver.action_driver.pause(wait_time).send_keys(Keys.ARROW_DOWN).perform()
            
            send_enter = True
        if send_enter:
            self.driver.action_driver.pause(wait_time).send_keys(Keys.ENTER).perform()
        if send_tab:
            self.driver.action_driver.pause(wait_time).send_keys(Keys.TAB).perform()

        time.sleep(wait_time)

P = ParamSpec("P") 
R = TypeVar("R")
    
def driver_wrapper(func: Callable[P, R]) -> Callable[P, R]:
    '''Wraps a Selenium-related function with common exception issues and captures it into a
    Result.
    '''
    # exception messages
    EXC_FAIL_FIND_ELE_MSG: str = "Driver failed to find target element"
    EXC_INTERCEPT_MSG: str = "Target element was intercepted, an unknown element is covering the target element"

    def wrapper(*args):
        res: Result = Result()
        try:
            res = func(*args, res)
        except (NoSuchElementException, TimeoutException):
            res.msg = EXC_FAIL_FIND_ELE_MSG
            res.err = True
        except ElementClickInterceptedException:
            res.msg = EXC_INTERCEPT_MSG
            res.err = True

        return res

    return wrapper