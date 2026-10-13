from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from .suica_parser import calculate_balance_changes
from .suica_record import CardSnapshot, SuicaHistoryRecord


SCHEMA_VERSION = 1


@dataclass(frozen=True)
class SaveStats:
    card_id: str
    records_read: int
    new_records: int
    duplicate_records: int
    total_records: int
    scanned_at: str


@dataclass(frozen=True)
class SaveResult:
    records: list[SuicaHistoryRecord]
    stats: SaveStats


def load_database(path: Path) -> dict[str, Any]:
    if not path.is_file() or path.stat().st_size == 0:
        return {"schema_version": SCHEMA_VERSION, "cards": {}}

    try:
        with path.open("r", encoding="utf-8") as json_file:
            data = json.load(json_file)
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(f"Could not read transaction database: {path}") from exc

    if data.get("schema_version") != SCHEMA_VERSION or not isinstance(data.get("cards"), dict):
        raise ValueError(f"Unsupported transaction database format: {path}")
    return data


def save_snapshot(path: Path, snapshot: CardSnapshot) -> SaveResult:
    database = load_database(path)
    cards = database["cards"]
    card = cards.setdefault(
        snapshot.card_id,
        {"pmm": snapshot.pmm, "last_scanned_at": None, "records": [], "scans": []},
    )
    card.setdefault("scans", [])

    existing = {record["record_id"]: record for record in card["records"]}
    existing_record_ids = set(existing)
    for record in snapshot.records:
        existing[record.record_id] = record.to_dict()
    scanned_record_ids = {record.record_id for record in snapshot.records}
    new_record_ids = scanned_record_ids - existing_record_ids

    sorted_records = sorted(
        existing.values(),
        key=lambda item: (item.get("used_at") or "", item.get("sequence_number", 0)),
        reverse=True,
    )
    merged_records = [SuicaHistoryRecord.from_dict(record) for record in sorted_records]
    for record in merged_records:
        record.balance_change_yen = None
        record.expense_yen = None
        record.charge_yen = None
    calculate_balance_changes(merged_records)

    card["pmm"] = snapshot.pmm
    card["last_scanned_at"] = snapshot.scanned_at.isoformat(timespec="seconds")
    card["records"] = [record.to_dict() for record in merged_records]
    database["updated_at"] = datetime.now().astimezone().isoformat(timespec="seconds")

    stats = SaveStats(
        card_id=snapshot.card_id,
        records_read=len(snapshot.records),
        new_records=len(new_record_ids),
        duplicate_records=len(scanned_record_ids) - len(new_record_ids),
        total_records=len(merged_records),
        scanned_at=card["last_scanned_at"],
    )
    card["scans"].append(
        {
            "scanned_at": stats.scanned_at,
            "records_read": stats.records_read,
            "new_records": stats.new_records,
            "duplicate_records": stats.duplicate_records,
            "total_records": stats.total_records,
        }
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    with temporary_path.open("w", encoding="utf-8", newline="\n") as json_file:
        json.dump(database, json_file, ensure_ascii=False, indent=2)
        json_file.write("\n")
    temporary_path.replace(path)

    return SaveResult(records=merged_records, stats=stats)
