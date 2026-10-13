from __future__ import annotations

import csv
from pathlib import Path

from .romanizer import JapaneseRomanizer
from .suica_record import Station


class StationResolver:
    """Resolve Cybernet station codes from furugori/ekicode's CSV format."""

    FIELD_NAMES = (
        "area",
        "line",
        "station",
        "company_name",
        "line_name",
        "station_name",
    )

    def __init__(
        self,
        csv_path: Path | None = None,
        *,
        require_romanization: bool = False,
    ) -> None:
        self._stations: dict[tuple[int, int, int], Station] = {}
        self._romanizer = JapaneseRomanizer()
        if csv_path and csv_path.is_file() and csv_path.stat().st_size:
            if require_romanization and not self._romanizer.available:
                raise RuntimeError(
                    "Station romanization requires pykakasi. Install requirements.txt."
                )
            self._load(csv_path)

    @property
    def station_count(self) -> int:
        return len(self._stations)

    def resolve(self, area_code: int, line_code: int, station_code: int) -> Station:
        key = (area_code, line_code, station_code)
        return self._stations.get(
            key,
            Station(
                area_code=area_code,
                line_code=line_code,
                station_code=station_code,
            ),
        )

    def _load(self, csv_path: Path) -> None:
        last_error: UnicodeDecodeError | None = None
        for encoding in ("utf-8-sig", "cp932"):
            try:
                with csv_path.open("r", encoding=encoding, newline="") as csv_file:
                    reader = csv.DictReader(csv_file, fieldnames=self.FIELD_NAMES)
                    stations = self._parse_rows(reader)
                self._stations = stations
                return
            except UnicodeDecodeError as exc:
                last_error = exc

        raise ValueError(f"Could not decode station table: {csv_path}") from last_error

    def _parse_rows(self, rows: csv.DictReader) -> dict[tuple[int, int, int], Station]:
        stations: dict[tuple[int, int, int], Station] = {}
        for line_number, row in enumerate(rows, start=1):
            area_value = row["area"].strip()
            line_value = row["line"].strip()
            station_value = row["station"].strip()
            if line_number == 1 and area_value.lower() in {"area", "地域コード"}:
                continue

            try:
                area = int(area_value, 16)
                line = int(line_value, 16)
                station = int(station_value, 16)
            except (AttributeError, TypeError, ValueError) as exc:
                raise ValueError(f"Invalid station code on CSV line {line_number}") from exc

            stations[(area, line, station)] = Station(
                area_code=area,
                line_code=line,
                station_code=station,
                company_name=row["company_name"].strip() or None,
                line_name=row["line_name"].strip() or None,
                station_name=row["station_name"].strip() or None,
                station_name_romaji=self._romanizer.romanize(row["station_name"].strip()),
            )
        return stations
