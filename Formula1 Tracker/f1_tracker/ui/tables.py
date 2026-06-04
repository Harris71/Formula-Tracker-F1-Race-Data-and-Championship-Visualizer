from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Iterable, Sequence

import pandas as pd

from f1_tracker.config import PRIMARY_COLOR
from f1_tracker.services.standings import ConstructorStanding, DriverStanding


def format_time(value) -> str:
    try:
        total_seconds = pd.to_timedelta(value).total_seconds()
        if pd.isna(total_seconds):
            return "-"
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        milliseconds = int((total_seconds - int(total_seconds)) * 1000)
        return f"{minutes:02}:{seconds:02}.{milliseconds:03}"
    except Exception:
        return "-"


def _row_tag(position: int) -> str:
    if position == 1:
        return "gold"
    if position == 2:
        return "silver"
    if position == 3:
        return "bronze"
    return "even" if position % 2 == 0 else "odd"


def show_table_window(title: str, columns: Sequence[str], rows: Iterable[Sequence]) -> None:
    window = tk.Toplevel()
    window.title(title)
    window.geometry("760x560")

    frame = tk.Frame(window, bg=PRIMARY_COLOR, padx=10, pady=10)
    frame.pack(fill="both", expand=True)

    tk.Label(frame, text=title, font=("Arial", 14, "bold"), bg=PRIMARY_COLOR, fg="white").pack(pady=5)

    table_frame = tk.Frame(frame)
    table_frame.pack(fill="both", expand=True)

    scrollbar = tk.Scrollbar(table_frame)
    scrollbar.pack(side="right", fill="y")

    tree = ttk.Treeview(table_frame, columns=columns, show="headings", yscrollcommand=scrollbar.set)
    scrollbar.config(command=tree.yview)

    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
    style.configure("Treeview", font=("Arial", 11), rowheight=25)
    style.map("Treeview", background=[("selected", PRIMARY_COLOR)])

    default_widths = {
        "Pos": 50,
        "Driver": 170,
        "Team": 160,
        "Constructor": 220,
        "Nationality": 110,
        "Points": 80,
        "Wins": 70,
        "Gap": 110,
        "Q1": 100,
        "Q2": 100,
        "Q3": 100,
    }

    for column in columns:
        tree.heading(column, text=column)
        tree.column(column, anchor="center" if column in {"Pos", "Points", "Wins", "Gap", "Q1", "Q2", "Q3"} else "w", width=default_widths.get(column, 120))

    tree.tag_configure("gold", background="#FFD700")
    tree.tag_configure("silver", background="#C0C0C0")
    tree.tag_configure("bronze", background="#CD7F32")
    tree.tag_configure("even", background="#fff8f8")
    tree.tag_configure("odd", background="#e0e0e0")

    for row in rows:
        position = int(row[0]) if str(row[0]).isdigit() else 0
        tree.insert("", "end", values=row, tags=(_row_tag(position),))

    tree.pack(fill="both", expand=True, padx=10, pady=10)


def show_race_results(session) -> None:
    if session is None or session.results is None or session.results.empty:
        raise ValueError("No race results are loaded yet.")

    rows = []
    for _, row in session.results.iterrows():
        rows.append((
            int(row.get("Position", 0)),
            row.get("FullName", row.get("Driver", "Unknown")),
            row.get("TeamName", "Unknown"),
            int(row.get("Points", 0)),
            format_time(row.get("Time")),
        ))

    title = f"{session.event['EventName']} {session.event.year} Race Results"
    show_table_window(title, ("Pos", "Driver", "Team", "Points", "Gap"), rows)


def show_qualifying_results(session) -> None:
    if session is None or session.results is None or session.results.empty:
        raise ValueError("No qualifying results are loaded yet.")

    rows = []
    for _, row in session.results.iterrows():
        rows.append((
            int(row.get("Position", 0)),
            row.get("FullName", row.get("Driver", "Unknown")),
            row.get("TeamName", "Unknown"),
            format_time(row.get("Q1")),
            format_time(row.get("Q2")),
            format_time(row.get("Q3")),
        ))

    title = f"{session.event['EventName']} {session.event.year} Qualifying Results"
    show_table_window(title, ("Pos", "Driver", "Team", "Q1", "Q2", "Q3"), rows)


def show_wdc_standings(year: int, standings: list[DriverStanding]) -> None:
    rows = [(s.position, s.driver, s.nationality, s.team, s.points, s.wins) for s in standings]
    show_table_window(
        f"{year} World Drivers' Championship Standings",
        ("Pos", "Driver", "Nationality", "Team", "Points", "Wins"),
        rows,
    )


def show_wcc_standings(year: int, standings: list[ConstructorStanding]) -> None:
    rows = [(s.position, s.constructor, s.points, s.wins) for s in standings]
    show_table_window(
        f"{year} Constructors' Championship Standings",
        ("Pos", "Constructor", "Points", "Wins"),
        rows,
    )
