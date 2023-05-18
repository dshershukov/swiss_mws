import tkinter as tk
import tkinter.ttk as ttk


from .common.fighter import ActiveFighter
from .common.timer import Timer
from .common.settings import Storage

from .widgets.fighter import FighterSecretaryWidget
from .widgets.timer import TimerWidget
from .widgets.settings import StorageWidget, FightLoadWidget
from .widgets.judge_screen import JudgeScreen


def prepare_app() -> tk.Tk:
    win = tk.Tk()

    win.title('Secretary UI')

    tabs = ttk.Notebook(win)

    fight_tab = ttk.Frame(tabs)
    red_fighter = ActiveFighter()
    blue_fighter = ActiveFighter()
    timer = Timer(win)
    storage = Storage(red_fighter, blue_fighter, None, None)

    w_timer = TimerWidget(fight_tab, timer, column=0, row=0, columnspan=2)
    w_red_fighter = FighterSecretaryWidget(fight_tab, red_fighter, color='red', column=0, row=1, columnspan=1,
                                           rowspan=1)
    w_blue_fighter = FighterSecretaryWidget(fight_tab, blue_fighter, color='blue', column=1, row=1, columnspan=1,
                                            rowspan=1)
    w_fight_choice = FightLoadWidget(fight_tab, storage, column=0, row=2, columnspan=2)

    tabs.add(fight_tab, text='Бой')

    settings_tab = ttk.Frame(tabs)
    w_storage = StorageWidget(settings_tab, storage, timer)
    tabs.add(settings_tab, text='Настройки')

    tabs.pack()

    judges_window = tk.Toplevel()
    judges_window.title('Fight UI')

    w_judges_frame = JudgeScreen(judges_window, red_fighter, blue_fighter, timer)

    return win
