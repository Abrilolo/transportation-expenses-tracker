from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime
from typing import Any


@dataclass(frozen=True)
class Station:
    area_code: int
    line_code: int
    station_code: int
    company_name: str | None = None
    line_name: str | None = None
    station_name: str | None = None
    station_name_romaji: str | None = None

    @property
    def display_name(self) -> str:
        return self.station_name_romaji or self.station_name or (
            f"Unknown ({self.area_code:02X}-{self.line_code:02X}-{self.station_code:02X})"
        )


@dataclass
class SuicaHistoryRecord:
    index: int
    used_at: date | None
    balance_yen: int
    terminal_code: int
    terminal_name: str
    process_code: int
    process_name: str
    entry_station: Station | None
    exit_station: Station | None
    sequence_number: int
    raw_hex: str
    balance_change_yen: int | None = None
    expense_yen: int | None = None
    charge_yen: int | None = None

    @property
    def record_id(self) -> str:
        return f"{self.sequence_number:06x}:{self.raw_hex.replace(' ', '')}"

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["used_at"] = self.used_at.isoformat() if self.used_at else None
        result["record_id"] = self.record_id
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SuicaHistoryRecord:
        entry_data = data.get("entry_station")
        exit_data = data.get("exit_station")
        return cls(
            index=int(data["index"]),
            used_at=date.fromisoformat(data["used_at"]) if data.get("used_at") else None,
            balance_yen=int(data["balance_yen"]),
            terminal_code=int(data["terminal_code"]),
            terminal_name=str(data["terminal_name"]),
            process_code=int(data["process_code"]),
            process_name=str(data["process_name"]),
            entry_station=Station(**entry_data) if entry_data else None,
            exit_station=Station(**exit_data) if exit_data else None,
            sequence_number=int(data["sequence_number"]),
            raw_hex=str(data["raw_hex"]),
            balance_change_yen=data.get("balance_change_yen"),
            expense_yen=data.get("expense_yen"),
            charge_yen=data.get("charge_yen"),
        )


@dataclass
class CardSnapshot:
    card_id: str
    pmm: str
    scanned_at: datetime
    records: list[SuicaHistoryRecord]

    def to_dict(self) -> dict[str, Any]:
        return {
            "card_id": self.card_id,
            "pmm": self.pmm,
            "scanned_at": self.scanned_at.astimezone().isoformat(timespec="seconds"),
            "records": [record.to_dict() for record in self.records],
        }
