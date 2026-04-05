from typing import Any, Optional

from domain.query import TextQuery
from repository.core_api.errors import CoreApiNotFoundError


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
        self,
        limit: int,
        offset: int,
        query: TextQuery | None = None,
        extra_headers: Optional[dict[str, str]] = None,
    ) -> list[dict[str, Any]]:
        if self.should_throw_not_found:
            raise CoreApiNotFoundError("Profiles not found")

        filtered_profiles = self.profiles
        if query:
            filtered_profiles = [
                p
                for p in self.profiles
                if query.value.lower() in p.get("name", "").lower()
                or query.value.lower() in p.get("email", "").lower()
                or any(
                    query.value.lower() in str(value).lower()
                    for value in p.get("custom_fields", {}).values()
                )
            ]

        return filtered_profiles[offset : offset + limit]

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
    ) -> list[dict[str, Any]]:
        if self.should_throw_not_found:
            raise CoreApiNotFoundError("Segments not found")
        return self.segments[offset : offset + limit]

    def get_segment_members(
        self,
        segment_id: str,
        limit: int,
        offset: int,
        extra_headers: Optional[dict[str, str]] = None,
    ) -> list[dict[str, Any]]:
        if self.should_throw_not_found:
            raise CoreApiNotFoundError(f"Segment {segment_id} not found")
        members = [
            profile
            for profile in self.profiles
            if profile.get("custom_fields", {}).get("segment_id") == segment_id
        ]
        return members[offset : offset + limit]

    def trigger_export(
        self,
        segment_id: str,
        destination: str,
        extra_headers: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        if self.should_throw_not_found:
            raise CoreApiNotFoundError(f"Segment {segment_id} not found")
        job = {
            "id": f"job_{len(self.jobs) + 1}",
            "segment_id": segment_id,
            "status": "queued",
            "created_at": "2026-01-01T00:00:00",
            "updated_at": "2026-01-01T00:00:00",
            "completed_at": None,
        }
        self.jobs.append(job)
        return job

    def get_jobs(
        self, limit: int, offset: int, extra_headers: Optional[dict[str, str]] = None
    ) -> list[dict[str, Any]]:
        if self.should_throw_not_found:
            raise CoreApiNotFoundError("Jobs not found")
        return self.jobs[offset : offset + limit]

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
