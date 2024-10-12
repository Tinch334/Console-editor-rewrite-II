from asciimatics.screen import Screen
from asciimatics.event import Event, MouseEvent
from typing import Optional

from utils.point import Point

#Generates an input prompt at the specified with the given parameters. Can either return a string or "None" if the user pressed the escape key.
class InputPrompt():
    def __init__(self, screen: Screen, start: Point, width: int, fg: int, bg: int) -> None:
        self._start = start
        self._width = width
        self._screen = screen
        self._fg = fg
        self._bg = bg

        self._inp = ""
        self._cursor_pos = 0

    #Function to be called to get input from the prompt.
    def get_input(self, prompt: str) -> Optional[str]:
        self._prompt = prompt
        self._inp = ""
        self._cursor_pos = 0

        while True:
            self._display_input()

            event = self._screen.get_event()
            #Check if a valid event has occurred.
            if event == None or isinstance(event, MouseEvent):
                continue
            if event.key_code >= 32 and event.key_code <= 254:
                self._inp = f"{self._inp[:self._cursor_pos]}{chr(event.key_code)}{self._inp[self._cursor_pos:]}"
                self._cursor_pos += 1
            elif event.key_code == Screen.KEY_BACK:
                if self._cursor_pos > 0:
                    self._inp = f"{self._inp[:self._cursor_pos - 1]}{self._inp[self._cursor_pos:]}"
                    self._cursor_pos -= 1
            elif event.key_code == Screen.KEY_DELETE:
                if self._cursor_pos < len(self._inp):
                    self._inp = f"{self._inp[:self._cursor_pos + 1]}{self._inp[self._cursor_pos:]}"
            elif event.key_code == Screen.KEY_LEFT:
                if self._cursor_pos > 0:
                    self._cursor_pos -= 1
            elif event.key_code == Screen.KEY_RIGHT:
                if self._cursor_pos < len(self._inp):
                    self._cursor_pos += 1
            elif event.key_code == Screen.KEY_HOME:
                self._cursor_pos = 0
            elif event.key_code == Screen.KEY_END:
                self._cursor_pos = len(self._inp) - 1
            if event.key_code == 13:
                if self._inp != "":
                    return self._inp
            elif event.key_code == Screen.KEY_ESCAPE:
                return None

    #Displays the input prompt.
    def _display_input(self) -> None:
        #Only the section used for the prompt gets erased.
        self._screen.clear_buffer(Screen.COLOUR_WHITE, Screen.A_NORMAL, Screen.COLOUR_BLACK,
        self._start.x, self._start.y, self._start.x + self._width, self._start.y)

        prompt_spacing = self._start.x + len(self._prompt)
        y_pos = self._start.y
        #Print the prompt and associated text.
        self._screen.print_at(self._prompt, self._start.x, y_pos)
        self._screen.print_at(self._inp, prompt_spacing, y_pos)
        self._screen.print_at("(ESC to cancel)", prompt_spacing + len(self._inp) + 2, y_pos)

        #Check whether the cursor is at the end of the line and change it's colour appropriately.
        if self._cursor_pos > len(self._inp) - 1:
            self._screen.print_at(" ", prompt_spacing + self._cursor_pos, y_pos, bg = Screen.COLOUR_WHITE)
        else:
            self._screen.print_at(self._inp[self._cursor_pos], prompt_spacing + self._cursor_pos, y_pos,
                colour = Screen.COLOUR_BLACK, bg = Screen.COLOUR_WHITE)

        self._screen.refresh()



#Generates an input prompt at the specified with the given parameters. Can either return a string or "None" if the user pressed the escape key.
class ConfirmationPrompt():
    def __init__(self, screen: Screen, start: Point, width: int, fg: int, bg: int) -> None:
        self._start = start
        self._width = width
        self._screen = screen
        self._fg = fg
        self._bg = bg

    #Function to be called to get input from the prompt.
    def get_confirmation(self, prompt: str) -> Optional[bool]:
        self._prompt = prompt
        self._inp = ""
        self._cursor_pos = 0

        while True:
            self._display_confirmation()

            event = self._screen.get_event()
            #Check if a valid event has occurred.
            if event == None or isinstance(event, MouseEvent):
                continue
            if event.key_code == ord("y") or event.key_code == ord("Y"):
                return True
            elif event.key_code == ord("n") or event.key_code == ord("N"):
                return False
            elif event.key_code == Screen.KEY_ESCAPE:
                return None

    #Displays the input prompt.
    def _display_confirmation(self) -> None:
        #Only the section used for the prompt gets erased.
        self._screen.clear_buffer(Screen.COLOUR_WHITE, Screen.A_NORMAL, Screen.COLOUR_BLACK,
        self._start.x, self._start.y, self._start.x + self._width, self._start.y)

        prompt_spacing = self._start.x + len(self._prompt)
        y_pos = self._start.y
        #Print the prompt and associated text.
        self._screen.print_at(self._prompt, self._start.x, y_pos)
        self._screen.print_at(" Y: Yes - N: No - Esc: Cancel", prompt_spacing, y_pos)

        self._screen.refresh()