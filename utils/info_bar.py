from dataclasses import dataclass
from time import time
from threading import Timer


class InfoBar:
    def __init__(self, default_text: str, reset_time: float):
        self._default_text = default_text
        self._reset_time = reset_time
        self._current_text = self._default_text

    def get_current_text(self) -> str:
        return self._current_text

    def set_current_text(self, new_text: str) -> None:
        self._current_text = new_text
        t = Timer(self._reset_time, self._reset_current_text)
        t.start()

    def _reset_current_text(self) -> None:
        self._current_text = self._default_text