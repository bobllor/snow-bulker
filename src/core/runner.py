from getpass import getpass
import os

class Runner:
    '''Class with terminal related methods.'''
    def __init__(self, quit_str: str = "q"):
        '''
        Parameters
        ----------
            quit_str: str
                The string used for quitting.    
        '''
        self.quit_str: str = quit_str.lower()

    def clear(self) -> None:
        '''Clears the terminal.'''
        os.system("cls" if os.name == "nt" else "clear")
    
    def enter_to_continue(self) -> None:
        '''Invokes a `getpass` method to continue. It uses the `enter` key.'''
        getpass("\nPress 'enter' to continue")

    def menu(self, *, menu_txt: list[str], choices: list[str], banner_txt: str = "") -> str:
        '''Prints the menu and prompts for an input string. It will return the input string
        in lowercase.
        
        Parameters
        ----------
            menu_txt: list[str]
                A list of strings representing the text menu. This prints top
                to bottom from i to i + 1.

            choices: list[str]
                The choices. This must be the same size as the menu_txt. If
                an empty string is given, then the choice will not be appended to the
                menu text. The choices will automatically be lowercased.
                Example: Example Text 1 [q]
            
            banner: str
                The banner at the top to display. By default this is empty.
        '''
        if len(menu_txt) != len(choices):
            raise ValueError(f"'menu_txt' length ({len(menu_txt)}) does not match 'choices' length ({len(choices)})")
        
        choices = [choice.lower() for choice in choices]

        if banner_txt != "": 
            print(banner_txt + "\n")

        for i, txt in enumerate(menu_txt):
            choice: str = choices[i]
            msg: str = f"{txt} [{choice}]"

            print(msg)

        input_choice: str = input("Enter an option: ").lower().strip()
    
        return input_choice