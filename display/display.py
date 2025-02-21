from asciimatics.screen import Screen
from dataclasses import dataclass
from math import log10

from buffer.buffer import Buffer
from utils.info_bar import InfoBar

from configuration.config import Config


#This class contains configuration info pertaining to the buffer display. The X and Y end subtract from the total height or width respectively. For
#example, if "y_end" is (-2) that means that the Y size of the buffer will be the total height of the console window minus 2. The scroll indicates
#what part of the buffer is visible based on the position of the cursor. The width of the line number is the width of the longest line number, it's
#used to set x_start and to print the line numbers.
@dataclass
class DisplayInfo:
    x_start = 0
    y_start = 0
    x_end = 0
    y_end = -2
    x_scroll = 0
    y_scroll = 0
    line_number_width = 0


class Display():
    def __init__(self, buffer: Buffer, info_bar: InfoBar) -> None:
        self.buffer = buffer
        self.info_bar = info_bar

        self.display_info = DisplayInfo()


    def display_to_screen(self, screen: Screen) -> None:
        screen.clear_buffer(Screen.COLOUR_WHITE, Screen.A_NORMAL, Screen.COLOUR_BLACK)

        self.calculate_x_start()
        #Before printing anything we update the scroll variables.
        self.scroll_handler(screen)

        self.display_buffer(screen)
        self.display_line_nums(screen)
        self.display_cursor(screen)
        self.display_status_bar(screen)
        self.display_info_bar(screen)

        screen.refresh()

    #Calculates how many characters are required to display the maximum number of lines.
    def calculate_x_start(self) -> None:
        self.display_info.line_number_width = max(int(log10(self.buffer.get_length())) + 1, 2)
        self.display_info.x_start = self.display_info.line_number_width

    #Handles the horizontal and vertical scroll for printing the appropriate part of the buffer depending on the position of the cursor. 
    def scroll_handler(self, screen: Screen) -> None:
        end_x = screen.dimensions[1] + self.display_info.x_end
        end_y = screen.dimensions[0] + self.display_info.y_end
        cursor_pos = self.buffer.get_cursor_pos()

        #First we check if the cursor has gone beneath the printed part of the buffer. For this we check the Y position of the cursor against
        #the final size of the printed buffer, "end_y", added to the current Y scroll minus 1, to account for the index. In case it's true we
        #set the scroll to be enough so the cursor appears on the last line.
        if cursor_pos.y > end_y + self.display_info.y_scroll - 1:
            self.display_info.y_scroll = cursor_pos.y - end_y + 1
        #If the cursor goes above the printed part of the buffer we set the scroll to the cursor's position, which is just enough for the cursor
        #to appear on the first line.
        elif cursor_pos.y < self.display_info.y_scroll:
            self.display_info.y_scroll = cursor_pos.y

        #Same concept except in the X axis, except that we also take into account the fact that "start_x" can be not zero, when the line
        #numbers are enabled.
        if cursor_pos.x > end_x - self.display_info.x_start + self.display_info.x_scroll - 1:
            self.display_info.x_scroll = cursor_pos.x - end_x + self.display_info.x_start + 1 
        #If the cursor goes above the printed part of the buffer we set the scroll to the cursor's position, which is just enough for the cursor
        #to appear on the first line.
        elif cursor_pos.x < self.display_info.x_scroll:
            self.display_info.x_scroll = cursor_pos.x

    #Displays the buffer according to the scroll.
    def display_buffer(self, screen: Screen) -> None:
        display_y = self.display_info.y_start

        end_x = screen.dimensions[1] + self.display_info.x_end
        end_y = screen.dimensions[0] + self.display_info.y_end

        normal_fg = Config.get_config()["COLOURS"]["text"]["fg"]
        normal_bg = Config.get_config()["COLOURS"]["text"]["bg"]
        highlighted_fg = Config.get_config()["COLOURS"]["highlight"]["fg"]
        highlighted_bg = Config.get_config()["COLOURS"]["highlight"]["bg"]

        #We iterate through every line between the scroll and the end of the buffer, we do the same in each line with the characters. Every iteration
        #we check if the printing indexes we are using have exceeded the ones specified in the buffer configuration to avoid printing out of bounds.
        for y in range(self.display_info.y_scroll, self.buffer.get_length()):
            display_x = self.display_info.x_start
            current_line = self.buffer.get_line(y)

            #Avoids unnecessary checks if there are no highlighted sections on the line.
            if current_line.highlight == None:
                for x in range(self.display_info.x_scroll, len(current_line.data)):
                    screen.print_at(current_line.data[x], display_x, display_y,
                        colour = normal_fg, bg = normal_bg)

                    #X printing index check.
                    display_x += 1
                    if display_x >= end_x:
                        break
            else:
                for x in range(self.display_info.x_scroll, len(current_line.data)):
                    if x in current_line.highlight:
                        fg_colour = highlighted_fg
                        bg_colour = highlighted_bg
                    else:
                        fg_colour = normal_fg
                        bg_colour = normal_bg

                    screen.print_at(current_line.data[x], display_x, display_y,
                        colour = fg_colour, bg = bg_colour)

                    #X printing index check.
                    display_x += 1
                    if display_x >= end_x:
                        break

            #Y printing index check.
            display_y += 1
            if display_y > end_y:
                break

    #Displays the cursor.
    def display_cursor(self, screen: Screen) -> None:
        cursor_pos = self.buffer.get_cursor_pos()
        current_line_data = self.buffer.get_line(cursor_pos.y).data

        #Check whether the cursor is at the end of the line and change it's colour appropriately.
        if cursor_pos.x > len(current_line_data) - 1:
            screen.print_at(" ", cursor_pos.x + self.display_info.x_start, cursor_pos.y - self.display_info.y_scroll,
                bg = Config.get_config()["COLOURS"]["cursor"]["bg"])
        else:
            screen.print_at(current_line_data[cursor_pos.x], cursor_pos.x + self.display_info.x_start, cursor_pos.y - self.display_info.y_scroll,
                colour = Config.get_config()["COLOURS"]["cursor"]["fg"], bg = Config.get_config()["COLOURS"]["cursor"]["bg"])

    #Displays the line numbers.
    def display_line_nums(self, screen: Screen) -> None:
        line_count = self.buffer.get_length()

        for y in range(self.display_info.y_start, screen.dimensions[0] + self.display_info.y_end):
            line_number = y + self.display_info.y_scroll + 1

            #if the number exists in the buffer print it with the appropriate amount of padding.
            if line_number < line_count + 1:
                number_width = int(log10(line_number)) + 1
                padding = " " * (self.display_info.line_number_width - number_width)
                screen.print_at(f"{padding}{line_number}", 0, y, colour = Screen.COLOUR_BLACK, bg = Screen.COLOUR_WHITE)
            else:
                screen.print_at("~", 0, y)

    #Displays the status bar.
    def display_status_bar(self, screen: Screen) -> None:
        buffer_length = self.buffer.get_length()
        #Note the use of single quotes, inside the f-string.
        filename = self.buffer.get_filename() if self.buffer.get_filename() != None else "[No filename]"
        modified = "(modified)" if self.buffer.get_dirty() else ""
        left_text = f"{filename} - {buffer_length} line{('' if buffer_length == 1 else 's')} {modified}"

        cursor_pos = self.buffer.get_cursor_pos()
        right_text = f"{cursor_pos.x},{cursor_pos.y} "

        #Note the use of single quotes, inside the f-string.
        final_string = f"{left_text}{' ' * (screen.dimensions[1] - len(left_text) - len(right_text))}{right_text}"

        #The status bar is printed right after the buffer.
        screen.print_at(final_string, 0, screen.dimensions[0] + self.display_info.y_end, colour = Config.get_config()["COLOURS"]["status bar"]["fg"], bg = Config.get_config()["COLOURS"]["status bar"]["bg"])

    def display_info_bar(self, screen: Screen) -> None:
        screen.print_at(self.info_bar.get_current_text(), 0, screen.dimensions[0] + self.display_info.y_end + 1)