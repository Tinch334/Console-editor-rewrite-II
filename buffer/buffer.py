from dataclasses import dataclass
from typing import Optional
import os.path
import re

from buffer.line_array import LineArray, Line
from buffer.cursor import Cursor, CursorMoveDirection
from utils.point import Point
from utils.prompts import InputPrompt, ConfirmationPrompt


@dataclass
class BufferFileInfo:
    filename: str = None
    dirty: bool = False


class Buffer:
    def __init__(self):
        self._buffer_file_info = BufferFileInfo()

        self._l_array = LineArray()
        self._cursor = Cursor(self._l_array, 0, 0)

#################
#Buffer handling
#################
    #Adds a character to the buffer on the cursors current position.
    def add_str(self, string: str) -> None:
        self._buffer_modified_handler()

        #Insert the word in the line array and move the cursor accordingly.
        self._l_array.larray_insert(self._cursor.get_position(), string)
        self._cursor.move_to_point(Point(self._cursor.get_position().x + len(string), self._cursor.get_position().y))

    #Add the necessary amount of spaces to move the cursor the next tabulation line.
    def add_tab(self, tab_width: int) -> None:
        self._buffer_modified_handler()

        cursor_pos = self._cursor.get_position()
        #Get the amount of required spaces.
        diff = tab_width - (cursor_pos.x % tab_width)

        self._l_array.larray_insert(cursor_pos, " " * diff)
        self._cursor.move_to_point(Point(cursor_pos.x + diff, cursor_pos.y)) 

    #Performs a line-break at the cursor's position.
    def perform_linebreak(self) -> None:
        self._buffer_modified_handler()

        cursor_pos = self._cursor.get_position()
        #Store what's right of the cursor and delete it from the current line.
        right_of_cursor = self._l_array.larray_get_line(cursor_pos.y).data[cursor_pos.x:]
        self._l_array.larray_delete_slice(cursor_pos.y, cursor_pos.x, len(self._l_array.larray_get_line(cursor_pos.y).data))

        #Create a new line with what was right of the cursor. First we get how many spaces there are at the beginning of the line, the same
        #amount is added to the new line.
        tab_amount = len(self._l_array.larray_get_line(cursor_pos.y).data) - len(self._l_array.larray_get_line(cursor_pos.y).data.lstrip(" "))

        self._l_array.larray_add_newline(cursor_pos.y + 1)
        self._l_array.larray_insert(Point(0, cursor_pos.y + 1), f"{' ' * tab_amount}{right_of_cursor}")

        #Update the cursor's position.
        self._cursor.move_to_point(Point(tab_amount, cursor_pos.y + 1))

    #Removes the character at the back of the cursor.
    def remove_char_back(self) -> None:
        self._buffer_modified_handler()
        
        cursor_pos = self._cursor.get_position()

        if cursor_pos.x != 0:
            self._l_array.larray_delete_pos(cursor_pos)
            self._cursor.move(CursorMoveDirection.LEFT)
        else:
            #If we are at the end of the line whatever remains should be appended to the line on top.
            if cursor_pos.y > 0:
                insert_x = len(self._l_array.larray_get_line(cursor_pos.y - 1).data)
                self._l_array.larray_insert(Point(insert_x, cursor_pos.y - 1), self._l_array.larray_get_line(cursor_pos.y).data)

                self._l_array.larray_delete_line(cursor_pos.y)

                #Move the cursor to the appropriate position.
                self._cursor.move_to_point(Point(insert_x, cursor_pos.y - 1))

    #Removes the character in front of the cursor.
    def remove_char_front(self) -> None:
        self._buffer_modified_handler()

        cursor_pos = self._cursor.get_position()

        #If we are on the end of the line add the line below to it, assuming it exists.
        if cursor_pos.x == len(self._l_array.larray_get_line(cursor_pos.y).data):
            if cursor_pos.y < self._l_array.larray_get_length() - 1:
                self._l_array.larray_insert(cursor_pos, self._l_array.larray_get_line(cursor_pos.y + 1).data)
                self._l_array.larray_delete_line(cursor_pos.y + 1)
        else:
            self._l_array.larray_delete_pos(Point(cursor_pos.x + 1, cursor_pos.y))

    #Searches the buffer for strings that match the given regex and highlights them, returns the amount of matches found, this can be zero.
    #If the given regex is invalid returns "None".
    def highlight_regex(self, regex: str) -> Optional[int]:
        #Clear any previous highlighted text.
        self._l_array.larray_highlight_clear()
        
        #Check if the given regex is valid.
        try:
            complied_re = re.compile(regex)
        except:
            return None

        match_count = 0

        #Go through each line in the buffer and iterate through all the matches highlighting and counting them.
        for a in range(self._l_array.larray_get_length()):
            matches = complied_re.finditer(self._l_array.larray_get_line(a).data)

            for match in matches:
                self._l_array.larray_highlight_slice(a, match.start(), match.end())
                match_count += 1

        return match_count

    #Replaces the with the specified string. Returns how many replacements were performed, can be zero. #If the given regex is invalid returns
    #"None".
    def replace_regex(self, regex: str, replace_with: str) -> Optional[int]:
        total_substitutions = 0

        #Check if the given regex is valid.
        try:
            complied_re = re.compile(regex)
        except:
            return None

        #Go through each line in the buffer and replaces the matching regex, counts how many replacements were performed.
        for a in range(self._l_array.larray_get_length()):
            (updated_line, line_substitutions) = re.subn(regex, replace_with, self._l_array.larray_get_line(a).data) 
            self._l_array.larray_set_line(a, updated_line)
            total_substitutions += line_substitutions

        #If any substitutions were performed the buffer has been modified.
        if total_substitutions:
            self._buffer_modified_handler()

        return total_substitutions

    #To be called each time the buffer is modified.
    def _buffer_modified_handler(self) -> None:
        self._set_dirty(True)
        #Matched strings could have been modified.
        self._l_array.larray_highlight_clear()

