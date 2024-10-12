from asciimatics.screen import Screen, ManagedScreen
from asciimatics.event import MouseEvent

from buffer.buffer import Buffer
from buffer.cursor import CursorMoveDirection
from display.display import Display
from utils.prompts import InputPrompt, ConfirmationPrompt
from utils.info_bar import InfoBar
from utils.point import Point
from configuration.config import Config

class ConsoleEditor():
    def __init__(self) -> None:
        self.buffer = Buffer()
        self.info_bar = InfoBar("Commands: Ctrl+O: Save - Ctrl+R: Load - Ctrl+Q: Quit", 3.5)
        self.display = Display(self.buffer, self.info_bar)
        self.config = Config("configuration/config.yaml")

        self.input_prompt = None
        self.confirmation_prompt = None

    def create_prompts(self, screen: Screen) -> None:
        self.input_prompt = InputPrompt(screen, Point(0, screen.dimensions[0] - 1), screen.dimensions[1],
            Screen.COLOUR_WHITE, Screen.COLOUR_BLACK)
        self.confirmation_prompt = ConfirmationPrompt(screen, Point(0, screen.dimensions[0] - 1), screen.dimensions[1],
            Screen.COLOUR_WHITE, Screen.COLOUR_BLACK)

    def console_editor(self) -> None:
        with ManagedScreen() as screen:
            self.create_prompts(screen)

            while True:
                self.get_input(screen)
                self.display.display_to_screen(screen)

                #raise Exception(Config.get_config()["VARS"]["name"])


    def get_input(self, screen: Screen) -> None:
        event = screen.get_event()

        if event == None or isinstance(event, MouseEvent):
            return

        key_code = event.key_code

        if key_code >= 32 and event.key_code <= 254:
            self.buffer.add_str(chr(event.key_code))
        elif key_code == Screen.KEY_BACK:
            self.buffer.remove_char_back()
        elif key_code == Screen.KEY_DELETE:
            self.buffer.remove_char_front()
        elif key_code == Screen.KEY_LEFT:
            self.buffer.move_cursor(CursorMoveDirection.LEFT)
        elif key_code == Screen.KEY_RIGHT:
            self.buffer.move_cursor(CursorMoveDirection.RIGHT)
        elif key_code == Screen.KEY_UP:
            self.buffer.move_cursor(CursorMoveDirection.UP)
        elif key_code == Screen.KEY_DOWN:
            self.buffer.move_cursor(CursorMoveDirection.DOWN)
        elif key_code == Screen.KEY_HOME:
            self.buffer.move_cursor_start()
        elif key_code == Screen.KEY_END:
            self.buffer.move_cursor_end()
        elif key_code == 13:
            self.buffer.perform_linebreak()
        elif key_code == Screen.KEY_TAB:
            self.buffer.add_tab(4)

        elif key_code == Screen.ctrl("o"):
            result = self.buffer.save_buffer(self.input_prompt, self.confirmation_prompt)

            if result != None:
                self.info_bar.set_current_text(result)

        elif key_code == Screen.ctrl("r"):
            result = self.buffer.load_buffer(self.input_prompt, self.confirmation_prompt)

            if result != None:
                self.info_bar.set_current_text(result)

        elif key_code == Screen.ctrl("q"):
            if self.buffer.get_dirty():
                if self.confirmation_prompt.get_confirmation("Exit with unsaved changes?"):
                    quit()
            else:
                quit()

        #Up
        elif key_code == Screen.ctrl("i"):
            pass
        #Down
        elif key_code == Screen.ctrl("k"):
            pass
        #Left
        elif key_code == Screen.ctrl("j"):
            pass
        #Right
        elif key_code == Screen.ctrl("l"):
            pass
        else:
            raise Exception(key_code)



editor = ConsoleEditor()
editor.console_editor()