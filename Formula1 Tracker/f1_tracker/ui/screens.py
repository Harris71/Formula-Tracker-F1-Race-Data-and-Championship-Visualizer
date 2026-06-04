from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import Button, Canvas, PhotoImage, messagebox

from f1_tracker.config import ASSETS_DIR, BACKGROUND_COLOR, LIGHT_TEXT_COLOR, PRIMARY_COLOR
from f1_tracker.services.standings import (
    fetch_constructor_standings,
    fetch_driver_standings,
    get_wcc_summary,
    get_wdc_summary,
)
from f1_tracker.ui.tables import (
    show_qualifying_results,
    show_race_results,
    show_wcc_standings,
    show_wdc_standings,
)
from f1_tracker.visualizations.plots import (
    plot_circuit,
    plot_laptimes,
    plot_position_changes,
    plot_team_pace,
    plot_tire_strategies,
)


class BaseScreen(tk.Frame):
    asset_folder = ""

    def __init__(self, parent, controller) -> None:
        super().__init__(parent, bg=BACKGROUND_COLOR)
        self.controller = controller
        self.images: list[PhotoImage] = []
        self.canvas = Canvas(
            self,
            bg=BACKGROUND_COLOR,
            height=600,
            width=600,
            bd=0,
            highlightthickness=0,
            relief="ridge",
        )
        self.canvas.place(x=0, y=0)

    @property
    def assets_path(self) -> Path:
        return ASSETS_DIR / self.asset_folder

    def asset(self, file_name: str) -> Path:
        return self.assets_path / file_name

    def photo(self, file_name: str) -> PhotoImage:
        image = PhotoImage(file=self.asset(file_name))
        self.images.append(image)
        return image

    def draw_header(self, title: str, x: float = 300.0) -> None:
        self.canvas.create_rectangle(0.0, 0.0, 600.0, 200.0, fill=PRIMARY_COLOR, outline="")
        self.canvas.create_text(x, 100.0, anchor="center", text=title, fill=LIGHT_TEXT_COLOR, font=("Inter", 30))

    def image_button(self, image_name: str, command, x: float, y: float, width: float, height: float) -> Button:
        image = self.photo(image_name)
        button = Button(self, image=image, borderwidth=0, highlightthickness=0, command=command, relief="flat")
        button.image = image
        button.place(x=x, y=y, width=width, height=height)
        return button

    def text_entry(self, image_name: str, x: float, y: float, width: float, height: float) -> tk.Entry:
        entry_image = self.photo(image_name)
        self.canvas.create_image(x + width / 2, y + height / 2, image=entry_image)
        entry = tk.Entry(self, bd=0, bg="#D9D9D9", fg="#000716", highlightthickness=0, font=("Arial", 12))
        entry.place(x=x, y=y, width=width, height=height)
        return entry


def parse_year(raw_year: str) -> int | None:
    raw_year = raw_year.strip()
    if not raw_year.isdigit():
        return None
    return int(raw_year)


def handle_action(action, error_title: str = "Error") -> None:
    try:
        action()
    except Exception as exc:
        messagebox.showerror(error_title, str(exc))


class MainMenuScreen(BaseScreen):
    asset_folder = "MainMenu_Frame"

    def __init__(self, parent, controller) -> None:
        super().__init__(parent, controller)
        self.draw_header("F1 Project")
        self.image_button("button_1.png", lambda: controller.show_frame(RaceDataInputScreen), 200, 240, 200, 70)
        self.image_button("button_2.png", lambda: controller.show_frame(CircuitInputScreen), 200, 340, 200, 70)
        self.image_button("button_3.png", lambda: controller.show_frame(ChampionshipsScreen), 200, 440, 200, 70)


class ChampionshipsScreen(BaseScreen):
    asset_folder = "Championships_Frame"

    def __init__(self, parent, controller) -> None:
        super().__init__(parent, controller)
        self.draw_header("Find Champions")
        self.image_button("button_1.png", lambda: controller.show_frame(WdcInputScreen), 200, 270, 200, 65)
        self.image_button("button_2.png", lambda: controller.show_frame(WccInputScreen), 200, 387, 200, 65)
        self.image_button("button_3.png", lambda: controller.show_frame(MainMenuScreen), 250, 503, 100, 45)


