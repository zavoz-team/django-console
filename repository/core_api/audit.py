from repository.core_api.client import CoreApiClient
from usecase.interface import AuditGateway


class CoreApiAuditGateway(AuditGateway):
    def __init__(self, client: CoreApiClient) -> None:
        self._client = client

    def log_action(
        self, operator_id: str, action: str, target_id: str | None = None
    ) -> None:
        payload = {
            "operator_id": operator_id,
            "action": action,
            "target_id": target_id,
        }
        self._client.log_audit_action(payload)
