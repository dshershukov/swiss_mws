import tkinter as tk
import tkinter.ttk as ttk

from ..common.fighter import ActiveFighter
from ..common.timer import Timer


class JudgeScreen:
    def __init__(self, master: tk.Misc, red_fighter: ActiveFighter, blue_fighter: ActiveFighter, timer: Timer):
        self.red_fighter = red_fighter
        self.blue_fighter = blue_fighter
        self.timer = timer

        self.master = master
        self.frame = ttk.Frame(master)

        timer_style = ttk.Style()
        timer_style.configure('Timer.Label', font='helvetica 144', background='white')

        red_name_style = ttk.Style()
        red_name_style.configure('RedName.Label', font='helvetica 64', background='red')

        blue_name_style = ttk.Style()
        blue_name_style.configure('BlueName.Label', font='helvetica 64', background='blue')

        red_cell_style = ttk.Style()
        red_cell_style.configure('RedCell.Label', font='helvetica 72', background='red')
        blue_cell_style = ttk.Style()
        blue_cell_style.configure('BlueCell.Label', font='helvetica 72', background='blue')
        white_cell_style = ttk.Style()
        white_cell_style.configure('WhiteCell.Label', font='helvetica 36', background='white')

        self.timer_label = ttk.Label(self.frame, textvariable=self.timer.text, style='Timer.Label', anchor='center')

        self.red_name_label = ttk.Label(self.frame, textvariable=self.red_fighter.name, style='RedName.Label',
                                        anchor='center', wraplength=700)
        self.blue_name_label = ttk.Label(self.frame, textvariable=self.blue_fighter.name, style='BlueName.Label',
                                         anchor='center', wraplength=700)
        self.blank_label = ttk.Label(self.frame, text='', style='WhiteCell.Label', anchor='center')

        self.entry_hp_label = ttk.Label(self.frame, text='HP до боя', style='WhiteCell.Label', anchor='center')
        self.red_entry_hp_label = ttk.Label(self.frame, textvariable=self.red_fighter.entry_hp, style='RedCell.Label',
                                            anchor='center')
        self.blue_entry_hp_label = ttk.Label(self.frame, textvariable=self.blue_fighter.entry_hp,
                                             style='BlueCell.Label', anchor='center')

        self.hp_change_label = ttk.Label(self.frame, text='изменение HP', style='WhiteCell.Label', anchor='center')
        self.red_hp_change_label = ttk.Label(self.frame, textvariable=self.red_fighter.hp_change, style='RedCell.Label',
                                             anchor='center')
        self.blue_hp_change_label = ttk.Label(self.frame, textvariable=self.blue_fighter.hp_change,
                                              style='BlueCell.Label',  anchor='center')

        self.warnings_label = ttk.Label(self.frame, text='предупреждения', style='WhiteCell.Label', anchor='center')
        self.red_warnings_label = ttk.Label(self.frame, textvariable=self.red_fighter.total_warnings,
                                            style='RedCell.Label', anchor='center')
        self.blue_warnings_label = ttk.Label(self.frame, textvariable=self.blue_fighter.total_warnings,
                                             style='BlueCell.Label',  anchor='center')

        self.layout()

    def layout(self):
        red_column = 0
        blue_column = 2

        top = self.frame.winfo_toplevel()
        top.columnconfigure(0, weight=1)
        top.rowconfigure(0, weight=1)

        # self.master.columnconfigure('all', weight=1)
        # self.master.rowconfigure('all', weight=1)
        self.frame.grid(column=0, row=0, sticky='nsew')

        self.timer_label.grid(column=0, row=0, columnspan=3, sticky='nsew')

        self.red_name_label.grid(column=red_column, row=1, sticky='nsew')
        self.blue_name_label.grid(column=blue_column, row=1, sticky='nsew')
        self.blank_label.grid(column=1, row=1, sticky='nsew')

        self.entry_hp_label.grid(column=1, row=2, sticky='nsew')
        self.red_entry_hp_label.grid(column=red_column, row=2, sticky='nsew')
        self.blue_entry_hp_label.grid(column=blue_column, row=2, sticky='nsew')

        self.hp_change_label.grid(column=1, row=3, sticky='nsew')
        self.red_hp_change_label.grid(column=red_column, row=3, sticky='nsew')
        self.blue_hp_change_label.grid(column=blue_column, row=3, sticky='nsew')

        self.warnings_label.grid(column=1, row=4, sticky='nsew')
        self.red_warnings_label.grid(column=red_column, row=4, sticky='nsew')
        self.blue_warnings_label.grid(column=blue_column, row=4, sticky='nsew')

        self.frame.columnconfigure(0, weight=3, minsize=700)
        self.frame.columnconfigure(1, weight=0)
        self.frame.columnconfigure(2, weight=3, minsize=700)
        self.frame.rowconfigure('all', weight=1)
