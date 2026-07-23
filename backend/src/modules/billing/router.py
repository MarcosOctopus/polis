"""Billing router — credits, plans, subscriptions, invoices, gateways."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.dependencies import get_db
from src.modules.billing.service import BillingService, InsufficientCreditsError
from src.modules.billing.schemas import (
    PlanOut,
    PlanCreate,
    PlanUpdate,
    SubscriptionOut,
    SubscriptionCreate,
    SubscriptionChangePlan,
    SubscriptionCancel,
    InvoiceOut,
    ManualPaymentRequest,
    ManualInvoiceCreate,
    ManualCreditAdjustment,
    GatewayConfigOut,
    GatewayConfigSet,
    CreditPackageOut,
    TenantCreditOut,
    CreditTransactionOut,
    ChannelCostOut,
    ChannelCostCreate,
    PurchaseCreditsRequest,
    CreditBalanceResponse,
    PaginatedResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/billing", tags=["Billing"])


# ── Helpers ──────────────────────────────────────────────────────────

def _require_admin(request: Request) -> None:
    if not getattr(request.state, "is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")


async def _get_tenant_id(request: Request) -> str:
    tid = getattr(request.state, "tenant_id", None)
    if not tid:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return tid


# ═════════════════════════════════════════════════════════════════════
# CREDIT PACKAGES
# ═════════════════════════════════════════════════════════════════════

@router.get("/packages", response_model=list[CreditPackageOut])
async def list_packages(
    db: AsyncSession = Depends(get_db),
):
    """Listar pacotes de crédito disponíveis."""
    return await BillingService.get_credit_packages(db)


# ═════════════════════════════════════════════════════════════════════
# CREDITS
# ═════════════════════════════════════════════════════════════════════

@router.get("/balance", response_model=CreditBalanceResponse)
async def get_balance(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Saldo de créditos do tenant autenticado."""
    tenant_id = await _get_tenant_id(request)
    return await BillingService.check_balance(db, tenant_id)


