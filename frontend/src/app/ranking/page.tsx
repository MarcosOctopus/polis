'use client';

import { useState, useMemo } from 'react';
import {
  TrendingUp,
  TrendingDown,
  Minus,
  AlertTriangle,
  Search,
  ChevronLeft,
  ChevronRight,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  BarChart3,
  MapPin,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  type TooltipProps,
} from 'recharts';
import type {
  ValueType,
  NameType,
} from 'recharts/types/component/DefaultTooltipContent';

// ── Mock Data ──────────────────────────────────────────────

type Period = 'Hoje' | 'Semana' | 'Mês';
type SortKey =
  | 'posicao'
  | 'bairro'
  | 'total'
  | 'abertas'
  | 'andamento'
  | 'resolvidas'
  | 'prioridade'
  | 'tendencia';
type SortDir = 'asc' | 'desc';
type Tendency = 'up' | 'down' | 'stable';

interface BairroData {
  id: number;
  bairro: string;
  total: number;
  abertas: number;
  andamento: number;
  resolvidas: number;
  prioridadeMedia: number;
  tendencia: Tendency;
  pctChange: number;
  tipoComum: string;
  alerta: 'Crítico' | 'Alto' | 'Moderado';
}

interface TipoData {
  tipo: string;
  total: number;
  pctChange: number;
  tendencia: Tendency;
}

const bairrosList = [
  'Capão Redondo',
  'Brasilândia',
  'Cidade Tiradentes',
  'Grajaú',
  'Itaquera',
  'São Miguel Paulista',
  'Campo Limpo',
  'Jardim Ângela',
  'Jardim São Luís',
  'Parelheiros',
  'Sapopemba',
  'Vila Maria',
  'Santana',
  'Moema',
  'Pinheiros',
  'Vila Mariana',
  'Butantã',
  'Tatuapé',
  'Bela Vista',
  'Jardins',
];

const tiposList = [
  'Infraestrutura',
  'Segurança',
  'Limpeza Urbana',
  'Iluminação Pública',
  'Trânsito',
  'Barulho',
  'Saneamento',
  'Transporte',
  'Meio Ambiente',
  'Saúde',
  'Educação',
  'Habitação',
];

