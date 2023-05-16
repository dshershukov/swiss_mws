import csv
import dataclasses
import os
import re
import shutil
import time
import tkinter as tk
import tkinter.messagebox as msg
import tkinter.ttk as ttk


class Timer:
    SLEEP_MILLISECONDS = 50

    def __init__(self, master: tk.Misc, *, column: int, row: int, columnspan: int = 1, rowspan: int = 1,
                 default_duration_seconds: int = 45):
        self.frame = ttk.Frame(master)
        self.text = tk.StringVar()
        self._is_running = False
        self._seconds = 0
        self._monotonic_previous = 0
        self._monotonic_current = 0
        self._default_duration_seconds = default_duration_seconds

        self._value_check = re.compile(f'^[0-5][0-9]:[0-5][0-9]$')
        validation_command = self.frame.register(self._validate_timer)
        self.field = ttk.Entry(self.frame, textvariable=self.text, validate='focusout',
                               validatecommand=(validation_command, '%P'))

        self.start_button = ttk.Button(self.frame, text='>', command=self._start)
        self.pause_button = ttk.Button(self.frame, text='||', command=self._pause)
        self.reset_button = ttk.Button(self.frame, text='x', command=self._reset)

        self.frame.grid(column=column, row=row, columnspan=columnspan, rowspan=rowspan)
        self._set_layout()
        self._display(self._default_duration_seconds)

    def _set_layout(self):
        self.field.grid(column=0, row=0)
        self.start_button.grid(column=1, row=0)
        self.pause_button.grid(column=2, row=0)
        self.reset_button.grid(column=3, row=0)

    def _validate_timer(self, new_text):
        if self._is_running:
            msg.showerror(message='Stop the running timer first')
            return False

        if not self._value_check.match(new_text):
            msg.showerror(message='Timer should be set between 00:00 and 59:59')
            return False

        return True

    def _start(self):
        timer_str = self.text.get()

        # Will not start if timer is already running or if input is bad
        if not self._validate_timer(timer_str):
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
            self.frame.after(self.SLEEP_MILLISECONDS, self._tick)
        else:
            self.frame.bell()
            msg.showinfo(message='Time to end the fight!!!')

    def _pause(self):
        self._is_running = False

    def _reset(self):
        self._is_running = False
        self._display(self._default_duration_seconds)

    def update_default_duration(self, seconds: int):
        if seconds < 1 or seconds > 3559:
            msg.showerror('Default fight duration must be between 1 and 3559 seconds')
            return
        self._default_duration_seconds = seconds


@dataclasses.dataclass
class Fighter:
    name: str
    entry_hp: int
    hp_change: int
    total_warnings: int


@dataclasses.dataclass
class Fight:
    number: int
    red: Fighter
    blue: Fighter


