from __future__ import annotations

from datetime import datetime
from pathlib import Path

import nfc
from nfc.tag import tt3

from .station_resolver import StationResolver
from .suica_parser import calculate_balance_changes, parse_suica_history_record
from .suica_record import CardSnapshot, SuicaHistoryRecord


DEFAULT_READER_PATH = "usb:054c:02e1"
SUICA_HISTORY_SERVICE_CODE = 0x090F
MAX_HISTORY_RECORDS = 20


class NfcReaderError(RuntimeError):
    pass


def build_service_code(service_code: int) -> tt3.ServiceCode:
    return tt3.ServiceCode(service_code >> 6, service_code & 0x3F)


def read_history(
    tag: tt3.Type3Tag,
    stations: StationResolver,
    max_records: int = MAX_HISTORY_RECORDS,
) -> list[SuicaHistoryRecord]:
    service_code = build_service_code(SUICA_HISTORY_SERVICE_CODE)
    records: list[SuicaHistoryRecord] = []

    for block_number in range(max_records):
        block_code = tt3.BlockCode(block_number, service=0)
        try:
            raw = bytes(tag.read_without_encryption([service_code], [block_code]))
        except tt3.Type3TagCommandError:
            break

        if not raw or raw == b"\x00" * 16:
            continue
        records.append(parse_suica_history_record(block_number, raw, stations))

    calculate_balance_changes(records)
    return records


def scan_card(
    reader_path: str = DEFAULT_READER_PATH,
    station_csv: Path | None = None,
) -> CardSnapshot:
    stations = StationResolver(station_csv, require_romanization=True)
    snapshot: CardSnapshot | None = None

    def on_connect(tag: object) -> bool:
        nonlocal snapshot
        if not isinstance(tag, tt3.Type3Tag):
            raise NfcReaderError(f"Unsupported NFC tag: {tag}")

        snapshot = CardSnapshot(
            card_id=tag.idm.hex(),
            pmm=tag.pmm.hex(),
            scanned_at=datetime.now().astimezone(),
            records=read_history(tag, stations),
        )
        return True

    try:
        with nfc.ContactlessFrontend(reader_path) as frontend:
            frontend.connect(rdwr={"on-connect": on_connect})
    except OSError as exc:
        raise NfcReaderError(
            f"Could not open NFC reader '{reader_path}'. Check the USB connection and driver."
        ) from exc

    if snapshot is None:
        raise NfcReaderError("The reader closed before a compatible card was detected.")
    return snapshot
