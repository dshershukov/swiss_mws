import csv
import os
import tkinter as tk
import tkinter.ttk as ttk

from collections.abc import Callable
from dataclasses import dataclass

from tkinter.messagebox import (
    showerror,
)

from .fighter import (
    Fighter,
    ActiveFighter,
    BadFighterStateError,
)


@dataclass
class Fight:
    number: int
    red: Fighter
    blue: Fighter


class Storage:
    def __init__(self, red_fighter: ActiveFighter, blue_fighter: ActiveFighter, table: ttk.Treeview | None,
                 combobox: ttk.Combobox | None):
        self.directory = tk.StringVar(value='./')
        self.file_prefix = tk.StringVar(value='mws')
        self.round_number = tk.StringVar(value='1')
        self.fight_number = tk.IntVar(value=0)

        self.red_fighter = red_fighter
        self.blue_fighter = blue_fighter
        self.table = table

        self.fields = {
            k: v for k, v in zip(
                [x.strip() for x in 'RED, Red HP, Red score, Red warnings, '
                                    'Blue warnings, Blue score, Blue HP, BLUE'.split(',')],
                [str, int, int, int, int, int, int, str],
            )
        }
        self.fights: dict[int, Fight] = {}
        self.current_fight: Fight = self._get_dummy_fight()
        self.path = ''
        self.combobox = combobox

    @staticmethod
    def _get_dummy_fighter() -> Fighter:
        return Fighter('', 0, 0, 0)

    def _get_dummy_fight(self) -> Fight:
        return Fight(0, self._get_dummy_fighter(), self._get_dummy_fighter())

    def _input_is_not_changed(self) -> bool:
        """
        Check that displayed data is the same as stored internally
        :return: bool
        """
        # If displayed data is not valid, ask operator to fix it first
        try:
            displayed_red_fighter = self.red_fighter.get()
            displayed_blue_fighter = self.blue_fighter.get()
        except BadFighterStateError:
            showerror(message='Отображаемый бой должен быть валидным')
            return False

        test = (displayed_red_fighter == self.current_fight.red and displayed_blue_fighter == self.current_fight.blue)
        return test

    def _validate_record(self, i, row: dict):
        type_matches = []
        for k, v in self.fields.items():

            if v == str and len(row[k].strip()):
                type_matches.append(True)
            elif v == int and row[k].strip() == '':
                row[k] = 0
                type_matches.append(True)
            elif v == int:
                try:
                    int(row[k].strip())
                    row[k] = int(row[k].strip())
                    type_matches.append(True)
                except ValueError:
                    type_matches.append(False)
            else:
                type_matches.append(False)

        type_matches = [isinstance(row.get(k, None), v) for k, v in self.fields.items()]
        if all(type_matches):
            return True

        incorrect_fields = ', '.join([key for key, match in zip(row, type_matches) if not match])
        showerror(message=f'In row {i} fields {incorrect_fields} are malformed')
        return False

    def _load_fights(self):
        csv_folder = self.directory.get()
        if not os.path.exists(csv_folder):
            showerror(message=f'Directory does not exist: {csv_folder}')
            return

        prefix = self.file_prefix.get()
        round_number = self.round_number.get()

        backup_path = f'{csv_folder}/{prefix}{round_number}_backup.csv'
        path = f'{csv_folder}/{prefix}{round_number}.csv'

        if not os.path.exists(path):
            showerror(message=f'File does not exist: {path}')
            return

        if os.path.exists(backup_path):
            showerror(message=f'Backup file already exists {backup_path}')
            return

        fights_ = {}
        try:
            with open(path, 'r', newline='') as f:
                reader = csv.DictReader(f, fieldnames=[x for x in self.fields.keys()])
                next(reader)  # Skip header
                for i, row in enumerate(reader, 1):
                    if not self._validate_record(i, row):
                        raise ValueError('Bad input')
                    fights_[i] = Fight(
                        number=i,
                        red=Fighter(row['RED'], row['Red HP'], row['Red score'], row['Red warnings']),
                        blue=Fighter(row['BLUE'], row['Blue HP'], row['Blue score'], row['Blue warnings']),
                    )
        except Exception as e:
            showerror(message='Не удалось прочитать файл')
            return

        if not fights_:
            showerror(message='В файле нет боёв?')

        self.fights = fights_
        self.path = path

    def load_round(self):
        if not self._input_is_not_changed():
            showerror(message='Отображаемый бой не сохранён. Сохраните его или сбросьте.')
            return
        self._load_fights()
        self._set_current_fight(1)

        self.repopulate_table()
        if self.combobox is not None:
            self.combobox['values'] = tuple(x for x in self.fights.keys())
            self.combobox.set(1)

    def _set_current_fight(self, fight_number: int) -> None:
        """
        Sets displayed fight, assumes validated input

        :param fight_number: fight number, 0 to reset UI, otherwise validated int
        :return: None
        """
        new_fight = self._get_dummy_fight()
        if fight_number != 0:
            new_fight = self.fights[fight_number]

        self.red_fighter.set(new_fight.red)
        self.blue_fighter.set(new_fight.blue)
        self.current_fight = new_fight

    def choose_fight(self):
        """
        Display a fight specified in fight_number variable

        Allow displaying only if red_fighter and blue_fighter are consistent with saved data.
        This requires the operator to either explicitly save or reset the previous fight.
        """
        # If displayed data is not valid, ask operator to fix it first
        if not self._input_is_not_changed():
            showerror(message='Отображаемый бой не сохранён. Сохраните его или сбросьте.')
            return

        self._set_current_fight(self.fight_number.get())

    def _save_round(self):
        # Can always add '/' as path will be normalised.
        with open(self.path, 'w', newline='') as f:
            f.write(', '.join(self.fields.keys()) + '\n')
            for fight in self.fights.values():
                red = fight.red
                blue = fight.blue
                f.write(
                    f'{red.name},{red.entry_hp},{red.hp_change},{red.total_warnings},'
                    f'{blue.total_warnings},{blue.hp_change},{blue.entry_hp},{blue.name}\n')

    def save_fight(self):
        # If displayed data is not valid, ask operator to fix it first
        try:
            displayed_red_fighter = self.red_fighter.get()
            displayed_blue_fighter = self.blue_fighter.get()
        except BadFighterStateError:
            showerror(message='Отображаемый бой должен быть валидным')
            return

        self.current_fight = Fight(self.current_fight.number, displayed_red_fighter, displayed_blue_fighter)
        self.fights[self.current_fight.number] = self.current_fight
        self.repopulate_table()
        try:
            self._save_round()
        except Exception as e:
            showerror(message='Не получилось сохранить текуший раунд')
            return

    def reset_fight(self):
        self.red_fighter.set(self.current_fight.red)
        self.blue_fighter.set(self.current_fight.blue)

    def fight_as_list(self, i: int):
        red = self.fights[i].red
        blue = self.fights[i].blue

        return [
            i,
            red.name, red.entry_hp, red.hp_change, red.total_warnings,
            blue.total_warnings, blue.hp_change, blue.entry_hp, blue.name
        ]

    def repopulate_table(self):
        if self.table is None:
            return

        for k in self.table.get_children():
            self.table.delete(k)
        for k in self.fights.keys():
            self.table.insert('', 'end', values=self.fight_as_list(k))
