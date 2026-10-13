from __future__ import annotations

from datetime import date

from .code_maps import console_name, is_rail_process, process_name
from .station_resolver import StationResolver
from .suica_record import SuicaHistoryRecord


RECORD_SIZE = 16


def parse_suica_history_record(
    index: int,
    raw: bytes,
    stations: StationResolver,
) -> SuicaHistoryRecord:
    if len(raw) != RECORD_SIZE:
        raise ValueError(f"A history record must contain 16 bytes, received {len(raw)}")

    date_value = int.from_bytes(raw[4:6], byteorder="big")
    year = 2000 + ((date_value >> 9) & 0x7F)
    month = (date_value >> 5) & 0x0F
    day = date_value & 0x1F

    try:
        used_at = date(year, month, day)
    except ValueError:
        used_at = None

    entry_area = (raw[15] >> 6) & 0x03
    exit_area = (raw[15] >> 4) & 0x03

    process_code = raw[1]
    entry_station = None
    exit_station = None
    if is_rail_process(process_code):
        entry_station = stations.resolve(entry_area, raw[6], raw[7])
        exit_station = stations.resolve(exit_area, raw[8], raw[9])

    return SuicaHistoryRecord(
        index=index,
        used_at=used_at,
        balance_yen=int.from_bytes(raw[10:12], byteorder="little"),
        terminal_code=raw[0],
        terminal_name=console_name(raw[0]),
        process_code=process_code,
        process_name=process_name(process_code),
        entry_station=entry_station,
        exit_station=exit_station,
        sequence_number=int.from_bytes(raw[12:15], byteorder="big"),
        raw_hex=raw.hex(" "),
    )


def calculate_balance_changes(records: list[SuicaHistoryRecord]) -> None:
    """Calculate each operation from consecutive post-transaction balances."""
    for current, previous in zip(records, records[1:]):
        change = current.balance_yen - previous.balance_yen
        current.balance_change_yen = change
        current.expense_yen = -change if change < 0 else 0
        current.charge_yen = change if change > 0 else 0
