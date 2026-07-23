"""Extended models — Credit System, Classification, Segments, Consents, Templates.

TABELAS NOVAS:
  - credit_packages       → pacotes de crédito pré-definidos
  - tenant_credits        → saldo de cada tenant
  - channel_costs         → custo por canal (default Meta, admin pode sobrescrever)
  - message_classifications → classificação IA de cada mensagem
  - segments              → públicos segmentados
  - segment_contacts      → contatos de um segmento manual
  - consents              → consentimento por contato + canal
  - message_templates     → templates de mensagem

CAMPOS NOVOS EM TABELAS EXISTENTES:
  - contacts: consent_* flags, communication_preference, last_interaction_at, interaction_count, source
  - territorial_events: report_count, unique_citizens, sentiment_score, resolution_status
  - campaigns: strategy, tone, secondary_channel_id, approval_status, approved_by, cost_estimate, credit_cost
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models import Base, utcnow


# ═══════════════════════════════════════════════════════════════
# CREDIT SYSTEM (Sistema de Créditos)
# ═══════════════════════════════════════════════════════════════


class CreditPackage(Base):
    """Pacote de créditos pré-definido que um tenant pode comprar."""

    __tablename__ = "credit_packages"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)          # ex: "Básico", "Profissional"
    credits: Mapped[int] = mapped_column(Integer, nullable=False)           # quantidade de créditos
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)       # preço em centavos (BRL)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=utcnow
    )


class TenantCredit(Base):
    """Saldo de créditos de cada tenant."""

    __tablename__ = "tenant_credits"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id"), nullable=False, unique=True, index=True
    )
    balance: Mapped[int] = mapped_column(Integer, default=0)               # saldo atual
    total_purchased: Mapped[int] = mapped_column(Integer, default=0)       # total comprado (histórico)
    total_spent: Mapped[int] = mapped_column(Integer, default=0)           # total gasto (histórico)
    low_balance_threshold: Mapped[int] = mapped_column(Integer, default=100)  # alerta qdo abaixo
    is_auto_recharge: Mapped[bool] = mapped_column(Boolean, default=False)
    auto_recharge_package_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("credit_packages.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=utcnow
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), default=None
    )

    tenant = relationship("Tenant", lazy="selectin")
    auto_recharge_package = relationship("CreditPackage", lazy="selectin")


class CreditTransaction(Base):
    """Histórico de movimentação de créditos (débito/crédito)."""

    __tablename__ = "credit_transactions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id"), nullable=False, index=True
    )
    type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # purchase, spend, refund, admin_adjustment
    amount: Mapped[int] = mapped_column(Integer, nullable=False)            # positivo = crédito, negativo = débito
    balance_after: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    channel: Mapped[str | None] = mapped_column(String(50), nullable=True)  # whatsapp, sms, email
    campaign_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("campaigns.id"), nullable=True
    )
    message_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("messages.id"), nullable=True
    )
    metadata_: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=utcnow
    )

    tenant = relationship("Tenant", lazy="selectin")
    campaign = relationship("Campaign", lazy="selectin")
    message = relationship("Message", lazy="selectin")


class ChannelCost(Base):
    """Custo por canal e tipo de mensagem.

    Defaults seguem os valores da Meta para WhatsApp.
    Admin pode sobrescrever por tenant.
    """

    __tablename__ = "channel_costs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    tenant_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("tenants.id"), nullable=True, index=True
    )  # null = default global
    channel: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # whatsapp, sms, email
    message_type: Mapped[str] = mapped_column(
        String(50), default="text"
    )  # text, template, media, marketing, utility, service
    cost_per_message: Mapped[float] = mapped_column(Float, nullable=False)  # em créditos (1 crédito = $0.001)
    is_admin_override: Mapped[bool] = mapped_column(Boolean, default=False)  # TRUE = admin colocou preço manual
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=utcnow
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), default=None
    )

    tenant = relationship("Tenant", lazy="selectin")


# ═══════════════════════════════════════════════════════════════
# CLASSIFICATION (Pipeline de IA)
# ═══════════════════════════════════════════════════════════════


class MessageClassification(Base):
    """Classificação de uma mensagem pelo pipeline de IA."""

    __tablename__ = "message_classifications"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id"), nullable=False, index=True
    )
    message_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("messages.id"), nullable=False, unique=True, index=True
    )
    # Tipo de mensagem
    classification_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # complaint, praise, suggestion, question, denunciation, support, criticism, emergency, general
    category: Mapped[str | None] = mapped_column(
        String(100), nullable=True, index=True
    )  # infraestrutura, saude, educacao, seguranca, etc.
    subcategory: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Sentimento
    sentiment: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )  # positivo, negativo, neutro
    sentiment_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Urgência e risco
    urgency: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )  # baixa, media, alta, emergencia
    risk: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )  # baixo, medio, alto

    # Localização extraída
    extracted_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    extracted_neighborhood: Mapped[str | None] = mapped_column(String(100), nullable=True)
    extracted_city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    extracted_state: Mapped[str | None] = mapped_column(String(50), nullable=True)
    reference_point: Mapped[str | None] = mapped_column(Text, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    geocode_source: Mapped[str | None] = mapped_column(String(50), nullable=True)  # nominatim, google, manual

    # IA
    suggested_department: Mapped[str | None] = mapped_column(String(255), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    keywords: Mapped[list | None] = mapped_column(JSON, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)  # modelo usado
    raw_classification: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # JSON cru da LLM

    # Vínculo com evento territorial
    territorial_event_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("territorial_events.id"), nullable=True, index=True
    )

    # Timestamps
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=utcnow
    )

    tenant = relationship("Tenant", lazy="selectin")
    message = relationship("Message", lazy="selectin")
    territorial_event = relationship("TerritorialEvent", lazy="selectin")


# ═══════════════════════════════════════════════════════════════
# SEGMENTS (Segmentação de Público)
# ═══════════════════════════════════════════════════════════════


class Segment(Base):
    """Segmento de público-alvo para campanhas."""

    __tablename__ = "segments"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    segment_type: Mapped[str] = mapped_column(
        String(50), default="dynamic"
    )  # manual, dynamic, imported, ai_generated, territorial
    filters: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )  # para dynamic: critérios de filtro
    territorial_event_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("territorial_events.id"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    contact_count: Mapped[int] = mapped_column(Integer, default=0)  # cache da contagem
    created_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=utcnow
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), default=None
    )

    tenant = relationship("Tenant", lazy="selectin")
    territorial_event = relationship("TerritorialEvent", lazy="selectin")
    creator = relationship("User", lazy="selectin", foreign_keys=[created_by])


class SegmentContact(Base):
    """Relação N:N entre segmentos manuais e contatos."""

    __tablename__ = "segment_contacts"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    segment_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("segments.id"), nullable=False, index=True
    )
    contact_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("contacts.id"), nullable=False, index=True
    )
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=utcnow
    )


# ═══════════════════════════════════════════════════════════════
# CONSENTS (Consentimento por Canal)
# ═══════════════════════════════════════════════════════════════


class Consent(Base):
    """Consentimento de um contato para receber mensagens por canal."""

    __tablename__ = "consents"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id"), nullable=False, index=True
    )
    contact_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("contacts.id"), nullable=False, index=True
    )
    channel: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # whatsapp, sms, email
    status: Mapped[str] = mapped_column(
        String(20), default="granted"
    )  # granted, denied, pending
    source: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # opt_in_form, campaign, manual, import, opt_out_message
    granted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    denied_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    metadata_: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=utcnow
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), default=None
    )

    __table_args__ = (
        # Um único consentimento por contato + canal
        UniqueConstraint("tenant_id", "contact_id", "channel", name="uq_consent_contact_channel"),
    )


# ═══════════════════════════════════════════════════════════════
# MESSAGE TEMPLATES (Templates de Mensagem)
# ═══════════════════════════════════════════════════════════════


class MessageTemplate(Base):
    """Template reutilizável de mensagem."""

    __tablename__ = "message_templates"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    channel: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # whatsapp, sms, email
    message_type: Mapped[str] = mapped_column(
        String(50), default="text"
    )  # text, html, template
    subject: Mapped[str | None] = mapped_column(String(500), nullable=True)  # para email
    body: Mapped[str] = mapped_column(Text, nullable=False)
    variables: Mapped[list | None] = mapped_column(JSON, nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=utcnow
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), default=None
    )

    tenant = relationship("Tenant", lazy="selectin")
    creator = relationship("User", lazy="selectin", foreign_keys=[created_by])


# ═══════════════════════════════════════════════════════════════
# PLANS (Planos de Assinatura)
# ═══════════════════════════════════════════════════════════════


class Plan(Base):
    """Plano de assinatura — define limites e recursos por tier."""

    __tablename__ = "plans"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price_cents_monthly: Mapped[int] = mapped_column(Integer, default=0)
    price_cents_annual: Mapped[int] = mapped_column(Integer, default=0)
    credits_monthly: Mapped[int] = mapped_column(Integer, default=0)
    max_contacts: Mapped[int] = mapped_column(Integer, default=100)
    max_messages_month: Mapped[int] = mapped_column(Integer, default=500)
    max_campaigns: Mapped[int] = mapped_column(Integer, default=5)
    max_segments: Mapped[int] = mapped_column(Integer, default=5)
    max_users: Mapped[int] = mapped_column(Integer, default=1)
    max_whatsapp_phone: Mapped[int] = mapped_column(Integer, default=1)
    features: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_highlighted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=utcnow
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), default=None
    )


# ═══════════════════════════════════════════════════════════════
# SUBSCRIPTIONS (Assinaturas dos Tenants)
# ═══════════════════════════════════════════════════════════════


class TenantSubscription(Base):
    """Assinatura ativa/inativa de um tenant."""

    __tablename__ = "tenant_subscriptions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id"), nullable=False, unique=True, index=True
    )
    plan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("plans.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), default="active"
    )  # active, trialing, past_due, cancelled, expired
    billing_cycle: Mapped[str] = mapped_column(
        String(10), default="monthly"
    )  # monthly, annual
    current_period_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    current_period_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    trial_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    payment_gateway: Mapped[str] = mapped_column(
        String(30), default="manual"
    )  # manual, stripe, asaas, mercadopago, pagseguro
    gateway_subscription_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    metadata_: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=utcnow
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), default=None
    )

    tenant = relationship("Tenant", lazy="selectin")
    plan = relationship("Plan", lazy="selectin")


# ═══════════════════════════════════════════════════════════════
# INVOICES (Faturas)
# ═══════════════════════════════════════════════════════════════


class Invoice(Base):
    """Fatura de assinatura ou compra avulsa de créditos."""

    __tablename__ = "invoices"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id"), nullable=False, index=True
    )
    subscription_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("tenant_subscriptions.id"), nullable=True
    )
    plan_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("plans.id"), nullable=True
    )
    invoice_type: Mapped[str] = mapped_column(
        String(20), default="subscription"
    )  # subscription, credit_purchase, manual_adjustment
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    credits: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(
        String(20), default="pending"
    )  # pending, paid, overdue, cancelled, refunded
    payment_method: Mapped[str] = mapped_column(
        String(30), default="manual"
    )  # manual, pix, boleto, credit_card, gateway_transfer
    gateway: Mapped[str | None] = mapped_column(String(30), nullable=True)
    gateway_invoice_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    gateway_payment_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=utcnow
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), default=None
    )

    tenant = relationship("Tenant", lazy="selectin")
    subscription = relationship("TenantSubscription", lazy="selectin")
    plan = relationship("Plan", lazy="selectin")


# ═══════════════════════════════════════════════════════════════
# PAYMENT GATEWAY CONFIG (Config de Gateways por Tenant)
# ═══════════════════════════════════════════════════════════════


class PaymentGatewayConfig(Base):
    """Configuração de gateway de pagamento por tenant."""

    __tablename__ = "payment_gateway_configs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id"), nullable=False, index=True
    )
    gateway: Mapped[str] = mapped_column(String(30), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    config: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=utcnow
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), default=None
    )

    __table_args__ = (
        UniqueConstraint("tenant_id", "gateway", name="uq_gateway_tenant"),
    )

    tenant = relationship("Tenant", lazy="selectin")
