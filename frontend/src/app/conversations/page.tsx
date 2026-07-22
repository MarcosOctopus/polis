'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import {
  MessageSquare,
  CheckCircle2,
  Clock,
  Filter,
  Search,
  ArrowUpRight,
  AlertCircle,
  Play,
  XCircle,
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
} from 'recharts';

/* ───── Tipos ───── */

type StatusTab = 'todas' | 'ativas' | 'resolvidas' | 'pendentes';

type Conversation = {
  id: string;
  user: string;
  agent: string;
  status: 'ativa' | 'resolvida' | 'pendente';
  duration: string;
  messages: number;
  lastActivity: string;
};

/* ───── Mock data ───── */

const statusIcons: Record<Conversation['status'], typeof Clock> = {
  ativa: Play,
  resolvida: CheckCircle2,
  pendente: AlertCircle,
};

const statusColors: Record<Conversation['status'], string> = {
  ativa: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
  resolvida: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20',
  pendente: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
};

const allConversations: Conversation[] = [
  { id: 'CONV-001', user: 'Ana Silva', agent: 'Atendente Virtual', status: 'ativa', duration: '12m 34s', messages: 23, lastActivity: '2 min atrás' },
  { id: 'CONV-002', user: 'Carlos Oliveira', agent: 'Suporte Técnico', status: 'resolvida', duration: '8m 12s', messages: 15, lastActivity: '15 min atrás' },
  { id: 'CONV-003', user: 'Mariana Costa', agent: 'Vendas', status: 'ativa', duration: '25m 00s', messages: 42, lastActivity: '1 min atrás' },
  { id: 'CONV-004', user: 'Pedro Santos', agent: 'Atendente Virtual', status: 'pendente', duration: '3m 45s', messages: 7, lastActivity: '5 min atrás' },
  { id: 'CONV-005', user: 'Juliana Lima', agent: 'Suporte Técnico', status: 'resolvida', duration: '10m 20s', messages: 19, lastActivity: '30 min atrás' },
  { id: 'CONV-006', user: 'Rafael Almeida', agent: 'Vendas', status: 'resolvida', duration: '6m 18s', messages: 11, lastActivity: '1h atrás' },
  { id: 'CONV-007', user: 'Beatriz Rocha', agent: 'Atendente Virtual', status: 'ativa', duration: '18m 05s', messages: 31, lastActivity: 'agora' },
  { id: 'CONV-008', user: 'Lucas Pereira', agent: 'Suporte Técnico', status: 'pendente', duration: '1m 22s', messages: 3, lastActivity: '10 min atrás' },
  { id: 'CONV-009', user: 'Fernanda Dias', agent: 'Vendas', status: 'resolvida', duration: '15m 40s', messages: 27, lastActivity: '45 min atrás' },
  { id: 'CONV-010', user: 'Thiago Martins', agent: 'Atendente Virtual', status: 'ativa', duration: '7m 55s', messages: 14, lastActivity: '3 min atrás' },
  { id: 'CONV-011', user: 'Larissa Campos', agent: 'Suporte Técnico', status: 'resolvida', duration: '9m 30s', messages: 16, lastActivity: '2h atrás' },
  { id: 'CONV-012', user: 'Gabriel Nunes', agent: 'Vendas', status: 'pendente', duration: '4m 10s', messages: 8, lastActivity: '8 min atrás' },
];

const hourlyChartData = [
  { hora: '00h', conversas: 12 },
  { hora: '01h', conversas: 8 },
  { hora: '02h', conversas: 5 },
  { hora: '03h', conversas: 3 },
  { hora: '04h', conversas: 2 },
  { hora: '05h', conversas: 4 },
  { hora: '06h', conversas: 10 },
  { hora: '07h', conversas: 18 },
  { hora: '08h', conversas: 35 },
  { hora: '09h', conversas: 52 },
  { hora: '10h', conversas: 68 },
  { hora: '11h', conversas: 74 },
  { hora: '12h', conversas: 61 },
  { hora: '13h', conversas: 55 },
  { hora: '14h', conversas: 70 },
  { hora: '15h', conversas: 82 },
  { hora: '16h', conversas: 91 },
  { hora: '17h', conversas: 85 },
  { hora: '18h', conversas: 72 },
  { hora: '19h', conversas: 58 },
  { hora: '20h', conversas: 45 },
  { hora: '21h', conversas: 38 },
  { hora: '22h', conversas: 25 },
  { hora: '23h', conversas: 18 },
];

