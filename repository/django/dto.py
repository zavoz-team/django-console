from domain.audit import AuditEntry
from domain.user import User
from repository.django.models import AuditEntryRecord, UserRecord


def to_domain(record: UserRecord) -> User:
    return User(id=record.id, email=record.email, name=record.name)


def to_record_data(user: User) -> dict[str, str]:
    return {'email': user.email, 'name': user.name}


def to_domain_audit_entry(record: AuditEntryRecord) -> AuditEntry:
    payload = record.payload_json if isinstance(record.payload_json, dict) else {}
    return AuditEntry(
        id=record.id,
        actor_email=record.actor_email,
        action=record.action,
        target_type=record.target_type,
        target_id=record.target_id,
        status=record.status,
        payload_json=payload,
        trace_id=record.trace_id,
        created_at=record.created_at,
    )


def to_audit_record_data(entry: AuditEntry) -> dict[str, object]:
    return {
        'actor_email': entry.actor_email,
        'action': entry.action,
        'target_type': entry.target_type,
        'target_id': entry.target_id,
        'status': entry.status,
        'payload_json': dict(entry.payload_json),
        'trace_id': entry.trace_id,
    }