@router.get("/credits", response_model=TenantCreditOut)
async def get_credits(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Detalhes do crédito do tenant."""
    tenant_id = await _get_tenant_id(request)
    credit = await BillingService.get_tenant_credit(db, tenant_id)
    if credit is None:
        credit = await BillingService.get_or_create_tenant_credit(db, tenant_id)
    return credit


@router.get("/transactions", response_model=PaginatedResponse)
async def list_transactions(
    request: Request,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Extrato de transações do tenant."""
    tenant_id = await _get_tenant_id(request)
    items = await BillingService.get_transactions(db, tenant_id, limit=limit, offset=offset)
    return PaginatedResponse(items=items, total=len(items), limit=limit, offset=offset)


@router.post("/credits/adjust", response_model=CreditTransactionOut)
async def manual_credit_adjustment(
    request: Request,
    body: ManualCreditAdjustment,
    db: AsyncSession = Depends(get_db),
):
    """Ajustar créditos manualmente (admin). Positivo=creditar, Negativo=debitar."""
    _require_admin(request)
    try:
        tx = await BillingService.adjust_credits_manual(
            db,
            tenant_id=body.tenant_id,
            amount=body.amount,
            description=f"{body.description} — {body.reason}",
        )
        return tx
    except InsufficientCreditsError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ═════════════════════════════════════════════════════════════════════
# PLANS
# ═════════════════════════════════════════════════════════════════════

@router.get("/plans", response_model=list[PlanOut])
async def list_plans(
    db: AsyncSession = Depends(get_db),
):
    """Listar planos ativos."""
    return await BillingService.get_plans(db)


@router.get("/plans/{plan_id}", response_model=PlanOut)
async def get_plan(
    plan_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Obter um plano específico."""
    plan = await BillingService.get_plan(db, plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@router.post("/plans", response_model=PlanOut, status_code=201)
async def create_plan(
    request: Request,
    body: PlanCreate,
    db: AsyncSession = Depends(get_db),
):
    """Criar plano (admin)."""
    _require_admin(request)
    return await BillingService.create_plan(db, body)


@router.put("/plans/{plan_id}", response_model=PlanOut)
async def update_plan(
    request: Request,
    plan_id: str,
    body: PlanUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Atualizar plano (admin)."""
    _require_admin(request)
    plan = await BillingService.update_plan(db, plan_id, body)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


# ═════════════════════════════════════════════════════════════════════
# SUBSCRIPTIONS
# ═════════════════════════════════════════════════════════════════════

@router.post("/subscriptions", response_model=SubscriptionOut, status_code=201)
async def create_subscription(
    request: Request,
    body: SubscriptionCreate,
    db: AsyncSession = Depends(get_db),
):
    """Assinar um plano."""
    tenant_id = await _get_tenant_id(request)
    try:
        sub = await BillingService.create_subscription(db, tenant_id, body)
        # Carregar plan_name
        plan = await BillingService.get_plan(db, sub.plan_id)
        plan_name = plan.name if plan else ""
        return _sub_to_out(sub, plan_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/subscriptions/current", response_model=SubscriptionOut)
async def current_subscription(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Assinatura atual do tenant."""
    tenant_id = await _get_tenant_id(request)
    sub = await BillingService.get_subscription(db, tenant_id)
    if sub is None:
        raise HTTPException(status_code=404, detail="No active subscription")
    plan = await BillingService.get_plan(db, sub.plan_id)
    plan_name = plan.name if plan else ""
    return _sub_to_out(sub, plan_name)


@router.get("/subscriptions", response_model=list[SubscriptionOut])
async def list_subscriptions(
    request: Request,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Listar assinaturas (admin)."""
    _require_admin(request)
    subs = await BillingService.list_subscriptions(db, limit=limit, offset=offset, status_filter=status)
    result = []
    for sub in subs:
        plan = await BillingService.get_plan(db, sub.plan_id)
        plan_name = plan.name if plan else ""
        result.append(_sub_to_out(sub, plan_name))
    return result


@router.post("/subscriptions/change-plan", response_model=SubscriptionOut)
async def change_plan(
    request: Request,
    body: SubscriptionChangePlan,
    db: AsyncSession = Depends(get_db),
):
    """Trocar de plano."""
    tenant_id = await _get_tenant_id(request)
    sub = await BillingService.change_plan(db, tenant_id, body.plan_id)
    if sub is None:
        raise HTTPException(status_code=404, detail="No active subscription")
    plan = await BillingService.get_plan(db, sub.plan_id)
    plan_name = plan.name if plan else ""
    return _sub_to_out(sub, plan_name)


@router.post("/subscriptions/cancel", response_model=SubscriptionOut)
async def cancel_subscription(
    request: Request,
    body: Optional[SubscriptionCancel] = None,
    db: AsyncSession = Depends(get_db),
):
    """Cancelar assinatura."""
    tenant_id = await _get_tenant_id(request)
    reason = body.reason if body else None
    sub = await BillingService.cancel_subscription(db, tenant_id, reason=reason)
    if sub is None:
        raise HTTPException(status_code=404, detail="No active subscription")
    plan = await BillingService.get_plan(db, sub.plan_id)
    plan_name = plan.name if plan else ""
    return _sub_to_out(sub, plan_name)


def _sub_to_out(sub, plan_name: str) -> SubscriptionOut:
    return SubscriptionOut(
        id=sub.id,
        tenant_id=sub.tenant_id,
        plan_id=sub.plan_id,
        plan_name=plan_name,
        status=sub.status,
        billing_cycle=sub.billing_cycle,
        current_period_start=sub.current_period_start,
        current_period_end=sub.current_period_end,
        trial_end=sub.trial_end,
        cancelled_at=sub.cancelled_at,
        payment_gateway=sub.payment_gateway,
        gateway_subscription_id=sub.gateway_subscription_id,
        metadata_=sub.metadata_,
        created_at=sub.created_at,
        updated_at=sub.updated_at,
    )


# ═════════════════════════════════════════════════════════════════════
# INVOICES
# ═════════════════════════════════════════════════════════════════════

@router.get("/invoices", response_model=list[InvoiceOut])
async def list_invoices(
    request: Request,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Faturas do tenant autenticado."""
    tenant_id = await _get_tenant_id(request)
    invoices = await BillingService.list_invoices(db, tenant_id, limit=limit, offset=offset, status_filter=status)
    return await _enrich_invoices(db, invoices)


@router.get("/invoices/{invoice_id}", response_model=InvoiceOut)
async def get_invoice(
    invoice_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Detalhe de uma fatura."""
    tenant_id = await _get_tenant_id(request)
    inv = await BillingService.get_invoice(db, invoice_id)
    if inv is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if not getattr(request.state, "is_admin", False) and inv.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Invoice not found")
    enriched = await _enrich_invoices(db, [inv])
    return enriched[0] if enriched else inv


@router.post("/invoices", response_model=InvoiceOut, status_code=201)
async def create_invoice(
    request: Request,
    body: ManualInvoiceCreate,
    db: AsyncSession = Depends(get_db),
):
    """Criar fatura manual (admin)."""
    _require_admin(request)
    inv = await BillingService.create_invoice(
        db,
        tenant_id=body.tenant_id,
        amount_cents=body.amount_cents,
        credits=body.credits,
        description=body.description,
        due_at=body.due_at,
    )
    return inv


@router.post("/invoices/{invoice_id}/pay", response_model=InvoiceOut)
async def pay_invoice(
    request: Request,
    invoice_id: str,
    body: ManualPaymentRequest,
    db: AsyncSession = Depends(get_db),
):
    """Pagamento manual de fatura (admin)."""
    _require_admin(request)
    inv = await BillingService.pay_invoice_manual(
        db,
        invoice_id=invoice_id,
        payment_method=body.payment_method,
    )
    if inv is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return inv


async def _enrich_invoices(db: AsyncSession, invoices: list) -> list:
    """Adiciona plan_name às faturas."""
    result = []
    for inv in invoices:
        plan_name = None
        if inv.plan_id:
            plan = await BillingService.get_plan(db, inv.plan_id)
            plan_name = plan.name if plan else None
        d = {
            "id": inv.id,
            "tenant_id": inv.tenant_id,
            "subscription_id": inv.subscription_id,
            "plan_id": inv.plan_id,
            "plan_name": plan_name,
            "invoice_type": inv.invoice_type,
            "amount_cents": inv.amount_cents,
            "credits": inv.credits,
            "status": inv.status,
            "payment_method": inv.payment_method,
            "gateway": inv.gateway,
            "gateway_invoice_id": inv.gateway_invoice_id,
            "gateway_payment_url": inv.gateway_payment_url,
            "paid_at": inv.paid_at,
            "due_at": inv.due_at,
            "description": inv.description,
            "metadata_": inv.metadata_,
            "created_at": inv.created_at,
            "updated_at": inv.updated_at,
        }
        result.append(InvoiceOut(**d))
    return result


# ═════════════════════════════════════════════════════════════════════
# CHANNEL COSTS
# ═════════════════════════════════════════════════════════════════════

@router.get("/channels/costs", response_model=list[ChannelCostOut])
async def list_channel_costs(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Custos de canal (globais + do tenant)."""
    tenant_id = await _get_tenant_id(request)
    return await BillingService.get_channel_costs(db, tenant_id=tenant_id)


@router.post("/channels/costs", response_model=ChannelCostOut, status_code=201)
async def set_channel_cost(
    request: Request,
    body: ChannelCostCreate,
    db: AsyncSession = Depends(get_db),
):
    """Definir custo de canal (admin)."""
    _require_admin(request)
    return await BillingService.set_channel_cost(db, body)


# ═════════════════════════════════════════════════════════════════════
# PAYMENT GATEWAYS
# ═════════════════════════════════════════════════════════════════════

@router.get("/gateways", response_model=list[GatewayConfigOut])
async def list_gateways(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Listar gateways configurados do tenant."""
    tenant_id = await _get_tenant_id(request)
    return await BillingService.list_gateway_configs(db, tenant_id)


@router.post("/gateways/{gateway}", response_model=GatewayConfigOut)
async def set_gateway(
    request: Request,
    gateway: str,
    body: GatewayConfigSet,
    db: AsyncSession = Depends(get_db),
):
    """Configurar gateway de pagamento (ex: stripe, asaas, mercadopago)."""
    tenant_id = await _get_tenant_id(request)
    return await BillingService.set_gateway_config(
        db,
        tenant_id=tenant_id,
        gateway=gateway,
        is_active=body.is_active,
        config=body.config,
    )


@router.delete("/gateways/{gateway}", status_code=204)
async def delete_gateway(
    request: Request,
    gateway: str,
    db: AsyncSession = Depends(get_db),
):
    """Remover configuração de gateway."""
    tenant_id = await _get_tenant_id(request)
    cfg = await BillingService.get_gateway_config(db, tenant_id, gateway)
    if cfg is None:
        raise HTTPException(status_code=404, detail="Gateway config not found")
    await BillingService.delete_gateway_config(db, cfg.id)
