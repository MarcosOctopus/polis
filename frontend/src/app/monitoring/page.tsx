'use client';

import { useState } from 'react';
import {
  Activity,
  Zap,
  Clock,
  AlertTriangle,
  CheckCircle,
  XCircle,
  ArrowUpRight,
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

const kpiCards = [
  {
    title: 'Uptime',
    value: '99.97%',
    icon: Activity,
    change: 'Últimos 30 dias',
    changeType: 'positive' as const,
  },
  {
    title: 'Latência Média',
    value: '42ms',
    icon: Clock,
    change: '-8ms vs ontem',
    changeType: 'positive' as const,
  },
  {
    title: 'Requests/min',
    value: '1,247',
    icon: Zap,
    change: '+18.3% vs ontem',
    changeType: 'positive' as const,
  },
  {
    title: 'Taxa de Erro',
    value: '0.03%',
    icon: AlertTriangle,
    change: '-0.01% melhoria',
    changeType: 'positive' as const,
  },
];

const latencyData = [
  { hora: '00:00', latencia: 38 },
  { hora: '01:00', latencia: 35 },
  { hora: '02:00', latencia: 33 },
  { hora: '03:00', latencia: 31 },
  { hora: '04:00', latencia: 30 },
  { hora: '05:00', latencia: 34 },
  { hora: '06:00', latencia: 42 },
  { hora: '07:00', latencia: 48 },
  { hora: '08:00', latencia: 55 },
  { hora: '09:00', latencia: 62 },
  { hora: '10:00', latencia: 65 },
  { hora: '11:00', latencia: 68 },
  { hora: '12:00', latencia: 64 },
  { hora: '13:00', latencia: 60 },
  { hora: '14:00', latencia: 58 },
  { hora: '15:00', latencia: 56 },
  { hora: '16:00', latencia: 59 },
  { hora: '17:00', latencia: 63 },
  { hora: '18:00', latencia: 61 },
  { hora: '19:00', latencia: 52 },
  { hora: '20:00', latencia: 46 },
  { hora: '21:00', latencia: 42 },
  { hora: '22:00', latencia: 39 },
  { hora: '23:00', latencia: 36 },
];

interface Alert {
  id: number;
  severity: 'critical' | 'warning' | 'info';
  service: string;
  message: string;
  timestamp: string;
}

const alerts: Alert[] = [
  {
    id: 1,
    severity: 'critical',
    service: 'API Gateway',
    message: 'Tempo de resposta acima de 5s por 3 minutos consecutivos',
    timestamp: '2 min atrás',
  },
  {
    id: 2,
    severity: 'warning',
    service: 'Database',
    message: 'Pool de conexões em 85% da capacidade',
    timestamp: '15 min atrás',
  },
  {
    id: 3,
    severity: 'info',
    service: 'Redis',
    message: 'Cache hit rate: 94.2% — operando normalmente',
    timestamp: '1h atrás',
  },
  {
    id: 4,
    severity: 'warning',
    service: 'Workers',
    message: 'Fila de processamento com 1.240 itens pendentes',
    timestamp: '2h atrás',
  },
  {
    id: 5,
    severity: 'critical',
    service: 'Database',
    message: 'Replicação atrasada em 12s no nó secundário',
    timestamp: '3h atrás',
  },
  {
    id: 6,
    severity: 'info',
    service: 'API Gateway',
    message: 'Nova versão v2.14.3 implantada com sucesso',
    timestamp: '5h atrás',
  },
];

interface ServiceStatus {
  name: string;
  status: 'healthy' | 'degraded' | 'down';
  uptime: string;
  color: string;
}

const services: ServiceStatus[] = [
  { name: 'API', status: 'healthy', uptime: '99.99%', color: '#22c55e' },
  { name: 'Database', status: 'healthy', uptime: '99.97%', color: '#22c55e' },
  { name: 'Redis', status: 'degraded', uptime: '99.82%', color: '#eab308' },
  { name: 'Workers', status: 'healthy', uptime: '99.95%', color: '#22c55e' },
];

// ── Severity helpers ───────────────────────────────────────

const severityConfig = {
  critical: {
    label: 'Crítico',
    dot: 'bg-red-500',
    badge: 'bg-red-500/10 text-red-400 border-red-500/20',
  },
  warning: {
    label: 'Aviso',
    dot: 'bg-yellow-500',
    badge: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
  },
  info: {
    label: 'Info',
    dot: 'bg-blue-500',
    badge: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  },
};

// ── Component ──────────────────────────────────────────────

export default function Monitoring() {
  const [selectedAlert] = useState<Alert | null>(null);

  return (
    <div className="p-6 lg:p-8 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Monitoramento</h1>
          <p className="text-sm text-gray-400 mt-1">
            Status em tempo real da infraestrutura Polis
          </p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-500/10 text-emerald-400 rounded-lg border border-emerald-500/20 text-xs font-medium">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
          </span>
          Todos os sistemas operacionais
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpiCards.map((card) => (
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
            <p
              className={`text-xs mt-1 ${
                card.changeType === 'positive'
                  ? 'text-emerald-400'
                  : card.changeType === 'negative'
                    ? 'text-red-400'
                    : 'text-gray-500'
              }`}
            >
              {card.change}
            </p>
          </div>
        ))}
      </div>

      {/* Latency Chart + Service Status side by side */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Latency Area Chart — 24h */}
        <div className="lg:col-span-2 bg-gray-900/60 border border-gray-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-sm font-semibold text-white">
              Latência (ms) — Últimas 24h
            </h2>
            <span className="text-xs text-gray-500">Atualizado há 1 min</span>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={latencyData}>
                <defs>
                  <linearGradient
                    id="gradientLatency"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1"
                  >
                    <stop offset="0%" stopColor="#06b6d4" stopOpacity={0.35} />
                    <stop offset="100%" stopColor="#06b6d4" stopOpacity={0} />
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
                <YAxis
                  stroke="#6b7280"
                  fontSize={11}
                  tickLine={false}
                  domain={[0, 'dataMax + 15']}
                  unit="ms"
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#111827',
                    border: '1px solid #1f2937',
                    borderRadius: '8px',
                    color: '#e4e4e7',
                    fontSize: '13px',
                  }}
                  formatter={(value: any) => [`${value}ms`, 'Latência']}
                />
                <Area
                  type="monotone"
                  dataKey="latencia"
                  stroke="#06b6d4"
                  strokeWidth={2}
                  fill="url(#gradientLatency)"
                  dot={false}
                  activeDot={{ r: 4, fill: '#06b6d4', stroke: '#0a0a0f', strokeWidth: 2 }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Service Status Cards */}
        <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-sm font-semibold text-white">
              Status dos Serviços
            </h2>
            <span className="text-xs text-gray-500">Tempo real</span>
          </div>
          <div className="space-y-4">
            {services.map((svc) => (
              <div
                key={svc.name}
                className="flex items-center justify-between py-3 px-4 rounded-lg bg-gray-800/40 border border-gray-800"
              >
                <div className="flex items-center gap-3">
                  {svc.status === 'healthy' ? (
                    <CheckCircle className="w-5 h-5 text-emerald-400" />
                  ) : svc.status === 'degraded' ? (
                    <XCircle className="w-5 h-5 text-yellow-400" />
                  ) : (
                    <XCircle className="w-5 h-5 text-red-400" />
                  )}
                  <div>
                    <p className="text-sm font-medium text-white">{svc.name}</p>
                    <p className="text-xs text-gray-500">Uptime {svc.uptime}</p>
                  </div>
                </div>
                <span
                  className="w-2.5 h-2.5 rounded-full"
                  style={{ backgroundColor: svc.color }}
                />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Alerts Table */}
      <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <h2 className="text-sm font-semibold text-white">
              Alertas Recentes
            </h2>
            <span className="text-xs text-gray-500">Últimas 24h</span>
          </div>
          <button className="text-xs text-cyan-400 hover:text-cyan-300 transition-colors">
            Ver todos
          </button>
        </div>

        {/* Table header — hidden on small screens */}
        <div className="hidden sm:grid grid-cols-4 gap-4 px-4 py-2 text-xs font-medium text-gray-500 uppercase tracking-wider border-b border-gray-800">
          <span>Severidade</span>
          <span>Serviço</span>
          <span className="col-span-2">Mensagem</span>
          <span className="text-right">Horário</span>
        </div>

        <div className="divide-y divide-gray-800">
          {alerts.map((alert) => {
            const sev = severityConfig[alert.severity];
            return (
              <div
                key={alert.id}
                className={`grid grid-cols-1 sm:grid-cols-4 gap-2 sm:gap-4 px-4 py-4 hover:bg-gray-800/30 transition-colors rounded-lg ${
                  selectedAlert?.id === alert.id ? 'bg-gray-800/40' : ''
                }`}
              >
                {/* Mobile layout: inline */}
                <div className="flex items-center gap-2 sm:contents">
                  <div className="flex items-center gap-2 sm:flex">
                    <span
                      className={`w-2 h-2 rounded-full ${sev.dot} shrink-0`}
                    />
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full border font-medium ${sev.badge}`}
                    >
                      {sev.label}
                    </span>
                  </div>
                  <span className="text-sm font-medium text-white sm:block">
                    {alert.service}
                  </span>
                </div>

                <span className="text-sm text-gray-300 col-span-2">
                  {alert.message}
                </span>

                <div className="flex items-center justify-between sm:justify-end gap-2">
                  <span className="text-xs text-gray-500">
                    {alert.timestamp}
                  </span>
                  <ArrowUpRight className="w-3.5 h-3.5 text-gray-600 shrink-0" />
                </div>
              </div>
            );
          })}
        </div>

        {alerts.length === 0 && (
          <div className="flex flex-col items-center py-12 text-gray-500">
            <CheckCircle className="w-10 h-10 mb-3 text-emerald-400" />
            <p className="text-sm">Nenhum alerta ativo</p>
            <p className="text-xs">Todos os sistemas operam normalmente</p>
          </div>
        )}
      </div>
    </div>
  );
}
