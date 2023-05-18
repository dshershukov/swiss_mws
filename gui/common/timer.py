import time

import tkinter as tk

from tkinter.messagebox import (
    showerror,
    showinfo,
)

from .validation import (
    Validator,
    nonnegative_integer_validator,
)


class Timer:
    SLEEP_MILLISECONDS = 50

    def __init__(self, master: tk.Misc):
        self._master = master
        self.text = tk.StringVar(value='00:45')
        self._is_running = False
        self._seconds: float = 0.0
        self._monotonic_previous: float = 0.0
        self._monotonic_current: float = 0.0
        self.default_duration_seconds = tk.IntVar(value=45)

        # Text validator
        # - should validate focusout only, so partial test is ''
        # - should check current state apart from value, so it is later wrapped into text_validator method
        self._text_validator = Validator(r'^[0-5][0-9]:[0-5][0-9]$', '', 'Timer value must be MM:SS')
        self._default_duration_validator = nonnegative_integer_validator

    def text_validator(self, value, reason):
        assert reason == 'focusout'

        if self._is_running:
            showerror(message='Stop the running timer first')
            return False

        if not self._text_validator(value, reason):
            return False

        return True

    def start(self):
        timer_str = self.text.get()

        # Will not start if timer is already running or if input is bad
        # Imitating focusout
        if not self.text_validator(timer_str, 'focusout'):
            return

        minutes_str, seconds_str = timer_str.split(':', 1)
        self._seconds = int(minutes_str) * 60 + int(seconds_str)

        self._monotonic_previous = time.monotonic()
        self._is_running = True
        self._tick()

    def _display(self, value):
        minutes, seconds = divmod(value, 60)
        if minutes > 59:
            raise RuntimeError('Somehow managed to get timer value over 59:59...')
        self.text.set(f'{int(minutes):02}:{int(seconds):02d}')

    def _tick(self):
        if not self._is_running:  # User has paused the timer after last tick
            return

        # Update remaining time
        self._monotonic_current = time.monotonic()
        self._seconds -= (self._monotonic_current - self._monotonic_previous)
        self._monotonic_previous = self._monotonic_current

        # If time has become 0 or below, timer ends.
        # Do not display negative time.
        if self._seconds <= 0:
            self._seconds = 0
            self._is_running = False

        # Update displayed time
        self._display(self._seconds)

        # Proceed or warn that the fight has ended
        if self._is_running:
            self._master.after(self.SLEEP_MILLISECONDS, self._tick)
        else:
            showinfo(message='Time to end the fight!!!')

    def pause(self):
        self._is_running = False

    def reset(self):
        self._is_running = False
        self._display(self.default_duration_seconds.get())

    def default_duration_validator(self, value, reason):
        if not self._default_duration_validator(value, reason):
            return False

        if int(value) < 1 or int(value) > 3600 - 1:
            showerror(message='Timer value must be between 1 and 3559 seconds')
            return False

        return True
