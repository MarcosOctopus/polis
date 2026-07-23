"""Billing schemas — credit packages, plans, subscriptions, invoices, gateways."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


# ═══════════════════════════════════════════════════════════════════
# CRÉDITOS
# ═══════════════════════════════════════════════════════════════════

class CreditPackageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    credits: int
    price_cents: int
    description: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None


class TenantCreditOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    balance: int
    total_purchased: int
    total_spent: int
    low_balance_threshold: int = 100
    is_auto_recharge: bool = False
    auto_recharge_package_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CreditTransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    type: str
    amount: int
    balance_after: int
    description: Optional[str] = None
    channel: Optional[str] = None
    campaign_id: Optional[str] = None
    message_id: Optional[str] = None
    metadata_: Optional[dict[str, Any]] = None
    created_at: Optional[datetime] = None


class ChannelCostOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: Optional[str] = None
    channel: str
    message_type: str
    cost_per_message: float
    is_admin_override: bool = False
    is_active: bool = True


class ChannelCostCreate(BaseModel):
    channel: str
    message_type: str
    cost_per_message: float
    tenant_id: Optional[str] = None


class PurchaseCreditsRequest(BaseModel):
    package_id: str


class CreditBalanceResponse(BaseModel):
    balance: int
    total_purchased: int
    total_spent: int
    low_balance: bool


# ═══════════════════════════════════════════════════════════════════
# PLANOS
# ═══════════════════════════════════════════════════════════════════

class PlanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    price_cents_monthly: int = 0
    price_cents_annual: int = 0
    credits_monthly: int = 0
    max_contacts: int = 100
    max_messages_month: int = 500
    max_campaigns: int = 5
    max_segments: int = 5
    max_users: int = 1
    max_whatsapp_phone: int = 1
    features: Optional[dict[str, Any]] = None
    is_active: bool = True
    sort_order: int = 0
    is_highlighted: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PlanCreate(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    price_cents_monthly: int = 0
    price_cents_annual: int = 0
    credits_monthly: int = 0
    max_contacts: int = 100
    max_messages_month: int = 500
    max_campaigns: int = 5
    max_segments: int = 5
    max_users: int = 1
    max_whatsapp_phone: int = 1
    features: Optional[dict[str, Any]] = None
    is_active: bool = True
    sort_order: int = 0
    is_highlighted: bool = False


class PlanUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    price_cents_monthly: Optional[int] = None
    price_cents_annual: Optional[int] = None
    credits_monthly: Optional[int] = None
    max_contacts: Optional[int] = None
    max_messages_month: Optional[int] = None
    max_campaigns: Optional[int] = None
    max_segments: Optional[int] = None
    max_users: Optional[int] = None
    max_whatsapp_phone: Optional[int] = None
    features: Optional[dict[str, Any]] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None
    is_highlighted: Optional[bool] = None


# ═══════════════════════════════════════════════════════════════════
# ASSINATURAS
# ═══════════════════════════════════════════════════════════════════

class SubscriptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    plan_id: str
    plan_name: str = ""
    status: str
    billing_cycle: str = "monthly"
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    payment_gateway: str = "manual"
    gateway_subscription_id: Optional[str] = None
    metadata_: Optional[dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class SubscriptionCreate(BaseModel):
    plan_id: str
    billing_cycle: str = "monthly"
    payment_gateway: str = "manual"
    gateway_subscription_id: Optional[str] = None


class SubscriptionChangePlan(BaseModel):
    plan_id: str


class SubscriptionCancel(BaseModel):
    reason: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════
# FATURAS
# ═══════════════════════════════════════════════════════════════════

class InvoiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    subscription_id: Optional[str] = None
    plan_id: Optional[str] = None
    plan_name: Optional[str] = None
    invoice_type: str
    amount_cents: int
    credits: int = 0
    status: str = "pending"
    payment_method: Optional[str] = "manual"
    gateway: Optional[str] = None
    gateway_invoice_id: Optional[str] = None
    gateway_payment_url: Optional[str] = None
    paid_at: Optional[datetime] = None
    due_at: Optional[datetime] = None
    description: Optional[str] = None
    metadata_: Optional[dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ManualPaymentRequest(BaseModel):
    invoice_id: str
    payment_method: str = "manual"
    notes: Optional[str] = None


class ManualInvoiceCreate(BaseModel):
    tenant_id: str
    amount_cents: int
    credits: int = 0
    description: Optional[str] = None
    due_at: Optional[datetime] = None


# ═══════════════════════════════════════════════════════════════════
# AJUSTE MANUAL DE CRÉDITOS
# ═══════════════════════════════════════════════════════════════════

class ManualCreditAdjustment(BaseModel):
    tenant_id: str
    amount: int  # positivo = creditar, negativo = debitar
    description: str
    reason: str


# ═══════════════════════════════════════════════════════════════════
# GATEWAYS DE PAGAMENTO
# ═══════════════════════════════════════════════════════════════════

class GatewayConfigOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: Optional[str] = None
    gateway: str
    is_active: bool = True
    config: Optional[dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class GatewayConfigSet(BaseModel):
    is_active: bool = True
    config: dict[str, Any] = {}


# ═══════════════════════════════════════════════════════════════════
# PAGINAÇÃO
# ═══════════════════════════════════════════════════════════════════

class PaginatedResponse(BaseModel):
    items: list[Any]
    total: int
    limit: int
    offset: int