#################
#Cursor handling
#################

    #Moves the cursor in the specified position.
    def move_cursor(self, dir: CursorMoveDirection) -> None:
        self._cursor.move(dir)

    #Moves the cursor to the end of the current line.
    def move_cursor_end(self) -> None:
        self._cursor.move_to_point(Point(len(self._l_array.larray_get_line(self._cursor.get_y()).data), self._cursor.get_y()))

    #Moves the cursor to the start of the current line.
    def move_cursor_start(self) -> None:
        self._cursor.move_to_point(Point(0, self._cursor.get_y()))

    #Gets the length of the line array associated with the buffer, this is done to maintain "_l_array" private.
    def get_length(self) -> int:
        return self._l_array.larray_get_length()

    #Gets the line in the line array associated with the buffer, this is done to maintain "_l_array" private.
    def get_line(self, index: int) -> Line:
        return self._l_array.larray_get_line(index)

    #Gets the position of the cursor associated with the buffer, this is done to maintain "_cursor" private.
    def get_cursor_pos(self) -> Point:
        return self._cursor.get_position()

#################
#Highlight handling
#################

    #Sets the portion of the line between "start" and "end" at the specified line as highlighted.
    def set_highlight(self, index: int, start: int, end: int) -> None:
        self._l_array.larray_highlight_slice(index, start, end)

    #Clears the highlighted sections from all lines.
    def clear_highlight(self) -> None:
        self._l_array.larray_highlight_clear()

#################
#File handling
#################

    #Returns the filename associated with the buffer.
    def get_filename(self) -> Optional[str]:
        return self._buffer_file_info.filename

    #Returns whether the buffer is "dirty".
    def get_dirty(self) -> bool:
        return self._buffer_file_info.dirty

    #Sets the dirty flag to the specified value.
    def _set_dirty(self, dirty: bool) -> None:
        self._buffer_file_info.dirty = dirty

    #Saves the buffer, if necessary handles getting the filename.
    def save_buffer(self, input_prompt: InputPrompt, confirmation_prompt: ConfirmationPrompt, line_ending: str = "\n") -> Optional[str]:
        #Check if the file already has a filename, if not get it.
        if self._buffer_file_info.filename == None:
            filename = input_prompt.get_input("Save file: ")

            #The user pressed the escape key.
            if filename == None:
                return None
            #If the file already exists ask the user if they want to overwrite it.
            elif os.path.isfile(filename):
                if confirmation_prompt.get_confirmation(f"The file \"{filename}\" already exists, overwrite?") != True:
                    return None
        else:
            filename = self._buffer_file_info.filename
                
        try:
            file = open(filename, "w")
        #In case an error occurred.
        except OSError:
            return "The given file path cannot be accessed"
        else:
            try:
                #We read each line in the buffer and write it to the file, adding the corresponding line ending.
                for y in range(0, self._l_array.larray_get_length()):
                    file.write(f"{self._l_array.larray_get_line(y).data}{line_ending}")
                    
                file.close()
            except:
               return "The given file path could not be written to"
            else:
                #If the file could be written set the filename.
                self._buffer_file_info.filename = filename
                #The file was saved, therefore the buffer is no longer different from the file.
                self._buffer_file_info.dirty = False

                #No errors occurred, return the number of bytes written to disk.
                return f"{os.path.getsize(filename)} bytes written to disk"

    #Loads a file to the buffer, handles getting the filename.
    def load_buffer(self, input_prompt: InputPrompt, confirmation_prompt: ConfirmationPrompt) -> Optional[str]:
        #If there are unsaved changes ask the user what to do with them.
        if self._buffer_file_info.dirty:
            if confirmation_prompt.get_confirmation("Discard unsaved file?") != True:
                return None

        filename = input_prompt.get_input("Load file: ")

        #The user pressed the escape key.
        if filename == None:
            return None

        try:
            file = open(filename, "r")
        #In case an error occurred.
        except OSError:
            return "The given file path cannot be accessed"
        else:
            self._l_array.larray_initialize()

            try:
                index = 0

                #We read each line in the file and write it to the buffer.
                for line in file.readlines():
                    self._l_array.larray_insert(Point(0, index), line.rstrip())
                    self._l_array.larray_add_newline(index + 1)

                    index += 1

                #An additional empty line is added by the loop, this is the most elegant way of eliminating it.
                self._l_array.larray_delete_line(index)
                file.close()
            except:
                return "The given file path cannot be read"
            else:
                #If the file could be loaded set the filename.
                self._buffer_file_info.filename = filename
                #A file was just loaded, therefore the buffer is no longer different from the file.
                self._buffer_file_info.dirty = False

                #No errors occurred, return the number of bytes written to disk.
                return f"{os.path.getsize(filename)} bytes loaded from disk"