/* ───── Stats ───── */

const statsCards = [
  { label: 'Total', value: '1,247', icon: MessageSquare, color: 'text-cyan-400', bg: 'bg-cyan-500/10', border: 'border-cyan-500/20' },
  { label: 'Ativas Hoje', value: '89', icon: Play, color: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/20' },
  { label: 'Resolvidas', value: '1,158', icon: CheckCircle2, color: 'text-blue-400', bg: 'bg-blue-500/10', border: 'border-blue-500/20' },
  { label: 'Média de Mensagens', value: '12.5', icon: Clock, color: 'text-purple-400', bg: 'bg-purple-500/10', border: 'border-purple-500/20' },
];

/* ───── Componente de loading ───── */

function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center h-full">
      <div className="flex flex-col items-center gap-3">
        <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
        <p className="text-sm text-gray-400">Carregando...</p>
      </div>
    </div>
  );
}

/* ───── Página principal ───── */

export default function ConversationsPage() {
  const { isAuthenticated, loading } = useAuth();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'todas' | 'ativa' | 'resolvida' | 'pendente'>('todas');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/login');
    }
  }, [loading, isAuthenticated, router]);

  if (loading) return <LoadingSpinner />;
  if (!isAuthenticated) return null;

  /* ───── Tabs ───── */
  const tabs: { key: typeof activeTab; label: string }[] = [
    { key: 'todas', label: 'Todas' },
    { key: 'ativa', label: 'Ativas' },
    { key: 'resolvida', label: 'Resolvidas' },
    { key: 'pendente', label: 'Pendentes' },
  ];

  /* ───── Filtro + busca ───── */
  const filtered = allConversations.filter((c) => {
    if (activeTab !== 'todas' && c.status !== activeTab) return false;
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      c.id.toLowerCase().includes(q) ||
      c.user.toLowerCase().includes(q) ||
      c.agent.toLowerCase().includes(q)
    );
  });

  return (
    <div className="p-6 lg:p-8 space-y-8">
      {/* ─── Cabeçalho ─── */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Conversas</h1>
          <p className="text-sm text-gray-400 mt-1">
            Gerencie e monitore todas as conversas da plataforma
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-cyan-500/10 text-cyan-400 rounded-lg border border-cyan-500/20 hover:bg-cyan-500/20 transition-all text-sm font-medium">
          <MessageSquare className="w-4 h-4" />
          Nova Conversa
        </button>
      </div>

      {/* ─── Cards de Estatísticas ─── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statsCards.map((s) => {
          const Icon = s.icon;
          return (
            <div
              key={s.label}
              className={`${s.bg} ${s.border} border rounded-xl p-5 flex items-center gap-4`}
            >
              <div className={`${s.color} ${s.bg} p-3 rounded-lg`}>
                <Icon className="w-5 h-5" />
              </div>
              <div>
                <p className="text-2xl font-bold text-white">{s.value}</p>
                <p className="text-xs text-gray-400">{s.label}</p>
              </div>
            </div>
          );
        })}
      </div>

      {/* ─── Gráfico de Conversas por Hora (24h) ─── */}
      <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-sm font-semibold text-white">
            Conversas por Hora
          </h2>
          <span className="text-xs text-gray-500">Últimas 24 horas</span>
        </div>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={hourlyChartData}>
              <defs>
                <linearGradient id="lineConversas" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.25} />
                  <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
              <XAxis
                dataKey="hora"
                stroke="#6b7280"
                fontSize={11}
                tickLine={false}
                interval={2}
              />
              <YAxis stroke="#6b7280" fontSize={12} tickLine={false} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#111827',
                  border: '1px solid #1f2937',
                  borderRadius: '8px',
                  color: '#e4e4e7',
                  fontSize: 13,
                }}
                labelStyle={{ color: '#9ca3af' }}
              />
              <Area
                type="monotone"
                dataKey="conversas"
                stroke="none"
                fill="url(#lineConversas)"
              />
              <Line
                type="monotone"
                dataKey="conversas"
                stroke="#06b6d4"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4, fill: '#06b6d4', stroke: '#0a0a0f', strokeWidth: 2 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* ─── Tabela de Conversas ─── */}
      <div className="bg-gray-900/60 border border-gray-800 rounded-xl overflow-hidden">
        {/* Filtros e Busca */}
        <div className="p-4 border-b border-gray-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          {/* Tabs de Status */}
          <div className="flex gap-1 bg-gray-800/50 rounded-lg p-1">
            {tabs.map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all ${
                  activeTab === tab.key
                    ? 'bg-cyan-500/20 text-cyan-400 shadow-sm'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Busca */}
          <div className="relative w-full sm:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input
              type="text"
              placeholder="Buscar por ID, usuário ou agente..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-gray-800/50 border border-gray-700 rounded-lg text-white text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/40 focus:border-cyan-500/50 transition-all"
            />
          </div>
        </div>

        {/* Tabela */}
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-800 text-gray-500 text-xs uppercase tracking-wider">
                <th className="text-left px-6 py-3 font-medium">ID</th>
                <th className="text-left px-6 py-3 font-medium">Usuário</th>
                <th className="text-left px-6 py-3 font-medium">Agente</th>
                <th className="text-left px-6 py-3 font-medium">Status</th>
                <th className="text-left px-6 py-3 font-medium">Duração</th>
                <th className="text-left px-6 py-3 font-medium">Mensagens</th>
                <th className="text-left px-6 py-3 font-medium">Última Atividade</th>
                <th className="text-right px-6 py-3 font-medium" />
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60">
              {filtered.map((conv) => {
                const StatusIcon = statusIcons[conv.status];
                return (
                  <tr
                    key={conv.id}
                    className="hover:bg-gray-800/30 transition-colors group"
                  >
                    <td className="px-6 py-4 font-mono text-xs text-cyan-400">
                      {conv.id}
                    </td>
                    <td className="px-6 py-4 text-white font-medium">
                      {conv.user}
                    </td>
                    <td className="px-6 py-4 text-gray-300">{conv.agent}</td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${statusColors[conv.status]}`}
                      >
                        <StatusIcon className="w-3 h-3" />
                        {conv.status.charAt(0).toUpperCase() + conv.status.slice(1)}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-gray-400">{conv.duration}</td>
                    <td className="px-6 py-4 text-gray-400">{conv.messages}</td>
                    <td className="px-6 py-4 text-gray-400">
                      {conv.lastActivity}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button className="opacity-0 group-hover:opacity-100 text-gray-500 hover:text-cyan-400 transition-all">
                        <ArrowUpRight className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>

          {filtered.length === 0 && (
            <div className="flex flex-col items-center py-16 text-gray-500">
              <MessageSquare className="w-10 h-10 mb-3 opacity-40" />
              <p className="text-sm">Nenhuma conversa encontrada</p>
            </div>
          )}
        </div>

        {/* Rodapé da tabela */}
        <div className="px-6 py-3 border-t border-gray-800 flex items-center justify-between text-xs text-gray-500">
          <span>
            Exibindo {filtered.length} de {allConversations.length} conversas
          </span>
          <div className="flex items-center gap-2">
            <Filter className="w-3.5 h-3.5" />
            <span>Filtros aplicados: {activeTab !== 'todas' ? `Status: ${activeTab}` : 'Nenhum'}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
