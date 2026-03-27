from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ExportJobStatus(str, Enum):
    queued = 'queued'
    running = 'running'
    done = 'done'
    failed = 'failed'


@dataclass(frozen=True, slots=True, kw_only=True)
class ExportJobSummary:
    id: str
    status: ExportJobStatus
    created_at: datetime
    finished_at: datetime | None = None
    records_count: int | None = None
    error_code: str | None = None
