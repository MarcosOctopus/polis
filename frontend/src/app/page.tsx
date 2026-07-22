'use client';

import { useEffect, useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import {
  MessageSquare, AlertTriangle, Clock, CheckCircle2,
  TrendingUp, MapPin, BarChart3, Users, Zap, ArrowUpRight,
  Send, Mail, Smartphone, Phone, Globe,
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  AreaChart, Area, LineChart, Line,
} from 'recharts';

type Status = 'aberto' | 'em_andamento' | 'resolvido';
type Prioridade = 'baixa' | 'média' | 'alta' | 'urgente';

interface Reclamacao {
  id: string;
  bairro: string;
  tipo: string;
  descricao: string;
  status: Status;
  prioridade: Prioridade;
  timestamp: number;
  reclamante: string;
}

const BAIRROS = ['Moema','Pinheiros','Vila Mariana','Centro','Jardins','Santo Amaro','Tatuapé','Lapa','Santana','Butantã','Capão Redondo','Brasilândia'];
const TIPOS = ['Infraestrutura','Segurança','Limpeza Urbana','Iluminação','Trânsito','Barulho','Saneamento','Transporte','Calçadas','Esgoto'];
const NOMES = ['Ana Silva','Carlos Oliveira','Mariana Costa','João Santos','Julia Lima','Pedro Almeida','Fernanda Souza','Lucas Pereira','Camila Rodrigues','Rafael Barbosa'];
const STATUS: Status[] = ['aberto','em_andamento','resolvido'];
const PRIORIDADES: Prioridade[] = ['baixa','média','alta','urgente'];

function gerarDados(): Reclamacao[] {
  const items: Reclamacao[] = [];
  const agora = Date.now();
  for (let i = 0; i < 48; i++) {
    items.push({
      id: `REC-${String(i+1).padStart(4,'0')}`,
      bairro: BAIRROS[Math.floor(Math.random() * BAIRROS.length)],
      tipo: TIPOS[Math.floor(Math.random() * TIPOS.length)],
      descricao: `${TIPOS[Math.floor(Math.random() * TIPOS.length)]} — ${['Problema crítico na região','Solicitação de reparo urgente','Moradores reclamam há semanas','Necessita intervenção imediata','Relato de ocorrência grave'][Math.floor(Math.random()*5)]}`,
      status: STATUS[Math.floor(Math.random() * 3)],
      prioridade: PRIORIDADES[Math.floor(Math.random() * 4)],
      timestamp: agora - Math.floor(Math.random() * 21600000),
      reclamante: NOMES[Math.floor(Math.random() * NOMES.length)],
    });
  }
  return items.sort((a, b) => b.timestamp - a.timestamp);
}

const DADOS_SEMANA = [
  { nome: 'Seg', reclamações: 34, resolvidas: 22 },
  { nome: 'Ter', reclamações: 41, resolvidas: 28 },
  { nome: 'Qua', reclamações: 38, resolvidas: 25 },
  { nome: 'Qui', reclamações: 52, resolvidas: 33 },
  { nome: 'Sex', reclamações: 47, resolvidas: 30 },
  { nome: 'Sáb', reclamações: 29, resolvidas: 18 },
  { nome: 'Dom', reclamações: 22, resolvidas: 14 },
];

const DADOS_HORA = [
  { hora: '06h', chamados: 8 }, { hora: '08h', chamados: 24 }, { hora: '10h', chamados: 42 },
  { hora: '12h', chamados: 35 }, { hora: '14h', chamados: 51 }, { hora: '16h', chamados: 48 },
  { hora: '18h', chamados: 32 }, { hora: '20h', chamados: 19 }, { hora: '22h', chamados: 11 },
];

export default function DashboardReclamacoes() {
  const { isAuthenticated, loading } = useAuth();
  const router = useRouter();
  const [reclamacoes] = useState(gerarDados);
  const [ultimaAtualizacao] = useState(new Date().toLocaleTimeString('pt-BR'));

  useEffect(() => {
    if (!loading && !isAuthenticated) router.push('/login');
  }, [loading, isAuthenticated, router]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
          <p className="text-sm text-gray-400">Carregando...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) return null;

  const abertas = reclamacoes.filter((r) => r.status === 'aberto').length;
  const emAndamento = reclamacoes.filter((r) => r.status === 'em_andamento').length;
  const resolvidas = reclamacoes.filter((r) => r.status === 'resolvido').length;
  const urgentes = reclamacoes.filter((r) => r.prioridade === 'urgente').length;
  const bairrosAfetados = new Set(reclamacoes.map((r) => r.bairro)).size;

  const envios = { whatsapp: 847, email: 523, sms: 391 };
  const resolvidasHoje = 124;

  // Top bairros por reclamação
  const contagemBairros = useMemo(() => {
    const m = new Map<string, number>();
    reclamacoes.forEach((r) => m.set(r.bairro, (m.get(r.bairro) || 0) + 1));
    return [...m.entries()].sort((a, b) => b[1] - a[1]).slice(0, 8).map(([nome, valor]) => ({ nome, valor }));
  }, [reclamacoes]);

  const recentes = reclamacoes.slice(0, 8);

  return (
    <div className="p-6 lg:p-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            Polis — Central de Reclamações
          </h1>
          <p className="text-sm text-gray-400 mt-1">
            Última atualização: {ultimaAtualizacao} · Dados em tempo real
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 px-4 py-2 bg-emerald-500/10 text-emerald-400 rounded-lg border border-emerald-500/20 hover:bg-emerald-500/20 transition-all text-sm font-medium">
            <Send className="w-4 h-4" />
            Novo Envio
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-cyan-500/10 text-cyan-400 rounded-lg border border-cyan-500/20 hover:bg-cyan-500/20 transition-all text-sm font-medium">
            <Zap className="w-4 h-4" />
            Nova Reclamação
          </button>
        </div>
      </div>

      {/* Métricas principais */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6 gap-4">
        <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-500 font-medium">Abertas</span>
            <AlertTriangle className="w-4 h-4 text-yellow-400" />
          </div>
          <p className="text-2xl font-bold text-white">{abertas}</p>
          <p className="text-xs text-yellow-400/70 mt-1">Aguardando atendimento</p>
        </div>
        <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-500 font-medium">Em Andamento</span>
            <Clock className="w-4 h-4 text-cyan-400" />
          </div>
          <p className="text-2xl font-bold text-white">{emAndamento}</p>
          <p className="text-xs text-cyan-400/70 mt-1">Em análise</p>
        </div>
        <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-500 font-medium">Resolvidas Hoje</span>
            <CheckCircle2 className="w-4 h-4 text-green-400" />
          </div>
          <p className="text-2xl font-bold text-white">{resolvidasHoje}</p>
          <p className="text-xs text-green-400/70 mt-1">+{resolvidas} fechadas</p>
        </div>
        <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-500 font-medium">Urgentes</span>
            <AlertTriangle className="w-4 h-4 text-red-400" />
          </div>
          <p className="text-2xl font-bold text-white">{urgentes}</p>
          <p className="text-xs text-red-400/70 mt-1">Prioridade máxima</p>
        </div>
        <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-500 font-medium">Bairros</span>
            <MapPin className="w-4 h-4 text-purple-400" />
          </div>
          <p className="text-2xl font-bold text-white">{bairrosAfetados}</p>
          <p className="text-xs text-purple-400/70 mt-1">Com ocorrências</p>
        </div>
        <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-500 font-medium">Total Período</span>
            <TrendingUp className="w-4 h-4 text-cyan-400" />
          </div>
          <p className="text-2xl font-bold text-white">{reclamacoes.length}</p>
          <p className="text-xs text-cyan-400/70 mt-1">Registradas</p>
        </div>
      </div>

      {/* Envios */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-emerald-500/5 border border-emerald-500/20 rounded-xl p-4 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-500/10 flex items-center justify-center"><Smartphone className="w-6 h-6 text-emerald-400" /></div>
          <div>
            <p className="text-xs text-gray-500 font-medium">WhatsApp Enviados</p>
            <p className="text-xl font-bold text-white">{envios.whatsapp}</p>
            <p className="text-xs text-emerald-400/70">Hoje</p>
          </div>
        </div>
        <div className="bg-purple-500/5 border border-purple-500/20 rounded-xl p-4 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center"><Mail className="w-6 h-6 text-purple-400" /></div>
          <div>
            <p className="text-xs text-gray-500 font-medium">E-mails Enviados</p>
            <p className="text-xl font-bold text-white">{envios.email}</p>
            <p className="text-xs text-purple-400/70">Hoje</p>
          </div>
        </div>
        <div className="bg-blue-500/5 border border-blue-500/20 rounded-xl p-4 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center"><Phone className="w-6 h-6 text-blue-400" /></div>
          <div>
            <p className="text-xs text-gray-500 font-medium">SMS Enviados</p>
            <p className="text-xl font-bold text-white">{envios.sms}</p>
            <p className="text-xs text-blue-400/70">Hoje</p>
          </div>
        </div>
      </div>

      {/* Gráficos + Top Bairros */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Reclamações por Dia */}
        <div className="lg:col-span-2 bg-gray-900/60 border border-gray-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-sm font-semibold text-white">Reclamações por Dia</h2>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1.5"><div className="w-3 h-3 rounded bg-cyan-500" /><span className="text-xs text-gray-500">Abertas</span></div>
              <div className="flex items-center gap-1.5"><div className="w-3 h-3 rounded bg-green-500" /><span className="text-xs text-gray-500">Resolvidas</span></div>
            </div>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={DADOS_SEMANA}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                <XAxis dataKey="nome" stroke="#6b7280" fontSize={12} tickLine={false} />
                <YAxis stroke="#6b7280" fontSize={12} tickLine={false} />
                <Tooltip contentStyle={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '8px', color: '#e4e4e7' }} />
                <Bar dataKey="reclamações" fill="#06b6d4" radius={[4,4,0,0]} name="Abertas" />
                <Bar dataKey="resolvidas" fill="#22c55e" radius={[4,4,0,0]} name="Resolvidas" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top Bairros */}
        <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-white">Top Bairros</h2>
            <MapPin className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="space-y-3">
            {contagemBairros.map((b, i) => {
              const maxVal = contagemBairros[0]?.valor || 1;
              const pct = (b.valor / maxVal) * 100;
              return (
                <div key={b.nome}>
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-gray-500 w-5">{i+1}.</span>
                      <span className="text-sm text-gray-300">{b.nome}</span>
                    </div>
                    <span className="text-xs font-mono text-gray-400">{b.valor}</span>
                  </div>
                  <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
                    <div className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-purple-500 transition-all" style={{ width: `${pct}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>


      {/* Redes Sociais — Monitoramento */}
      <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Globe className="w-5 h-5 text-purple-400" />
            <h2 className="text-sm font-semibold text-white">Monitoramento de Redes Sociais</h2>
          </div>
          <span className="text-xs text-gray-600">Últimas 24h</span>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 mb-4">
          <div className="bg-[#0a0a0f] rounded-xl p-4 border border-gray-800/50">
            <p className="text-xs text-gray-500 mb-1">Menções totais</p>
            <p className="text-2xl font-bold text-white">156</p>
            <p className="text-xs text-gray-600">+12% vs ontem</p>
          </div>
          <div className="bg-[#0a0a0f] rounded-xl p-4 border border-gray-800/50">
            <p className="text-xs text-gray-500 mb-1">😊 Positivas</p>
            <p className="text-2xl font-bold text-green-400">89</p>
            <p className="text-xs text-green-400/70">57% do total</p>
          </div>
          <div className="bg-[#0a0a0f] rounded-xl p-4 border border-gray-800/50">
            <p className="text-xs text-gray-500 mb-1">😡 Negativas</p>
            <p className="text-2xl font-bold text-red-400">47</p>
            <p className="text-xs text-red-400/70">30% do total</p>
          </div>
          <div className="bg-[#0a0a0f] rounded-xl p-4 border border-gray-800/50">
            <p className="text-xs text-gray-500 mb-1">😐 Neutras</p>
            <p className="text-2xl font-bold text-gray-400">20</p>
            <p className="text-xs text-gray-500/70">13% do total</p>
          </div>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="bg-[#0a0a0f] rounded-xl p-4 border border-gray-800/50">
            <h3 className="text-xs font-semibold text-gray-500 uppercase mb-3">Por Plataforma</h3>
            <div className="space-y-3">
              <div><div className="flex justify-between text-xs mb-1"><span className="text-gray-400">Twitter/X</span><span className="text-gray-500">72</span></div><div className="h-1.5 bg-gray-800 rounded-full"><div className="h-full w-[46%] bg-cyan-400 rounded-full" /></div></div>
              <div><div className="flex justify-between text-xs mb-1"><span className="text-gray-400">Instagram</span><span className="text-gray-500">48</span></div><div className="h-1.5 bg-gray-800 rounded-full"><div className="h-full w-[31%] bg-pink-400 rounded-full" /></div></div>
              <div><div className="flex justify-between text-xs mb-1"><span className="text-gray-400">Facebook</span><span className="text-gray-500">36</span></div><div className="h-1.5 bg-gray-800 rounded-full"><div className="h-full w-[23%] bg-blue-400 rounded-full" /></div></div>
            </div>
          </div>
          <div className="bg-[#0a0a0f] rounded-xl p-4 border border-gray-800/50">
            <h3 className="text-xs font-semibold text-gray-500 uppercase mb-3">Principais Tópicos</h3>
            <div className="space-y-2">
              <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-red-500/5"><span className="text-xs">😡</span><span className="text-xs text-gray-300">Esgoto a céu aberto</span><span className="text-xs text-gray-600 ml-auto">12 menções</span></div>
              <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-green-500/5"><span className="text-xs">😊</span><span className="text-xs text-gray-300">Nova iluminação pública</span><span className="text-xs text-gray-600 ml-auto">9 menções</span></div>
              <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-red-500/5"><span className="text-xs">😡</span><span className="text-xs text-gray-300">Ônibus superlotado</span><span className="text-xs text-gray-600 ml-auto">8 menções</span></div>
              <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-green-500/5"><span className="text-xs">😊</span><span className="text-xs text-gray-300">Coleta seletiva funciona</span><span className="text-xs text-gray-600 ml-auto">6 menções</span></div>
              <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-yellow-500/5"><span className="text-xs">😐</span><span className="text-xs text-gray-300">Reunião do conselho</span><span className="text-xs text-gray-600 ml-auto">4 menções</span></div>
            </div>
          </div>
        </div>
      </div>

      {/* Reclamações em Tempo Real */}
      <div className="bg-gray-900/60 border border-gray-800 rounded-xl">
        <div className="px-6 py-4 border-b border-gray-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            <h2 className="text-sm font-semibold text-white">Reclamações em Tempo Real</h2>
          </div>
          <button
            onClick={() => router.push('/messages')}
            className="text-xs text-cyan-400 hover:text-cyan-300 transition-colors"
          >
            Ver todas →
          </button>
        </div>
        <div className="divide-y divide-gray-800/50">
          {recentes.map((r) => {
            const diff = Date.now() - r.timestamp;
            const mins = Math.floor(diff / 60000);
            const tempo = mins < 1 ? 'Agora mesmo' : mins < 60 ? `Há ${mins} min` : `Há ${Math.floor(mins/60)}h`;
            return (
              <div key={r.id} className="flex items-center gap-4 px-6 py-3 hover:bg-gray-800/20 transition-colors">
                <div className={`w-2 h-2 rounded-full shrink-0 ${
                  r.status === 'aberto' ? 'bg-yellow-400' : r.status === 'em_andamento' ? 'bg-cyan-400' : 'bg-green-400'
                }`} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-white truncate">{r.reclamante}</span>
                    <span className="text-[10px] text-gray-600 font-mono">{r.id}</span>
                  </div>
                  <p className="text-xs text-gray-400 truncate">{r.descricao}</p>
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  <span className="text-xs text-gray-500">{r.bairro}</span>
                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                    r.prioridade === 'urgente' ? 'bg-red-500/10 text-red-400' :
                    r.prioridade === 'alta' ? 'bg-orange-500/10 text-orange-400' :
                    'bg-gray-500/10 text-gray-400'
                  }`}>{r.prioridade === 'urgente' ? 'Urgente' : r.prioridade === 'alta' ? 'Alta' : 'Normal'}</span>
                  <span className="text-xs text-gray-600">{tempo}</span>
                  <ArrowUpRight className="w-4 h-4 text-gray-600 shrink-0" />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
