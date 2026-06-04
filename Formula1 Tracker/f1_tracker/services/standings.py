from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests

from f1_tracker.config import JOLPICA_BASE_URL


@dataclass(frozen=True)
class DriverStanding:
    position: int
    driver: str
    nationality: str
    team: str
    points: str
    wins: str


@dataclass(frozen=True)
class ConstructorStanding:
    position: int
    constructor: str
    points: str
    wins: str


def _get_json(url: str) -> dict[str, Any]:
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return response.json()


def _standings_list(data: dict[str, Any]) -> list[dict[str, Any]]:
    return data.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [])


def fetch_driver_standings(year: int) -> list[DriverStanding]:
    url = f"{JOLPICA_BASE_URL}/{year}/driverstandings/?format=json"
    data = _get_json(url)
    lists = _standings_list(data)
    if not lists:
        return []

    standings: list[DriverStanding] = []
    for item in lists[0].get("DriverStandings", []):
        driver = item.get("Driver", {})
        constructor = (item.get("Constructors") or [{}])[0]
        standings.append(
            DriverStanding(
                position=int(item.get("position", 0)),
                driver=f"{driver.get('givenName', '')} {driver.get('familyName', '')}".strip(),
                nationality=driver.get("nationality", "-"),
                team=constructor.get("name", "-"),
                points=item.get("points", "0"),
                wins=item.get("wins", "0"),
            )
        )
    return standings


def fetch_constructor_standings(year: int) -> list[ConstructorStanding]:
    url = f"{JOLPICA_BASE_URL}/{year}/constructorstandings/?format=json"
    data = _get_json(url)
    lists = _standings_list(data)
    if not lists:
        return []

    standings: list[ConstructorStanding] = []
    for item in lists[0].get("ConstructorStandings", []):
        constructor = item.get("Constructor", {})
        standings.append(
            ConstructorStanding(
                position=int(item.get("position", 0)),
                constructor=constructor.get("name", "-"),
                points=item.get("points", "0"),
                wins=item.get("wins", "0"),
            )
        )
    return standings


def get_wdc_summary(year: int) -> str:
    standings = fetch_driver_standings(year)
    if not standings:
        return f"No World Drivers' Championship data found for {year}."
    champion = standings[0]
    return f"The {year} World Drivers' Champion: {champion.driver}"


def get_wcc_summary(year: int) -> str:
    standings = fetch_constructor_standings(year)
    if not standings:
        return f"No World Constructors' Championship data found for {year}."
    champion = standings[0]
    return f"The {year} World Constructors' Champion: {champion.constructor}"
