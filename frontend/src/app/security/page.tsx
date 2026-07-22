'use client';

import {
  Shield,
  ShieldCheck,
  ShieldAlert,
  Ban,
  LogOut,
  Lock,
  Eye,
  Server,
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

// ── Mock Data ──────────────────────────────────────────────

const statsCards = [
  {
    title: 'Ameaças Bloqueadas',
    value: '2,847',
    icon: ShieldAlert,
    change: '+12% este mês',
    changeType: 'positive' as const,
  },
  {
    title: 'IPs Blacklist',
    value: '143',
    icon: Ban,
    change: '+8 novos hoje',
    changeType: 'positive' as const,
  },
  {
    title: 'Tentativas de Login',
    value: '486',
    icon: LogOut,
    change: '42 suspeitas',
    changeType: 'warning' as const,
  },
  {
    title: 'Sessões Ativas',
    value: '12',
    icon: Eye,
    change: '3 admin / 9 usuários',
    changeType: 'info' as const,
  },
];

const accessChartData = [
  { dia: 'Seg', tentativas: 42, bloqueadas: 38 },
  { dia: 'Ter', tentativas: 58, bloqueadas: 52 },
  { dia: 'Qua', tentativas: 35, bloqueadas: 30 },
  { dia: 'Qui', tentativas: 71, bloqueadas: 65 },
  { dia: 'Sex', tentativas: 63, bloqueadas: 58 },
  { dia: 'Sáb', tentativas: 28, bloqueadas: 24 },
  { dia: 'Dom', tentativas: 31, bloqueadas: 27 },
];

interface AuditLog {
  id: number;
  timestamp: string;
  usuario: string;
  acao: string;
  ip: string;
  status: 'permitido' | 'bloqueado' | 'pendente';
}

const auditLogs: AuditLog[] = [
  { id: 1, timestamp: '2026-07-22 09:23:14', usuario: 'admin@polis.io', acao: 'Login SSH', ip: '192.168.1.42', status: 'permitido' },
  { id: 2, timestamp: '2026-07-22 09:15:02', usuario: '—', acao: 'Tentativa de força bruta', ip: '45.33.32.156', status: 'bloqueado' },
  { id: 3, timestamp: '2026-07-22 08:55:47', usuario: 'dev@polis.io', acao: 'Alteração de regra FW', ip: '10.0.0.15', status: 'pendente' },
  { id: 4, timestamp: '2026-07-22 08:30:00', usuario: '—', acao: 'Scan de porta detectado', ip: '185.220.101.23', status: 'bloqueado' },
  { id: 5, timestamp: '2026-07-22 08:12:33', usuario: 'ops@polis.io', acao: 'Acesso ao painel admin', ip: '10.0.0.8', status: 'permitido' },
  { id: 6, timestamp: '2026-07-22 07:45:18', usuario: '—', acao: 'SQL Injection attempt', ip: '103.235.46.88', status: 'bloqueado' },
  { id: 7, timestamp: '2026-07-22 07:20:55', usuario: 'user@exemplo.com', acao: 'Troca de senha', ip: '177.54.32.10', status: 'permitido' },
  { id: 8, timestamp: '2026-07-22 06:58:01', usuario: '—', acao: 'Acesso a endpoint proibido', ip: '91.121.87.200', status: 'bloqueado' },
];

interface StatusCard {
  title: string;
  label: string;
  icon: React.ElementType;
  badge: string;
  extra: string;
  color: string;
}

const statusCards: StatusCard[] = [
  {
    title: 'Firewall',
    label: 'Ativo ✅',
    icon: Shield,
    badge: '847 regras',
    extra: 'Bloqueando tráfego malicioso',
    color: 'emerald',
  },
  {
    title: '2FA',
    label: 'Habilitado 🔐',
    icon: Lock,
    badge: '92% adesão',
    extra: 'Autenticação em dois fatores',
    color: 'cyan',
  },
  {
    title: 'Criptografia',
    label: 'AES-256 🔒',
    icon: ShieldCheck,
    badge: 'Em repouso e trânsito',
    extra: 'Padrão militar',
    color: 'violet',
  },
  {
    title: 'Backup',
    label: 'Rodando 💾',
    icon: Server,
    badge: 'Último: há 2h',
    extra: 'Backup incremental diário',
    color: 'amber',
  },
];

const statusColorMap: Record<string, { bg: string; border: string; text: string; icon: string }> = {
  emerald: {
    bg: 'bg-emerald-500/10',
    border: 'border-emerald-500/20',
    text: 'text-emerald-400',
    icon: '#34d399',
  },
  cyan: {
    bg: 'bg-cyan-500/10',
    border: 'border-cyan-500/20',
    text: 'text-cyan-400',
    icon: '#22d3ee',
  },
  violet: {
    bg: 'bg-violet-500/10',
    border: 'border-violet-500/20',
    text: 'text-violet-400',
    icon: '#a78bfa',
  },
  amber: {
    bg: 'bg-amber-500/10',
    border: 'border-amber-500/20',
    text: 'text-amber-400',
    icon: '#fbbf24',
  },
};

const statusConfig = {
  permitido: {
    label: 'Permitido',
    badge: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  },
  bloqueado: {
    label: 'Bloqueado',
    badge: 'bg-red-500/10 text-red-400 border-red-500/20',
  },
  pendente: {
    label: 'Pendente',
    badge: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
  },
};

const changeStyles = {
  positive: 'text-emerald-400',
  warning: 'text-yellow-400',
  negative: 'text-red-400',
  info: 'text-gray-400',
} as const;

// ── Component ──────────────────────────────────────────────

export default function Security() {
  return (
    <div className="p-6 lg:p-8 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Segurança</h1>
          <p className="text-sm text-gray-400 mt-1">
            Postura de segurança e auditoria da plataforma Polis
          </p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 bg-cyan-500/10 text-cyan-400 rounded-lg border border-cyan-500/20 text-xs font-medium">
          <ShieldCheck className="w-4 h-4" />
          Sistema protegido
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statsCards.map((card) => (
          <div
            key={card.title}
            className="bg-gray-900/60 border border-gray-800 rounded-xl p-5 hover:border-gray-700 transition-all"
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-medium text-gray-400 uppercase tracking-wider">
                {card.title}
              </span>
              <card.icon className="w-4 h-4 text-cyan-400" />
            </div>
            <p className="text-2xl font-bold text-white">{card.value}</p>
            <p className={`text-xs mt-1 ${changeStyles[card.changeType]}`}>
              {card.change}
            </p>
          </div>
        ))}
      </div>

      {/* Access Attempts Chart + Status Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Access Attempts Area Chart — 7 days */}
        <div className="lg:col-span-2 bg-gray-900/60 border border-gray-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-sm font-semibold text-white">
              Tentativas de Acesso — Últimos 7 Dias
            </h2>
            <span className="text-xs text-gray-500">
              Total: {accessChartData.reduce((s, d) => s + d.tentativas, 0)} tentativas
            </span>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={accessChartData}>
                <defs>
                  <linearGradient
                    id="gradientTentativas"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1"
                  >
                    <stop offset="0%" stopColor="#f43f5e" stopOpacity={0.35} />
                    <stop offset="100%" stopColor="#f43f5e" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient
                    id="gradientBloqueadas"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1"
                  >
                    <stop offset="0%" stopColor="#06b6d4" stopOpacity={0.25} />
                    <stop offset="100%" stopColor="#06b6d4" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                <XAxis
                  dataKey="dia"
                  stroke="#6b7280"
                  fontSize={11}
                  tickLine={false}
                />
                <YAxis
                  stroke="#6b7280"
                  fontSize={11}
                  tickLine={false}
                  domain={[0, 'dataMax + 10']}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#111827',
                    border: '1px solid #1f2937',
                    borderRadius: '8px',
                    color: '#e4e4e7',
                    fontSize: '13px',
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="tentativas"
                  stroke="#f43f5e"
                  strokeWidth={2}
                  fill="url(#gradientTentativas)"
                  dot={false}
                  activeDot={{
                    r: 4,
                    fill: '#f43f5e',
                    stroke: '#0a0a0f',
                    strokeWidth: 2,
                  }}
                  name="Tentativas"
                />
                <Area
                  type="monotone"
                  dataKey="bloqueadas"
                  stroke="#06b6d4"
                  strokeWidth={2}
                  fill="url(#gradientBloqueadas)"
                  dot={false}
                  activeDot={{
                    r: 4,
                    fill: '#06b6d4',
                    stroke: '#0a0a0f',
                    strokeWidth: 2,
                  }}
                  name="Bloqueadas"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Status Cards */}
        <div className="space-y-3">
          {statusCards.map((card) => {
            const colors = statusColorMap[card.color];
            return (
              <div
                key={card.title}
                className={`${colors.bg} ${colors.border} border rounded-xl p-4 hover:brightness-110 transition-all`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <card.icon
                      className="w-5 h-5"
                      style={{ color: colors.icon }}
                    />
                    <span className="text-sm font-semibold text-white">
                      {card.title}
                    </span>
                  </div>
                  <span
                    className={`text-xs px-2 py-0.5 rounded-full border font-medium ${colors.text} ${colors.bg} ${colors.border}`}
                  >
                    {card.badge}
                  </span>
                </div>
                <p className={`text-sm font-medium ${colors.text}`}>
                  {card.label}
                </p>
                <p className="text-xs text-gray-500 mt-1">{card.extra}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <h2 className="text-sm font-semibold text-white">
              Logs de Auditoria
            </h2>
            <span className="text-xs text-gray-500">Tempo real</span>
          </div>
          <button className="text-xs text-cyan-400 hover:text-cyan-300 transition-colors">
            Exportar logs
          </button>
        </div>

        {/* Table header */}
        <div className="hidden sm:grid grid-cols-5 gap-4 px-4 py-2 text-xs font-medium text-gray-500 uppercase tracking-wider border-b border-gray-800">
          <span>Timestamp</span>
          <span>Usuário</span>
          <span>Ação</span>
          <span>IP</span>
          <span className="text-right">Status</span>
        </div>

        <div className="divide-y divide-gray-800">
          {auditLogs.map((log) => {
            const st = statusConfig[log.status];
            return (
              <div
                key={log.id}
                className="grid grid-cols-1 sm:grid-cols-5 gap-2 sm:gap-4 px-4 py-4 hover:bg-gray-800/30 transition-colors rounded-lg"
              >
                {/* Mobile: inline layout */}
                <div className="flex items-center gap-2 sm:contents">
                  <span className="text-xs text-gray-400 font-mono shrink-0">
                    {log.timestamp}
                  </span>
                </div>
                <span
                  className={`text-sm truncate ${
                    log.usuario === '—' ? 'text-gray-500' : 'text-gray-200'
                  }`}
                >
                  {log.usuario}
                </span>
                <span className="text-sm text-gray-300">{log.acao}</span>
                <span className="text-sm font-mono text-gray-400">
                  {log.ip}
                </span>
                <div className="flex items-center justify-end">
                  <span
                    className={`text-xs px-2 py-0.5 rounded-full border font-medium ${st.badge}`}
                  >
                    {st.label}
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        {auditLogs.length === 0 && (
          <div className="flex flex-col items-center py-12 text-gray-500">
            <ShieldCheck className="w-10 h-10 mb-3 text-emerald-400" />
            <p className="text-sm">Nenhum log de auditoria</p>
            <p className="text-xs">Todas as atividades estão limpas</p>
          </div>
        )}
      </div>
    </div>
  );
}
