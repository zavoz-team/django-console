from domain.profile import (
    ProfileCounters,
    ProfileDetails,
    ProfileIdentifiers,
    ProfileRecentEvent,
    ProfileSummary,
    ProfileTimestamps,
)
from domain.query import Pagination, TextQuery
from repository.core_api.client import CoreApiClient
from repository.core_api.errors import CoreApiNotFoundError
from usecase.interface import ProfileGateway


class CoreApiProfileGateway(ProfileGateway):
    def __init__(self, client: CoreApiClient) -> None:
        self._client = client

    def list(
        self, pagination: Pagination, query: TextQuery | None = None
    ) -> list[ProfileSummary]:
        response_data = self._client.get_profiles(
            limit=pagination.limit, offset=pagination.offset
        )

        profiles = []
        for item in response_data.get("items", []):
            profiles.append(
                ProfileSummary(
                    customer_id=item["customer_id"],
                    email=item.get("email"),
                    phone=item.get("phone"),
                    external_user_id=item.get("external_user_id"),
                    segments=item.get("segments", []),
                    total_orders=item.get("total_orders", 0),
                    total_revenue=float(item.get("total_revenue", 0.0)),
                    last_seen_at=item.get("last_seen_at"),
                )
            )

        return profiles

    def get(self, profile_id: str) -> ProfileDetails | None:
        try:
            response_data = self._client.get_profile(profile_id)
            idents = response_data.get("identifiers", {})
            counters = response_data.get("counters", {})
            timestamps = response_data.get("timestamps", {})
            return ProfileDetails(
                customer_id=response_data["customer_id"],
                identifiers=ProfileIdentifiers(
                    emails=idents.get("emails", []),
                    phones=idents.get("phones", []),
                    external_user_ids=idents.get("external_user_ids", []),
                ),
                attributes=response_data.get("attributes", {}),
                counters=ProfileCounters(
                    events_count=counters.get("events_count", 0),
                    page_views_count=counters.get("page_views_count", 0),
                    cart_adds_count=counters.get("cart_adds_count", 0),
                    orders_count=counters.get("orders_count", 0),
                ),
                total_revenue=response_data.get("total_revenue", 0.0),
                currency=response_data.get("currency"),
                timestamps=ProfileTimestamps(
                    first_seen_at=timestamps.get("first_seen_at"),
                    last_seen_at=timestamps.get("last_seen_at"),
                    created_at=timestamps.get("created_at"),
                    updated_at=timestamps.get("updated_at"),
                    last_purchase_at=timestamps.get("last_purchase_at"),
                ),
                segments=response_data.get("segments", []),
                recent_events=[
                    ProfileRecentEvent(
                        event_id=e["event_id"],
                        event_type=e["event_type"],
                        occurred_at=e.get("occurred_at"),
                    )
                    for e in response_data.get("recent_events", [])
                ],
            )
        except CoreApiNotFoundError:
            return None
