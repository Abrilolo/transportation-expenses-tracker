from __future__ import annotations

import sys
import unittest
from datetime import date
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from transportation.station_resolver import StationResolver
from transportation.suica_parser import calculate_balance_changes, parse_suica_history_record


class SuicaParserTests(unittest.TestCase):
    def test_parses_date_balance_codes_and_stations(self) -> None:
        encoded_date = ((2026 - 2000) << 9) | (9 << 5) | 24
        raw = bytes(
            [0x16, 0x01, 0x00, 0x00]
            + list(encoded_date.to_bytes(2, "big"))
            + [0x10, 0x20, 0x30, 0x40]
            + list((1234).to_bytes(2, "little"))
            + [0x01, 0x02, 0x03, 0x50]
        )

        record = parse_suica_history_record(0, raw, StationResolver())

        self.assertEqual(record.used_at, date(2026, 9, 24))
        self.assertEqual(record.balance_yen, 1234)
        self.assertEqual(record.terminal_name, "Automatic ticket gate")
        self.assertEqual(record.process_name, "Fare payment")
        self.assertEqual(record.entry_station.area_code, 1)
        self.assertEqual(record.exit_station.area_code, 1)
        self.assertEqual(record.sequence_number, 0x010203)

    def test_calculates_expense_from_consecutive_balances(self) -> None:
        resolver = StationResolver()
        current = bytearray(16)
        previous = bytearray(16)
        current[10:12] = (800).to_bytes(2, "little")
        previous[10:12] = (1000).to_bytes(2, "little")
        records = [
            parse_suica_history_record(0, bytes(current), resolver),
            parse_suica_history_record(1, bytes(previous), resolver),
        ]

        calculate_balance_changes(records)

        self.assertEqual(records[0].balance_change_yen, -200)
        self.assertEqual(records[0].expense_yen, 200)
        self.assertEqual(records[0].charge_yen, 0)
        self.assertIsNone(records[1].balance_change_yen)


if __name__ == "__main__":
    unittest.main()
