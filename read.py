from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from transportation.excel_exporter import export_to_excel  # noqa: E402
from transportation.dashboard_builder import build_dashboard_data  # noqa: E402
from transportation.storage import save_snapshot  # noqa: E402
from transportation.suica_record import SuicaHistoryRecord  # noqa: E402


DEFAULT_READER_PATH = "usb:054c:02e1"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read and export Suica/PASMO history.")
    parser.add_argument("--reader", default=DEFAULT_READER_PATH, help="nfcpy reader path")
    parser.add_argument("--no-excel", action="store_true", help="Skip Excel export")
    return parser.parse_args()


def print_record(record: SuicaHistoryRecord) -> None:
    used_at = record.used_at.isoformat() if record.used_at else "unknown"
    route = ""
    if record.entry_station and record.exit_station:
        route = f" | {record.entry_station.display_name} -> {record.exit_station.display_name}"
    change = "unknown" if record.balance_change_yen is None else f"{record.balance_change_yen:+d} yen"
    print(
        f"{record.index:02d} | {used_at} | {record.process_name} | "
        f"change={change} | balance={record.balance_yen} yen{route}"
    )


def main() -> int:
    args = parse_arguments()
    station_csv = PROJECT_ROOT / "data" / "ekicode.csv"
    json_path = PROJECT_ROOT / "output" / "transactions.json"
    excel_path = PROJECT_ROOT / "output" / "transactions.xlsx"
    dashboard_data_path = PROJECT_ROOT / "dashboard" / "data.js"

    print(f"Opening NFC reader: {args.reader}")
    print("Place your Suica/PASMO card on the reader...")

    try:
        from transportation.nfc_reader import NfcReaderError, scan_card
    except ImportError as exc:
        print(f"Error: missing dependency '{exc.name}'. Install requirements.txt.", file=sys.stderr)
        return 1

    try:
        snapshot = scan_card(args.reader, station_csv)
    except (NfcReaderError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"\nCard detected: {snapshot.card_id}")
    print(f"Records read: {len(snapshot.records)}\n")
    for record in snapshot.records:
        print_record(record)

    save_result = save_snapshot(json_path, snapshot)
    all_records = save_result.records
    stats = save_result.stats
    print(f"\nJSON updated: {json_path}")
    print(
        "Database merge: "
        f"{stats.new_records} new, "
        f"{stats.duplicate_records} duplicates, "
        f"{stats.total_records} total for this card"
    )

    if not args.no_excel:
        try:
            export_to_excel(excel_path, all_records)
        except RuntimeError as exc:
            print(f"Excel export skipped: {exc}", file=sys.stderr)
        else:
            print(f"Excel updated: {excel_path}")

    build_dashboard_data(json_path, dashboard_data_path)
    print(f"Dashboard data updated: {dashboard_data_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