class FighterDisplay:
    def __init__(self, master: tk.Misc, *, color: str, column: int, row: int, columnspan: int = 1, rowspan: int = 1):
        self.frame = ttk.Frame(master)
        if color in ('red', 'blue'):
            pass

        self.name = tk.StringVar()
        self._name_label = ttk.Label(self.frame, text='Fighter', background=color, state='disabled')
        self._name_entry = ttk.Entry(self.frame, textvariable=self.name)

        self.entry_hp = tk.IntVar()
        self._entry_hp_label = ttk.Label(self.frame, text='HP @ fight start')
        self._entry_hp_entry = ttk.Entry(self.frame, textvariable=self.entry_hp, state='disabled')

        self.hp_change = tk.IntVar()
        self._hp_change_label = ttk.Label(self.frame, text='HP change in fight')
        int_validation = self.frame.register(self._validate_integer)
        self._hp_change_entry = ttk.Entry(self.frame, textvariable=self.hp_change, validate='all',
                                          validatecommand=(int_validation, '%P', '%V'))

        # TODO: make total warnings changeable only via +1/-1 buttons
        self.total_warnings = tk.IntVar()
        self._total_warnings_label = ttk.Label(self.frame, text='N warnings')
        nonnegative_int_validation = self.frame.register(self._validate_nonnegative_integer)
        self._total_warnings_entry = ttk.Entry(self.frame, textvariable=self.total_warnings, validate='all',
                                               validatecommand=(nonnegative_int_validation, '%P', '%V'))

        self.frame.grid(column=column, row=row, columnspan=columnspan, rowspan=rowspan)
        self._set_layout()

    def _set_layout(self):
        self._name_label.grid(column=0, row=0)
        self._name_entry.grid(column=1, row=0)
        self._entry_hp_label.grid(column=0, row=1)
        self._entry_hp_entry.grid(column=1, row=1)
        self._hp_change_label.grid(column=0, row=2)
        self._hp_change_entry.grid(column=1, row=2)
        self._total_warnings_label.grid(column=0, row=3)
        self._total_warnings_entry.grid(column=1, row=3)

    def _validate_integer(self, value, reason) -> bool:
        if isinstance(value, int):
            return True
        if reason == 'focusin':
            return True
        if reason == 'focusout' or reason == 'forced':
            test = re.compile(r'^-?\d+$')
        else:
            test = re.compile(r'^-?\d*$')
        if not test.match(value):
            msg.showerror(message='Integer expected')
            return False
        return True

    def _validate_nonnegative_integer(self, value, reason) -> bool:
        if isinstance(value, int) and value >= 0:
            return True
        if reason == 'focusin':
            return True
        if reason == 'focusout' or reason == 'forced':
            test = re.compile(r'^\d+$')
        else:
            test = re.compile(r'^\d*$')
        if not test.match(value):
            msg.showerror(message='Nonnegative integer expected')
            return False
        return True

    def load_fighter(self, name: str, entry_hp: int, hp_change: int, total_warnings: int):
        self.name.set(name)
        self.entry_hp.set(entry_hp)
        self.hp_change.set(hp_change)
        self.total_warnings.set(total_warnings)

    def extract_fighter(self) -> Fighter | None:
        if not self._validate_integer(self.hp_change.get(), 'other'):
            return
        if not self._validate_nonnegative_integer(self.total_warnings.get(), 'other'):
            return

        name = self.name.get()
        entry_hp = self.entry_hp.get()

        hp_change = self.hp_change.get()
        total_warnings = self.total_warnings.get()

        return Fighter(name, entry_hp, hp_change, total_warnings)


class Storage:
    def __init__(self):
        self.fields = {
            k: v for k, v in zip(
            [x.strip() for x in 'RED, Red HP, Red score, Blue score, Blue HP, BLUE'.split(',')],
            [str, int, int, int, int, str],
            )
        }
        self.fights: dict[int, Fight] = {}
        self.unsaved_changes: bool = False
        self.path = ''

    def _parse_record(self, i, row: dict):
        type_matches = []
        for k, v in self.fields.items():

            if v == str and len(row[k].strip()):
                type_matches.append(True)
            elif v == int and row[k].strip().isnumeric():
                row[k] = int(row[k].strip())
                type_matches.append(True)
            elif v == int and row[k].strip() == '':
                row[k] = 0
                type_matches.append(True)
            else:
                type_matches.append(False)

        type_matches = [isinstance(row.get(k, None), v) for k, v in self.fields.items()]
        if all(type_matches):
            return True

        incorrect_fields = ', '.join([key for key, match in zip(row, type_matches) if not match])
        msg.showerror(message=f'In row {i} fields {incorrect_fields} are malformed')
        return False

    def load_round(self, path: str, backup_path: str, number: int):
        if os.path.exists(backup_path):
            raise ValueError('Round has already been loaded, rename backup file')  # TODO: change error to custom
        shutil.copy(path, backup_path)

        fights_ = {}
        with open(path, 'r', newline='') as f:
            reader = csv.DictReader(f, fieldnames=[x for x in self.fields.keys()])
            next(reader)  # Skip header
            for i, row in enumerate(reader, 1):
                if not self._parse_record(i, row):
                    raise ValueError('Bad input')
                fights_[i] = Fight(
                    number=i,
                    red=Fighter(row['RED'], row['Red HP'], row['Red score'], 0),
                    blue=Fighter(row['BLUE'], row['Blue HP'], row['Blue score'], 0),
                )
        self.fights = fights_
        self.path = path

    def dump_round(self):
        # Can always add '/' as path will be normalised.
        with open(self.path, 'w', newline='') as f:
            f.write(', '.join(self.fields.keys()) + '\n')
            for fight in self.fights.values():
                red = fight.red
                blue = fight.blue
                f.write(f'{red.name},{red.entry_hp},{red.hp_change},{blue.hp_change},{blue.entry_hp},{blue.name}\n')

    def fight_as_list(self, i: int):
        red = self.fights[i].red
        blue = self.fights[i].blue

        return [
            i,
            red.name, red.entry_hp, red.hp_change, red.total_warnings,
            blue.total_warnings, blue.hp_change, blue.entry_hp, blue.name
        ]

    def update_fight(self, number: int, red: Fighter, blue: Fighter):
        self.fights[number].red = red
        self.fights[number].blue = blue


