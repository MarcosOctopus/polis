'use client';

import { useState, useMemo, useEffect } from 'react';
import dynamic from 'next/dynamic';
import {
  MapPin, AlertTriangle, Building2, Activity, X,
  Layers, Clock, List, CircleDot, ThumbsUp, ThumbsDown, Globe,
  MessageSquare,
} from 'lucide-react';
import type { NeighborhoodGeo, NdMapItem } from '@/components/MapaLeaflet';

const MapaLeaflet = dynamic(() => import('@/components/MapaLeaflet'), { ssr: false });

type Modo = 'todos' | 'reclamacoes' | 'elogios';
type EntryStatus = 'aberto' | 'em_andamento' | 'resolvido' | 'fechado';
type Priority = 'baixa' | 'média' | 'alta' | 'crítica';

interface Entry {
  id: string;
  bairro: string;
  tipo: string;
  descricao: string;
  status: EntryStatus;
  prioridade: Priority;
  data: string;
  modo: 'reclamacoes' | 'elogios';
}

// ── Vila Velha neighborhoods (same coordinates) ──
const BAIRROS_GEO: NeighborhoodGeo[] = [
  { id: 'centro', nome: 'Centro',
    coordinates: [[-20.326,-40.292],[-20.326,-40.284],[-20.332,-40.284],[-20.334,-40.288],[-20.332,-40.294],[-20.326,-40.292]],
    centro: [-20.329,-40.288] },
  { id: 'praia-costa', nome: 'Praia da Costa',
    coordinates: [[-20.322,-40.286],[-20.322,-40.280],[-20.328,-40.278],[-20.332,-40.280],[-20.332,-40.284],[-20.326,-40.284],[-20.322,-40.286]],
    centro: [-20.327,-40.282] },
  { id: 'itaqua', nome: 'Itapuã',
    coordinates: [[-20.304,-40.286],[-20.304,-40.278],[-20.312,-40.278],[-20.314,-40.282],[-20.312,-40.288],[-20.304,-40.286]],
    centro: [-20.308,-40.282] },
  { id: 'gloria', nome: 'Glória',
    coordinates: [[-20.332,-40.294],[-20.334,-40.288],[-20.338,-40.290],[-20.338,-40.298],[-20.334,-40.300],[-20.332,-40.294]],
    centro: [-20.335,-40.294] },
  { id: 'ibes', nome: 'Ibes',
    coordinates: [[-20.338,-40.298],[-20.338,-40.290],[-20.344,-40.292],[-20.348,-40.298],[-20.346,-40.304],[-20.340,-40.306],[-20.338,-40.298]],
    centro: [-20.343,-40.298] },
  { id: 'cobilandia', nome: 'Cobilândia',
    coordinates: [[-20.296,-40.280],[-20.296,-40.272],[-20.304,-40.270],[-20.308,-40.274],[-20.306,-40.280],[-20.304,-40.286],[-20.298,-40.284],[-20.296,-40.280]],
    centro: [-20.301,-40.278] },
  { id: 'paul', nome: 'Paul',
    coordinates: [[-20.346,-40.304],[-20.348,-40.298],[-20.354,-40.300],[-20.358,-40.306],[-20.356,-40.312],[-20.350,-40.314],[-20.346,-40.304]],
    centro: [-20.352,-40.306] },
  { id: 'jardim-marilandia', nome: 'Jd. Marilândia',
    coordinates: [[-20.314,-40.306],[-20.314,-40.298],[-20.320,-40.296],[-20.324,-40.298],[-20.326,-40.304],[-20.320,-40.308],[-20.314,-40.306]],
    centro: [-20.319,-40.302] },
  { id: 'aracas', nome: 'Araçás',
    coordinates: [[-20.310,-40.282],[-20.310,-40.274],[-20.316,-40.273],[-20.318,-40.278],[-20.314,-40.282],[-20.310,-40.282]],
    centro: [-20.313,-40.278] },
  { id: 'vila-garrido', nome: 'Vila Garrido',
    coordinates: [[-20.324,-40.298],[-20.326,-40.292],[-20.332,-40.294],[-20.334,-40.300],[-20.328,-40.304],[-20.324,-40.298]],
    centro: [-20.329,-40.298] },
];

