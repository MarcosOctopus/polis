"""Billing service — credits, plans, subscriptions, invoices, gateways."""

import logging
from datetime import datetime, timezone, timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import (
    Plan,
    TenantSubscription,
    Invoice,
    PaymentGatewayConfig,
    TenantCredit,
    CreditTransaction,
    CreditPackage,
    ChannelCost,
)
from src.modules.billing.schemas import (
    PlanCreate,
    PlanUpdate,
    SubscriptionCreate,
    ChannelCostCreate,
)

logger = logging.getLogger(__name__)


class BillingError(Exception):
    """Base billing error."""
    pass


class InsufficientCreditsError(BillingError):
    pass


class BillingService:
    """Async billing: credits, plans, subscriptions, invoices, gateways."""

    # ═══════════════════════════════════════════════════════════════
    # CREDIT PACKAGES
    # ═══════════════════════════════════════════════════════════════

    @staticmethod
    async def get_credit_packages(
        session: AsyncSession,
    ) -> list[CreditPackage]:
        result = await session.execute(
            select(CreditPackage)
            .where(CreditPackage.is_active == True)
            .order_by(CreditPackage.price_cents)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_credit_package_by_id(
        session: AsyncSession, package_id: str
    ) -> CreditPackage | None:
        result = await session.execute(
            select(CreditPackage).where(CreditPackage.id == package_id)
        )
        return result.scalar_one_or_none()

    # ═══════════════════════════════════════════════════════════════
    # TENANT CREDITS
    # ═══════════════════════════════════════════════════════════════

    @staticmethod
    async def get_or_create_tenant_credit(
        session: AsyncSession, tenant_id: str
    ) -> TenantCredit:
        result = await session.execute(
            select(TenantCredit).where(TenantCredit.tenant_id == tenant_id)
        )
        tc = result.scalar_one_or_none()
        if tc is None:
            tc = TenantCredit(
                tenant_id=tenant_id,
                balance=0,
                total_purchased=0,
                total_spent=0,
            )
            session.add(tc)
            await session.flush()
            await session.refresh(tc)
        return tc

    @staticmethod
    async def get_tenant_credit(
        session: AsyncSession, tenant_id: str
    ) -> TenantCredit | None:
        result = await session.execute(
            select(TenantCredit).where(TenantCredit.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def purchase_credits(
        session: AsyncSession,
        tenant_id: str,
        package_id: str,
    ) -> CreditTransaction:
        pkg = await BillingService.get_credit_package_by_id(session, package_id)
        if pkg is None or not pkg.is_active:
            raise BillingError("Credit package not found or inactive")

        tc = await BillingService.get_or_create_tenant_credit(session, tenant_id)
        tc.balance += pkg.credits
        tc.total_purchased += pkg.credits

        tx = CreditTransaction(
            tenant_id=tenant_id,
            type="purchase",
            amount=pkg.credits,
            balance_after=tc.balance,
            description=f"Package: {pkg.name} ({pkg.credits} credits)",
        )
        session.add(tx)
        await session.flush()
        await session.refresh(tx)

        # Invoice automática
        inv = Invoice(
            tenant_id=tenant_id,
            invoice_type="credit_purchase",
            amount_cents=pkg.price_cents,
            credits=pkg.credits,
            status="paid",
            payment_method="manual",
            gateway="manual",
            description=f"Compra: {pkg.name}",
            paid_at=datetime.now(timezone.utc),
            due_at=datetime.now(timezone.utc),
        )
        session.add(inv)
        await session.flush()
        return tx

    @staticmethod
    async def spend_credits(
        session: AsyncSession,
        tenant_id: str,
        amount: int,
        description: str,
        channel: str | None = None,
        campaign_id: str | None = None,
        message_id: str | None = None,
    ) -> CreditTransaction | None:
        tc = await BillingService.get_or_create_tenant_credit(session, tenant_id)
        if tc.balance < amount:
            return None
        tc.balance -= amount
        tc.total_spent += amount
        tx = CreditTransaction(
            tenant_id=tenant_id,
            type="spend",
            amount=-amount,
            balance_after=tc.balance,
            description=description,
            channel=channel,
            campaign_id=campaign_id,
            message_id=message_id,
        )
        session.add(tx)
        await session.flush()
        await session.refresh(tx)
        return tx

    @staticmethod
    async def refund_credits(
        session: AsyncSession,
        tenant_id: str,
        amount: int,
        description: str,
    ) -> CreditTransaction:
        tc = await BillingService.get_or_create_tenant_credit(session, tenant_id)
        tc.balance += amount
        tc.total_spent = max(0, tc.total_spent - amount)
        tx = CreditTransaction(
            tenant_id=tenant_id,
            type="refund",
            amount=amount,
            balance_after=tc.balance,
            description=description,
        )
        session.add(tx)
        await session.flush()
        await session.refresh(tx)
        return tx

    @staticmethod
    async def get_transactions(
        session: AsyncSession,
        tenant_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> list[CreditTransaction]:
        result = await session.execute(
            select(CreditTransaction)
            .where(CreditTransaction.tenant_id == tenant_id)
            .order_by(CreditTransaction.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    @staticmethod
    async def check_balance(
        session: AsyncSession, tenant_id: str
    ) -> dict:
        tc = await BillingService.get_or_create_tenant_credit(session, tenant_id)
        return {
            "balance": tc.balance,
            "total_purchased": tc.total_purchased,
            "total_spent": tc.total_spent,
            "low_balance": tc.balance < tc.low_balance_threshold,
        }

    # ═══════════════════════════════════════════════════════════════
    # CHANNEL COSTS
    # ═══════════════════════════════════════════════════════════════

    @staticmethod
    async def get_channel_costs(
        session: AsyncSession, tenant_id: str | None = None
    ) -> list[ChannelCost]:
        stmt = select(ChannelCost).where(ChannelCost.is_active == True)
        if tenant_id:
            stmt = stmt.where(
                (ChannelCost.tenant_id == tenant_id)
                | (ChannelCost.tenant_id.is_(None))
            )
        else:
            stmt = stmt.where(ChannelCost.tenant_id.is_(None))
        stmt = stmt.order_by(ChannelCost.channel, ChannelCost.message_type)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_channel_cost(
        session: AsyncSession,
        channel: str,
        message_type: str,
        tenant_id: str | None = None,
    ) -> float:
        """Retorna o custo por mensagem. Prioridade: tenant override > global > 1.0."""
        if tenant_id:
            result = await session.execute(
                select(ChannelCost).where(
                    ChannelCost.tenant_id == tenant_id,
                    ChannelCost.channel == channel,
                    ChannelCost.message_type == message_type,
                    ChannelCost.is_active == True,
                )
            )
            cc = result.scalar_one_or_none()
            if cc:
                return cc.cost_per_message
        result = await session.execute(
            select(ChannelCost).where(
                ChannelCost.tenant_id.is_(None),
                ChannelCost.channel == channel,
                ChannelCost.message_type == message_type,
                ChannelCost.is_active == True,
            )
        )
        cc = result.scalar_one_or_none()
        return cc.cost_per_message if cc else 1.0

    @staticmethod
    async def set_channel_cost(
        session: AsyncSession,
        data: ChannelCostCreate,
    ) -> ChannelCost:
        stmt = select(ChannelCost).where(
            ChannelCost.channel == data.channel,
            ChannelCost.message_type == data.message_type,
        )
        if data.tenant_id:
            stmt = stmt.where(ChannelCost.tenant_id == data.tenant_id)
        else:
            stmt = stmt.where(ChannelCost.tenant_id.is_(None))
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            existing.cost_per_message = data.cost_per_message
            existing.is_admin_override = True
            await session.flush()
            await session.refresh(existing)
            return existing
        cc = ChannelCost(
            tenant_id=data.tenant_id,
            channel=data.channel,
            message_type=data.message_type,
            cost_per_message=data.cost_per_message,
            is_admin_override=True,
        )
        session.add(cc)
        await session.flush()
        await session.refresh(cc)
        return cc

    # ═══════════════════════════════════════════════════════════════
    # PLANS
    # ═══════════════════════════════════════════════════════════════

    @staticmethod
    async def get_plans(
        session: AsyncSession, only_active: bool = True
    ) -> list[Plan]:
        stmt = select(Plan)
        if only_active:
            stmt = stmt.where(Plan.is_active == True)
        stmt = stmt.order_by(Plan.sort_order, Plan.name)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_plan(
        session: AsyncSession, plan_id: str
    ) -> Plan | None:
        result = await session.execute(
            select(Plan).where(Plan.id == plan_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_plan_by_slug(
        session: AsyncSession, slug: str
    ) -> Plan | None:
        result = await session.execute(
            select(Plan).where(Plan.slug == slug)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_plan(
        session: AsyncSession, data: PlanCreate
    ) -> Plan:
        plan = Plan(
            name=data.name,
            slug=data.slug,
            description=data.description,
            price_cents_monthly=data.price_cents_monthly,
            price_cents_annual=data.price_cents_annual,
            credits_monthly=data.credits_monthly,
            max_contacts=data.max_contacts,
            max_messages_month=data.max_messages_month,
            max_campaigns=data.max_campaigns,
            max_segments=data.max_segments,
            max_users=data.max_users,
            max_whatsapp_phone=data.max_whatsapp_phone,
            features=data.features or {},
            is_active=data.is_active,
            sort_order=data.sort_order,
            is_highlighted=data.is_highlighted,
        )
        session.add(plan)
        await session.flush()
        await session.refresh(plan)
        return plan

    @staticmethod
    async def update_plan(
        session: AsyncSession, plan_id: str, data: PlanUpdate
    ) -> Plan | None:
        plan = await BillingService.get_plan(session, plan_id)
        if plan is None:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(plan, field, value)
        await session.flush()
        await session.refresh(plan)
        return plan

    # ═══════════════════════════════════════════════════════════════
    # SUBSCRIPTIONS
    # ═══════════════════════════════════════════════════════════════

    @staticmethod
    async def create_subscription(
        session: AsyncSession,
        tenant_id: str,
        data: SubscriptionCreate,
    ) -> TenantSubscription:
        plan = await BillingService.get_plan(session, data.plan_id)
        if plan is None or not plan.is_active:
            raise BillingError("Plan not found or inactive")

        now = datetime.now(timezone.utc)
        period_end = now + timedelta(days=30 if data.billing_cycle == "monthly" else 365)

        sub = TenantSubscription(
            tenant_id=tenant_id,
            plan_id=plan.id,
            status="active",
            billing_cycle=data.billing_cycle,
            current_period_start=now,
            current_period_end=period_end,
            payment_gateway=data.payment_gateway,
            gateway_subscription_id=data.gateway_subscription_id,
        )
        session.add(sub)
        await session.flush()
        await session.refresh(sub)

        price_cents = (
            plan.price_cents_annual
            if data.billing_cycle == "annual"
            else plan.price_cents_monthly
        )
        inv = Invoice(
            tenant_id=tenant_id,
            subscription_id=sub.id,
            plan_id=plan.id,
            invoice_type="subscription",
            amount_cents=price_cents,
            credits=plan.credits_monthly,
            status="pending",
            payment_method="manual",
            gateway=data.payment_gateway,
            description=f"Assinatura: {plan.name} ({data.billing_cycle})",
            due_at=period_end,
        )
        session.add(inv)
        await session.flush()
        await session.refresh(sub)
        return sub

    @staticmethod
    async def get_subscription(
        session: AsyncSession, tenant_id: str
    ) -> TenantSubscription | None:
        result = await session.execute(
            select(TenantSubscription)
            .where(TenantSubscription.tenant_id == tenant_id)
            .order_by(TenantSubscription.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_subscription_by_id(
        session: AsyncSession, sub_id: str
    ) -> TenantSubscription | None:
        result = await session.execute(
            select(TenantSubscription).where(TenantSubscription.id == sub_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_subscriptions(
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
        status_filter: str | None = None,
    ) -> list[TenantSubscription]:
        stmt = select(TenantSubscription)
        if status_filter:
            stmt = stmt.where(TenantSubscription.status == status_filter)
        stmt = stmt.order_by(TenantSubscription.created_at.desc())
        stmt = stmt.limit(limit).offset(offset)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def change_plan(
        session: AsyncSession,
        tenant_id: str,
        new_plan_id: str,
    ) -> TenantSubscription | None:
        sub = await BillingService.get_subscription(session, tenant_id)
        if sub is None:
            return None
        plan = await BillingService.get_plan(session, new_plan_id)
        if plan is None:
            return None
        sub.plan_id = plan.id
        await session.flush()
        await session.refresh(sub)
        return sub

    @staticmethod
    async def cancel_subscription(
        session: AsyncSession,
        tenant_id: str,
        reason: str | None = None,
    ) -> TenantSubscription | None:
        sub = await BillingService.get_subscription(session, tenant_id)
        if sub is None:
            return None
        sub.status = "cancelled"
        sub.cancelled_at = datetime.now(timezone.utc)
        await session.flush()
        await session.refresh(sub)
        logger.info("Subscription %s cancelled for tenant %s. Reason: %s", sub.id, tenant_id, reason)
        return sub

    # ═══════════════════════════════════════════════════════════════
    # INVOICES
    # ═══════════════════════════════════════════════════════════════

    @staticmethod
    async def create_invoice(
        session: AsyncSession,
        tenant_id: str,
        amount_cents: int,
        description: str | None = None,
        credits: int = 0,
        due_at: datetime | None = None,
    ) -> Invoice:
        inv = Invoice(
            tenant_id=tenant_id,
            invoice_type="manual_adjustment",
            amount_cents=amount_cents,
            credits=credits,
            status="pending",
            payment_method="manual",
            gateway="manual",
            description=description or "Fatura manual",
            due_at=due_at or datetime.now(timezone.utc) + timedelta(days=30),
        )
        session.add(inv)
        await session.flush()
        await session.refresh(inv)
        return inv

    @staticmethod
    async def get_invoice(
        session: AsyncSession, invoice_id: str
    ) -> Invoice | None:
        result = await session.execute(
            select(Invoice).where(Invoice.id == invoice_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_invoices(
        session: AsyncSession,
        tenant_id: str,
        limit: int = 50,
        offset: int = 0,
        status_filter: str | None = None,
    ) -> list[Invoice]:
        stmt = select(Invoice).where(Invoice.tenant_id == tenant_id)
        if status_filter:
            stmt = stmt.where(Invoice.status == status_filter)
        stmt = stmt.order_by(Invoice.created_at.desc())
        stmt = stmt.limit(limit).offset(offset)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def list_all_invoices(
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
        status_filter: str | None = None,
    ) -> list[Invoice]:
        stmt = select(Invoice)
        if status_filter:
            stmt = stmt.where(Invoice.status == status_filter)
        stmt = stmt.order_by(Invoice.created_at.desc())
        stmt = stmt.limit(limit).offset(offset)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def pay_invoice_manual(
        session: AsyncSession,
        invoice_id: str,
        payment_method: str = "manual",
    ) -> Invoice | None:
        inv = await BillingService.get_invoice(session, invoice_id)
        if inv is None or inv.status == "paid":
            return inv
        now = datetime.now(timezone.utc)
        inv.status = "paid"
        inv.paid_at = now
        inv.payment_method = payment_method

        # Se tem créditos para liberar
        if inv.credits and inv.invoice_type in ("subscription", "credit_purchase"):
            tc = await BillingService.get_or_create_tenant_credit(session, inv.tenant_id)
            tc.balance += inv.credits
            tc.total_purchased += inv.credits
            tx = CreditTransaction(
                tenant_id=inv.tenant_id,
                type="purchase",
                amount=inv.credits,
                balance_after=tc.balance,
                description=f"Pagamento manual fatura #{inv.id[:8]}",
            )
            session.add(tx)
        await session.flush()
        await session.refresh(inv)
        return inv

    # ═══════════════════════════════════════════════════════════════
    # MANUAL CREDIT ADJUSTMENT
    # ═══════════════════════════════════════════════════════════════

    @staticmethod
    async def adjust_credits_manual(
        session: AsyncSession,
        tenant_id: str,
        amount: int,
        description: str,
    ) -> CreditTransaction:
        """Ajuste manual. amount positivo = crédito, negativo = débito."""
        tc = await BillingService.get_or_create_tenant_credit(session, tenant_id)
        if amount < 0 and tc.balance < abs(amount):
            raise InsufficientCreditsError(
                f"Cannot debit {abs(amount)} credits — balance is {tc.balance}"
            )
        tc.balance += amount
        if amount >= 0:
            tc.total_purchased += amount
        else:
            tc.total_spent += abs(amount)

        tx = CreditTransaction(
            tenant_id=tenant_id,
            type="admin_adjustment",
            amount=amount,
            balance_after=tc.balance,
            description=description,
        )
        session.add(tx)
        await session.flush()
        await session.refresh(tx)

        inv = Invoice(
            tenant_id=tenant_id,
            invoice_type="manual_adjustment",
            amount_cents=0,
            credits=amount,
            status="paid",
            payment_method="manual",
            gateway="manual",
            description=f"Ajuste admin: {description}",
            paid_at=datetime.now(timezone.utc),
        )
        session.add(inv)
        await session.flush()
        return tx

    # ═══════════════════════════════════════════════════════════════
    # PAYMENT GATEWAYS
    # ═══════════════════════════════════════════════════════════════

    @staticmethod
    async def get_gateway_config(
        session: AsyncSession,
        tenant_id: str,
        gateway: str,
    ) -> PaymentGatewayConfig | None:
        result = await session.execute(
            select(PaymentGatewayConfig).where(
                PaymentGatewayConfig.tenant_id == tenant_id,
                PaymentGatewayConfig.gateway == gateway,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def set_gateway_config(
        session: AsyncSession,
        tenant_id: str,
        gateway: str,
        is_active: bool = True,
        config: dict | None = None,
    ) -> PaymentGatewayConfig:
        existing = await BillingService.get_gateway_config(session, tenant_id, gateway)
        if existing:
            existing.is_active = is_active
            if config is not None:
                existing.config = config
            await session.flush()
            await session.refresh(existing)
            return existing
        cfg = PaymentGatewayConfig(
            tenant_id=tenant_id,
            gateway=gateway,
            is_active=is_active,
            config=config or {},
        )
        session.add(cfg)
        await session.flush()
        await session.refresh(cfg)
        return cfg

    @staticmethod
    async def list_gateway_configs(
        session: AsyncSession, tenant_id: str
    ) -> list[PaymentGatewayConfig]:
        result = await session.execute(
            select(PaymentGatewayConfig)
            .where(PaymentGatewayConfig.tenant_id == tenant_id)
            .order_by(PaymentGatewayConfig.gateway)
        )
        return list(result.scalars().all())

    @staticmethod
    async def delete_gateway_config(
        session: AsyncSession, config_id: str
    ) -> bool:
        result = await session.execute(
            select(PaymentGatewayConfig).where(PaymentGatewayConfig.id == config_id)
        )
        cfg = result.scalar_one_or_none()
        if cfg is None:
            return False
        await session.delete(cfg)
        await session.flush()
        return True
