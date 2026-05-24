from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True, kw_only=True)
class ProfileSummary:
    customer_id: str
    email: str | None = None
    phone: str | None = None
    external_user_id: str | None = None
    segments: list[str] = field(default_factory=list)
    total_orders: int = 0
    total_revenue: float = 0.0
    last_seen_at: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class ProfileIdentifiers:
    emails: list[str]
    phones: list[str]
    external_user_ids: list[str]


@dataclass(frozen=True, slots=True, kw_only=True)
class ProfileCounters:
    events_count: int
    page_views_count: int
    cart_adds_count: int
    orders_count: int


@dataclass(frozen=True, slots=True, kw_only=True)
class ProfileTimestamps:
    first_seen_at: str | None
    last_seen_at: str | None
    created_at: str | None
    updated_at: str | None
    last_purchase_at: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class ProfileRecentEvent:
    event_id: str
    event_type: str
    occurred_at: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class ProfileDetails:
    customer_id: str
    identifiers: ProfileIdentifiers
    attributes: dict
    counters: ProfileCounters
    total_revenue: float
    currency: str | None
    timestamps: ProfileTimestamps
    segments: list[str]
    recent_events: list[ProfileRecentEvent]
