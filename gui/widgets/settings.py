import tkinter as tk
import tkinter.ttk as ttk


from ..common.settings import Storage
from ..common.timer import Timer
from ..common.validation import nonnegative_integer_validator


def generate_table(master: tk.Misc) -> ttk.Treeview:
    # , column_id_to_name_map: dict[str, str], wide_columns: list[str]

    column_id_to_name_map = {
        'fight_number': 'Бой',
        'red_name': 'Красный боец',
        'red_entry_hp': 'HP до боя',
        'red_hp_change': 'HP +/-',
        'red_total_warnings': 'Предупр.',
        'blue_total_warnings': 'Предупр.',
        'blue_hp_change': 'HP +/-',
        'blue_entry_hp': 'HP до боя',
        'blue_name': 'Синий боец',
    }
    wide_columns = ['red_name', 'blue_name']

    table = ttk.Treeview(master, columns=[x for x in column_id_to_name_map.keys()])

    table.column('#0', width=0)  # Set "tree column" to 0 width -- it is empty
    for column, name in column_id_to_name_map.items():
        table.heading(column, text=name)
        if column not in wide_columns:
            table.column(column, minwidth=len(name) * 8, width=len(name) * 8)
        else:
            table.column(column, minwidth=len(name) * 8, width=30 * 8)
    return table


class StorageWidget:
    def __init__(self, master: tk.Misc, storage: Storage, timer: Timer, *,
                 column: int = 0, row: int = 0, columnspan: int = 1, rowspan: int = 1):
        self.frame = ttk.Frame(master)
        self.storage = storage
        self.timer = timer

        self.default_duration_label = ttk.Label(self.frame, text='Продолжительность боя, сек.')
        default_duration_validator = self.frame.register(self.timer.default_duration_validator)
        self.default_duration_entry = ttk.Entry(self.frame, textvariable=self.timer.default_duration_seconds,
                                                validate='all',
                                                validatecommand=(default_duration_validator, '%P', '%V'))

        self.directory_label = ttk.Label(self.frame, text='Папка с csv')
        self.directory_entry = ttk.Entry(self.frame, textvariable=self.storage.directory)

        self.prefix_label = ttk.Label(self.frame, text='Префикс')
        self.prefix_entry = ttk.Entry(self.frame, textvariable=self.storage.file_prefix)

        self.round_number_label = ttk.Label(self.frame, text='Раунд')
        round_validator = self.frame.register(nonnegative_integer_validator)
        self.round_number_entry = ttk.Entry(self.frame, textvariable=self.storage.round_number, validate='all',
                                            validatecommand=(round_validator, '%P', '%V'))

        self.load_round_button = ttk.Button(self.frame, text='Загрузить раунд', command=self.storage.load_round)

        self.server_url_label = ttk.Label(self.frame, text='API URL')
        self.server_url_entry = ttk.Entry(self.frame, textvariable=self.storage.server_url)
        self.server_token_label = ttk.Label(self.frame, text='API Token')
        self.server_token_entry = ttk.Entry(self.frame, textvariable=self.storage.server_token, show='*')
        self.upload_checkbox = ttk.Checkbutton(self.frame, text='Отправлять данные на сервер',
                                               variable=self.storage.upload_to_server, onvalue=1, offvalue=0)

        self.table = generate_table(self.frame)
        self.storage.table = self.table

        self.layout(column, row, columnspan, rowspan)

    def layout(self, column: int = 0, row: int = 0, columnspan: int = 1, rowspan: int = 1):
        self.frame.grid(column=column, row=row, columnspan=columnspan, rowspan=rowspan, sticky='nsew')
        top = self.frame.winfo_toplevel()
        top.columnconfigure(0, weight=1)
        top.rowconfigure(0, weight=1)

        padding = {'padx': 2, 'pady': 2}

        self.default_duration_label.grid(column=0, row=0, sticky='we', **padding)
        self.default_duration_entry.grid(column=1, row=0, sticky='w', **padding)
        self.directory_label.grid(column=0, row=1, sticky='we', **padding)
        self.directory_entry.grid(column=1, row=1, columnspan=3, sticky='we', **padding)
        self.prefix_label.grid(column=0, row=2, sticky='we', **padding)
        self.prefix_entry.grid(column=1, row=2, sticky='w', **padding)
        self.round_number_label.grid(column=0, row=3, sticky='we', **padding)
        self.round_number_entry.grid(column=1, row=3, sticky='w', **padding)

        self.server_url_label.grid(column=2, row=2, sticky='we', **padding)
        self.server_url_entry.grid(column=3, row=2, sticky='we', **padding)
        self.server_token_label.grid(column=2, row=3, sticky='we', **padding)
        self.server_token_entry.grid(column=3, row=3, sticky='we', **padding)
        self.upload_checkbox.grid(column=3, row=4, sticky='w', **padding)

        self.load_round_button.grid(column=0, row=4, sticky='w', **padding)

        self.table.grid(column=0, row=5, columnspan=4, sticky='nsew')

        self.frame.columnconfigure(0, weight=0)
        self.frame.columnconfigure(1, weight=0)
        self.frame.columnconfigure(2, weight=0)
        self.frame.columnconfigure(3, weight=1)


class FightLoadWidget:
    def __init__(self, master: tk.Misc, storage: Storage, *, column: int, row: int, columnspan: int = 1,
                 rowspan: int = 1):
        self.storage = storage

        self.frame = ttk.Frame(master)
        self.fight_label = ttk.Label(self.frame, text='Бой')

        self.fight_number_combobox = ttk.Combobox(self.frame, textvariable=self.storage.fight_number, values=['0'],
                                                  state='readonly', width=12)
        self.storage.combobox = self.fight_number_combobox

        self.save_fight_button = ttk.Button(self.frame, text='Сохранить бой', command=self.storage.save_fight)
        self.load_fight_button = ttk.Button(self.frame, text='Загрузить бой', command=self.storage.choose_fight)
        self.reset_fight_button = ttk.Button(self.frame, text='Сбросить бой', command=self.storage.reset_fight)

        self.current_fight_label = ttk.Label(self.frame, text='Текущий бой: -')

        self.layout(column, row, columnspan, rowspan)

    def layout(self, column: int, row: int, columnspan: int = 1, rowspan: int = 1):
        self.frame.grid(column=column, row=row, columnspan=columnspan, rowspan=rowspan, padx=5, pady=5)

        padding = {'padx': 2, 'pady': 2}
        self.fight_label.grid(column=0, row=0, **padding)
        self.fight_number_combobox.grid(column=1, row=0, **padding)
        self.save_fight_button.grid(column=1, row=1, **padding)
        self.load_fight_button.grid(column=2, row=0, **padding)
        self.reset_fight_button.grid(column=2, row=1, **padding)
        # self.current_fight_label.grid(column=5, row=0)