function randomInt(min: number, max: number): number {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function pickTendency(weight = 0.5): Tendency {
  const r = Math.random();
  if (r < weight) return 'up';
  if (r < weight + 0.3) return 'down';
  return 'stable';
}

function pickAlerta(total: number): 'Crítico' | 'Alto' | 'Moderado' {
  if (total > 900) return 'Crítico';
  if (total > 600) return 'Alto';
  return 'Moderado';
}

function pickTipoComum(): string {
  return tiposList[randomInt(0, tiposList.length - 1)];
}

function buildBairrosData(): BairroData[] {
  return bairrosList.map((bairro, i) => {
    const total = randomInt(150, 1450);
    const abertas = randomInt(20, Math.round(total * 0.4));
    const andamento = randomInt(15, Math.round(total * 0.35));
    const resolvidas = total - abertas - andamento;
    const prioridade = parseFloat((Math.random() * 4 + 1).toFixed(1));
    return {
      id: i + 1,
      bairro,
      total,
      abertas,
      andamento,
      resolvidas,
      prioridadeMedia: prioridade,
      tendencia: pickTendency(0.45),
      pctChange: parseFloat((Math.random() * 60 - 10).toFixed(1)),
      tipoComum: pickTipoComum(),
      alerta: pickAlerta(total),
    };
  });
}

function buildTiposData(): TipoData[] {
  return tiposList.map((tipo) => ({
    tipo,
    total: randomInt(200, 1800),
    pctChange: parseFloat((Math.random() * 50 - 12).toFixed(1)),
    tendencia: pickTendency(0.5),
  }));
}

// Sort by total descending initially to match "top 10" ranking
const allBairros = buildBairrosData().sort((a, b) => b.total - a.total);
const allTipos = buildTiposData().sort((a, b) => b.total - a.total);

const top10Bairros = allBairros.slice(0, 10);
const top10Tipos = allTipos.slice(0, 10);
const worst3 = allBairros.slice(0, 3);

// ── Helpers ────────────────────────────────────────────────

const tendenciaIcon: Record<Tendency, React.ElementType> = {
  up: TrendingUp,
  down: TrendingDown,
  stable: Minus,
};

const tendenciaColor: Record<Tendency, string> = {
  up: 'text-red-400',
  down: 'text-emerald-400',
  stable: 'text-gray-500',
};

const tendenciaLabel: Record<Tendency, string> = {
  up: '↑ Subindo',
  down: '↓ Caindo',
  stable: '→ Estável',
};

const alertaConfig = {
  Crítico: { bg: 'bg-red-500/15', text: 'text-red-400', border: 'border-red-500/25', icon: AlertTriangle },
  Alto: { bg: 'bg-orange-500/15', text: 'text-orange-400', border: 'border-orange-500/25', icon: AlertTriangle },
  Moderado: { bg: 'bg-yellow-500/15', text: 'text-yellow-400', border: 'border-yellow-500/25', icon: AlertTriangle },
};

function getBarColor(value: number, max: number): string {
  const ratio = value / max;
  if (ratio > 0.75) return '#ef4444';
  if (ratio > 0.5) return '#f97316';
  if (ratio > 0.3) return '#eab308';
  return '#22c55e';
}

// ── Tooltip formatter ──────────────────────────────────────

const chartTooltipStyle = {
  backgroundColor: '#111827',
  border: '1px solid #1f2937',
  borderRadius: '8px',
  color: '#e4e4e7',
  fontSize: '13px',
};

interface ChartPayload {
  total: number;
  pctChange: number;
  bairro?: string;
  tipo?: string;
}

const barChartTooltipFormatter = (
  _value: ValueType,
  _name: NameType,
  props: TooltipProps<ValueType, NameType> & { payload?: ChartPayload },
) => {
  const d = props.payload;
  if (!d) return ['', ''];
  return [
    `${d.total.toLocaleString()} reclamações`,
    `${d.pctChange > 0 ? '+' : ''}${d.pctChange}% vs período anterior`,
  ];
};

// ── Component ──────────────────────────────────────────────

export default function RankingPage() {
  // Filters
  const [periodo, setPeriodo] = useState<Period>('Mês');
  const [tipoFilter, setTipoFilter] = useState('Todos');
  const [bairroFilter, setBairroFilter] = useState('Todos');

  // Table sorting & pagination
  const [sortKey, setSortKey] = useState<SortKey>('total');
  const [sortDir, setSortDir] = useState<SortDir>('desc');
  const [page, setPage] = useState(0);
  const perPage = 10;

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortKey(key);
      setSortDir(key === 'bairro' ? 'asc' : 'desc');
    }
    setPage(0);
  };

  const filteredBairros = useMemo(() => {
    let list = [...allBairros];
    if (bairroFilter !== 'Todos') {
      list = list.filter((b) => b.bairro === bairroFilter);
    }
    if (tipoFilter !== 'Todos') {
      list = list.filter((b) => b.tipoComum === tipoFilter);
    }
    return list;
  }, [bairroFilter, tipoFilter]);

  const sortedBairros = useMemo(() => {
    const list = [...filteredBairros];
    list.sort((a, b) => {
      let cmp = 0;
      switch (sortKey) {
        case 'posicao':
          cmp = a.id - b.id;
          break;
        case 'bairro':
          cmp = a.bairro.localeCompare(b.bairro);
          break;
        case 'total':
          cmp = a.total - b.total;
          break;
        case 'abertas':
          cmp = a.abertas - b.abertas;
          break;
        case 'andamento':
          cmp = a.andamento - b.andamento;
          break;
        case 'resolvidas':
          cmp = a.resolvidas - b.resolvidas;
          break;
        case 'prioridade':
          cmp = a.prioridadeMedia - b.prioridadeMedia;
          break;
        case 'tendencia': {
          const order: Record<Tendency, number> = { up: 2, down: 0, stable: 1 };
          cmp = order[a.tendencia] - order[b.tendencia];
          break;
        }
      }
      return sortDir === 'asc' ? cmp : -cmp;
    });
    return list;
  }, [filteredBairros, sortKey, sortDir]);

  const totalPages = Math.ceil(sortedBairros.length / perPage);
  const paginatedBairros = sortedBairros.slice(
    page * perPage,
    page * perPage + perPage,
  );

  const SortIcon = ({ column }: { column: SortKey }) => {
    if (sortKey !== column)
      return <ArrowUpDown className="w-3.5 h-3.5 ml-1 inline-block opacity-40" />;
    return sortDir === 'asc' ? (
      <ArrowUp className="w-3.5 h-3.5 ml-1 inline-block text-cyan-400" />
    ) : (
      <ArrowDown className="w-3.5 h-3.5 ml-1 inline-block text-cyan-400" />
    );
  };

  const maxBairroTotal = Math.max(...top10Bairros.map((b) => b.total));
  const maxTipoTotal = Math.max(...top10Tipos.map((t) => t.total));

  return (
    <div className="p-6 lg:p-8 space-y-8">
      {/* ── 1. Header ──────────────────────────────────────── */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Ranking de Reclamações</h1>
          <p className="text-sm text-gray-400 mt-1">
            Análise comparativa por região e categoria
          </p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 bg-cyan-500/10 text-cyan-400 rounded-lg border border-cyan-500/20 text-xs font-medium whitespace-nowrap">
          <BarChart3 className="w-4 h-4" />
          Dados atualizados em tempo real
        </div>
      </div>

      {/* Filters Row */}
      <div className="flex flex-wrap items-center gap-3">
        {/* Período */}
        <div className="flex items-center gap-1 bg-gray-900/60 border border-gray-800 rounded-lg p-1">
          {(['Hoje', 'Semana', 'Mês'] as Period[]).map((p) => (
            <button
              key={p}
              onClick={() => setPeriodo(p)}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all ${
                periodo === p
                  ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                  : 'text-gray-400 hover:text-gray-200 border border-transparent'
              }`}
            >
              {p}
            </button>
          ))}
        </div>

        {/* Tipo Filter */}
        <div className="relative">
          <select
            value={tipoFilter}
            onChange={(e) => {
              setTipoFilter(e.target.value);
              setPage(0);
            }}
            className="appearance-none bg-gray-900/60 border border-gray-800 rounded-lg px-3 py-1.5 pr-8 text-xs text-gray-300 focus:outline-none focus:border-cyan-500/50 cursor-pointer"
          >
            <option>Todos</option>
            {tiposList.map((t) => (
              <option key={t}>{t}</option>
            ))}
          </select>
          <Search className="absolute right-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-500 pointer-events-none" />
        </div>

        {/* Bairro Filter */}
        <div className="relative">
          <select
            value={bairroFilter}
            onChange={(e) => {
              setBairroFilter(e.target.value);
              setPage(0);
            }}
            className="appearance-none bg-gray-900/60 border border-gray-800 rounded-lg px-3 py-1.5 pr-8 text-xs text-gray-300 focus:outline-none focus:border-cyan-500/50 cursor-pointer"
          >
            <option>Todos</option>
            {bairrosList.map((b) => (
              <option key={b}>{b}</option>
            ))}
          </select>
          <MapPin className="absolute right-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-500 pointer-events-none" />
        </div>
      </div>

      {/* ── 2 + 3. Charts Row ─────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top 10 Bairros */}
        <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-sm font-semibold text-white">Top 10 Bairros</h2>
            <span className="text-xs text-gray-500">Por total de reclamações</span>
          </div>
          <div className="h-[380px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={top10Bairros}
                layout="vertical"
                margin={{ top: 0, right: 80, bottom: 0, left: 0 }}
                barCategoryGap={6}
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#1f2937"
                  horizontal={false}
                />
                <XAxis
                  type="number"
                  stroke="#6b7280"
                  fontSize={11}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis
                  type="category"
                  dataKey="bairro"
                  stroke="#6b7280"
                  fontSize={10}
                  tickLine={false}
                  axisLine={false}
                  width={120}
                  tickFormatter={(val: string) =>
                    val.length > 14 ? val.slice(0, 13) + '…' : val
                  }
                />
                <Tooltip
                  contentStyle={chartTooltipStyle}
                  formatter={barChartTooltipFormatter as any}
                />
                <Bar dataKey="total" radius={[0, 4, 4, 0]} maxBarSize={20}>
                  {top10Bairros.map((entry, idx) => (
                    <Cell
                      key={idx}
                      fill={getBarColor(entry.total, maxBairroTotal)}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          {/* Legend */}
          <div className="flex items-center justify-center gap-6 mt-4 text-xs text-gray-500">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-sm bg-red-500" />
              Maior incidência
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-sm bg-green-500" />
              Menor incidência
            </div>
          </div>
        </div>

        {/* Top 10 Tipos de Reclamação */}
        <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-sm font-semibold text-white">
              Top 10 Tipos de Reclamação
            </h2>
            <span className="text-xs text-gray-500">
              Comparativo vs período anterior
            </span>
          </div>
          <div className="h-[380px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={top10Tipos}
                layout="vertical"
                margin={{ top: 0, right: 60, bottom: 0, left: 0 }}
                barCategoryGap={6}
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#1f2937"
                  horizontal={false}
                />
                <XAxis
                  type="number"
                  stroke="#6b7280"
                  fontSize={11}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis
                  type="category"
                  dataKey="tipo"
                  stroke="#6b7280"
                  fontSize={10}
                  tickLine={false}
                  axisLine={false}
                  width={110}
                  tickFormatter={(val: string) =>
                    val.length > 14 ? val.slice(0, 13) + '…' : val
                  }
                />
                <Tooltip
                  contentStyle={chartTooltipStyle}
                  formatter={barChartTooltipFormatter as any}
                />
                <Bar dataKey="total" radius={[0, 4, 4, 0]} maxBarSize={20}>
                  {top10Tipos.map((entry, idx) => (
                    <Cell
                      key={idx}
                      fill={getBarColor(entry.total, maxTipoTotal)}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          {/* Arrows legend */}
          <div className="flex items-center justify-center gap-6 mt-4 text-xs text-gray-500">
            <div className="flex items-center gap-1.5">
              <TrendingUp className="w-3.5 h-3.5 text-red-400" />
              Aumento
            </div>
            <div className="flex items-center gap-1.5">
              <TrendingDown className="w-3.5 h-3.5 text-emerald-400" />
              Queda
            </div>
            <div className="flex items-center gap-1.5">
              <Minus className="w-3.5 h-3.5 text-gray-500" />
              Estável
            </div>
          </div>
          {/* Inline arrows per item */}
          <div className="mt-4 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2">
            {top10Tipos.map((t) => {
              const Icon = tendenciaIcon[t.tendencia];
              const color = tendenciaColor[t.tendencia];
              return (
                <div
                  key={t.tipo}
                  className="flex items-center gap-1.5 px-2 py-1 rounded bg-gray-800/30 border border-gray-800"
                >
                  <Icon className={`w-3 h-3 ${color} shrink-0`} />
                  <span className="text-[11px] text-gray-400 truncate">
                    {t.tipo}
                  </span>
                  <span className={`text-[11px] font-medium ml-auto ${color}`}>
                    {t.pctChange > 0 ? '+' : ''}
                    {t.pctChange}%
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* ── 4. Tabela de Ranking ───────────────────────────── */}
      <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <h2 className="text-sm font-semibold text-white">
              Ranking Completo
            </h2>
            <span className="text-xs text-gray-500">
              {filteredBairros.length} bairros
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500">
              Pág. {page + 1} de {totalPages}
            </span>
          </div>
        </div>

        {/* Table — desktop */}
        <div className="hidden lg:block overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-800">
                {([
                  { key: 'posicao', label: '#' },
                  { key: 'bairro', label: 'Bairro' },
                  { key: 'total', label: 'Total' },
                  { key: 'abertas', label: 'Aberta' },
                  { key: 'andamento', label: 'Em Andamento' },
                  { key: 'resolvidas', label: 'Resolvida' },
                  { key: 'prioridade', label: 'Prioridade Média' },
                  { key: 'tendencia', label: 'Tendência' },
                ] as { key: SortKey; label: string }[]).map((col) => (
                  <th
                    key={col.key}
                    onClick={() => handleSort(col.key)}
                    className="px-3 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider text-left cursor-pointer hover:text-gray-300 transition-colors select-none"
                  >
                    {col.key === 'bairro' || col.key === 'posicao' ? (
                      <span className="flex items-center">
                        {col.label}
                        <SortIcon column={col.key} />
                      </span>
                    ) : (
                      <span className="flex items-center justify-end">
                        {col.label}
                        <SortIcon column={col.key} />
                      </span>
                    )}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60">
              {paginatedBairros.map((b, idx) => {
                const TendIcon = tendenciaIcon[b.tendencia];
                const tendColor = tendenciaColor[b.tendencia];
                return (
                  <tr
                    key={b.id}
                    className="hover:bg-gray-800/20 transition-colors"
                  >
                    <td className="px-3 py-3.5 text-xs text-gray-500 font-mono">
                      {page * perPage + idx + 1}
                    </td>
                    <td className="px-3 py-3.5 text-sm font-medium text-white">
                      {b.bairro}
                    </td>
                    <td className="px-3 py-3.5 text-sm text-gray-200 text-right font-mono">
                      {b.total.toLocaleString()}
                    </td>
                    <td className="px-3 py-3.5 text-sm text-gray-200 text-right font-mono">
                      {b.abertas.toLocaleString()}
                    </td>
                    <td className="px-3 py-3.5 text-sm text-yellow-400 text-right font-mono">
                      {b.andamento.toLocaleString()}
                    </td>
                    <td className="px-3 py-3.5 text-sm text-emerald-400 text-right font-mono">
                      {b.resolvidas.toLocaleString()}
                    </td>
                    <td className="px-3 py-3.5 text-sm text-right font-mono">
                      <span
                        className={`px-2 py-0.5 rounded text-xs font-medium ${
                          b.prioridadeMedia > 3.5
                            ? 'bg-red-500/10 text-red-400'
                            : b.prioridadeMedia > 2.5
                              ? 'bg-yellow-500/10 text-yellow-400'
                              : 'bg-emerald-500/10 text-emerald-400'
                        }`}
                      >
                        {b.prioridadeMedia.toFixed(1)}
                      </span>
                    </td>
                    <td className="px-3 py-3.5 text-right">
                      <span
                        className={`inline-flex items-center gap-1 text-xs font-medium ${tendColor}`}
                        title={tendenciaLabel[b.tendencia]}
                      >
                        <TendIcon className="w-3.5 h-3.5" />
                        {b.pctChange > 0 ? '+' : ''}
                        {b.pctChange}%
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Table — mobile cards */}
        <div className="lg:hidden divide-y divide-gray-800">
          {paginatedBairros.map((b, idx) => {
            const TendIcon = tendenciaIcon[b.tendencia];
            const tendColor = tendenciaColor[b.tendencia];
            return (
              <div key={b.id} className="py-4 px-1">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-gray-500 font-mono">
                    #{page * perPage + idx + 1}
                  </span>
                  <span
                    className={`inline-flex items-center gap-1 text-xs font-medium ${tendColor}`}
                  >
                    <TendIcon className="w-3.5 h-3.5" />
                    {b.pctChange > 0 ? '+' : ''}
                    {b.pctChange}%
                  </span>
                </div>
                <p className="text-sm font-medium text-white mb-2">
                  {b.bairro}
                </p>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Total:</span>
                    <span className="text-gray-200 font-mono">
                      {b.total.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Aberta:</span>
                    <span className="text-gray-200 font-mono">
                      {b.abertas.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Andamento:</span>
                    <span className="text-yellow-400 font-mono">
                      {b.andamento.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Resolvida:</span>
                    <span className="text-emerald-400 font-mono">
                      {b.resolvidas.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between col-span-2">
                    <span className="text-gray-500">Prioridade:</span>
                    <span
                      className={`font-mono px-2 py-0.5 rounded text-xs font-medium ${
                        b.prioridadeMedia > 3.5
                          ? 'bg-red-500/10 text-red-400'
                          : b.prioridadeMedia > 2.5
                            ? 'bg-yellow-500/10 text-yellow-400'
                            : 'bg-emerald-500/10 text-emerald-400'
                      }`}
                    >
                      {b.prioridadeMedia.toFixed(1)}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between mt-6 pt-4 border-t border-gray-800">
          <button
            onClick={() => setPage(Math.max(0, page - 1))}
            disabled={page === 0}
            className="flex items-center gap-1 px-3 py-1.5 text-xs text-gray-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
            Anterior
          </button>
          <div className="flex items-center gap-1.5">
            {Array.from({ length: totalPages }, (_, i) => (
              <button
                key={i}
                onClick={() => setPage(i)}
                className={`w-7 h-7 rounded-md text-xs font-medium transition-colors ${
                  page === i
                    ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                    : 'text-gray-500 hover:text-gray-300 border border-transparent'
                }`}
              >
                {i + 1}
              </button>
            ))}
          </div>
          <button
            onClick={() => setPage(Math.min(totalPages - 1, page + 1))}
            disabled={page >= totalPages - 1}
            className="flex items-center gap-1 px-3 py-1.5 text-xs text-gray-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          >
            Próximo
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* ── 5. Worst Performing (cards) ────────────────────── */}
      <div>
        <div className="flex items-center gap-3 mb-4">
          <h2 className="text-sm font-semibold text-white">
            Piores Desempenhos
          </h2>
          <span className="text-xs text-gray-500">
            Bairros com maior volume de reclamações
          </span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {worst3.map((b, idx) => {
            const cfg = alertaConfig[b.alerta];
            const AlertIcon = cfg.icon;
            return (
              <div
                key={b.id}
                className={`${cfg.bg} ${cfg.border} border rounded-xl p-5 relative overflow-hidden`}
              >
                {/* Rank badge */}
                <div className="absolute top-3 right-3 text-3xl font-bold text-white/5 select-none">
                  #{idx + 1}
                </div>

                <div className="flex items-center gap-2 mb-3">
                  <AlertIcon className={`w-5 h-5 ${cfg.text}`} />
                  <span
                    className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${cfg.text} ${cfg.bg} ${cfg.border}`}
                  >
                    {b.alerta}
                  </span>
                </div>

                <h3 className="text-base font-bold text-white mb-2">
                  {b.bairro}
                </h3>

                <div className="space-y-1.5 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Total reclamações</span>
                    <span className="text-white font-semibold font-mono">
                      {b.total.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Tipo mais comum</span>
                    <span className="text-gray-200">{b.tipoComum}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Prioridade média</span>
                    <span className={`font-mono font-semibold ${cfg.text}`}>
                      {b.prioridadeMedia.toFixed(1)}
                    </span>
                  </div>
                </div>

                {/* Mini bar */}
                <div className="mt-3 h-1.5 w-full bg-gray-800 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${
                      b.alerta === 'Crítico'
                        ? 'bg-red-500'
                        : b.alerta === 'Alto'
                          ? 'bg-orange-500'
                          : 'bg-yellow-500'
                    }`}
                    style={{
                      width: `${Math.min(100, (b.total / maxBairroTotal) * 100)}%`,
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
