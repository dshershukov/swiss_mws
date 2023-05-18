import tkinter as tk
import tkinter.ttk as ttk


from ..common.timer import Timer


class TimerWidget:
    def __init__(self, master: tk.Misc, timer: Timer, *, column: int, row: int, columnspan: int = 1, rowspan: int = 1):
        self.frame = tk.Frame(master)
        self._timer = timer

        time_validation_command = self.frame.register(self._timer.text_validator)
        self.field = ttk.Entry(self.frame, textvariable=self._timer.text, validate='focusout',
                               validatecommand=(time_validation_command, '%P', '%V'))

        self.start_button = ttk.Button(self.frame, text='>', command=self._timer.start)
        self.pause_button = ttk.Button(self.frame, text='||', command=self._timer.pause)
        self.reset_button = ttk.Button(self.frame, text='x', command=self._timer.reset)

        self.layout(column, row, columnspan, rowspan)

    def layout(self, column: int, row: int, columnspan: int = 1, rowspan: int = 1) -> None:
        self.frame.grid(column=column, row=row, columnspan=columnspan, rowspan=rowspan)

        self.field.grid(column=0, row=0)
        self.start_button.grid(column=1, row=0)
        self.pause_button.grid(column=2, row=0)
        self.reset_button.grid(column=3, row=0)
