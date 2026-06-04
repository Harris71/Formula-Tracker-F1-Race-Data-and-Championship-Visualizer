import tkinter as tk
from tkinter import messagebox

from f1_tracker.config import APP_TITLE, CACHE_DIR, WINDOW_SIZE
from f1_tracker.services.sessions import load_f1_session
from f1_tracker.ui.screens import (
    ChampionshipsScreen,
    CircuitInputScreen,
    MainMenuScreen,
    RaceDataInputScreen,
    RaceOptionsScreen,
    WccInputScreen,
    WdcInputScreen,
)


class F1App(tk.Tk):
    """Main Tkinter application controller."""

    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(WINDOW_SIZE)
        self.resizable(False, False)

        self.race_session = None
        self.quali_session = None
        self.frames: dict[type[tk.Frame], tk.Frame] = {}

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        for screen in (
            MainMenuScreen,
            ChampionshipsScreen,
            WdcInputScreen,
            WccInputScreen,
            RaceDataInputScreen,
            CircuitInputScreen,
        ):
            self._build_screen(screen)

        self.show_frame(MainMenuScreen)

    def _build_screen(self, screen_class: type[tk.Frame], *args) -> tk.Frame:
        frame = screen_class(self.container, self, *args)
        self.frames[screen_class] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        return frame

    def show_frame(self, screen_class: type[tk.Frame], *args) -> None:
        if screen_class is RaceOptionsScreen:
            frame = self._build_screen(screen_class, *args)
        else:
            frame = self.frames[screen_class]
        frame.tkraise()

    def load_session(self, year: int, grand_prix: str, session_type: str):
        try:
            return load_f1_session(year, grand_prix, session_type, CACHE_DIR)
        except Exception as exc:
            messagebox.showerror("Session loading failed", str(exc))
            return None
