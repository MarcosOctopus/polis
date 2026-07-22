'use client';

import { useState } from 'react';
import {
  Bot,
  Wifi,
  WifiOff,
  AlertTriangle,
  Plus,
  PieChart,
  Activity,
} from 'lucide-react';
import {
  PieChart as RePieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';

// ── Agent type ──────────────────────────────────────────────────────────────
type AgentStatus = 'online' | 'offline' | 'busy' | 'error';

interface Agent {
  id: number;
  name: string;
  status: AgentStatus;
  model: string;
  successRate: number;
  lastActivity: string;
  conversations: number;
}

// ── Mock data ────────────────────────────────────────────────────────────────
const agents: Agent[] = [
  { id: 1,  name: 'Athena AI',        status: 'online',  model: 'GPT-4o',      successRate: 98.2, lastActivity: '2 min atrás',   conversations: 1247 },
  { id: 2,  name: 'Hermes Assist',    status: 'online',  model: 'Claude 4',    successRate: 97.5, lastActivity: '5 min atrás',   conversations: 982  },
  { id: 3,  name: 'Nova Chat',        status: 'busy',    model: 'Gemini 2.0',  successRate: 94.8, lastActivity: '1 min atrás',   conversations: 2103 },
  { id: 4,  name: 'Apollo Suporte',   status: 'online',  model: 'GPT-4o',      successRate: 96.1, lastActivity: '12 min atrás',  conversations: 567  },
  { id: 5,  name: 'Ícaro Vendas',     status: 'offline', model: 'Claude 4',    successRate: 91.3, lastActivity: '2h atrás',      conversations: 324  },
  { id: 6,  name: 'Selene IA',        status: 'online',  model: 'Llama 3.1',   successRate: 95.0, lastActivity: '8 min atrás',   conversations: 741  },
  { id: 7,  name: 'Odin Analytics',   status: 'busy',    model: 'Gemini 2.0',  successRate: 93.7, lastActivity: '3 min atrás',   conversations: 1596 },
  { id: 8,  name: 'Freya Creative',   status: 'online',  model: 'GPT-4o',      successRate: 99.0, lastActivity: '6 min atrás',   conversations: 412  },
  { id: 9,  name: 'Thor DevBot',      status: 'offline', model: 'Claude 4',    successRate: 88.4, lastActivity: '5h atrás',      conversations: 89   },
  { id: 10, name: 'Aurora Sugestora', status: 'online',  model: 'Llama 3.1',   successRate: 96.8, lastActivity: '10 min atrás',  conversations: 1153 },
  { id: 11, name: 'Orion Suporte T2', status: 'busy',    model: 'GPT-4o',    successRate: 78.2, lastActivity: '30 min atrás', conversations: 203  },
  { id: 12, name: 'Luna Tradutora',   status: 'online',  model: 'Gemini 2.0',  successRate: 97.9, lastActivity: '4 min atrás',   conversations: 2889 },
  { id: 13, name: 'Cronos Agenda',    status: 'offline', model: 'Claude 4',    successRate: 92.1, lastActivity: '1d atrás',      conversations: 456  },
  { id: 14, name: 'Eros RH',          status: 'online',  model: 'Llama 3.1',   successRate: 94.5, lastActivity: '15 min atrás',  conversations: 678  },
  { id: 15, name: 'Hades QA',         status: 'error',   model: 'GPT-4o',    successRate: 72.0, lastActivity: '45 min atrás', conversations: 134  },
  { id: 16, name: 'Héstia Admin',     status: 'online',  model: 'Gemini 2.0',  successRate: 99.2, lastActivity: '1 min atrás',   conversations: 4567 },
  { id: 17, name: 'Ares Estratégia',  status: 'busy',    model: 'Claude 4',    successRate: 95.6, lastActivity: '7 min atrás',   conversations: 891  },
  { id: 18, name: 'Deméter Produto',  status: 'online',  model: 'Llama 3.1',   successRate: 93.0, lastActivity: '20 min atrás',  conversations: 512  },
  { id: 19, name: 'Perséfone Jurídico', status: 'offline', model: 'GPT-4o',    successRate: 90.8, lastActivity: '3h atrás',      conversations: 267  },
  { id: 20, name: 'Hefesto Builder',  status: 'online',  model: 'Claude 4',    successRate: 97.1, lastActivity: '9 min atrás',   conversations: 1789 },
  { id: 21, name: 'Tália Social',     status: 'busy',    model: 'Gemini 2.0',  successRate: 93.4, lastActivity: '11 min atrás',  conversations: 2234 },
  { id: 22, name: 'Nêmesis Segurança',status: 'online',  model: 'Llama 3.1',   successRate: 98.8, lastActivity: '2 min atrás',   conversations: 345  },
  { id: 23, name: 'Harmonia Análise', status: 'offline', model: 'Claude 4',    successRate: 89.5, lastActivity: '8h atrás',      conversations: 178  },
  { id: 24, name: 'Ártemis Pesquisa', status: 'error',   model: 'Gemini 2.0',  successRate: 65.3, lastActivity: '1h atrás',      conversations: 91   },
];

const cleanAgents = agents;

// Compute stats
const total = 24;
const active = cleanAgents.filter((a) => a.status === 'online').length;
const inactive = cleanAgents.filter((a) => a.status === 'offline').length;
const error = cleanAgents.filter((a) => a.status === 'error').length;

// Model distribution
const modelCounts = cleanAgents.reduce<Record<string, number>>((acc, a) => {
  acc[a.model] = (acc[a.model] || 0) + 1;
  return acc;
}, {});

const modelPieData = Object.entries(modelCounts).map(([name, value]) => ({
  name,
  value,
}));

const PIE_COLORS = ['#06b6d4', '#8b5cf6', '#f59e0b', '#10b981'];

// ── Helpers ─────────────────────────────────────────────────────────────────
function getInitials(name: string) {
  return name
    .split(' ')
    .map((w) => w[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();
}

function getStatusConfig(status: AgentStatus | 'error') {
  switch (status) {
    case 'online':
      return { icon: Wifi, label: 'Online', color: 'text-emerald-400', bg: 'bg-emerald-500/10', dot: 'bg-emerald-400' };
    case 'offline':
      return { icon: WifiOff, label: 'Offline', color: 'text-gray-500', bg: 'bg-gray-500/10', dot: 'bg-gray-500' };
    case 'busy':
      return { icon: Activity, label: 'Ocupado', color: 'text-yellow-400', bg: 'bg-yellow-500/10', dot: 'bg-yellow-400' };
    case 'error':
      return { icon: AlertTriangle, label: 'Erro', color: 'text-red-400', bg: 'bg-red-500/10', dot: 'bg-red-400' };
  }
}

function getGradient(name: string) {
  const gradients: Record<string, string> = {
    'Athena AI':        'from-cyan-400 to-blue-500',
    'Hermes Assist':    'from-purple-400 to-pink-500',
    'Nova Chat':        'from-emerald-400 to-teal-500',
    'Apollo Suporte':   'from-sky-400 to-indigo-500',
    'Ícaro Vendas':     'from-orange-400 to-red-500',
    'Selene IA':        'from-violet-400 to-purple-500',
    'Odin Analytics':   'from-amber-400 to-yellow-500',
    'Freya Creative':   'from-pink-400 to-rose-500',
    'Thor DevBot':      'from-gray-400 to-gray-600',
    'Aurora Sugestora': 'from-cyan-400 to-teal-500',
    'Luna Tradutora':   'from-indigo-400 to-violet-500',
    'Cronos Agenda':    'from-slate-400 to-gray-500',
  };
  return gradients[name] || 'from-cyan-400 to-purple-500';
}

// ── Component ────────────────────────────────────────────────────────────────
export default function AgentsPage() {
  const [search, setSearch] = useState('');

  const filtered = cleanAgents.filter((a) =>
    a.name.toLowerCase().includes(search.toLowerCase())
  );

  const onlineCount = filtered.filter((a) => a.status === 'online').length;
  const offlineCount = filtered.filter((a) => a.status === 'offline').length;
  const busyCount = filtered.filter((a) => a.status === 'busy').length;
  const errorCount = filtered.filter((a) => a.status === 'error').length;

  return (
    <div className="p-6 lg:p-8 space-y-8">
      {/* ── Header ──────────────────────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Agentes</h1>
          <p className="text-sm text-gray-400 mt-1">
            Gerencie seus agentes de IA
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-cyan-500/10 text-cyan-400 rounded-lg border border-cyan-500/20 hover:bg-cyan-500/20 transition-all text-sm font-medium">
          <Plus className="w-4 h-4" />
          Criar Agente
        </button>
      </div>

      {/* ── Stats bar ───────────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-4 flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-cyan-500/10 text-cyan-400">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <p className="text-2xl font-bold text-white">{total}</p>
            <p className="text-xs text-gray-400">Total</p>
          </div>
        </div>
        <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-4 flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-emerald-500/10 text-emerald-400">
            <Wifi className="w-5 h-5" />
          </div>
          <div>
            <p className="text-2xl font-bold text-white">{active}</p>
            <p className="text-xs text-gray-400">Ativos</p>
          </div>
        </div>
        <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-4 flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-gray-500/10 text-gray-400">
            <WifiOff className="w-5 h-5" />
          </div>
          <div>
            <p className="text-2xl font-bold text-white">{inactive}</p>
            <p className="text-xs text-gray-400">Inativos</p>
          </div>
        </div>
        <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-4 flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-red-500/10 text-red-400">
            <AlertTriangle className="w-5 h-5" />
          </div>
          <div>
            <p className="text-2xl font-bold text-white">{error}</p>
            <p className="text-xs text-gray-400">Com erro</p>
          </div>
        </div>
      </div>

      {/* ── Charts + Search row ─────────────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Pie chart */}
        <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-6">
          <div className="flex items-center gap-2 mb-4">
            <PieChart className="w-4 h-4 text-cyan-400" />
            <h2 className="text-sm font-semibold text-white">
              Distribuição por Modelo
            </h2>
          </div>
          <div className="h-52">
            <ResponsiveContainer width="100%" height="100%">
              <RePieChart>
                <Pie
                  data={modelPieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {modelPieData.map((_, i) => (
                    <Cell
                      key={i}
                      fill={PIE_COLORS[i % PIE_COLORS.length]}
                      stroke="none"
                    />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#111827',
                    border: '1px solid #1f2937',
                    borderRadius: '8px',
                    color: '#e4e4e7',
                    fontSize: 12,
                  }}
                />
              </RePieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex flex-wrap justify-center gap-4 mt-2 text-xs">
            {modelPieData.map((d, i) => (
              <div key={d.name} className="flex items-center gap-1.5">
                <span
                  className="w-2.5 h-2.5 rounded-full"
                  style={{ backgroundColor: PIE_COLORS[i % PIE_COLORS.length] }}
                />
                <span className="text-gray-300">{d.name}</span>
                <span className="text-gray-500">{d.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Status summary */}
        <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-6 lg:col-span-2">
          <div className="flex items-center gap-2 mb-4">
            <Activity className="w-4 h-4 text-cyan-400" />
            <h2 className="text-sm font-semibold text-white">
              Resumo de Status
            </h2>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {[
              { label: 'Online',  count: onlineCount, color: 'text-emerald-400', bar: 'bg-emerald-400', pct: total ? Math.round((onlineCount / total) * 100) : 0 },
              { label: 'Ocupado', count: busyCount,  color: 'text-yellow-400',  bar: 'bg-yellow-400',  pct: total ? Math.round((busyCount / total) * 100) : 0 },
              { label: 'Offline', count: offlineCount, color: 'text-gray-400',  bar: 'bg-gray-500',    pct: total ? Math.round((offlineCount / total) * 100) : 0 },
              { label: 'Erro',    count: errorCount,  color: 'text-red-400',    bar: 'bg-red-400',      pct: total ? Math.round((errorCount / total) * 100) : 0 },
            ].map((s) => (
              <div key={s.label} className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className={s.color}>{s.label}</span>
                  <span className="text-gray-500">{s.count} agentes</span>
                </div>
                <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${s.bar}`}
                    style={{ width: `${s.pct}%` }}
                  />
                </div>
                <p className="text-right text-xs text-gray-600">{s.pct}%</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Search ──────────────────────────────────────────────────────── */}
      <div className="relative max-w-xs">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Buscar agente..."
          className="w-full px-4 py-2 bg-gray-800/50 border border-gray-700 rounded-lg text-white placeholder-gray-500 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/40 focus:border-cyan-500/50 transition-all"
        />
      </div>

      {/* ── Agent Grid ──────────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {filtered.map((agent) => {
          const statusCfg = getStatusConfig(agent.status);
          const StatusIcon = statusCfg.icon;
          return (
            <div
              key={agent.id}
              className="bg-gray-900/60 border border-gray-800 rounded-xl p-5 hover:border-gray-700 transition-all group"
            >
              {/* Avatar + status */}
              <div className="flex items-start justify-between mb-4">
                <div
                  className={`w-11 h-11 rounded-xl bg-gradient-to-br ${getGradient(agent.name)} flex items-center justify-center text-white font-bold text-sm shadow-lg`}
                >
                  {getInitials(agent.name)}
                </div>
                <span
                  className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium ${statusCfg.bg} ${statusCfg.color}`}
                >
                  <span className={`w-1.5 h-1.5 rounded-full ${statusCfg.dot}`} />
                  {statusCfg.label}
                </span>
              </div>

              {/* Name + model */}
              <h3 className="text-sm font-semibold text-white mb-1 group-hover:text-cyan-400 transition-colors">
                {agent.name}
              </h3>
              <p className="text-xs text-gray-500 mb-4">{agent.model}</p>

              {/* Stats */}
              <div className="grid grid-cols-2 gap-3 pt-3 border-t border-gray-800">
                <div>
                  <p className="text-[11px] text-gray-500 mb-0.5">Sucesso</p>
                  <p className="text-sm font-semibold text-emerald-400">
                    {agent.successRate}%
                  </p>
                </div>
                <div>
                  <p className="text-[11px] text-gray-500 mb-0.5">Atividade</p>
                  <p className="text-xs text-gray-400 truncate">
                    {agent.lastActivity}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {filtered.length === 0 && (
        <div className="text-center py-16">
          <Bot className="w-12 h-12 text-gray-700 mx-auto mb-3" />
          <p className="text-sm text-gray-500">Nenhum agente encontrado</p>
        </div>
      )}
    </div>
  );
}
