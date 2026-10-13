from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from transportation.romanizer import JapaneseRomanizer


class FakeKakasi:
    def convert(self, text: str) -> list[dict[str, str]]:
        self.last_text = text
        return [
            {"orig": "新宿", "passport": "shinjuku"},
            {"orig": "御苑前", "passport": "gyoemmae"},
        ]


class RomanizerTests(unittest.TestCase):
    def test_joins_passport_romaji_and_capitalizes_name(self) -> None:
        romanizer = JapaneseRomanizer.__new__(JapaneseRomanizer)
        romanizer._converter = FakeKakasi()

        result = romanizer.romanize("新宿御苑前")

        self.assertEqual(result, "Shinjukugyoemmae")

    def test_returns_none_when_dependency_is_unavailable(self) -> None:
        romanizer = JapaneseRomanizer.__new__(JapaneseRomanizer)
        romanizer._converter = None

        self.assertIsNone(romanizer.romanize("新宿"))


if __name__ == "__main__":
    unittest.main()