class StorageUI:
    def __init__(self, master: tk.Misc, red_fighter: FighterDisplay, blue_fighter: FighterDisplay, *, column: int = 0, row: int = 0,
                 columnspan: int = 1, rowspan: int = 1):
        self.frame = ttk.Frame(master)
        self.red_fighter = red_fighter
        self.blue_fighter = blue_fighter

        self.directory = tk.StringVar()
        self.directory.set('./')
        self._directory_label = ttk.Label(self.frame, text='Folder')
        self._directory_entry = ttk.Entry(self.frame, textvariable=self.directory)

        self.prefix = tk.StringVar()
        self.prefix.set('mws')
        self._prefix_label = ttk.Label(self.frame, text='File prefix')
        self._prefix_entry = ttk.Entry(self.frame, textvariable=self.prefix)

        self._storage = Storage()

        self.round_number = tk.IntVar()
        self._round_label = ttk.Label(self.frame, text='Round number')
        self._round_entry = ttk.Entry(self.frame, textvariable=self.round_number)
        self._load_file_button = ttk.Button(self.frame, text='Load round', command=self.load_round)

        self.fight_number = tk.IntVar()
        self._fight_label = ttk.Label(self.frame, text='Fight number')
        self._fight_entry = ttk.Entry(self.frame, textvariable=self.fight_number)
        self._load_fight_button = ttk.Button(self.frame, text='Load fight', command=self.load_fight)
        self._save_fight_button = ttk.Button(self.frame, text='Save fight', command=self.save_fight)

        self.table = ttk.Treeview(self.frame, columns=[
            'fight_number', 'red_name', 'red_entry_hp', 'red_hp_change', 'red_total_warnings',
            'blue_total_warnings', 'blue_hp_change', 'blue_entry_hp', 'blue_name',
        ])

        self.table.heading('fight_number', text='Fight number')
        self.table.heading('red_name', text='Red name')
        self.table.heading('red_entry_hp', text='Red entry HP')
        self.table.heading('red_hp_change', text='Red hp change')
        self.table.heading('red_total_warnings', text='Red total warnings')
        self.table.heading('blue_total_warnings', text='Blue total warnings')
        self.table.heading('blue_hp_change', text='Blue hp change')
        self.table.heading('blue_entry_hp', text='Blue entry HP')
        self.table.heading('blue_name', text='Blue name')

        self.frame.grid(column=column, row=row, columnspan=columnspan, rowspan=rowspan)
        self._set_layout()

    def _set_layout(self):
        self._directory_label.grid(column=0, row=0)
        self._directory_entry.grid(column=1, row=0)
        self._prefix_label.grid(column=0, row=1)
        self._prefix_entry.grid(column=1, row=1)

        self._round_label.grid(column=0, row=2)
        self._round_entry.grid(column=1, row=2)


        self._load_file_button.grid(column=1, row=3)

        self._fight_label.grid(column=0, row=4)
        self._fight_entry.grid(column=1, row=4)

        self._load_fight_button.grid(column=0, row=5)
        self._save_fight_button.grid(column=1, row=5)

        self.table.grid(column=0, row=6, columnspan=2)

    def load_round(self):
        csv_folder = self.directory.get()
        if not os.path.exists(csv_folder):
            msg.showerror(message=f'Directory does not exist: {csv_folder}')
            return

        prefix = self.prefix.get()
        round_number = self.round_number.get()

        if not isinstance(round_number, int) or round_number < 1:
            msg.showerror(message='Round number must be positive integer')

        backup_path = f'{csv_folder}/{prefix}{round_number}_backup.csv'
        path = f'{csv_folder}/{prefix}{round_number}.csv'

        if not os.path.exists(path):
            msg.showerror(message=f'File does not exist: {path}')
            return

        if os.path.exists(backup_path):
            msg.showerror(message=f'Backup file already exists {backup_path}')
            return

        for k in self.table.get_children():
            self.table.delete(k)
        self._storage.load_round(path, backup_path, int(round_number))
        for k in self._storage.fights.keys():
            self.table.insert('', 'end', values=self._storage.fight_as_list(k))

    def load_fight(self):
        print(self.fight_number.get())
        print(str(self.fight_number.get()).isnumeric())
        if not str(self.fight_number.get()).isnumeric():
            return
        number = int(self.fight_number.get())

        fight = self._storage.fights[number]

        self.red_fighter.name.set(fight.red.name)
        self.red_fighter.entry_hp.set(fight.red.entry_hp)
        self.red_fighter.hp_change.set(fight.red.hp_change)
        self.red_fighter.total_warnings.set(fight.red.total_warnings)

        self.blue_fighter.name.set(fight.blue.name)
        self.blue_fighter.entry_hp.set(fight.blue.entry_hp)
        self.blue_fighter.hp_change.set(fight.blue.hp_change)
        self.blue_fighter.total_warnings.set(fight.blue.total_warnings)

    def save_fight(self):
        if not str(self.fight_number.get()).isnumeric():
            return
        number = int(self.fight_number.get())

        red = self.red_fighter.extract_fighter()
        blue = self.blue_fighter.extract_fighter()

        if red is None or blue is None:
            msg.showerror(message='Failed to save fight, check inputs')

        fight = Fight(number=number, red=red, blue=blue)
        print(self._storage.fights)
        self._storage.fights[fight.number] = fight
        print(self._storage.fights)

        self._storage.dump_round()

        for k in self.table.get_children():
            self.table.delete(k)
        for k in self._storage.fights.keys():
            self.table.insert('', 'end', values=self._storage.fight_as_list(k))