class ChampionshipInputScreen(BaseScreen):
    title = ""
    summary_function = None
    standings_function = None
    table_function = None

    def __init__(self, parent, controller) -> None:
        super().__init__(parent, controller)
        self.draw_header(self.title)
        self.canvas.create_text(300, 276, anchor="center", text="Enter Year", fill="#000000", font=("Inter", 20))
        self.year_entry = self.text_entry("entry_1.png", 223, 290, 154, 38)
        self.image_button("button_1.png", self.fetch_summary, 249, 352, 110, 43)
        self.image_button("button_2.png", lambda: controller.show_frame(ChampionshipsScreen), 249, 410, 110, 43)
        self.result_label = tk.Label(self, text="", bg=BACKGROUND_COLOR, fg="black", font=("Inter", 15), wraplength=420)
        self.result_label.place(x=90, y=460, width=420)
        self.standings_button = None

    def _get_year(self) -> int | None:
        year = parse_year(self.year_entry.get())
        if year is None:
            self.result_label.config(text="Please enter a valid year.")
        return year

    def fetch_summary(self) -> None:
        year = self._get_year()
        if year is None:
            return

        try:
            self.result_label.config(text=self.summary_function(year))
            if self.standings_button is None:
                self.standings_button = self.image_button("button_3.png", self.show_standings, 190, 520, 225, 55)
        except Exception as exc:
            self.result_label.config(text=f"Could not fetch data: {exc}")

    def show_standings(self) -> None:
        year = self._get_year()
        if year is None:
            return
        try:
            standings = self.standings_function(year)
            if not standings:
                messagebox.showerror("No data", f"No standings found for {year}.")
                return
            self.table_function(year, standings)
        except Exception as exc:
            messagebox.showerror("Standings error", str(exc))


class WdcInputScreen(ChampionshipInputScreen):
    asset_folder = "WDC_Frame"
    title = "Find WDC"
    summary_function = staticmethod(get_wdc_summary)
    standings_function = staticmethod(fetch_driver_standings)
    table_function = staticmethod(show_wdc_standings)


class WccInputScreen(ChampionshipInputScreen):
    asset_folder = "WDC_Frame"
    title = "Find WCC"
    summary_function = staticmethod(get_wcc_summary)
    standings_function = staticmethod(fetch_constructor_standings)
    table_function = staticmethod(show_wcc_standings)


class SessionInputScreen(BaseScreen):
    asset_folder = "SessionInput_Frame"
    title = ""

    def __init__(self, parent, controller) -> None:
        super().__init__(parent, controller)
        self.draw_header(self.title)
        self.canvas.create_text(300, 248, anchor="center", text="Enter Grand Prix Name", fill="#000000", font=("Inter", 20))
        self.canvas.create_text(300, 348, anchor="center", text="Enter Year", fill="#000000", font=("Inter", 20))
        self.gp_entry = self.text_entry("entry_1.png", 176, 276, 238, 46)
        self.year_entry = self.text_entry("entry_2.png", 176, 376, 238, 46)
        self.image_button("button_1.png", self.submit, 161, 476, 126, 50)
        self.image_button("button_2.png", lambda: controller.show_frame(MainMenuScreen), 303, 476, 126, 50)

    def get_inputs(self) -> tuple[str, int] | None:
        grand_prix = self.gp_entry.get().strip()
        year = parse_year(self.year_entry.get())

        if not grand_prix:
            messagebox.showerror("Input error", "Please enter a Grand Prix name.")
            return None
        if year is None:
            messagebox.showerror("Input error", "Please enter a valid numeric year.")
            return None
        return grand_prix, year

    def submit(self) -> None:
        raise NotImplementedError


class RaceDataInputScreen(SessionInputScreen):
    title = "Enter Race Details"

    def submit(self) -> None:
        inputs = self.get_inputs()
        if inputs is None:
            return
        grand_prix, year = inputs

        self.controller.race_session = self.controller.load_session(year, grand_prix, "R")
        self.controller.quali_session = self.controller.load_session(year, grand_prix, "Q")

        if self.controller.race_session and self.controller.quali_session:
            messagebox.showinfo("Success", f"Loaded sessions for {grand_prix} {year}")
            self.controller.show_frame(RaceOptionsScreen, year)


class CircuitInputScreen(SessionInputScreen):
    title = "Enter Circuit Details"

    def submit(self) -> None:
        inputs = self.get_inputs()
        if inputs is None:
            return
        grand_prix, year = inputs
        session = self.controller.load_session(year, grand_prix, "Q")
        plot_circuit(session)


class RaceOptionsScreen(BaseScreen):
    asset_folder = "RaceOptions_Frame"

    def __init__(self, parent, controller, year: int) -> None:
        super().__init__(parent, controller)
        self.year = int(year)
        self.draw_header("Race Options")

        self.image_button("button_3.png", lambda: handle_action(lambda: show_race_results(controller.race_session)), 100, 240, 150, 70)
        self.image_button("button_4.png", lambda: handle_action(lambda: show_qualifying_results(controller.quali_session)), 350, 240, 150, 70)

        if self.year < 2018:
            tk.Label(
                self,
                text="Advanced FastF1 timing data is not available for races before 2018.",
                bg=BACKGROUND_COLOR,
                fg="black",
                font=("Inter", 10),
                wraplength=420,
            ).place(x=90, y=390, width=420)
        else:
            self.image_button("button_5.png", lambda: plot_position_changes(controller.race_session), 100, 340, 150, 70)
            self.image_button("button_6.png", lambda: plot_tire_strategies(controller.race_session), 350, 340, 150, 70)
            self.image_button("button_7.png", lambda: plot_team_pace(controller.race_session), 100, 440, 150, 70)
            self.image_button("button_1.png", lambda: plot_laptimes(controller.race_session), 350, 440, 150, 70)

        self.image_button("button_2.png", lambda: controller.show_frame(RaceDataInputScreen), 250, 532, 100, 50)