// ── Categories ──
const TIPOS_RECLAMACAO = [
  'Saneamento básico','Iluminação pública','Buracos na via','Coleta de lixo',
  'Transporte público','Segurança','Ruído excessivo','Área verde','Calçadas','Esgoto',
];

const TIPOS_ELOGIO = [
  'Atendimento excelente','Serviço rápido','Educação e cordialidade',
  'Limpeza urbana','Organização','Infraestrutura','Segurança',
  'Proatividade','Qualidade de vida','Sustentabilidade',
  'Acessibilidade','Inovação',
];

const STATUS_CFG: Record<EntryStatus, { label: string; color: string; bg: string }> = {
  aberto: { label: 'Aberto', color: 'text-yellow-400', bg: 'bg-yellow-400/10' },
  em_andamento: { label: 'Em Andamento', color: 'text-cyan-400', bg: 'bg-cyan-400/10' },
  resolvido: { label: 'Resolvido', color: 'text-green-400', bg: 'bg-green-400/10' },
  fechado: { label: 'Fechado', color: 'text-gray-500', bg: 'bg-gray-500/10' },
};

const PRIO_CFG: Record<Priority, { label: string; color: string }> = {
  baixa: { label: 'Baixa', color: 'text-green-400' },
  média: { label: 'Média', color: 'text-yellow-400' },
  alta: { label: 'Alta', color: 'text-orange-400' },
  crítica: { label: 'Crítica', color: 'text-red-400' },
};

// ── Generate mock data ──
function genEntries(): Entry[] {
  const all: Entry[] = [];
  let id = 1;
  const statuses: EntryStatus[] = ['aberto','em_andamento','resolvido','fechado'];
  const priorities: Priority[] = ['baixa','média','alta','crítica'];

  for (const b of BAIRROS_GEO) {
    const nRec = 5 + Math.floor(Math.random() * 20);
    for (let i = 0; i < nRec; i++) {
      const d = new Date(); d.setDate(d.getDate() - Math.floor(Math.random() * 90));
      all.push({
        id: `c-${id++}`, bairro: b.nome,
        tipo: TIPOS_RECLAMACAO[Math.floor(Math.random() * TIPOS_RECLAMACAO.length)],
        descricao: `Reclamação sobre ${TIPOS_RECLAMACAO[Math.floor(Math.random() * TIPOS_RECLAMACAO.length)].toLowerCase()} em ${b.nome}`,
        status: statuses[Math.floor(Math.random() * statuses.length)],
        prioridade: priorities[Math.floor(Math.random() * priorities.length)],
        data: d.toLocaleDateString('pt-BR'),
        modo: 'reclamacoes',
      });
    }
    const nElo = 3 + Math.floor(Math.random() * 12);
    for (let i = 0; i < nElo; i++) {
      const d = new Date(); d.setDate(d.getDate() - Math.floor(Math.random() * 60));
      all.push({
        id: `e-${id++}`, bairro: b.nome,
        tipo: TIPOS_ELOGIO[Math.floor(Math.random() * TIPOS_ELOGIO.length)],
        descricao: `Elogio: ${TIPOS_ELOGIO[Math.floor(Math.random() * TIPOS_ELOGIO.length)].toLowerCase()} em ${b.nome}`,
        status: statuses[Math.floor(Math.random() * statuses.length)],
        prioridade: priorities[Math.floor(Math.random() * priorities.length)],
        data: d.toLocaleDateString('pt-BR'),
        modo: 'elogios',
      });
    }
  }
  return all;
}

// ── Helpers ──
function getFillColor(n: number, modo: Modo): string {
  // For 'todos', blend colors: green for mostly elogios, red for mostly reclamações
  if (modo === 'todos') {
    if (n <= 10) return '#22c55e';
    if (n <= 20) return '#84cc16';
    if (n <= 30) return '#eab308';
    if (n <= 40) return '#f97316';
    return '#ef4444';
  }
  if (modo === 'elogios') {
    if (n <= 4) return '#22c55e';
    if (n <= 8) return '#16a34a';
    if (n <= 12) return '#15803d';
    return '#166534';
  }
  if (n <= 8) return '#22c55e';
  if (n <= 15) return '#eab308';
  if (n <= 22) return '#f97316';
  return '#ef4444';
}

