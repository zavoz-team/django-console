from repository.core_api.client import CoreApiClient
from usecase.interface import ExportGateway


class CoreApiExportGateway(ExportGateway):
    def __init__(self, client: CoreApiClient) -> None:
        self._client = client

    def trigger_export(self, segment_id: str) -> str:
        response_data = self._client.trigger_export(segment_id)
        
        job_id = response_data.get("job_id")
        if not isinstance(job_id, str):
            raise TypeError("Expected 'job_id' to be a string")
            
        return job_id
