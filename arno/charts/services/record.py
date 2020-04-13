import json
from datetime import datetime

from ..models import SensorRecord


def get_by_time(starting: datetime, to: datetime) -> list:
    return [record_to_dto(rec) for rec in SensorRecord.objects.filter(time__gte=starting, time__lt=to)]


def record_to_dto(record: SensorRecord) -> dict:
    data = json.loads(record.data)
    data['time'] = record.time.isoformat()
    return data