class JudgesFrame:
    def __init__(self, master: tk.Misc, timer: Timer, left_fighter: FighterDisplay, right_fighter: FighterDisplay):
        self.timer = timer
        self.left_fighter = left_fighter
        self.right_fighter = right_fighter

        self.frame = ttk.Frame(master)
        self.time = ttk.Label(self.frame, textvariable=timer.text)

        self.frame.grid(column=0, row=0, columnspan=2)
        self._set_layout()

    def _set_layout(self):
        self.time.grid(column=0, row=0, columnspan=4)


class JudgeFighterDisplay:
    def __init__(self, master: tk.Misc, fighter: FighterDisplay, *, row: int, column: int):
        self.frame = ttk.Frame(master)

        self.name = ttk.Label(self.frame, textvariable=fighter.name)
        self.entry_hp_label = ttk.Label(self.frame, text='HP в начале боя')
        self.entry_hp = ttk.Label(self.frame, textvariable=fighter.entry_hp)
        self.hp_change_label = ttk.Label(self.frame, text='Изменение HP')
        self.hp_change = ttk.Label(self.frame, textvariable=fighter.hp_change)
        self.warnings_label = ttk.Label(self.frame, text='Количество предупреждений')
        self.warnings = ttk.Label(self.frame, textvariable=fighter.total_warnings)

        self.frame.grid(column=column, row=row)

        self.name.grid(column=0, row=0, columnspan=2)

        self.entry_hp_label.grid(column=0, row=1)
        self.entry_hp.grid(column=1, row=1)
        self.hp_change_label.grid(column=0, row=2)
        self.hp_change.grid(column=1, row=2)
        self.warnings_label.grid(column=0, row=3)
        self.warnings.grid(column=1, row=3)


win = tk.Tk()
win.title('Secretary UI')

tabs = ttk.Notebook(win)

fight_tab = ttk.Frame(tabs)
timer = Timer(fight_tab, column=0, row=0, columnspan=2)
red_fighter = FighterDisplay(fight_tab, color='red', column=0, row=1)
blue_fighter = FighterDisplay(fight_tab, color='blue', column=1, row=1)
tabs.add(fight_tab, text='Fight')

csv_sync = ttk.Frame(tabs)
storage_ui = StorageUI(csv_sync, red_fighter, blue_fighter)
tabs.add(csv_sync, text='Round')

tabs.pack()


judges_window = tk.Toplevel()
judges_window.title('Tablo')

judges_frame = JudgesFrame(judges_window, timer, blue_fighter, red_fighter)
left_fighter = JudgeFighterDisplay(judges_window, blue_fighter, row=1, column=0)
right_fighter = JudgeFighterDisplay(judges_window, red_fighter, row=1, column=1)
