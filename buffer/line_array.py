from dataclasses import dataclass
from hashlib import sha3_384
from time import time_ns

from utils.point import Point


#A class is used to be able to easily add more information later.
@dataclass
class Line:
    data: str


class LineArray:
    def __init__(self) -> None:
        self._lines: list[Line] = [Line("")]

    #Adds an empty line at the specified index.
    def larray_add_newline(self, index: int) -> None:
        if index < 0 or index > len(self._lines):
            raise Exception("Invalid newline position for LineArray")

        self._lines.insert(index, Line(""))

    #Inserts the given string at the specified position
    def larray_insert(self, pos: Point, string: str) -> None:
        line_len = len(self._lines[pos.y].data)

        if pos.y < 0 or pos.y > len(self._lines) - 1:
            if pos.x < 0 or pos.x > line_len - 1:
                raise Exception("Invalid string insert position for LineArray")

        #We check where the character has to be inserted, this is because string slices are not very efficient to perform, the less they are
        #used the better.
        if pos.x == line_len - 1:
            self._lines[pos.y].data = f"{self._lines[pos.y].data}{string}"
        elif pos.x == 0:
            self._lines[pos.y].data = f"{string}{self._lines[pos.y].data}"
        else:
            self._lines[pos.y].data = f"{self._lines[pos.y].data[:pos.x]}{string}{self._lines[pos.y].data[pos.x:]}"

    #Deletes the specified position in the array.
    def larray_delete_pos(self, pos: Point) -> None:
        line_len = len(self._lines[pos.y].data)

        if pos.y < 0 or pos.y > len(self._lines) - 1:
            if pos.x < 0 or pos.x > line_len - 1:
                raise Exception("Invalid string delete position for LineArray")

        if (pos.x == line_len - 1):
            self._lines[pos.y].data = self._lines[pos.y].data[:line_len - 2]
        else:
            self._lines[pos.y].data = f"{self._lines[pos.y].data[:pos.x - 1]}{self._lines[pos.y].data[pos.x:]}"

    #Deletes the line at the specified index.
    def larray_delete_line(self, index: int) -> None:
        if index < 0 or index > len(self._lines) - 1:
            raise Exception("Invalid line delete position for LineArray")

        del self._lines[index]

    #Deletes the portion of text between "start" and "end" at the specified line.
    def larray_delete_slice(self, index: int, start: int, end: int) -> None:
        if index < 0 or index > len(self._lines) - 1:
            raise Exception("Invalid line slice delete position for LineArray")

        if start < 0 or end > len(self._lines[index].data):
            raise Exception("Invalid line slice delete position for LineArray")

        self._lines[index].data = f"{self._lines[index].data[:start]}{self._lines[index].data[end:]}"

    #Gets the character at the specified position.
    def larray_get_char(self, pos: Point) -> str:
        if pos.y < 0 or pos.y > len(self._lines) - 1:
            if pos.x < 0 or pos.x > len(self._lines[pos.y].data) - 1:
                raise Exception("Invalid position for character in LineArray")

        return self._lines[pos.y].data[pos.x]

    #Gets the line at the specified index.
    def larray_get_line(self, index: int) -> Line:
        if index < 0 or index > len(self._lines) - 1:
            raise Exception("Invalid line return position for LineArray")

        return self._lines[index]

    #Returns the length of the line array.
    def larray_get_length(self) -> int:
        return len(self._lines)

    def larray_empty(self) -> None:
        self._lines = [Line("")]

    #Returns the hash of the line array.
    def get_hash(self) -> str:
        #Only static objects can be hashed, we turn the list into a string.
        list_as_text = "".join(line.data for line in self._lines)
        return sha3_384(list_as_text.encode('utf-8')).hexdigest()