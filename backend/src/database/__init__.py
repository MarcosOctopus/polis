"""Database package — models, session, and metadata."""

# ═══════════════════════════════════════════════════════════════
# Import all models so SQLAlchemy picks them up
# ═══════════════════════════════════════════════════════════════
from src.database.models import Base, Tenant, User, Contact, Campaign, Message, Conversation
from src.database.models_extensions import (
    CreditPackage,
    TenantCredit,
    CreditTransaction,
    ChannelCost,
    MessageClassification,
    Segment,
    SegmentContact,
    Consent,
    MessageTemplate,
    Plan,
    TenantSubscription,
    Invoice,
    PaymentGatewayConfig,
)

__all__ = [
    "Base",
    "Tenant",
    "User",
    "Contact",
    "Campaign",
    "Message",
    "Conversation",
    "CreditPackage",
    "TenantCredit",
    "CreditTransaction",
    "ChannelCost",
    "MessageClassification",
    "Segment",
    "SegmentContact",
    "Consent",
    "MessageTemplate",
    "Plan",
    "TenantSubscription",
    "Invoice",
    "PaymentGatewayConfig",
]