function getMarkerColor(n: number, modo: Modo): string {
  if (modo === 'todos') {
    if (n <= 10) return '#4ade80';
    if (n <= 20) return '#a3e635';
    if (n <= 30) return '#facc15';
    if (n <= 40) return '#fb923c';
    return '#f87171';
  }
  if (modo === 'elogios') {
    if (n <= 4) return '#4ade80';
    if (n <= 8) return '#22c55e';
    if (n <= 12) return '#16a34a';
    return '#15803d';
  }
  if (n <= 8) return '#22c55e';
  if (n <= 15) return '#eab308';
  if (n <= 22) return '#f97316';
  return '#ef4444';
}

function getDensityLabel(n: number, modo: Modo): string {
  if (modo === 'todos') {
    if (n <= 10) return 'Baixa atividade';
    if (n <= 20) return 'Média atividade';
    if (n <= 30) return 'Alta atividade';
    if (n <= 40) return 'Muito alta';
    return 'Crítico';
  }
  if (modo === 'elogios') {
    if (n <= 4) return 'Poucos elogios';
    if (n <= 8) return 'Bons elogios';
    if (n <= 12) return 'Muitos elogios';
    return 'Destaque!';
  }
  if (n <= 8) return 'Poucas reclamações';
  if (n <= 15) return 'Médias reclamações';
  if (n <= 22) return 'Muitas reclamações';
  return 'Crítico';
}

function topTypes(entries: Entry[], n = 3) {
  const m = new Map<string, number>();
  entries.forEach((c) => m.set(c.tipo, (m.get(c.tipo) || 0) + 1));
  return [...m.entries()].sort((a, b) => b[1] - a[1]).slice(0, n).map(([tipo, count]) => ({ tipo, count }));
}

// ── Social Media Mock Data ──
interface SocialPost {
  id: string;
  rede: string;
  texto: string;
  sentimento: 'positivo' | 'neutro' | 'negativo';
  data: string;
  bairro: string;
}

function genSocialPosts(): SocialPost[] {
  const posts: SocialPost[] = [];
  const redes = ['Twitter/X', 'Instagram', 'Facebook', 'WhatsApp'];
  const textos = [
    'O prefeito precisa fazer algo sobre o esgoto na Praia da Costa!',
    'Que bom que arrumaram a iluminação do Centro, ficou ótimo!',
    'Alguém sabe o que está acontecendo em Itapuã? Muito barulho essa noite.',
    'Atendimento maravilhoso na UBS do bairro hoje. Parabéns!',
    'Mais um dia sem coleta de lixo em Cobilândia. Inacreditável.',
    'A praia de Vila Velha está linda hoje! 💙',
    'Buraqueira na Paul, difícil até andar de carro. #Reclamação',
    'A segurança melhorou muito em Glória nos últimos meses!',
    'Alagamento na Avenida principal depois da chuva de ontem.',
    'Finalmente arrumaram a praça do bairro. As crianças amaram!',
  ];
  for (let i = 0; i < 12; i++) {
    const d = new Date(); d.setHours(d.getHours() - Math.floor(Math.random() * 48));
    posts.push({
      id: `sp-${i}`,
      rede: redes[Math.floor(Math.random() * redes.length)],
      texto: textos[Math.floor(Math.random() * textos.length)],
      sentimento: (['positivo','neutro','negativo'] as const)[Math.floor(Math.random() * 3)],
      data: d.toLocaleString('pt-BR'),
      bairro: BAIRROS_GEO[Math.floor(Math.random() * BAIRROS_GEO.length)].nome,
    });
  }
  return posts.sort((a, b) => new Date(b.data).getTime() - new Date(a.data).getTime());
}

