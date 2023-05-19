import tkinter as tk
import tkinter.ttk as ttk

from ..common.fighter import (
    ActiveFighter,
)

from ..common.validation import (
    integer_validator,
    nonnegative_integer_validator,
)


class FighterSecretaryWidget:
    def __init__(self, master: tk.Misc, active_fighter: ActiveFighter, *, color: str, column: int, row: int,
                 columnspan: int, rowspan: int):
        self.frame = tk.Frame(master)
        self.active_fighter = active_fighter

        self.name_label = ttk.Label(self.frame, textvariable=active_fighter.name, background=color)

        self.entry_hp_label = ttk.Label(self.frame, text='HP в начале боя')
        self.entry_hp_value = ttk.Label(self.frame, textvariable=active_fighter.entry_hp, width=7)

        self.hp_change_label = ttk.Label(self.frame, text='изменение HP в бою')
        hp_validation_command = self.frame.register(integer_validator)
        self.hp_change_entry = ttk.Entry(self.frame, textvariable=active_fighter.hp_change, validate='all',
                                         validatecommand=(hp_validation_command, '%P', '%V'), width=7)

        self.warnings_label = ttk.Label(self.frame, text='предупреждения за турнир')
        warnings_validation_command = self.frame.register(nonnegative_integer_validator)
        self.warnings_entry = ttk.Entry(self.frame, textvariable=active_fighter.total_warnings, validate='all',
                                        validatecommand=(warnings_validation_command, '%P', '%V'), width=7)

        self.layout(column, row, columnspan, rowspan)

    def layout(self, column: int, row: int, columnspan: int = 1, rowspan: int = 1) -> None:
        self.frame.grid(column=column, row=row, columnspan=columnspan, rowspan=rowspan)

        padding = {'padx': 2, 'pady': 2}
        self.name_label.grid(column=0, row=0, columnspan=2, sticky='ew', padx=5, pady=5)
        self.entry_hp_label.grid(column=0, row=1, sticky='ew', **padding)
        self.entry_hp_value.grid(column=1, row=1, sticky='ew', **padding)
        self.hp_change_label.grid(column=0, row=2, sticky='ew', **padding)
        self.hp_change_entry.grid(column=1, row=2, sticky='ew', **padding)
        self.warnings_label.grid(column=0, row=3, sticky='ew', **padding)
        self.warnings_entry.grid(column=1, row=3, sticky='ew', **padding)
