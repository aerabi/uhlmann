import json
import re
from datetime import datetime
from typing import List, Optional

from .ftp import load_rows_from_ftp
from ..models import SensorRecord, FtpCredential


def migrate_ftp_file(filename: str, ftp_name: str, year: Optional[int] = None) -> list:
    rows, ftp = load_rows_from_ftp(filename, ftp_name)
    _year_: int = year or datetime.today().year
    records = _create_data_from_rows_(rows, filename, ftp, year=_year_)
    return SensorRecord.objects.bulk_create(records)


def _create_data_from_rows_(rows: List[List[str]], filename: str, ftp: FtpCredential, year=2020) -> List[SensorRecord]:
    data: List[SensorRecord] = []
    keys: List[str] = []
    for row in rows:
        # key definitions
        if row[0][0] == '/':
            for i in range(1, len(row) - 1):
                if i % 2 == 0:
                    continue
                key = _normalize_key_(row[i])
                keys.append(key)
            continue

        # empty rows
        if len(row) == 0:
            continue

        # data rows
        record_data = {}
        row_length = min(len(keys) + 1, len(row))
        for i in range(1, row_length):
            value = _parse_value_(row[i])
            record_data[keys[i - 1]] = value
        time = _make_datetime_(filename=filename, year=year, time=row[0])
        record = SensorRecord(source=ftp, time=time, data=json.dumps(record_data))
        data.append(record)

    return data


def _normalize_key_(key: str) -> str:
    return re.sub(r'[\W_]+', '', key)


def _parse_value_(value: str) -> float:
    if len(value) == 0:
        return 0
    try:
        return float(value)
    except:
        return 0


def _make_datetime_(filename: str, year: int, time: str) -> datetime:
    month = int(filename[:2])
    day = int(filename[2:])
    hour = int(time[:2])
    minutes = int(time[2:])
    return datetime(year, month, day, hour, minutes)