// ── Main Component ──
export default function MapaPage() {
  const [mounted, setMounted] = useState(false);
  const [all, setAll] = useState<Entry[]>([]);
  const [socialPosts, setSocialPosts] = useState<SocialPost[]>([]);
  useEffect(() => {
    setAll(genEntries());
    setSocialPosts(genSocialPosts());
    setMounted(true);
  }, []);

  const [modo, setModo] = useState<Modo>('reclamacoes');
  const [selected, setSelected] = useState<string | null>(null);
  const [hovered, setHovered] = useState<string | null>(null);
  const [filterBairro, setFilterBairro] = useState<string | null>(null);
  const [socialTab, setSocialTab] = useState<'feed' | 'redes'>('feed');

  const filteredByModo = useMemo(() => {
    if (modo === 'todos') return all;
    return all.filter((e) => e.modo === modo);
  }, [all, modo]);

  const ndMap: NdMapItem[] = useMemo(() =>
    BAIRROS_GEO.map((n) => {
      const cs = filteredByModo.filter((e) => e.bairro === n.nome);
      return { neighborhood: n, count: cs.length };
    }), [filteredByModo]);

  const allEntries = useMemo(() => BAIRROS_GEO.map((n) => ({
    neighborhood: n,
    entries: filteredByModo.filter((e) => e.bairro === n.nome),
  })), [filteredByModo]);

  const selData = selected ? allEntries.find((n) => n.neighborhood.id === selected) ?? null : null;
  const hovData = hovered ? allEntries.find((n) => n.neighborhood.id === hovered) ?? null : null;

  const filtered = filterBairro ? filteredByModo.filter((e) => e.bairro === filterBairro) : filteredByModo;
  const ativas = mounted ? filteredByModo.filter((e) => e.status === 'aberto' || e.status === 'em_andamento').length : '—';

  let maxCount = 0, maxLabel = '—';
  for (const nd of ndMap) { if (nd.count > maxCount) { maxCount = nd.count; maxLabel = nd.neighborhood.nome; } }

  const totalEntries = mounted ? filteredByModo.length : '—';
  const totalRec = mounted ? all.filter((e) => e.modo === 'reclamacoes').length : '—';
  const totalElo = mounted ? all.filter((e) => e.modo === 'elogios').length : '—';

  const handleClick = (id: string, nome: string) => {
    const next = selected === id ? null : id;
    setSelected(next);
    setFilterBairro(next ? nome : null);
  };

  const modoLabels: Record<Modo, { label: string; labelLower: string; labelPlural: string }> = {
    todos: { label: 'Geral', labelLower: 'atividade geral', labelPlural: 'registros' },
    reclamacoes: { label: 'Reclamações', labelLower: 'reclamações', labelPlural: 'reclamações' },
    elogios: { label: 'Elogios', labelLower: 'elogios', labelPlural: 'elogios' },
  };
  const ml = modoLabels[modo];

  const legendItems = modo === 'reclamacoes'
    ? [
        { color: '#22c55e', label: 'Poucas reclamações' },
        { color: '#eab308', label: 'Médias reclamações' },
        { color: '#f97316', label: 'Muitas reclamações' },
        { color: '#ef4444', label: 'Crítico' },
      ]
    : modo === 'elogios'
    ? [
        { color: '#22c55e', label: 'Poucos elogios' },
        { color: '#16a34a', label: 'Bons elogios' },
        { color: '#15803d', label: 'Muitos elogios' },
        { color: '#166534', label: 'Destaque!' },
      ]
    : [
        { color: '#22c55e', label: 'Baixa atividade' },
        { color: '#84cc16', label: 'Média atividade' },
        { color: '#eab308', label: 'Alta atividade' },
        { color: '#f97316', label: 'Muito alta' },
        { color: '#ef4444', label: 'Crítico' },
      ];

  const modoColors: Record<Modo, string> = {
    todos: 'from-cyan-400 to-purple-500',
    reclamacoes: 'from-red-500 to-orange-500',
    elogios: 'from-green-500 to-emerald-500',
  };

  function getSocialBadge(sentimento: string) {
    if (sentimento === 'positivo') return 'text-green-400 bg-green-400/10';
    if (sentimento === 'negativo') return 'text-red-400 bg-red-400/10';
    return 'text-gray-400 bg-gray-400/10';
  }

  function getSocialIcon(sentimento: string) {
    if (sentimento === 'positivo') return '😊';
    if (sentimento === 'negativo') return '😡';
    return '😐';
  }

  const sentCounts = !mounted ? { positivo: '—', neutro: '—', negativo: '—' } : (() => {
    const c = { positivo: 0, neutro: 0, negativo: 0 };
    socialPosts.forEach((p) => c[p.sentimento]++);
    return c;
  })();

  return (
    <div className="p-6 lg:p-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between gap-3 mb-2">
        <div className="flex items-center gap-3">
          <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${modoColors[modo]} flex items-center justify-center`}>
            <MapPin className="w-4 h-4 text-white" />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-bold text-white">Mapa Interativo</h1>
            <p className="text-xs sm:text-sm text-gray-500">
              Vila Velha — {modo === 'todos' ? 'reclamações e elogios por bairro' : `${ml.labelLower} por bairro`}
            </p>
          </div>
        </div>

        {/* Mode Toggle */}
        <div className="flex items-center gap-1 bg-gray-900/60 border border-gray-800 rounded-lg p-1">
          <button
            onClick={() => { setModo('todos'); setSelected(null); setFilterBairro(null); }}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md transition-all ${
              modo === 'todos'
                ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                : 'text-gray-400 hover:text-gray-200 border border-transparent'
            }`}
          >
            <Globe className="w-3.5 h-3.5" />
            Geral
          </button>
          <button
            onClick={() => { setModo('reclamacoes'); setSelected(null); setFilterBairro(null); }}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md transition-all ${
              modo === 'reclamacoes'
                ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                : 'text-gray-400 hover:text-gray-200 border border-transparent'
            }`}
          >
            <ThumbsDown className="w-3.5 h-3.5" />
            Reclamações
          </button>
          <button
            onClick={() => { setModo('elogios'); setSelected(null); setFilterBairro(null); }}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md transition-all ${
              modo === 'elogios'
                ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                : 'text-gray-400 hover:text-gray-200 border border-transparent'
            }`}
          >
            <ThumbsUp className="w-3.5 h-3.5" />
            Elogios
          </button>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-4 flex items-center gap-3">
          <div className={`w-10 h-10 rounded-lg flex items-center justify-center bg-gradient-to-br ${modoColors[modo]} bg-opacity-10`}>
            <MessageSquare className={`w-5 h-5 text-white`} />
          </div>
          <div>
            <p className="text-xs text-gray-500 font-medium">Total {ml.label}</p>
            <p className="text-xl font-bold text-white">{totalEntries}</p>
          </div>
        </div>
        <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-4 flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-red-400/10 flex items-center justify-center">
            <ThumbsDown className="w-5 h-5 text-red-400" />
          </div>
          <div>
            <p className="text-xs text-gray-500 font-medium">Reclamações</p>
            <p className="text-xl font-bold text-white">{totalRec}</p>
          </div>
        </div>
        <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-4 flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-green-400/10 flex items-center justify-center">
            <ThumbsUp className="w-5 h-5 text-green-400" />
          </div>
          <div>
            <p className="text-xs text-gray-500 font-medium">Elogios</p>
            <p className="text-xl font-bold text-white">{totalElo}</p>
          </div>
        </div>
        <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-4 flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-cyan-400/10 flex items-center justify-center">
            <Activity className="w-5 h-5 text-cyan-400" />
          </div>
          <div>
            <p className="text-xs text-gray-500 font-medium">Ativas(os)</p>
            <p className="text-xl font-bold text-white">{ativas}</p>
          </div>
        </div>
      </div>

      {/* Map + Sidebar */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-gray-900/60 border border-gray-800 rounded-xl p-1 overflow-hidden">
          <MapaLeaflet
            centro={[-20.329, -40.287]}
            zoom={12.5}
            ndMap={ndMap}
            selected={selected}
            hovered={hovered}
            onPolygonClick={handleClick}
            onHoverChange={setHovered}
            getFillColor={(n: number) => getFillColor(n, modo)}
            getStrokeColor={(id: string) => {
              if (selected === id) return '#22d3ee';
              if (hovered === id) return '#a78bfa';
              return '#374151';
            }}
            getMarkerColor={(n: number) => getMarkerColor(n, modo)}
          />
        </div>

        <div className="space-y-4">
          {/* Legend */}
          <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-4">
            <h3 className="text-sm font-semibold text-gray-300 mb-3 flex items-center gap-2">
              <Layers className="w-4 h-4 text-cyan-400" /> Legenda
            </h3>
            <div className="space-y-2">
              {legendItems.map((item) => (
                <div key={item.label} className="flex items-center gap-2">
                  <div className="w-5 h-5 rounded-full" style={{ backgroundColor: item.color }} />
                  <span className="text-xs text-gray-400">{item.label}</span>
                </div>
              ))}
            </div>
            <div className="mt-4 pt-3 border-t border-gray-800">
              <p className="text-xs text-gray-500 mb-2 flex items-center gap-1">
                <CircleDot className="w-3 h-3" /> Densidade
              </p>
              <div className="flex items-center gap-2">
                {legendItems.map((item) => (
                  <div key={item.color} className="h-2 w-6 rounded" style={{ backgroundColor: item.color }} />
                ))}
                <span className="text-[10px] text-gray-600 ml-1">Baixa → Alta</span>
              </div>
            </div>
          </div>

          {/* Selected neighborhood detail */}
          {selData && (
            <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Building2 className="w-5 h-5 text-cyan-400" />
                  <h3 className="text-base font-bold text-white">{selData.neighborhood.nome}</h3>
                </div>
                <button
                  onClick={() => { setSelected(null); setFilterBairro(null); }}
                  className="p-1 rounded-lg hover:bg-gray-800 text-gray-500"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              <div className="bg-[#0a0a0f] rounded-lg p-3 mb-3 flex items-center justify-between">
                <span className="text-sm text-gray-400">Total</span>
                <span className="text-2xl font-bold text-white">{selData.entries.length}</span>
              </div>
              <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">
                Principais {modo === 'elogios' ? 'Categorias' : 'Tipos'}
              </h4>
              <div className="space-y-1.5 mb-3">
                {topTypes(selData.entries).map((t, i) => (
                  <div key={t.tipo} className="flex items-center justify-between px-2 py-1.5 rounded-lg bg-[#0a0a0f]">
                    <span className="text-xs text-gray-500 w-4">{i+1}.</span>
                    <span className="text-sm text-gray-300">{t.tipo}</span>
                    <span className="text-xs font-mono text-gray-500">{t.count}</span>
                  </div>
                ))}
              </div>
              <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">Recentes</h4>
              <div className="space-y-2">
                {[...selData.entries]
                  .sort((a, b) => {
                    const da = a.data.split('/').reverse().join('-');
                    const db = b.data.split('/').reverse().join('-');
                    return new Date(db).getTime() - new Date(da).getTime();
                  })
                  .slice(0, 3)
                  .map((c) => (
                    <div key={c.id} className="px-3 py-2 rounded-lg bg-[#0a0a0f] border border-gray-800/50">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-medium text-gray-300">{c.tipo}</span>
                        <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded-full ${STATUS_CFG[c.status].bg} ${STATUS_CFG[c.status].color}`}>
                          {STATUS_CFG[c.status].label}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-[11px] text-gray-500 flex items-center gap-1">
                          <Clock className="w-3 h-3" />{c.data}
                        </span>
                        <span className={`text-[10px] font-medium ${PRIO_CFG[c.prioridade].color}`}>
                          {PRIO_CFG[c.prioridade].label}
                        </span>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          )}

          {/* Social Media Feed — só renderiza após mount pra evitar hydration mismatch */}
          {mounted && (
            <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-semibold text-gray-300 flex items-center gap-2">
                  <Globe className="w-4 h-4 text-purple-400" /> Redes Sociais
                </h3>
                <span className="text-[10px] text-gray-600">Últimas 24h</span>
              </div>

              {/* Sentiment Summary */}
              <div className="grid grid-cols-3 gap-2 mb-3">
                <div className="bg-green-400/5 rounded-lg p-2 text-center">
                  <span className="text-lg">{sentCounts.positivo}</span>
                  <p className="text-[10px] text-gray-500">😊 Positivo</p>
                </div>
                <div className="bg-yellow-400/5 rounded-lg p-2 text-center">
                  <span className="text-lg">{sentCounts.neutro}</span>
                  <p className="text-[10px] text-gray-500">😐 Neutro</p>
                </div>
                <div className="bg-red-400/5 rounded-lg p-2 text-center">
                  <span className="text-lg">{sentCounts.negativo}</span>
                  <p className="text-[10px] text-gray-500">😡 Negativo</p>
                </div>
              </div>

              {/* Posts */}
              <div className="space-y-2 max-h-64 overflow-y-auto custom-scrollbar">
                {socialPosts.slice(0, 6).map((post) => (
                  <div key={post.id} className="bg-[#0a0a0f] rounded-lg p-3 border border-gray-800/30">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-[10px] text-gray-600">{post.rede}</span>
                      <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${getSocialBadge(post.sentimento)}`}>
                        {getSocialIcon(post.sentimento)} {post.sentimento}
                      </span>
                    </div>
                    <p className="text-xs text-gray-300 leading-relaxed">{post.texto}</p>
                    <div className="flex items-center justify-between mt-1.5">
                      <span className="text-[10px] text-gray-600">{post.bairro}</span>
                      <span className="text-[10px] text-gray-700">{post.data}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Table */}
      <div className="bg-gray-900/60 border border-gray-800 rounded-xl overflow-hidden">
        <div className="px-4 py-3 border-b border-gray-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <List className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-semibold text-white">
              {filterBairro ? `${ml.label} — ${filterBairro}` : `Todas ${
                modo === 'todos' ? 'as reclamações e elogios' : `as ${ml.labelLower}`
              }`}
            </h3>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500">{filtered.length} registro(s)</span>
            {filterBairro && (
              <button
                onClick={() => { setFilterBairro(null); setSelected(null); }}
                className="text-xs text-cyan-400 hover:text-cyan-300 underline"
              >
                Limpar filtro
              </button>
            )}
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-800/60">
                <th className="text-left px-4 py-2.5 text-[11px] font-semibold text-gray-500 uppercase">Bairro</th>
                <th className="text-left px-4 py-2.5 text-[11px] font-semibold text-gray-500 uppercase">Categoria</th>
                <th className="text-left px-4 py-2.5 text-[11px] font-semibold text-gray-500 uppercase">Status</th>
                <th className="text-left px-4 py-2.5 text-[11px] font-semibold text-gray-500 uppercase">Prioridade</th>
                <th className="text-left px-4 py-2.5 text-[11px] font-semibold text-gray-500 uppercase">Data</th>
                {modo === 'todos' && (
                  <th className="text-left px-4 py-2.5 text-[11px] font-semibold text-gray-500 uppercase">Tipo</th>
                )}
              </tr>
            </thead>
            <tbody>
              {filtered.map((c) => (
                <tr key={c.id} className="border-b border-gray-800/30 hover:bg-gray-800/20 transition-colors">
                  <td className="px-4 py-2.5 text-gray-300 font-medium">{c.bairro}</td>
                  <td className="px-4 py-2.5 text-gray-400">{c.tipo}</td>
                  <td className="px-4 py-2.5">
                    <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-full ${STATUS_CFG[c.status].bg} ${STATUS_CFG[c.status].color}`}>
                      {STATUS_CFG[c.status].label}
                    </span>
                  </td>
                  <td className={`px-4 py-2.5 text-xs font-semibold ${PRIO_CFG[c.prioridade].color}`}>
                    {PRIO_CFG[c.prioridade].label}
                  </td>
                  <td className="px-4 py-2.5 text-gray-500 text-xs">{c.data}</td>
                  {modo === 'todos' && (
                    <td className={`px-4 py-2.5 text-xs font-medium ${
                      c.modo === 'elogios' ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {c.modo === 'elogios' ? '✅ Elogio' : '⚠️ Reclamação'}
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {filtered.length === 0 && (
          <div className="py-12 text-center text-gray-600 text-sm">Nenhum registro encontrado.</div>
        )}
      </div>
    </div>
  );
}
