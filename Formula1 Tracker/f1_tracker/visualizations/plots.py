from __future__ import annotations

from tkinter import messagebox

import fastf1.plotting
import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def rotate_coordinates(xy, *, angle: float):
    rotation_matrix = np.array([
        [np.cos(angle), np.sin(angle)],
        [-np.sin(angle), np.cos(angle)],
    ])
    return np.matmul(xy, rotation_matrix)


def require_session(session, session_name: str = "session") -> None:
    if session is None:
        raise ValueError(f"No {session_name} loaded yet.")


def plot_circuit(session) -> None:
    try:
        require_session(session, "qualifying session")
        lap = session.laps.pick_fastest()
        position_data = lap.get_pos_data()
        circuit_info = session.get_circuit_info()

        track = position_data.loc[:, ("X", "Y")].to_numpy()
        track_angle = circuit_info.rotation / 180 * np.pi
        rotated_track = rotate_coordinates(track, angle=track_angle)

        fig, ax = plt.subplots(figsize=(8, 6), facecolor="grey")
        ax.set_facecolor("gray")
        ax.plot(rotated_track[:, 0], rotated_track[:, 1], color="white")

        offset_vector = [500, 0]
        for _, corner in circuit_info.corners.iterrows():
            label = f"{corner['Number']}{corner['Letter']}"
            offset_angle = corner["Angle"] / 180 * np.pi
            offset_x, offset_y = rotate_coordinates(offset_vector, angle=offset_angle)

            text_x = corner["X"] + offset_x
            text_y = corner["Y"] + offset_y
            text_x, text_y = rotate_coordinates([text_x, text_y], angle=track_angle)
            track_x, track_y = rotate_coordinates([corner["X"], corner["Y"]], angle=track_angle)

            ax.scatter(text_x, text_y, color="grey", s=140)
            ax.plot([track_x, text_x], [track_y, text_y], color="grey")
            ax.text(text_x, text_y, label, va="center_baseline", ha="center", size="small", color="white")

        ax.set_title(session.event["Location"])
        ax.set_xticks([])
        ax.set_yticks([])
        ax.axis("equal")
        plt.tight_layout()
        plt.show()
    except Exception as exc:
        messagebox.showerror("Plot error", f"Could not plot circuit: {exc}")


def plot_position_changes(session) -> None:
    try:
        require_session(session, "race session")
        fig, ax = plt.subplots(figsize=(8.0, 4.9))

        result_index = "Driver" if "Driver" in session.results.columns else "Abbreviation"
        grid_positions = session.results.set_index(result_index)["GridPosition"]

        for driver_number in session.drivers:
            driver_laps = session.laps.pick_drivers(driver_number)
            if driver_laps.empty:
                continue

            abbreviation = driver_laps["Driver"].iloc[0]
            style = fastf1.plotting.get_driver_style(
                identifier=abbreviation,
                style=["color", "linestyle"],
                session=session,
            )

            if abbreviation in grid_positions:
                lap_zero = pd.DataFrame({"LapNumber": [0], "Position": [int(grid_positions[abbreviation])]})
                driver_laps = pd.concat([lap_zero, driver_laps], ignore_index=True)

            ax.plot(driver_laps["LapNumber"], driver_laps["Position"], label=abbreviation, **style)

        ax.set_ylim([20.5, 0.5])
        ax.set_yticks([1, 5, 10, 15, 20])
        ax.set_xlabel("Lap")
        ax.set_ylabel("Position")
        ax.legend(bbox_to_anchor=(1.0, 1.02))
        plt.tight_layout()
        plt.show()
    except Exception as exc:
        messagebox.showerror("Plot error", f"Could not plot position changes: {exc}")


