from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.shadowroot import ShadowRoot
from selenium.common.exceptions import TimeoutException, NoSuchFrameException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from typing import Any, Literal
from .support.types import Locator, Options
import selenium.webdriver.chrome.webdriver as chrome
import selenium.webdriver.firefox.webdriver as firefox
import time

type Drivers = Literal["chrome", "firefox"]

class Driver:
    '''Base class for WebDriver related navigation and methods.'''
    def __init__(self, 
    driver: Drivers = "chrome", 
    *, 
    options: Options = None,
    wait_timer: int = 10,):
        '''
        Parameters
        ----------
            driver: Drivers
                A string representing the driver to choose. By default it
                uses ChromeDriver with `chrome`.
            
            options: Options
                An object that contains keys for the options to enable for the driver. By default
                it is None.

            wait_timer: int
                The default time to wait for finding elements in seconds. If the timer
                reaches the given number then a TimeoutException is raised. By default it is 10 seconds.
        '''
        if driver == 'chrome':
            chrome_options: ChromeOptions = ChromeOptions()
            if options is not None:
                if options.get("headless", False):
                    chrome_options.add_argument("--headless=new")

                if options.get("silent", False):
                    chrome_options.add_argument('--log-level=3')
                    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
                    chrome_options.add_argument('--disable-logging')

            driver = chrome.WebDriver(options=chrome_options)
        elif driver == 'firefox':
            ff_options: FirefoxOptions = FirefoxOptions()
            if options is not None:
                if options.get("headless", False):
                    ff_options.add_argument("headless")

                if options.get("silent", False):
                    ff_options.log.level = "fatal"
            driver = firefox.WebDriver(options=options)
        
        self.driver: WebDriver = driver
        
        self.driver_wait: WebDriverWait = WebDriverWait(self.driver, wait_timer)
        self.action_driver: ActionChains = ActionChains(self.driver)
        
    def set_wait_timer(self, value: float | int) -> None:
        '''Sets the wait timer for WebDriverWait. This effects the max time in
        seconds before a `TimeoutException` occurs while finding a DOM element.

        Parameters
        -----------
            value: float | int
                The wait time in seconds, it can be a float or integer.
        '''
        self.driver_wait = WebDriverWait(self.driver, value)
    
    def send_keys(self, key: str, 
        *, 
        element: WebElement = None, 
        pause: int | float = 0, 
        pre_pause: int | float = 0
        ) -> ActionChains:
        '''Uses the action driver or WebElement to send a key. It will return the
        final state of the action driver, which is after sending the keys has been
        performed.
        
        Parameters
        ----------
            key: str
                The key to send to the action driver.
            
            pause: int | float
                A number used to pause the action driver after sending the key. By default
                it is 0 seconds.
            
            pre_pause: int | float
                A number used to pause the action driver before sending the key. By default
                it is 0 seconds.
        '''
        if element is None:
            return self.action_driver.pause(pre_pause).send_keys(key).pause(pause).perform()
        else:
            return self.action_driver.pause(pre_pause).send_keys_to_element(element, key).pause(pause).perform()
    
    def click(self, element: WebElement, *, pause: int | float = 0, pre_pause: int | float = 0) -> ActionChains:
        '''Clicks on the given element.
        
        Parameters
        ----------
            element: WebElement
                The WebElement.
            
            pause: int | float
                The time used to pause the action after it is performed. By default it
                is 0 seconds.
            
            pre_pause: int | float
                The time used to pause the action before it is performed. By default it
                is 0 seconds.
        '''
        return self.action_driver.pause(pre_pause).click(element).pause(pause).perform()
    
    def go_to(self, url: str) -> None:
        '''Sends the driver to a URL.'''
        if not isinstance(url, str):
            raise TypeError(f'Expected url to be type str but got {type(url)}')
        
        self.driver.get(url)
    
    def switch_frames(self, frame_name: str | WebElement = 'gsft_main', *, return_default: bool = True):
        '''Switch frames on the current page. If the frame isn't found, it will remain on the default frame
        of the page.

        Parameters
        ----------
            frame_name: str | WebElement
                The name of the frame to switch to, it can be a string or a WebElement.
                By default the value is `gsft_main`.

            return_default: bool 
                Switch the drive back to the default frame of the page before switching to a new frame.
                Default is `True`.
        '''
        if return_default:
            self.driver.switch_to.default_content()
        
        try:
            self.driver_wait.until(
                EC.frame_to_be_available_and_switch_to_it
                    (self.driver.switch_to.frame(frame_name))
                )
        except (TimeoutException, NoSuchFrameException):
            self.driver.switch_to.default_content()
    
    def switch_default_frame(self):
        '''Returns the driver back to the default frame.'''
        self.driver.switch_to.default_content()
    
    def get_shadowroot_element(self, locator: str | By = By.CSS_SELECTOR, *, html_elements: list[str] = None) -> ShadowRoot:
        '''Returns a ShadowRoot of the last element in the list.
        
        Parameters
        ----------
            by: str | By
                Locator strategy, can use the literal string equivalent or the By strategy. 
                By default it locates by `css selector`.

            html_elements: list[str]
                Any list structure containing HTML elements that contains a shadow root.
        '''
        if not any(isinstance(element, str) for element in html_elements):
            raise TypeError('Got unexpected type in html_elements')

        if len(html_elements) < 1:
            raise ValueError(f'Cannot have an empty iterable, got {len(html_elements)} size')
        
        sr = self.driver.find_element(locator, html_elements[0]).shadow_root
        
        if len(html_elements) > 1:
            for s_root in html_elements[1:]:
                sr = sr.find_element(locator, s_root).shadow_root

        return sr
    
    def navigate_shadowroot(self, locator: str | By = By.CSS_SELECTOR, html_elements: list[str] = None):
        '''Navigates the driver into a ShadowRoot that contains an iframe. This methods assumes the last
        element in the list will have an iframe.

        If attempting to search in a ShadowRoot, it is better to use `get_shadowroot_element` for the
        ShadowRoot. Shadow roots do not have an ID for the driver to switch focus to.
        
        Parameters
        ----------
            by: str | By
                Locator strategy, can use the literal string equivalent or the By strategy. 
                By default it locates by `css selector`.

            html_elements: list[str]
                Any list structure containing HTML elements that contains a shadow root.
        '''
        if not all(isinstance(element, str) for element in html_elements):
            raise TypeError('Got unexpected type in html_elements')

        if len(html_elements) < 1:
            raise ValueError(f'Cannot have an empty iterable, got {len(html_elements)} size')
        
        sr = self.driver.find_element(locator, html_elements[0]).shadow_root
        
        if len(html_elements) > 1:
            for s_root in html_elements[1:]:
                sr = sr.find_element(locator, s_root).shadow_root

        self.switch_frames(sr.find_element(By.CSS_SELECTOR, 'iframe'))
            
    def find_element(self, locator: Locator = "id", value: str = None, *, return_none: bool = False) -> WebElement:
        '''Returns a WebElement if found using the value and locator. 

        If no element is found, a `TimeoutException` exception is raised. This can return None if
        `return_none` is true.
        
        Parameters
        ----------
            by: str | By
                Locator strategy, can use the literal string equivalent or the By strategy. 
                By default it locates by `id`.

            value: str
                The attribute of a HTML element. This can be any `str` value that matches the locator strategy.
            
            return_none: bool
                If true, then return `None` when the `TimeoutException` occurs. By default it is false.
        '''
        if not isinstance(value, str):
            raise TypeError(f"Cannot perform operation on given value type '{type(value)}`")

        try:
            ele = self.driver_wait.until(EC.presence_of_element_located(
                (locator, value)
            ))
        except TimeoutException as exc:
            if return_none:
                return None

            raise exc
        
        return ele

    def find_elements(self, locator: str | By, value: str) -> list[WebElement]:
        '''Returns a list of WebElements containing all elements matching the value.
        If none found, then an empty list is returned.'''
        return self.driver.find_elements(locator, value)
    
    def scroll_to_element(self, web_element: WebElement, *,
                          main_scroll_element: str = None,
                          tags_to_scroll: list[str] = None,
                          css_properties: list[str] = None,
                          loop_limit: int = 20
                          ):
        '''Scroll to a web element on the page.

        If a web element is not visible, then this method will invoke JavaScript functions to scroll 
        to the element automatically. If found, the driver is positioned in a way where the element
        is interactable.
        
        Parameters
        ----------
            web_element: WebElement
                The Web Element on the given page.

            main_scroll_element: str
                The main container that enables scrolling on a page. This is used if the `web_element`
                is not visible on the page. This is used as an argument for a JavaScript function,
                which returns a `boolean` if the main page is scrollable. Primarily used to check 
                if a custom container is present. 
                By default, it is None. The default target is the document `body`.

            tags_to_scroll: list[str]
                A list of element tags that represents the scrollable container.
                At most it can only contain two elements.
                A JavaScript function is executed that returns a scrollable element.
                By default, it is None. It defaults to search all `div` elements on a page.

            css_properties: list[str]
                A list of CSS properties that can be found on an element.
                At most it can only contain two elements.
                These JavaScript function looks for the values 'auto' and 'scroll' for the property.
                By default, it is None. It defaults to search for the `overflow` property on an element.

            loop_limit: int
                A number representing the maximum loop count in a JavaScript function. This is used
                only if the `web_element` is not visible.
                By default it loops 20 times.
        '''
        # check if element is visible first
        element_visible: bool = self._execute_js('return arguments[0].checkVisibility();', web_element)

        if element_visible is False:
            self._inject_script('scroll-utils/is-scrollable.js')
            
             # the body is scrollable, e.g. the scroll is normal for a page.
            is_scrollable: bool = self._execute_js('return isScrollable();', main_scroll_element)

            if is_scrollable is False:
                self._inject_script('scroll-utils/find-scrollable-element.js')
                self._inject_script('scroll-utils/scroll-until-found.js')
                
                if tags_to_scroll is None or len(tags_to_scroll) == 0:
                    tags_to_scroll = ['div']

                if css_properties is None:
                    css_properties = ['overflow' for _ in range(len(tags_to_scroll))]

                scroll_elements = []

                for i, tag in enumerate(tags_to_scroll):
                    # parameters: elementTag, property
                    scroll = self._execute_js(
                        'return findScrollableElement(arguments[0], arguments[1])',
                        tag,
                        css_properties[i]
                    )

                    scroll_elements.append(scroll)

                # the next JS function expects a value or null as an argument, if the list is 1
                # then append None to the list.
                if len(scroll_elements) != 2:
                    scroll_elements.append(None)
                
                # parameters: scrollOne, scrollTwo, webElement, loopLimit
                self._execute_js(
                    'scrollUntilFound(arguments[0], arguments[1], arguments[2], arguments[3]);',
                    *scroll_elements,
                    web_element,
                    loop_limit
                )
                
                # loop used to ensure the JS function above completes.
                for i in range(loop_limit + 3):
                    if i % 3 == 0:
                        element_found: bool = self._execute_js(
                            'return arguments[0].checkVisibility()', web_element)
                    
                    if element_found:
                        break
                    
                    time.sleep(.5)

        self._execute_js('arguments[0].scrollIntoView()', web_element)
    
    def check_url(self, substring: str, *, throw: bool = False) -> bool:
        '''Checks if a substring is contained inside the current URL. It will return a
        bool indicating if the substring was found or not.

        The substring check is case sensitive.

        Parameters
        ----------
            substring: str
                The substring used to find in the current URL. 
            
            throw: bool
                Flag used to raise a TimeoutException. By default this is False and
                will return `False` if a TimeoutException occurs.
        '''
        msg: str = f"{substring} cannot be found in {self.driver.current_url}"
        try:
            return self.driver_wait.until(EC.url_contains(substring), msg)
        except TimeoutException as err:
            if not throw:
                return False
            
            raise err
    
    def is_visible(self, element: WebElement) -> bool:
        '''Returns True if a WebElement is inside the viewport of the driver.'''

        return self._execute_js('return arguments[0].checkVisibility()', element)

    def _inject_script(self, script_name: str):
        '''Inject a script into the current window. The path is automatically pointed to the `js_scripts`
        directory, the script_name is the directory and file name.
        
        A script must be using the Window API in order to keep it persistent in the window.
        '''
        # default location for scripts
        builder = ['librelnium/js_scripts/', script_name]

        with open(''.join(builder), 'r') as file:
            # maybe parse out comments? probably not needed in the long run.
            script = file.read()

        self._execute_js(script)
        
    def _traverse_html_elements(self, strategy: str | By, locators: list[str]) -> WebElement:
        '''Iterate through a list of locators and return the last WebElement.
    
        If not found, a `NoSuchElementException` exception is raised.
        '''
        element = self.find_element(strategy, value=locators[0])

        for i in locators[1:]:
            element = element.find_element(strategy, i)
        
        return element
    
    def _execute_js(self, js: str, *args: Any) -> WebElement:
        '''Execute JavaScript in the current window.'''
        return self.driver.execute_script(js, *args)
    
    def quit(self):
        '''Terminate the session.'''
        self.driver.quit()