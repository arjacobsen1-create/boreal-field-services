"""Boreal Field Services - the stock picture.

Stock's raw material: what the system of record shows, what is actually
there, and how fresh each line is. The distinction this module exists to
protect is the one the whole design turns on:

    confirmed stock  !=  a number on a screen

A line is only CONFIRMED when the station's data is verified and fresh.
A line whose system quantity disagrees with the physical count is a
PHANTOM. A line that cannot be confirmed because the station has not
synced is UNVERIFIED, and stale data must never be treated as confirmed
stock (see governance/gates.yaml).

Stdlib only. Data comes from ../data/sample-stock.json (100% synthetic).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "sample-stock.json"

CONFIRMED = "confirmed"
PHANTOM = "phantom"
UNVERIFIED = "unverified"


@dataclass
class StockLine:
    station: str
    system_shows: int
    actual: int | None
    status: str  # as recorded in the source data: verified / phantom / unverified
    last_sync: str | None = None
    transfer_eta: str | None = None
    detail: str = ""

    @property
    def classification(self) -> str:
        """The line's standing for decision-making.

        A phantom is not stock at all, whatever the screen says.
        An unverified line might be stock, but nobody may plan on it.
        Only a verified line with a matching physical count is confirmed.
        """
        if self.actual is not None and self.system_shows != self.actual:
            return PHANTOM
        if self.status == "verified" and self.actual:
            return CONFIRMED
        if self.status == "phantom":
            return PHANTOM
        return UNVERIFIED

    @property
    def available(self) -> int:
        """Units an agent may actually plan against."""
        if self.classification == CONFIRMED:
            return self.actual or 0
        return 0


@dataclass
class StockPicture:
    part: str
    lines: list[StockLine] = field(default_factory=list)
    required_by: dict = field(default_factory=dict)

    def line_for(self, station: str) -> StockLine:
        for line in self.lines:
            if line.station == station:
                return line
        raise KeyError(f"No stock line for station: {station}")

    def confirmed_sources(self) -> list[StockLine]:
        return [line for line in self.lines if line.classification == CONFIRMED]

    def summary(self) -> str:
        rows = []
        for line in self.lines:
            rows.append(
                f"  {line.station:<12} system shows {line.system_shows}, "
                f"classification: {line.classification}"
            )
        return f"Stock picture for {self.part}:\n" + "\n".join(rows)


def load_stock_picture(path: Path = DATA_FILE) -> StockPicture:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    lines = [
        StockLine(
            station=entry["station"],
            system_shows=entry["systemShows"],
            actual=entry["actual"],
            status=entry["status"],
            last_sync=entry.get("lastSync"),
            transfer_eta=entry.get("transferEta"),
            detail=entry.get("detail", ""),
        )
        for entry in raw["stations"]
    ]
    return StockPicture(
        part=raw["part"], lines=lines, required_by=raw.get("requiredBy", {})
    )
