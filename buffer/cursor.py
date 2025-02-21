from enum import Enum, auto
from typing import Optional

from buffer.line_array import LineArray, Line
from utils.point import Point


class CursorMoveDirection(Enum):
    LEFT = auto()
    RIGHT = auto()
    UP = auto()
    DOWN = auto()

class Cursors(Enum):
    MAIN_CURSOR = auto()
    SELECTION_CURSOR = auto()


class Cursor:
    def __init__(self, l_array: LineArray, xPos: int, yPos: int) -> None:
        self._l_array = l_array
        self._position = Point(xPos, yPos)
        #The end position of the text selected by the cursor.
        self._cursor_selection: Optional[Point] = None
        #This variables stores the X position the cursor would like to be in, it's used when moving vertically from one line to another line 
        #and the line we are moving to isn't long enough for the cursor to have it's previous horizontal position. When not in use it's set to
        #"-1" to allow for easy and always false comparisons using "max".
        self._desired_x_position = -1

    def get_position(self) -> Point:
        return self._position

    def get_x(self) -> int:
        return self._position.x

    def get_y(self) -> int:
        return self._position.y

    #If there's selected text returns the position of the second cursor.
    def get_selection_position(self) -> Optional[Point]:
        if self._cursor_selection != None:
            return self._cursor_selection
        
        return None

    #If possible moves the cursor in the specified direction.
    def move(self, dir: CursorMoveDirection) -> None:
        match dir:
            case CursorMoveDirection.LEFT:
                #If we move horizontally the desired X position is reset.
                self._desired_x_position = -1

                if self._position.x > 0:
                    self._position.x -= 1
                else:
                    if self._position.y > 0:
                        self._position.y -= 1
                        #If we move the the previous line the cursor should be at it's end.
                        self._position.x = len(self._l_array.larray_get_line(self._position.y).data)

            case CursorMoveDirection.RIGHT:
                #If we move horizontally the desired X position is reset.
                self._desired_x_position = -1

                if self._position.x < len(self._l_array.larray_get_line(self._position.y).data):
                    self._position.x += 1
                else:
                    if (self._position.y < self._l_array.larray_get_length() - 1):
                        self._position.y += 1
                        self._position.x = 0

            case CursorMoveDirection.UP:
                self._change_y_pos(-1)

            case CursorMoveDirection.DOWN:
                self._change_y_pos(1)

    #Changes the Y position of the cursor, the change can be both positive or negative.
    def _change_y_pos(self, change: int) -> None:
        new_y = self._position.y + change

        #Ensure the Y position remains in bounds.
        if new_y < 0:
            new_y = 0
        elif new_y > self._l_array.larray_get_length() - 1:
            new_y = self._l_array.larray_get_length() - 1

        self._position.y = new_y

        new_line_len = len(self._l_array.larray_get_line(new_y).data)
        new_x = max(self._position.x, self._desired_x_position)

        #If new_x is shorter than the line, we set the cursors X position normally. Otherwise we set the cursor to the end of the line and set
        #the desired position.
        if new_x < new_line_len:
            self._desired_x_position = -1
            self._position.x = new_x
        else:
            #We only set the desired position if it's not already set.
            if self._desired_x_position == -1:
                self._desired_x_position = self._position.x

            self._position.x = new_line_len

    #Moves the cursor to the given position, if it's valid.
    def move_to_point(self, pos: Point) -> None:
        if 0 <= pos.y <= self._l_array.larray_get_length():
            if 0 <= pos.x <= len(self._l_array.larray_get_line(pos.y).data):
                self._desired_x_position = -1

                self._position = pos