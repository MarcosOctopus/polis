'use client';

import { useState } from 'react';
import {
  FileText,
  BarChart3,
  Download,
  Calendar,
  Clock,
  RefreshCw,
  CheckCircle2,
  Loader2,
  AlertCircle,
  ArrowUpRight,
  Search,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

/* ───── Tipos ───── */

type ReportStatus = 'pronto' | 'gerando' | 'erro';

type AvailableReport = {
  id: string;
  name: string;
  description: string;
  icon: typeof FileText;
  lastGeneration: string;
  status: ReportStatus;
};

type GeneratedReport = {
  id: string;
  name: string;
  period: string;
  format: string;
  size: string;
  date: string;
};

type PeriodTab = 'diario' | 'semanal' | 'mensal' | 'anual';

/* ───── Mock data ───── */

const statusConfig: Record<ReportStatus, { icon: typeof Loader2; label: string; color: string; bg: string }> = {
  pronto: {
    icon: CheckCircle2,
    label: 'Pronto',
    color: 'text-emerald-400',
    bg: 'bg-emerald-500/10 border-emerald-500/20',
  },
  gerando: {
    icon: Loader2,
    label: 'Gerando',
    color: 'text-yellow-400',
    bg: 'bg-yellow-500/10 border-yellow-500/20',
  },
  erro: {
    icon: AlertCircle,
    label: 'Erro',
    color: 'text-red-400',
    bg: 'bg-red-500/10 border-red-500/20',
  },
};

const availableReports: AvailableReport[] = [
  {
    id: 'rep-001',
    name: 'Relatório de Conversas',
    description: 'Análise completa de volume, duração e satisfação das conversas',
    icon: FileText,
    lastGeneration: '2 min atrás',
    status: 'pronto',
  },
  {
    id: 'rep-002',
    name: 'Performance de Agentes',
    description: 'Métricas de desempenho, taxa de sucesso e tempo de resposta por agente',
    icon: BarChart3,
    lastGeneration: '15 min atrás',
    status: 'pronto',
  },
  {
    id: 'rep-003',
    name: 'Análise de Uso',
    description: 'Distribuição de requisições por horário, fonte e modelo de IA',
    icon: Clock,
    lastGeneration: '1h atrás',
    status: 'pronto',
  },
  {
    id: 'rep-004',
    name: 'Relatório de Erros',
    description: 'Log consolidado de falhas, exceções e alertas críticos do sistema',
    icon: AlertCircle,
    lastGeneration: '30 min atrás',
    status: 'gerando',
  },
  {
    id: 'rep-005',
    name: 'Resumo Mensal',
    description: 'Panorama geral com indicadores chave e tendências do período',
    icon: Calendar,
    lastGeneration: '3 dias atrás',
    status: 'pronto',
  },
  {
    id: 'rep-006',
    name: 'Auditoria de Segurança',
    description: 'Eventos de segurança, acessos suspeitos e conformidade',
    icon: FileText,
    lastGeneration: '---',
    status: 'erro',
  },
];

const generatedReports: GeneratedReport[] = [
  { id: 'GEN-001', name: 'Relatório de Conversas - Julho', period: '01/07 - 31/07', format: 'PDF', size: '2.4 MB', date: '31/07/2025' },
  { id: 'GEN-002', name: 'Performance de Agentes - Julho', period: '01/07 - 31/07', format: 'XLSX', size: '1.8 MB', date: '31/07/2025' },
  { id: 'GEN-003', name: 'Análise de Uso - Semana 30', period: '21/07 - 27/07', format: 'PDF', size: '1.2 MB', date: '28/07/2025' },
  { id: 'GEN-004', name: 'Resumo Mensal - Junho', period: '01/06 - 30/06', format: 'PDF', size: '3.1 MB', date: '30/06/2025' },
  { id: 'GEN-005', name: 'Relatório de Erros - Junho', period: '01/06 - 30/06', format: 'CSV', size: '856 KB', date: '30/06/2025' },
  { id: 'GEN-006', name: 'Relatório de Conversas - Junho', period: '01/06 - 30/06', format: 'PDF', size: '2.6 MB', date: '30/06/2025' },
  { id: 'GEN-007', name: 'Performance de Agentes - Junho', period: '01/06 - 30/06', format: 'XLSX', size: '1.9 MB', date: '30/06/2025' },
  { id: 'GEN-008', name: 'Auditoria de Segurança - Q2', period: '01/04 - 30/06', format: 'PDF', size: '4.2 MB', date: '01/07/2025' },
];

/* ───── Dados do gráfico de barras por período ───── */

const periodChartData: Record<PeriodTab, { label: string; requests: number }[]> = {
  diario: [
    { label: '00h', requests: 320 },
    { label: '02h', requests: 180 },
    { label: '04h', requests: 150 },
    { label: '06h', requests: 290 },
    { label: '08h', requests: 680 },
    { label: '10h', requests: 1240 },
    { label: '12h', requests: 980 },
    { label: '14h', requests: 1350 },
    { label: '16h', requests: 1450 },
    { label: '18h', requests: 1120 },
    { label: '20h', requests: 780 },
    { label: '22h', requests: 510 },
  ],
  semanal: [
    { label: 'Seg', requests: 8240 },
    { label: 'Ter', requests: 9100 },
    { label: 'Qua', requests: 8750 },
    { label: 'Qui', requests: 9430 },
    { label: 'Sex', requests: 10200 },
    { label: 'Sáb', requests: 5670 },
    { label: 'Dom', requests: 4320 },
  ],
  mensal: [
    { label: 'Sem 1', requests: 42100 },
    { label: 'Sem 2', requests: 45600 },
    { label: 'Sem 3', requests: 43800 },
    { label: 'Sem 4', requests: 48700 },
  ],
  anual: [
    { label: 'Jan', requests: 152000 },
    { label: 'Fev', requests: 148000 },
    { label: 'Mar', requests: 165000 },
    { label: 'Abr', requests: 171000 },
    { label: 'Mai', requests: 183000 },
    { label: 'Jun', requests: 179000 },
    { label: 'Jul', requests: 194000 },
  ],
};

/* ───── KPI Cards ───── */

const kpiCards = [
  { label: 'Relatórios Gerados', value: '1,247', icon: FileText, color: 'text-cyan-400', bg: 'bg-cyan-500/10', border: 'border-cyan-500/20' },
  { label: 'Este Mês', value: '89', icon: Calendar, color: 'text-purple-400', bg: 'bg-purple-500/10', border: 'border-purple-500/20' },
  { label: 'Taxa de Sucesso', value: '98.3%', icon: CheckCircle2, color: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/20' },
  { label: 'Requests Hoje', value: '12.5K', icon: BarChart3, color: 'text-blue-400', bg: 'bg-blue-500/10', border: 'border-blue-500/20' },
];

/* ───── Página principal ───── */

export default function ReportsPage() {
  const [periodTab, setPeriodTab] = useState<PeriodTab>('semanal');
  const [searchQuery, setSearchQuery] = useState('');

  /* ───── Tabs de período ───── */
  const periodTabs: { key: PeriodTab; label: string }[] = [
    { key: 'diario', label: 'Diário' },
    { key: 'semanal', label: 'Semanal' },
    { key: 'mensal', label: 'Mensal' },
    { key: 'anual', label: 'Anual' },
  ];

  const chartData = periodChartData[periodTab];

  /* ───── Filtro da tabela ───── */
  const filteredReports = generatedReports.filter((r) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      r.id.toLowerCase().includes(q) ||
      r.name.toLowerCase().includes(q) ||
      r.format.toLowerCase().includes(q)
    );
  });

  return (
    <div className="p-6 lg:p-8 space-y-8">
      {/* ─── Cabeçalho ─── */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Relatórios</h1>
          <p className="text-sm text-gray-400 mt-1">
            Gere e gerencie relatórios da plataforma
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-cyan-500/10 text-cyan-400 rounded-lg border border-cyan-500/20 hover:bg-cyan-500/20 transition-all text-sm font-medium">
          <FileText className="w-4 h-4" />
          Gerar Novo Relatório
        </button>
      </div>

      {/* ─── KPI Cards ─── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpiCards.map((s) => {
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

      {/* ─── Gráfico de Requisições por Período ─── */}
      <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-6">
        <div className="flex items-center justify-between flex-wrap gap-4 mb-6">
          <div className="flex items-center gap-3">
            <BarChart3 className="w-4 h-4 text-cyan-400" />
            <h2 className="text-sm font-semibold text-white">
              Requisições por Período
            </h2>
          </div>

          {/* Seletor de período em tabs */}
          <div className="flex gap-1 bg-gray-800/50 rounded-lg p-1">
            {periodTabs.map((tab) => (
              <button
                key={tab.key}
                onClick={() => setPeriodTab(tab.key)}
                className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all ${
                  periodTab === tab.key
                    ? 'bg-cyan-500/20 text-cyan-400 shadow-sm'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} barCategoryGap="20%">
              <defs>
                <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#06b6d4" stopOpacity={0.9} />
                  <stop offset="100%" stopColor="#8b5cf6" stopOpacity={0.6} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
              <XAxis
                dataKey="label"
                stroke="#6b7280"
                fontSize={12}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                stroke="#6b7280"
                fontSize={12}
                tickLine={false}
                axisLine={false}
                tickFormatter={(v: number) =>
                  v >= 1000 ? `${(v / 1000).toFixed(0)}K` : String(v)
                }
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#111827',
                  border: '1px solid #1f2937',
                  borderRadius: '8px',
                  color: '#e4e4e7',
                  fontSize: 13,
                }}
                labelStyle={{ color: '#9ca3af' }}
                formatter={(value: any) => [
                  Number(value).toLocaleString('pt-BR'),
                  'Requisições',
                ]}
                cursor={{ fill: 'rgba(6, 182, 212, 0.08)' }}
              />
              <Bar
                dataKey="requests"
                fill="url(#barGradient)"
                radius={[4, 4, 0, 0]}
                maxBarSize={48}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* ─── Cards de Relatórios Disponíveis ─── */}
      <div>
        <h2 className="text-sm font-semibold text-white mb-4">
          Relatórios Disponíveis
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {availableReports.map((report) => {
            const StatusIcon = statusConfig[report.status].icon;
            const status = statusConfig[report.status];
            return (
              <div
                key={report.id}
                className="bg-gray-900/60 border border-gray-800 rounded-xl p-5 hover:border-gray-700 transition-all group"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="p-2.5 rounded-lg bg-purple-500/10 text-purple-400">
                    <report.icon className="w-5 h-5" />
                  </div>
                  <span
                    className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${status.bg} ${status.color}`}
                  >
                    <StatusIcon
                      className={`w-3 h-3 ${
                        report.status === 'gerando' ? 'animate-spin' : ''
                      }`}
                    />
                    {status.label}
                  </span>
                </div>

                <h3 className="text-sm font-semibold text-white mb-1 group-hover:text-cyan-400 transition-colors">
                  {report.name}
                </h3>
                <p className="text-xs text-gray-400 mb-4 line-clamp-2">
                  {report.description}
                </p>

                <div className="flex items-center justify-between pt-3 border-t border-gray-800">
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <RefreshCw className="w-3 h-3" />
                    <span>{report.lastGeneration}</span>
                  </div>
                  <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 hover:bg-cyan-500/20 transition-all opacity-0 group-hover:opacity-100">
                    <Download className="w-3 h-3" />
                    Gerar
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* ─── Tabela de Relatórios Gerados Recentemente ─── */}
      <div className="bg-gray-900/60 border border-gray-800 rounded-xl overflow-hidden">
        {/* Header da tabela */}
        <div className="p-4 border-b border-gray-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-cyan-400" />
            <h2 className="text-sm font-semibold text-white">
              Relatórios Gerados Recentemente
            </h2>
          </div>

          <div className="relative w-full sm:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input
              type="text"
              placeholder="Buscar relatório..."
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
                <th className="text-left px-6 py-3 font-medium">Relatório</th>
                <th className="text-left px-6 py-3 font-medium">Período</th>
                <th className="text-left px-6 py-3 font-medium">Formato</th>
                <th className="text-left px-6 py-3 font-medium">Tamanho</th>
                <th className="text-left px-6 py-3 font-medium">Data</th>
                <th className="text-right px-6 py-3 font-medium">Ações</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60">
              {filteredReports.map((r) => (
                <tr
                  key={r.id}
                  className="hover:bg-gray-800/30 transition-colors group"
                >
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400">
                        <FileText className="w-4 h-4" />
                      </div>
                      <span className="text-white font-medium">{r.name}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-gray-400">{r.period}</td>
                  <td className="px-6 py-4">
                    <span className="inline-flex px-2.5 py-1 rounded-md text-xs font-medium bg-gray-800/60 text-gray-300 border border-gray-700">
                      {r.format}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-gray-400">{r.size}</td>
                  <td className="px-6 py-4 text-gray-400">{r.date}</td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-all">
                      <button className="p-1.5 rounded-lg text-gray-500 hover:text-cyan-400 hover:bg-cyan-500/10 transition-all">
                        <Download className="w-4 h-4" />
                      </button>
                      <button className="p-1.5 rounded-lg text-gray-500 hover:text-purple-400 hover:bg-purple-500/10 transition-all">
                        <ArrowUpRight className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {filteredReports.length === 0 && (
            <div className="flex flex-col items-center py-16 text-gray-500">
              <FileText className="w-10 h-10 mb-3 opacity-40" />
              <p className="text-sm">Nenhum relatório encontrado</p>
            </div>
          )}
        </div>

        {/* Rodapé da tabela */}
        <div className="px-6 py-3 border-t border-gray-800 flex items-center justify-between text-xs text-gray-500">
          <span>
            Exibindo {filteredReports.length} de {generatedReports.length} relatórios
          </span>
          <div className="flex items-center gap-2">
            <Download className="w-3.5 h-3.5" />
            <span>{filteredReports.length} disponíveis para download</span>
          </div>
        </div>
      </div>
    </div>
  );
}
