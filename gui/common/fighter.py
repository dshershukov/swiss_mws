from dataclasses import dataclass
from tkinter import (
    StringVar,
    IntVar,
)


@dataclass
class Fighter:
    name: str
    entry_hp: int
    hp_change: int
    total_warnings: int


class BadFighterStateError(Exception):
    pass


class ActiveFighter:
    def __init__(self):
        self.name = StringVar()
        self.entry_hp = IntVar()
        self.hp_change = IntVar()
        self.total_warnings = IntVar()

    def set(self, fighter: Fighter) -> None:
        self.name.set(fighter.name)
        self.entry_hp.set(fighter.entry_hp)
        self.hp_change.set(fighter.hp_change)
        self.total_warnings.set(fighter.total_warnings)

    def get(self) -> Fighter:
        try:
            fighter = Fighter(self.name.get(), self.entry_hp.get(), self.hp_change.get(), self.total_warnings.get())
        except Exception as e:
            raise BadFighterStateError() from e

        return fighter
