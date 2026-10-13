from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .storage import load_database


def build_dashboard_payload(database_path: Path) -> dict[str, Any]:
    database = load_database(database_path)
    cards = database.get("cards", {})
    transactions: list[dict[str, Any]] = []

    for card_id, card in cards.items():
        for record in card.get("records", []):
            entry_station = record.get("entry_station") or {}
            exit_station = record.get("exit_station") or {}
            entry_name = _station_display_name(entry_station)
            exit_name = _station_display_name(exit_station)
            route = f"{entry_name} to {exit_name}" if entry_name and exit_name else ""

            transactions.append(
                {
                    "cardId": card_id,
                    "usedAt": record.get("used_at"),
                    "balanceYen": record.get("balance_yen"),
                    "balanceChangeYen": record.get("balance_change_yen"),
                    "expenseYen": record.get("expense_yen") or 0,
                    "chargeYen": record.get("charge_yen") or 0,
                    "terminalName": record.get("terminal_name"),
                    "processName": record.get("process_name"),
                    "entryStation": entry_name,
                    "exitStation": exit_name,
                    "entryStationJapanese": entry_station.get("station_name"),
                    "exitStationJapanese": exit_station.get("station_name"),
                    "route": route,
                    "sequenceNumber": record.get("sequence_number"),
                    "recordId": record.get("record_id"),
                }
            )

    transactions.sort(
        key=lambda item: (item.get("usedAt") or "", item.get("sequenceNumber") or 0),
        reverse=True,
    )

    return {
        "schemaVersion": 1,
        "generatedAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "source": str(database_path),
        "cards": [
            {
                "cardId": card_id,
                "pmm": card.get("pmm"),
                "lastScannedAt": card.get("last_scanned_at"),
                "recordCount": len(card.get("records", [])),
                "scanCount": len(card.get("scans", [])),
                "lastScan": _last_scan(card),
            }
            for card_id, card in sorted(cards.items())
        ],
        "scans": [
            {
                "cardId": card_id,
                "scannedAt": scan.get("scanned_at"),
                "recordsRead": scan.get("records_read", 0),
                "newRecords": scan.get("new_records", 0),
                "duplicateRecords": scan.get("duplicate_records", 0),
                "totalRecords": scan.get("total_records", len(card.get("records", []))),
            }
            for card_id, card in sorted(cards.items())
            for scan in card.get("scans", [])
        ],
        "transactions": transactions,
    }


def build_dashboard_data(database_path: Path, output_path: Path) -> None:
    payload = build_dashboard_payload(database_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    json_text = json.dumps(payload, ensure_ascii=False, indent=2)
    output_path.write_text(f"window.TRANSPORTATION_DASHBOARD_DATA = {json_text};\n", encoding="utf-8")


def _station_display_name(station: dict[str, Any]) -> str:
    return (
        station.get("station_name_romaji")
        or station.get("station_name")
        or _station_code(station)
        or ""
    )


def _station_code(station: dict[str, Any]) -> str:
    try:
        return (
            f"Unknown ({int(station['area_code']):02X}-"
            f"{int(station['line_code']):02X}-"
            f"{int(station['station_code']):02X})"
        )
    except (KeyError, TypeError, ValueError):
        return ""


def _last_scan(card: dict[str, Any]) -> dict[str, Any] | None:
    scans = card.get("scans") or []
    if not scans:
        return None
    scan = scans[-1]
    return {
        "scannedAt": scan.get("scanned_at"),
        "recordsRead": scan.get("records_read", 0),
        "newRecords": scan.get("new_records", 0),
        "duplicateRecords": scan.get("duplicate_records", 0),
        "totalRecords": scan.get("total_records", len(card.get("records", []))),
    }
