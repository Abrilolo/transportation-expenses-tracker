from __future__ import annotations


class JapaneseRomanizer:
    """Offline Japanese-to-Romaji conversion backed by pykakasi."""

    def __init__(self) -> None:
        try:
            import pykakasi
        except ImportError:
            self._converter = None
        else:
            self._converter = pykakasi.kakasi()

    @property
    def available(self) -> bool:
        return self._converter is not None

    def romanize(self, text: str | None) -> str | None:
        if not text or self._converter is None:
            return None

        converted = self._converter.convert(text)
        value = "".join(item.get("passport") or item["orig"] for item in converted).strip()
        if not value:
            return None
        return value[0].upper() + value[1:]
