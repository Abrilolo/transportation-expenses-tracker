from __future__ import annotations

from collections import Counter
from typing import Any

from .suica_record import SuicaHistoryRecord


def build_summary(records: list[SuicaHistoryRecord]) -> dict[str, Any]:
    dated_records = [record for record in records if record.used_at]
    expenses = [record.expense_yen or 0 for record in records]
    station_visits = Counter(
        station.display_name
        for record in records
        for station in (record.entry_station, record.exit_station)
        if station and station.station_name
    )

    return {
        "transaction_count": len(records),
        "total_expense_yen": sum(expenses),
        "latest_balance_yen": records[0].balance_yen if records else None,
        "first_date": min((record.used_at for record in dated_records), default=None),
        "last_date": max((record.used_at for record in dated_records), default=None),
        "most_visited_stations": station_visits.most_common(10),
    }
