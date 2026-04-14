from getpass import getpass
from pynput import keyboard
import threading
import os
import time

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
    
    def key_listener_exit_thread(self, event: threading.Event, loop_pause: int | float = .07, quit_key: str = "Q") -> None:
        '''A key listener method to be used with Thread. This listens for keyboard
        movement and if the quit_key is detected, then it will set the event flag to True
        causing the threads to exit.
        '''
        def on_press(key: keyboard.KeyCode | keyboard.Key):
            if isinstance(key, keyboard.KeyCode):
                if key.char == quit_key:
                    print("Termination signal sent")
                    event.set()

        listener: keyboard.Listener = keyboard.Listener(on_press=on_press)
        listener.start()

        print("\nPress 'SHIFT + Q' to quit the process and return back to menu")
        print("When 'SHIFT + Q' is pressed, it will wait until the next cycle to start before stopping\n")
        while not event.is_set():
            time.sleep(loop_pause)
 
        listener.stop()

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