def plot_tire_strategies(session) -> None:
    try:
        require_session(session, "race session")
        driver_codes = [session.get_driver(driver)["Abbreviation"] for driver in session.drivers]
        stints = session.laps[["Driver", "Stint", "Compound", "LapNumber"]]
        stints = stints.groupby(["Driver", "Stint", "Compound"]).count().reset_index()
        stints = stints.rename(columns={"LapNumber": "StintLength"})

        fig, ax = plt.subplots(figsize=(5, 10))
        for driver in driver_codes:
            driver_stints = stints.loc[stints["Driver"] == driver]
            previous_stint_end = 0
            for _, row in driver_stints.iterrows():
                compound_color = fastf1.plotting.get_compound_color(row["Compound"], session=session)
                ax.barh(
                    y=driver,
                    width=row["StintLength"],
                    left=previous_stint_end,
                    color=compound_color,
                    edgecolor="black",
                    fill=True,
                )
                previous_stint_end += row["StintLength"]

        ax.set_xlabel("Lap Number")
        ax.grid(False)
        ax.invert_yaxis()
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        plt.tight_layout()
        plt.show()
    except Exception as exc:
        messagebox.showerror("Plot error", f"Could not plot tire strategies: {exc}")


def plot_laptimes(session) -> None:
    try:
        require_session(session, "race session")
        fastf1.plotting.setup_mpl(mpl_timedelta_support=True, misc_mpl_mods=False, color_scheme="fastf1")

        point_finishers = session.drivers[:10]
        driver_laps = session.laps.pick_drivers(point_finishers).pick_quicklaps().reset_index()
        finishing_order = [session.get_driver(driver)["Abbreviation"] for driver in point_finishers]
        driver_laps["LapTime (s)"] = driver_laps["LapTime"].dt.total_seconds()

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.violinplot(
            data=driver_laps,
            x="Driver",
            y="LapTime (s)",
            hue="Driver",
            inner=None,
            density_norm="area",
            order=finishing_order,
            palette=fastf1.plotting.get_driver_color_mapping(session=session),
            ax=ax,
        )
        sns.swarmplot(
            data=driver_laps,
            x="Driver",
            y="LapTime (s)",
            order=finishing_order,
            hue="Compound",
            palette=fastf1.plotting.get_compound_mapping(session=session),
            hue_order=driver_laps["Compound"].unique().tolist(),
            linewidth=0,
            size=4,
            ax=ax,
        )

        ax.set_xlabel("Driver")
        ax.set_ylabel("Lap Time (s)")
        plt.suptitle(f"{session.event.year} {session.event.Location} Grand Prix Lap Time Distributions")
        sns.despine(left=True, bottom=True)
        plt.tight_layout()
        plt.show()
    except Exception as exc:
        messagebox.showerror("Plot error", f"Could not plot lap times: {exc}")


def plot_team_pace(session) -> None:
    try:
        require_session(session, "race session")
        fastf1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False, color_scheme="fastf1")

        laps = session.laps.pick_quicklaps()
        transformed_laps = laps.copy()
        transformed_laps.loc[:, "LapTime (s)"] = laps["LapTime"].dt.total_seconds()

        team_order = (
            transformed_laps[["Team", "LapTime (s)"]]
            .groupby("Team")
            .median()["LapTime (s)"]
            .sort_values()
            .index
        )
        team_palette = {team: fastf1.plotting.get_team_color(team, session=session) for team in team_order}

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.boxplot(
            data=transformed_laps,
            x="Team",
            y="LapTime (s)",
            hue="Team",
            order=team_order,
            palette=team_palette,
            whiskerprops={"color": "white"},
            boxprops={"edgecolor": "white"},
            medianprops={"color": "grey"},
            capprops={"color": "white"},
            ax=ax,
        )

        ax.set_title(f"{session.event['EventName']} {session.event.year} Team Pace")
        ax.grid(visible=False)
        ax.set(xlabel=None)
        plt.tight_layout()
        plt.show()
    except Exception as exc:
        messagebox.showerror("Plot error", f"Could not plot team pace: {exc}")
