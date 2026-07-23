'use client';

import { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import {
  Check,
  Zap,
  CreditCard,
  Shield,
  TrendingUp,
  Clock,
  Users,
  MessageSquare,
  Bot,
  BarChart3,
  Download,
  CheckCircle2,
  XCircle,
  Loader2,
  ArrowUpRight,
} from 'lucide-react';

/* ── Planos ── */

type PlanTier = 'free' | 'basic' | 'pro' | 'enterprise';

const plans = [
  {
    id: 'free' as PlanTier,
    name: 'Grátis',
    price: 'R$ 0',
    period: '/mês',
    description: 'Para testes e uso pessoal',
    features: [
      'Até 50 reclamações/mês',
      'WhatsApp básico',
      'Dashboard padrão',
      '1 agente IA',
    ],
    notIncluded: [
      'Automações avançadas',
      'Relatórios personalizados',
      'Múltiplos agentes',
      'Suporte prioritário',
      'API completa',
    ],
    highlighted: false,
    cta: 'Começar Grátis',
    current: true,
  },
  {
    id: 'basic' as PlanTier,
    name: 'Básico',
    price: 'R$ 97',
    period: '/mês',
    description: 'Para pequenas equipes e PMEs',
    features: [
      'Até 500 reclamações/mês',
      'WhatsApp + Email + SMS',
      'Dashboard completo',
      '3 agentes IA',
      'Automações básicas',
      'Relatórios semanais',
    ],
    notIncluded: [
      'API completa',
      'Múltiplos departamentos',
      'Suporte 24h',
    ],
    highlighted: false,
    cta: 'Assinar Básico',
  },
  {
    id: 'pro' as PlanTier,
    name: 'Profissional',
    price: 'R$ 297',
    period: '/mês',
    description: 'Para equipes em crescimento',
    features: [
      'Até 2.000 reclamações/mês',
      'WhatsApp + Email + SMS ilimitado',
      'Dashboard avançado + Analytics',
      'Agentes IA ilimitados',
      'Automações avançadas',
      'Relatórios personalizados',
      'API completa',
      'CRM integrado',
      'Múltiplos departamentos',
    ],
    notIncluded: [
      'Suporte 24h dedicado',
      'Onboarding personalizado',
    ],
    highlighted: true,
    cta: 'Assinar Profissional',
  },
  {
    id: 'enterprise' as PlanTier,
    name: 'Enterprise',
    price: 'R$ 997',
    period: '/mês',
    description: 'Para governos e grandes operações',
    features: [
      'Reclamações ilimitadas',
      'Todos os canais ilimitados',
      'Dashboard white-label',
      'Agentes IA ilimitados',
      'Automações customizadas',
      'Relatórios avançados',
      'API completa + Webhooks',
      'CRM + ERP integração',
      'Suporte 24h dedicado',
      'Onboarding personalizado',
      'SLA garantido',
      'Treinamento da equipe',
    ],
    notIncluded: [],
    highlighted: false,
    cta: 'Falar com Vendas',
  },
];

/* ─── Credit Packs ─── */

const creditPacks = [
  { amount: 500, price: 'R$ 19', popular: false },
  { amount: 2000, price: 'R$ 59', popular: true },
  { amount: 5000, price: 'R$ 129', popular: false },
  { amount: 15000, price: 'R$ 299', popular: false },
];

/* ─── Usage Summary ─── */
function getUsageStats(credits?: number) {
  return [
    { label: 'Créditos Restantes', value: (credits ?? 2450).toLocaleString("pt-BR"), icon: Zap, color: 'text-yellow-400', bg: 'bg-yellow-500/10' },
    { label: 'Mensagens Enviadas', value: '1.234', icon: MessageSquare, color: 'text-cyan-400', bg: 'bg-cyan-500/10' },
    { label: 'Agentes Ativos', value: '3', icon: Bot, color: 'text-purple-400', bg: 'bg-purple-500/10' },
    { label: 'Média Mensal', value: 'R$ 97', icon: TrendingUp, color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
  ];
}

/* ─── Invoices ─── */

const invoices = [
  { id: 'INV-2026-07', date: '15/07/2026', value: 'R$ 97,00', status: 'pago' as const, plan: 'Básico' },
  { id: 'INV-2026-06', date: '15/06/2026', value: 'R$ 97,00', status: 'pago' as const, plan: 'Básico' },
  { id: 'INV-2026-05', date: '15/05/2026', value: 'R$ 97,00', status: 'pago' as const, plan: 'Básico' },
];

type InvoiceStatus = 'pago' | 'pendente' | 'cancelado';

const invoiceStatusConfig: Record<InvoiceStatus, { label: string; color: string; bg: string }> = {
  pago: { label: 'Pago', color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
  pendente: { label: 'Pendente', color: 'text-yellow-400', bg: 'bg-yellow-500/10' },
  cancelado: { label: 'Cancelado', color: 'text-gray-400', bg: 'bg-gray-500/10' },
};

/* ─── Componentes ─── */

function ToggleSwitch({ enabled, onChange }: { enabled: boolean; onChange: () => void }) {
  return (
    <button
      type="button"
      onClick={onChange}
      className={`relative inline-flex h-5 w-9 items-center rounded-full transition-all ${
        enabled ? 'bg-emerald-500' : 'bg-gray-700'
      }`}
    >
      <span
        className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-all ${
          enabled ? 'translate-x-4' : 'translate-x-1'
        }`}
      />
    </button>
  );
}

/* ─── Page ─── */

export default function PlansPage() {
  const [selectedPlan, setSelectedPlan] = useState<PlanTier>('basic');
  const { user } = useAuth();
  const [autoTopup, setAutoTopup] = useState(false);
  const [loading, setLoading] = useState(false);

  const currentPlan = plans.find((p) => p.current);

  const handleSubscribe = async (planId: PlanTier) => {
    setLoading(true);
    // Mock: simulate API call
    await new Promise((r) => setTimeout(r, 1500));
    setLoading(false);
    setSelectedPlan(planId);
  };

  return (
    <div className="p-6 lg:p-8 space-y-8">
      {/* ── Header ── */}
      <div>
        <h1 className="text-2xl font-bold text-white">Planos & Faturamento</h1>
        <p className="text-sm text-gray-400 mt-1">
          Gerencie sua assinatura, créditos e faturas
        </p>
      </div>

      {/* ── Stats ── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {getUsageStats(user?.credits).map((stat) => (
          <div
            key={stat.label}
            className="bg-gray-900/60 border border-gray-800 rounded-xl p-4 hover:border-gray-700 transition-all"
          >
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-lg ${stat.bg}`}>
                <stat.icon className={`w-4 h-4 ${stat.color}`} />
              </div>
              <div>
                <p className="text-lg font-bold text-white">{stat.value}</p>
                <p className="text-xs text-gray-500">{stat.label}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* ── Current Plan Banner ── */}
      {currentPlan && (
        <div className="bg-gradient-to-r from-cyan-500/5 via-purple-500/5 to-cyan-500/5 border border-cyan-500/20 rounded-xl p-5">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-4">
              <div className="p-2 rounded-lg bg-cyan-500/10">
                <Zap className="w-5 h-5 text-cyan-400" />
              </div>
              <div>
                <p className="text-sm font-semibold text-white">
                  Plano Atual: {currentPlan.name}
                </p>
                <p className="text-xs text-gray-400 mt-0.5">
                  Próxima cobrança: 15/08/2026 — {currentPlan.price}{currentPlan.period}
                </p>
              </div>
            </div>
            <button className="px-4 py-2 bg-cyan-500/10 text-cyan-400 rounded-lg border border-cyan-500/20 text-sm font-medium hover:bg-cyan-500/20 transition-all">
              Gerenciar Assinatura
            </button>
          </div>
        </div>
      )}

      {/* ── Plan Cards ── */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {plans.map((plan) => (
          <div
            key={plan.id}
            className={`relative bg-gray-900/60 border rounded-xl p-5 transition-all ${
              plan.highlighted
                ? 'border-cyan-500/40 shadow-[0_0_20px_rgba(6,182,212,0.1)]'
                : 'border-gray-800 hover:border-gray-700'
            } ${plan.current ? 'ring-1 ring-cyan-500/30' : ''}`}
          >
            {plan.highlighted && (
              <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-0.5 bg-cyan-500 text-black text-[10px] font-bold rounded-full uppercase tracking-wider">
                Mais Popular
              </div>
            )}
            {plan.current && (
              <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-0.5 bg-emerald-500/20 text-emerald-400 text-[10px] font-bold rounded-full uppercase tracking-wider border border-emerald-500/30">
                Atual
              </div>
            )}

            <div className="mb-4">
              <h3 className="text-sm font-semibold text-white">{plan.name}</h3>
              <div className="mt-2">
                <span className="text-2xl font-bold text-white">{plan.price}</span>
                <span className="text-sm text-gray-500">{plan.period}</span>
              </div>
              <p className="text-xs text-gray-500 mt-1">{plan.description}</p>
            </div>

            <ul className="space-y-2 mb-4">
              {plan.features.map((f) => (
                <li key={f} className="flex items-start gap-2 text-xs text-gray-300">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                  {f}
                </li>
              ))}
              {plan.notIncluded.map((f) => (
                <li key={f} className="flex items-start gap-2 text-xs text-gray-600">
                  <XCircle className="w-3.5 h-3.5 text-gray-600 shrink-0 mt-0.5" />
                  {f}
                </li>
              ))}
            </ul>

            <button
              onClick={() => handleSubscribe(plan.id)}
              disabled={plan.current || loading}
              className={`w-full py-2 rounded-lg text-sm font-medium transition-all ${
                plan.current
                  ? 'bg-gray-800/50 text-gray-500 cursor-default'
                  : plan.highlighted
                  ? 'bg-cyan-500 text-black hover:bg-cyan-400'
                  : 'bg-gray-800/50 text-gray-300 hover:bg-gray-700/50 border border-gray-700'
              }`}
            >
              {plan.current ? 'Plano Atual' : plan.cta}
            </button>
          </div>
        ))}
      </div>

      {/* ── Créditos ── */}
      <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
            <CreditCard className="w-4 h-4 text-emerald-400" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-white">Créditos</h2>
            <p className="text-xs text-gray-500">Compre créditos para enviar mensagens adicionais</p>
          </div>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
          {creditPacks.map((pack) => (
            <button
              key={pack.amount}
              className={`relative p-4 rounded-xl border transition-all text-left ${
                pack.popular
                  ? 'border-emerald-500/40 bg-emerald-500/5'
                  : 'border-gray-800 bg-gray-800/20 hover:border-gray-700'
              }`}
            >
              {pack.popular && (
                <span className="text-[10px] text-emerald-400 font-semibold uppercase tracking-wider">
                  Melhor custo
                </span>
              )}
              <p className="text-lg font-bold text-white mt-1">{pack.amount.toLocaleString("pt-BR")}</p>
              <p className="text-xs text-gray-500">créditos</p>
              <div className="mt-2 flex items-center justify-between">
                <span className="text-sm font-semibold text-emerald-400">{pack.price}</span>
                <ArrowUpRight className="w-3.5 h-3.5 text-gray-500" />
              </div>
            </button>
          ))}
        </div>

        {/* Auto top-up */}
        <div className="flex items-center justify-between py-3 px-4 rounded-lg bg-gray-800/30 border border-gray-800">
          <div>
            <p className="text-sm font-medium text-white">Recarga Automática</p>
            <p className="text-xs text-gray-500 mt-0.5">
              {autoTopup
                ? 'Ativa — recarregar 2.000 créditos quando saldo estiver abaixo de 200'
                : 'Recarregue automaticamente quando o saldo estiver baixo'}
            </p>
          </div>
          <ToggleSwitch enabled={autoTopup} onChange={() => setAutoTopup(!autoTopup)} />
        </div>
      </div>

      {/* ── Faturas ── */}
      <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-blue-500/10 border border-blue-500/20">
              <BarChart3 className="w-4 h-4 text-blue-400" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-white">Histórico de Faturas</h2>
              <p className="text-xs text-gray-500">Últimos 3 meses</p>
            </div>
          </div>
          <button className="flex items-center gap-2 px-3 py-1.5 bg-gray-800/50 border border-gray-700 rounded-lg text-xs text-gray-400 hover:text-white transition-all">
            <Download className="w-3.5 h-3.5" />
            Todas as Faturas
          </button>
        </div>

        <div className="space-y-2">
          {invoices.map((inv) => {
            const st = invoiceStatusConfig[inv.status];
            return (
              <div
                key={inv.id}
                className="flex items-center justify-between py-3 px-4 rounded-lg bg-gray-800/20 border border-gray-800 hover:bg-gray-800/40 transition-all"
              >
                <div className="flex items-center gap-4">
                  <div>
                    <p className="text-sm font-medium text-white">{inv.id}</p>
                    <p className="text-xs text-gray-500">{inv.date}</p>
                  </div>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${st.bg} ${st.color}`}>
                    {st.label}
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-sm font-medium text-white">{inv.value}</span>
                  <span className="text-xs text-gray-500">{inv.plan}</span>
                  <button className="text-xs text-cyan-400 hover:text-cyan-300 transition-colors">
                    Download
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
