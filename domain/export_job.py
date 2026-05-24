from dataclasses import dataclass
from enum import Enum


class ExportJobStatus(str, Enum):
    queued = 'queued'
    running = 'running'
    done = 'done'
    failed = 'failed'


@dataclass(frozen=True, slots=True, kw_only=True)
class ExportJobSummary:
    job_id: str
    segment_id: str
    status: ExportJobStatus
    requested_at: str
    completed_at: str | None = None
    members_count: int | None = None
    error_reason: str | None = None
    requested_by: str | None = None
