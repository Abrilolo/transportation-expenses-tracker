from __future__ import annotations

import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from transportation.station_resolver import StationResolver
from transportation.dashboard_builder import build_dashboard_payload
from transportation.storage import load_database, save_snapshot
from transportation.suica_parser import parse_suica_history_record
from transportation.suica_record import CardSnapshot


def make_record(index: int, balance: int, sequence: int):
    encoded_date = ((2026 - 2000) << 9) | (9 << 5) | 24
    raw = bytearray(16)
    raw[0] = 0x16
    raw[1] = 0x01
    raw[4:6] = encoded_date.to_bytes(2, "big")
    raw[10:12] = balance.to_bytes(2, "little")
    raw[12:15] = sequence.to_bytes(3, "big")
    return parse_suica_history_record(index, bytes(raw), StationResolver())


class StorageAndStationTests(unittest.TestCase):
    def test_station_resolver_reads_headerless_hex_csv(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            csv_path = Path(temporary_directory) / "ekicode.csv"
            csv_path.write_text("0,10,20,JR East,Yamanote Line,Tokyo\n", encoding="utf-8")

            resolver = StationResolver(csv_path)
            station = resolver.resolve(0x00, 0x10, 0x20)

            self.assertEqual(resolver.station_count, 1)
            self.assertEqual(station.station_name, "Tokyo")
            self.assertEqual(station.line_name, "Yamanote Line")

    def test_station_resolver_accepts_current_japanese_header(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            csv_path = Path(temporary_directory) / "ekicode.csv"
            csv_path.write_text(
                "地域コード,路線コード,駅順コード,会社名,線区名,駅名\n"
                "0,e5,32,東京地下鉄,4号線丸ノ内,新宿御苑前\n",
                encoding="utf-8",
            )

            resolver = StationResolver(csv_path)
            station = resolver.resolve(0x00, 0xE5, 0x32)

            self.assertEqual(resolver.station_count, 1)
            self.assertEqual(station.station_name, "新宿御苑前")

    def test_storage_deduplicates_and_recalculates_merged_history(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "transactions.json"
            scanned_at = datetime.now().astimezone()
            older = make_record(1, 1000, 1)
            current = make_record(0, 800, 2)
            snapshot = CardSnapshot("card", "pmm", scanned_at, [current, older])

            first_result = save_snapshot(path, snapshot)
            second_result = save_snapshot(path, snapshot)
            database = load_database(path)

            self.assertEqual(len(first_result.records), 2)
            self.assertEqual(len(second_result.records), 2)
            self.assertEqual(first_result.records[0].expense_yen, 200)
            self.assertEqual(first_result.stats.records_read, 2)
            self.assertEqual(first_result.stats.new_records, 2)
            self.assertEqual(first_result.stats.duplicate_records, 0)
            self.assertEqual(first_result.stats.total_records, 2)
            self.assertEqual(second_result.stats.new_records, 0)
            self.assertEqual(second_result.stats.duplicate_records, 2)
            self.assertEqual(second_result.stats.total_records, 2)
            self.assertEqual(len(database["cards"]["card"]["records"]), 2)
            self.assertEqual(len(database["cards"]["card"]["scans"]), 2)
            self.assertEqual(database["cards"]["card"]["scans"][0]["new_records"], 2)
            self.assertEqual(database["cards"]["card"]["scans"][1]["duplicate_records"], 2)

            dashboard_payload = build_dashboard_payload(path)
            self.assertEqual(dashboard_payload["cards"][0]["scanCount"], 2)
            self.assertEqual(dashboard_payload["cards"][0]["lastScan"]["duplicateRecords"], 2)
            self.assertEqual(len(dashboard_payload["scans"]), 2)


if __name__ == "__main__":
    unittest.main()
