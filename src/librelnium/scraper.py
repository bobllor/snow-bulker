from .driver import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException
from .support.utils import is_list_tuple

class Scraper(Driver):
    '''Class to scrape and interact with pages.'''
    def __init__(self, driver):
        super().__init__(driver)

    def get_element_attribute(self, html_elements: list[str], *, locator: str | By = By.ID, attribute: str = 'value') -> str:
        '''Get the attribute of an HTML element.
        
        Parameters
        ----------
            html_elements: list[str]
                A list of HTML elements used to get an attribute of an element. The last element in the list
                is where the search is being performed on. If more than one element is given, the method
                assumes it is a nested element and navigates the tree accordingly.

            locator: str | By, default 'id'
                The locator used to search for the element. By default it searches by ID.

            attribute: str, default 'value'
                The HTML attribute to get the value from. By default is retrieves the `value` attribute.
        '''
        web_ele: WebElement = self._traverse_html_elements(locator, html_elements)

        return web_ele.get_attribute(attribute)
    
    def get_element(self, *, strategy: str | By = By.ID, locator: str) -> WebElement:
        '''Return a WebElement with the given strategy and locator.
        
        Parameters
        ----------
            strategy: str | By, default 'id'
                The locator strategy used to find the element.

            locator: str
                The locator for an HTML element.
        '''
        return self.find_element(strategy, locator)
    
    def get_elements(self, locators: list[tuple[str, str] | str] | tuple[tuple[str, str] | str, ...]) -> list[WebElement]:
        '''Returns a list of WebElements based on the last locator in the list. The first value of 
        
        If multiple locators are given, then the method will assume the last locator is the TARGET
        and will navigate each item where the list of elements matching the TARGET is returned by
        searching the second to last locator.

        Parameters
        ----------
            locators: list[tuple[str,str] | str]
                A list of locators, consisting of either:
                    1. A tuple consisting of two strings, `[STRATEGY, LOCATOR]`. The `STRATEGY` represents
                    the locator strategy (By.XPATH, 'xpath') and `LOCATOR` represents the locator string
                    (e.g. '//div[@id="some-id-here"]').
                    2. A string representing a locator. If used, the method will use the previous
                    strategy specified from a tuple.
                
                The first element in `locators` **must be a tuple**, while each subsequent element can
                be a tuple (with a new strategy) or a string.
        '''
        if not is_list_tuple(locators[0]):
            raise ValueError(f'Got unexpected type {type(locators[0])}, expected type list or tuple.')
        
        first_locator: str = locators.pop(0)

        if not all([isinstance(item, str) for item in first_locator]):
            raise TypeError('Got unexpected type in locators, expected type str')

        strategy: str = first_locator[0]
        locator: str = first_locator[1]

        # this does nothing but ensure the page loads, if it fails then an exception is thrown
        self.find_element(strategy, locator)

        if len(locators) > 0:
            last_locator = locators.pop()

            # returns a strategy and locator.
            traversal_data = self._traverse_locators(strategy, locator, locators)
            
            # tuple means a new selector -> replace old selector
            if isinstance(last_locator, tuple):
                strategy = last_locator[0]
                locator = last_locator[1]
            else:
                # traversal_data can either be the original strategy or a new one, depending
                # on the values inside the locators list.
                strategy = traversal_data[0]
                locator = last_locator
            
            element: WebElement = traversal_data[1]

            return element.find_elements(strategy, locator)
            
        return self.find_elements(strategy, locator)
    
    def search_text(self, search_val: str) -> WebElement | None:
        '''Searches for a text and returns a WebElement matching the text.
        If not found, None is returned.

        It uses the XML function `contains()` to get the result, which is **case sensitive**.
        
        Parameters
        ----------
            search_val: str
                Text that can be found in the card container on the VTB. The elements returned from
                this method searches elements that contain the text value.
        '''
        if not isinstance(search_val, str):
            raise TypeError(f'Expected search_val to be type str, instead got {type(search_val)}.')

        try:
            element = self.find_element(By.XPATH,
            f'//*[contains(text(), "{search_val}")]')
        except TimeoutException:
            return None
        
        return element

    def search_all_text(self, search_val: str, html_elements: list[str]) -> list[WebElement] | list:
        '''Searches for a text and returns a list of WebElements matching the text.

        Searches for the elements based on the value of `search_val`, and returns WebElements that contains
        `search_val`. It uses the XML function `contains()` to get the result.
        If attempting to find nested elements, the final xpath in the list **must be a relative path**.
        Absolute paths will ignore the hierarchy of the DOM and will attempt to search for all matching tags.
        
        Parameters
        ----------
            search_val: str
                Text that can be found in the card container on the VTB. The elements returned from
                this method searches elements that contain the text value.

            html_elements: list[str]
                A list of HTML elements that are the parents to the last element in the list.
                This must be in a format of an **XPATH**.
        '''
        if len(html_elements) == 0:
            raise ValueError('Cannot have an empty list for html_elements')

        # ignore the last element in the list, it is where the search is performed.
        if len(html_elements) > 1:
            last_element = html_elements.pop()
            parent_element = self._traverse_html_elements(By.XPATH, html_elements)

            elements = parent_element.find_elements(By.XPATH,
            f'{last_element}[contains(text(), "{search_val}")]')
        else:
            elements = self.find_elements(By.XPATH, f'{last_element}[contains(text(), "{search_val}")]')
        
        return elements

    def drag(self, 
             drag_to: str, 
             locator: str | By = By.XPATH, 
             search_val: str | WebElement = None):
        '''Drags an element to a desired location on a page.
        
        This method assumes that the **element is always interactable**. If an element can be
        hidden by overflow or not displayed to the driver, call the `scroll_to_element` method 
        to get to the element before calling this method. If an element is not interactable, 
        `ElementNotInteractableException` or `JavascriptException` exceptions are raised.

        Parameters
        ----------
            drag_to: str
                The location the task is dragged to.

            locator: str | By
                The locator strategy used to search for the `drag_to` string.
                By default it uses the By.XPATH strategy.

            search_val: str | WebElement
                The value that is the dragged element. A string or WebElement can be used.
                If a string is given, a search on the page for the string returns a WebElement.
        '''       
        if search_val is None:
            raise ValueError('Expected a type str or type WebElement for search_val')
        
        if isinstance(search_val, str):
            element = self.get_element(search_val)

            if element is None:
                raise ValueError(f'Could not find {search_val}')
        elif isinstance(search_val, WebElement):
            element = search_val
        else:
            raise TypeError(f'Expected type str or WebElement for search_val, got type {type(search_val)}')

        drag_to_element = self.find_element(locator, drag_to)

        self.action_driver.click_and_hold(element).pause(.3)

        # the pause is necessary to wait for JS to update the new card location.
        self.action_driver.move_to_element(drag_to_element).release(drag_to_element).pause(.8)
        self.action_driver.perform()

    def _traverse_locators(self,
                        strategy: str, 
                        locator: str,
                        locators: list[tuple[str, str] | str]) -> tuple[str, WebElement]:
        '''Traverses a list of locators and return a tuple consisting of a strategy 
        locator and a WebElement.
        
        Before calling this method, ensure that the **first and last locator are excluded** from 
        the list of locators. This method is expected to traverse and return a WebElement of the second-to-last 
        locator of the original list. The last locator is used as the query outside of this method, while the 
        first locator is used as the `strategy` and `locator` parameters of this method.

        If an empty list is given, then it returns the WebElement of the arguments `strategy` and `locator` 
        (which are the values of the first tuple).

        Parameters
        ----------
            strategy: str
                The strategy locator of the first tuple.

            locator: str
                The locator of the first tuple.

            locators: list[tuple[str, str] | str]
                A list of locators (tuples of strategy/locator or strings) that are used
                for traversal.

        Return
        ----------
            tuple[str | None, WebElement]
                A tuple containing:
                    1. A string representing the locator strategy. This will be the first
                    tuple strategy or a strategy from the tuple in the locator list. This will be
                    overwritten in the calling method if the last locator is a tuple.
                    2. The WebElement of the **second-to-last locator** in the original list of locators.
        '''
        traversed_element = self.find_element(strategy, locator)

        if len(locators) > 0:
            for item in locators:
                if isinstance(item, tuple):
                    strategy = item[0]
                    locator = item[1]
                elif isinstance(item, str):
                    locator = item
                else:
                    raise TypeError(f'Expected item to be of type str or tuple, but got {type(item)}')

                traversed_element = traversed_element.find_element(strategy, locator)

        return strategy, traversed_element