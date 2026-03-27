from domain.audit import AuditEntry
from domain.query import Pagination
from repository.django.dto import to_audit_record_data, to_domain_audit_entry
from repository.django.models import AuditEntryRecord
from usecase.interface import AuditLogRepository, Tracer


class DjangoAuditLogRepository(AuditLogRepository):
    def __init__(self, tracer: Tracer) -> None:
        self._tracer = tracer

    def save(self, entry: AuditEntry) -> AuditEntry:
        with self._tracer.start_span(
            'repository.audit_log.save',
            attrs={'audit.action': entry.action, 'audit.status': entry.status},
        ):
            record = AuditEntryRecord.objects.create(**to_audit_record_data(entry))
            return to_domain_audit_entry(record)

    def list_recent(self, pagination: Pagination) -> list[AuditEntry]:
        with self._tracer.start_span(
            'repository.audit_log.list_recent',
            attrs={
                'pagination.limit': pagination.limit,
                'pagination.offset': pagination.offset,
            },
        ):
            records = AuditEntryRecord.objects.order_by('-created_at')[
                pagination.offset : pagination.offset + pagination.limit
            ]
            return [to_domain_audit_entry(record) for record in records]

    def list_by_target(
        self,
        target_type: str,
        target_id: str,
        pagination: Pagination,
    ) -> list[AuditEntry]:
        with self._tracer.start_span(
            'repository.audit_log.list_by_target',
            attrs={
                'audit.target_type': target_type,
                'audit.target_id': target_id,
                'pagination.limit': pagination.limit,
                'pagination.offset': pagination.offset,
            },
        ):
            records = AuditEntryRecord.objects.filter(
                target_type=target_type,
                target_id=target_id,
            ).order_by('-created_at')[pagination.offset : pagination.offset + pagination.limit]
            return [to_domain_audit_entry(record) for record in records]
