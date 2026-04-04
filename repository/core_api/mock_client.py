from typing import Any, Optional

from repository.core_api.errors import CoreApiNotFoundError
from usecase.dto import SystemStatusDTO


class MockCoreApiClient:
    def __init__(self) -> None:
        self.profiles: list[dict[str, Any]] = []
        self.segments: list[dict[str, Any]] = []
        self.jobs: list[dict[str, Any]] = []
        self.audit_logs: list[dict[str, Any]] = []
        self.should_throw_not_found: bool = False

    def shutdown(self) -> None:
        pass

    def get_profiles(
        self, limit: int, offset: int, extra_headers: Optional[dict[str, str]] = None
    ) -> dict[str, Any]:
        if self.should_throw_not_found:
            raise CoreApiNotFoundError("Profiles not found")
        return {"profiles": self.profiles[offset : offset + limit]}

    def get_profile(
        self, customer_id: str, extra_headers: Optional[dict[str, str]] = None
    ) -> dict[str, Any]:
        if self.should_throw_not_found:
            raise CoreApiNotFoundError(f"Profile {customer_id} not found")
        for profile in self.profiles:
            if profile.get("id") == customer_id:
                return profile
        raise CoreApiNotFoundError(f"Profile {customer_id} not found")

    def get_segments(
        self, limit: int, offset: int, extra_headers: Optional[dict[str, str]] = None
    ) -> dict[str, Any]:
        if self.should_throw_not_found:
            raise CoreApiNotFoundError("Segments not found")
        return {"segments": self.segments[offset : offset + limit]}

    def get_segment_members(
        self,
        segment_id: str,
        limit: int,
        offset: int,
        extra_headers: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        if self.should_throw_not_found:
            raise CoreApiNotFoundError(f"Segment {segment_id} not found")
        return {"members": [{"profile_id": p["id"]} for p in self.profiles]}

    def trigger_export(
        self, segment_id: str, extra_headers: Optional[dict[str, str]] = None
    ) -> dict[str, Any]:
        if self.should_throw_not_found:
            raise CoreApiNotFoundError(f"Segment {segment_id} not found")
        job = {"id": f"job_{len(self.jobs) + 1}", "segment_id": segment_id, "status": "PENDING"}
        self.jobs.append(job)
        return job

    def get_jobs(
        self, limit: int, offset: int, extra_headers: Optional[dict[str, str]] = None
    ) -> dict[str, Any]:
        if self.should_throw_not_found:
            raise CoreApiNotFoundError("Jobs not found")
        return {"jobs": self.jobs[offset : offset + limit]}

    def get_job(
        self, job_id: str, extra_headers: Optional[dict[str, str]] = None
    ) -> dict[str, Any]:
        if self.should_throw_not_found:
            raise CoreApiNotFoundError(f"Job {job_id} not found")
        for job in self.jobs:
            if job.get("id") == job_id:
                return job
        raise CoreApiNotFoundError(f"Job {job_id} not found")

    def get_system_status(
        self, extra_headers: Optional[dict[str, str]] = None
    ) -> dict[str, Any]:
        return {"status": "ok", "app": "mock-core-api", "env": "test"}

    def log_audit_action(
        self, payload: dict[str, Any], extra_headers: Optional[dict[str, str]] = None
    ) -> None:
        self.audit_logs.append(payload)


class MockCoreApiSystemStatusGateway:
    def __init__(self, client: MockCoreApiClient) -> None:
        self._client = client

    def get_status(self) -> SystemStatusDTO:
        response_data = self._client.get_system_status()
        return SystemStatusDTO(**response_data)
