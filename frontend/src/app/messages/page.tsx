'use client';

import { useState, useMemo, useEffect, useRef } from 'react';
import {
  MessageSquare,
  Send,
  Search,
  Filter,
  Phone,
  Mail,
  Smartphone,
  AlertCircle,
  CheckCircle2,
  Clock,
  Loader2,
  Plus,
  FileText,
  Download,
  ChevronDown,
  X,
  MessageCircle,
  Zap,
  ArrowUpRight,
  MapPin,
  Tag,
  User,
} from 'lucide-react';

/* ───── Types ───── */

type StatusReclamacao = 'aberto' | 'em_andamento' | 'resolvido';
type Prioridade = 'baixa' | 'média' | 'alta' | 'urgente';
type TipoReclamacao =
  | 'Infraestrutura'
  | 'Segurança'
  | 'Limpeza'
  | 'Iluminação'
  | 'Trânsito'
  | 'Barulho'
  | 'Outro';
type ComunicacaoTab = 'whatsapp' | 'email' | 'sms';
type EnvioStatus = 'enviado' | 'falhou' | 'pendente';

type Reclamacao = {
  id: string;
  timestamp: Date;
  bairro: string;
  tipo: TipoReclamacao;
  descricao: string;
  status: StatusReclamacao;
  prioridade: Prioridade;
  nome: string;
};

type Envio = {
  id: string;
  tipo: ComunicacaoTab;
  destino: string;
  mensagem: string;
  status: EnvioStatus;
  timestamp: Date;
};

type NovaReclamacaoForm = {
  nome: string;
  telefone: string;
  bairro: string;
  tipo: TipoReclamacao;
  descricao: string;
  prioridade: Prioridade;
};

/* ───── Mock data generators ───── */

const bairrosSP = [
  'Moema',
  'Pinheiros',
  'Vila Mariana',
  'Jardins',
  'Centro',
  'Santo Amaro',
  'Tatuapé',
  'Butantã',
  'Liberdade',
  'Santana',
  'Perdizes',
  'Vila Madalena',
  'Itaim Bibi',
  'Brooklin',
  'Morumbi',
  'Lapa',
  'Bela Vista',
  'Jardim Paulista',
  'Alto de Pinheiros',
  'Campo Belo',
];

const tipos: TipoReclamacao[] = [
  'Infraestrutura',
  'Segurança',
  'Limpeza',
  'Iluminação',
  'Trânsito',
  'Barulho',
  'Outro',
];

const prioridades: Prioridade[] = ['baixa', 'média', 'alta', 'urgente'];
const statusList: StatusReclamacao[] = ['aberto', 'em_andamento', 'resolvido'];

const nomes = [
  'Carlos Silva',
  'Ana Oliveira',
  'Pedro Santos',
  'Maria Costa',
  'João Lima',
  'Fernanda Souza',
  'Lucas Almeida',
  'Juliana Pereira',
  'Rafael Martins',
  'Camila Rocha',
  'Bruno Barbosa',
  'Larissa Dias',
  'Gabriel Nunes',
  'Amanda Carvalho',
  'Diego Rodrigues',
  'Letícia Gomes',
  'Thiago Fernandes',
  'Vanessa Ribeiro',
  'Eduardo Campos',
  'Patrícia Azevedo',
];

const descricoes = [
  'Buraco na via pública próximo à calçada, perigoso para pedestres e veículos',
  'Poste de iluminação apagado há mais de uma semana, rua completamente escura',
  'Acúmulo de lixo na esquina, com mau cheiro e presença de ratos',
  'Pista escorregadia após obra mal finalizada na avenida principal',
  'Som alto vindo de obra irregular após as 22h, perturbação do sossego',
  'Semaforo quebrado no cruzamento, trânsito intenso e risco de acidentes',
  'Falta de coleta seletiva no bairro há mais de 15 dias',
  'Árvore caída após temporal, bloqueando parcialmente a rua',
  'Esgoto a céu aberto na rua de trás, risco de doenças',
  'Ponto de ônibus sem cobertura, passageiros expostos à chuva e sol',
  'Crackozinhos fazendo uso de drogas na praça, moradores com medo',
  'Calçada irregular com degrau alto, cadeirantes não conseguem passar',
  'Obra pública abandonada no final da rua, acumula sujeira e entulho',
  'Rua sem sinalização de mão única, motoristas entram na contramão',
  'Fiação elétrica baixa e solta, risco de choque em dias de chuva',
  'Praça sem manutenção, brinquedos quebrados e mato alto',
  'Vazamento de água há dias na esquina, desperdício e poça enorme',
  'Falta de faixa de pedestres perto da escola, crianças atravessam no risco',
  'Rua esburacada após serviço da SABESP mal finalizado',
  'Terreno baldio com mato alto e entulho, foco de dengue e animais peçonhentos',
];

const telefones = [
  '(11) 91234-5678',
  '(11) 97654-3210',
  '(11) 98877-6655',
  '(11) 95544-3322',
  '(11) 99988-7766',
  '(11) 94433-2211',
  '(11) 97766-5544',
  '(11) 93322-1100',
  '(11) 91234-4321',
  '(11) 99887-6655',
];

const emails = [
  'contato@sp.gov.br',
  'ouvidoria@prefeitura.sp.gov.br',
  'subprefeitura.pinheiros@sp.gov.br',
  'zeze@uol.com.br',
  'joaopereira@gmail.com',
  'carlosdasilva@outlook.com',
];

function randomItem<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
}

function randomDateRecent(): Date {
  const now = Date.now();
  const range = 4 * 60 * 60 * 1000; // last 4 hours
  return new Date(now - Math.random() * range);
}

function generateMockComplaints(count: number): Reclamacao[] {
  const result: Reclamacao[] = [];
  for (let i = 0; i < count; i++) {
    const status: StatusReclamacao = randomItem(statusList);
    const prioridade: Prioridade =
      status === 'resolvido'
        ? (randomItem(['baixa', 'média']) as Prioridade)
        : randomItem(prioridades);
    result.push({
      id: `REC-${String(i + 1).padStart(4, '0')}`,
      timestamp: randomDateRecent(),
      bairro: randomItem(bairrosSP),
      tipo: randomItem(tipos),
      descricao: randomItem(descricoes),
      status,
      prioridade,
      nome: randomItem(nomes),
    });
  }
  return result.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
}

function timeAgo(date: Date): string {
  const seconds = Math.floor((Date.now() - date.getTime()) / 1000);
  if (seconds < 60) return 'agora mesmo';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes} min atrás`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h atrás`;
  const days = Math.floor(hours / 24);
  return `${days}d atrás`;
}

/* ───── Status config ───── */

const statusConfig: Record<
  StatusReclamacao,
  { label: string; color: string; bg: string; dot: string }
> = {
  aberto: {
    label: 'Aberto',
    color: 'text-yellow-400',
    bg: 'bg-yellow-500/10 border-yellow-500/20',
    dot: 'bg-yellow-400',
  },
  em_andamento: {
    label: 'Em Andamento',
    color: 'text-blue-400',
    bg: 'bg-blue-500/10 border-blue-500/20',
    dot: 'bg-blue-400',
  },
  resolvido: {
    label: 'Resolvido',
    color: 'text-emerald-400',
    bg: 'bg-emerald-500/10 border-emerald-500/20',
    dot: 'bg-emerald-400',
  },
};

const prioridadeConfig: Record<
  Prioridade,
  { label: string; color: string; bg: string }
> = {
  baixa: {
    label: 'Baixa',
    color: 'text-gray-400',
    bg: 'bg-gray-700/40 border-gray-600',
  },
  média: {
    label: 'Média',
    color: 'text-yellow-400',
    bg: 'bg-yellow-500/10 border-yellow-500/20',
  },
  alta: {
    label: 'Alta',
    color: 'text-orange-400',
    bg: 'bg-orange-500/10 border-orange-500/20',
  },
  urgente: {
    label: 'Urgente',
    color: 'text-red-400',
    bg: 'bg-red-500/10 border-red-500/20',
  },
};

const tipoConfig: Record<TipoReclamacao, { color: string; bg: string }> = {
  Infraestrutura: { color: 'text-cyan-400', bg: 'bg-cyan-500/10' },
  Segurança: { color: 'text-red-400', bg: 'bg-red-500/10' },
  Limpeza: { color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
  Iluminação: { color: 'text-yellow-400', bg: 'bg-yellow-500/10' },
  Trânsito: { color: 'text-orange-400', bg: 'bg-orange-500/10' },
  Barulho: { color: 'text-purple-400', bg: 'bg-purple-500/10' },
  Outro: { color: 'text-gray-400', bg: 'bg-gray-500/10' },
};

const envioStatusConfig: Record<
  EnvioStatus,
  { icon: typeof CheckCircle2; label: string; color: string }
> = {
  enviado: {
    icon: CheckCircle2,
    label: 'Enviado',
    color: 'text-emerald-400',
  },
  falhou: {
    icon: AlertCircle,
    label: 'Falhou',
    color: 'text-red-400',
  },
  pendente: {
    icon: Loader2,
    label: 'Pendente',
    color: 'text-yellow-400',
  },
};

/* ───── Initial mock data ───── */

const INITIAL_COMPLAINTS = generateMockComplaints(24);

const initialEnvioHistory: Envio[] = [
  {
    id: 'ENV-001',
    tipo: 'whatsapp',
    destino: '(11) 91234-5678',
    mensagem: 'Sua reclamação REC-0001 foi registrada. Protocolo: #1234',
    status: 'enviado',
    timestamp: new Date(Date.now() - 5 * 60 * 1000),
  },
  {
    id: 'ENV-002',
    tipo: 'email',
    destino: 'contato@sp.gov.br',
    mensagem: 'Relatório diário de reclamações - 22/07/2026',
    status: 'enviado',
    timestamp: new Date(Date.now() - 15 * 60 * 1000),
  },
  {
    id: 'ENV-003',
    tipo: 'sms',
    destino: '(11) 97654-3210',
    mensagem: 'Atualização: sua reclamação REC-0003 foi resolvida.',
    status: 'falhou',
    timestamp: new Date(Date.now() - 30 * 60 * 1000),
  },
  {
    id: 'ENV-004',
    tipo: 'whatsapp',
    destino: '(11) 98877-6655',
    mensagem: 'Confirmação de recebimento - Reclamação REC-0005',
    status: 'pendente',
    timestamp: new Date(Date.now() - 2 * 60 * 1000),
  },
];

/* ───── Priority ordering for sorting ───── */

const priorityOrder: Record<Prioridade, number> = {
  urgente: 0,
  alta: 1,
  média: 2,
  baixa: 3,
};

/* ───── Page component ───── */

export default function MessagesPage() {
  const [complaints, setComplaints] = useState<Reclamacao[]>(INITIAL_COMPLAINTS);
  const [activeStatusTab, setActiveStatusTab] = useState<string>('todas');
  const [searchQuery, setSearchQuery] = useState('');
  const [commsTab, setCommsTab] = useState<ComunicacaoTab>('whatsapp');
  const [envioHistory, setEnvioHistory] = useState<Envio[]>(initialEnvioHistory);
  const [showNewForm, setShowNewForm] = useState(false);
  const [showSendPanel, setShowSendPanel] = useState(false);

  /* ───── WhatsApp state ───── */
  const [whatsPhone, setWhatsPhone] = useState('');
  const [whatsMsg, setWhatsMsg] = useState('');
  const [whatsSending, setWhatsSending] = useState(false);

  /* ───── Email state ───── */
  const [emailTo, setEmailTo] = useState('');
  const [emailSubject, setEmailSubject] = useState('');
  const [emailMsg, setEmailMsg] = useState('');
  const [emailSending, setEmailSending] = useState(false);

  /* ───── SMS state ───── */
  const [smsPhone, setSmsPhone] = useState('');
  const [smsMsg, setSmsMsg] = useState('');
  const [smsSending, setSmsSending] = useState(false);

  /* ───── New complaint form ───── */
  const [newForm, setNewForm] = useState<NovaReclamacaoForm>({
    nome: '',
    telefone: '',
    bairro: '',
    tipo: 'Outro',
    descricao: '',
    prioridade: 'média',
  });
  const [formSubmitting, setFormSubmitting] = useState(false);

  const formRef = useRef<HTMLDivElement>(null);

  /* ───── Stats ───── */
  const hojeTotal = useMemo(
    () => complaints.filter((c) => {
      const now = new Date();
      return c.timestamp.toDateString() === now.toDateString();
    }).length,
    [complaints]
  );

  const stats = useMemo(
    () => [
      {
        label: 'Total de reclamações (hoje)',
        value: hojeTotal,
        icon: MessageSquare,
        color: 'text-cyan-400',
        bg: 'bg-cyan-500/10',
        border: 'border-cyan-500/20',
      },
      {
        label: 'WhatsApp enviados',
        value: envioHistory.filter((e) => e.tipo === 'whatsapp' && e.status === 'enviado').length,
        icon: MessageCircle,
        color: 'text-emerald-400',
        bg: 'bg-emerald-500/10',
        border: 'border-emerald-500/20',
      },
      {
        label: 'E-mails enviados',
        value: envioHistory.filter((e) => e.tipo === 'email' && e.status === 'enviado').length,
        icon: Mail,
        color: 'text-purple-400',
        bg: 'bg-purple-500/10',
        border: 'border-purple-500/20',
      },
      {
        label: 'SMS enviados',
        value: envioHistory.filter((e) => e.tipo === 'sms' && e.status === 'enviado').length,
        icon: Smartphone,
        color: 'text-blue-400',
        bg: 'bg-blue-500/10',
        border: 'border-blue-500/20',
      },
    ],
    [hojeTotal, envioHistory]
  );

  /* ───── Filtered complaints ───── */
  const filteredComplaints = useMemo(() => {
    return complaints
      .filter((c) => {
        if (activeStatusTab === 'todas') return true;
        return c.status === activeStatusTab;
      })
      .filter((c) => {
        if (!searchQuery) return true;
        const q = searchQuery.toLowerCase();
        return (
          c.id.toLowerCase().includes(q) ||
          c.bairro.toLowerCase().includes(q) ||
          c.tipo.toLowerCase().includes(q) ||
          c.descricao.toLowerCase().includes(q) ||
          c.nome.toLowerCase().includes(q)
        );
      })
      .sort(
        (a, b) =>
          priorityOrder[a.prioridade] - priorityOrder[b.prioridade] ||
          b.timestamp.getTime() - a.timestamp.getTime()
      );
  }, [complaints, activeStatusTab, searchQuery]);

  /* ───── Filter tabs ───── */
  const statusTabs: { key: string; label: string }[] = [
    { key: 'todas', label: 'Todas' },
    { key: 'aberto', label: 'Abertas' },
    { key: 'em_andamento', label: 'Em Andamento' },
    { key: 'resolvido', label: 'Resolvidas' },
  ];

  /* ───── Send helpers ───── */
  function simulateSend(
    tipo: ComunicacaoTab,
    destino: string,
    mensagem: string,
    setSending: (v: boolean) => void,
  ) {
    if (!destino.trim() || !mensagem.trim()) return;
    setSending(true);
    const newEnvio: Envio = {
      id: `ENV-${String(envioHistory.length + 1).padStart(3, '0')}`,
      tipo,
      destino: destino.trim(),
      mensagem: mensagem.trim(),
      status: 'pendente',
      timestamp: new Date(),
    };
    setEnvioHistory((prev) => [newEnvio, ...prev]);

    setTimeout(() => {
      const succeeded = Math.random() > 0.25;
      setEnvioHistory((prev) =>
        prev.map((e) =>
          e.id === newEnvio.id
            ? { ...e, status: succeeded ? ('enviado' as EnvioStatus) : ('falhou' as EnvioStatus) }
            : e,
        ),
      );
      setSending(false);
    }, 1500 + Math.random() * 1500);
  }

  function sendWhatsApp() {
    simulateSend('whatsapp', whatsPhone, whatsMsg, setWhatsSending);
    setWhatsPhone('');
    setWhatsMsg('');
  }

  function sendEmail() {
    const fullMsg = `Assunto: ${emailSubject}\n\n${emailMsg}`;
    simulateSend('email', emailTo, fullMsg, setEmailSending);
    setEmailTo('');
    setEmailSubject('');
    setEmailMsg('');
  }

  function sendSMS() {
    simulateSend('sms', smsPhone, smsMsg, setSmsSending);
    setSmsPhone('');
    setSmsMsg('');
  }

  /* ───── New complaint form ───── */
  function handleNewFormSubmit() {
    if (
      !newForm.nome.trim() ||
      !newForm.bairro.trim() ||
      !newForm.descricao.trim()
    )
      return;
    setFormSubmitting(true);

    const nova: Reclamacao = {
      id: `REC-${String(complaints.length + 1).padStart(4, '0')}`,
      timestamp: new Date(),
      bairro: newForm.bairro.trim(),
      tipo: newForm.tipo,
      descricao: newForm.descricao.trim(),
      status: 'aberto',
      prioridade: newForm.prioridade,
      nome: newForm.nome.trim(),
    };

    setTimeout(() => {
      setComplaints((prev) => [nova, ...prev]);
      setNewForm({
        nome: '',
        telefone: '',
        bairro: '',
        tipo: 'Outro',
        descricao: '',
        prioridade: 'média',
      });
      setShowNewForm(false);
      setFormSubmitting(false);
    }, 800);
  }

  /* ───── Auto-scroll to form ───── */
  useEffect(() => {
    if (showNewForm && formRef.current) {
      formRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }, [showNewForm]);

  return (
    <div className="p-6 lg:p-8 space-y-6">
      {/* ─── Header ─── */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Mensagens</h1>
          <p className="text-sm text-gray-400 mt-1">
            Feed de reclamações em tempo real
          </p>
        </div>
        <button
          onClick={() => setShowSendPanel(!showSendPanel)}
          className="flex items-center gap-2 px-4 py-2 bg-cyan-500/10 text-cyan-400 rounded-lg border border-cyan-500/20 hover:bg-cyan-500/20 transition-all text-sm font-medium lg:hidden"
        >
          <Send className="w-4 h-4" />
          {showSendPanel ? 'Fechar Painel' : 'Enviar Mensagem'}
        </button>
      </div>

      {/* ─── Stats row ─── */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {stats.map((s) => {
          const Icon = s.icon;
          return (
            <div
              key={s.label}
              className={`${s.bg} ${s.border} border rounded-xl p-4 flex items-center gap-3`}
            >
              <div className={`${s.color} ${s.bg} p-2.5 rounded-lg shrink-0`}>
                <Icon className="w-4 h-4" />
              </div>
              <div className="min-w-0">
                <p className="text-xl font-bold text-white">{s.value}</p>
                <p className="text-[10px] text-gray-400 leading-tight truncate">
                  {s.label}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {/* ─── Quick Actions ─── */}
      <div className="flex items-center gap-3 flex-wrap">
        <button
          onClick={() => setShowNewForm(!showNewForm)}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-all text-sm font-medium ${
            showNewForm
              ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40'
              : 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20 hover:bg-cyan-500/20'
          }`}
        >
          {showNewForm ? (
            <X className="w-4 h-4" />
          ) : (
            <Plus className="w-4 h-4" />
          )}
          Nova Reclamação
        </button>
        <button className="flex items-center gap-2 px-4 py-2 bg-purple-500/10 text-purple-400 rounded-lg border border-purple-500/20 hover:bg-purple-500/20 transition-all text-sm font-medium">
          <FileText className="w-4 h-4" />
          Relatório Diário
        </button>
        <button className="flex items-center gap-2 px-4 py-2 bg-blue-500/10 text-blue-400 rounded-lg border border-blue-500/20 hover:bg-blue-500/20 transition-all text-sm font-medium">
          <Download className="w-4 h-4" />
          Exportar CSV
        </button>
      </div>

      {/* ─── Inline New Complaint Form ─── */}
      <div
        ref={formRef}
        className={`overflow-hidden transition-all duration-300 ease-in-out ${
          showNewForm ? 'max-h-[600px] opacity-100' : 'max-h-0 opacity-0'
        }`}
      >
        <div className="bg-gray-900/60 border border-cyan-500/30 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              <Plus className="w-4 h-4 text-cyan-400" />
              Nova Reclamação
            </h3>
            <button
              onClick={() => setShowNewForm(false)}
              className="p-1 rounded-lg text-gray-500 hover:text-white hover:bg-gray-800 transition-all"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs text-gray-400 font-medium">Nome</label>
              <input
                type="text"
                placeholder="Nome do reclamante"
                value={newForm.nome}
                onChange={(e) =>
                  setNewForm((prev) => ({ ...prev, nome: e.target.value }))
                }
                className="w-full px-3 py-2 bg-gray-800/50 border border-gray-700 rounded-lg text-white text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/40 focus:border-cyan-500/50 transition-all"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs text-gray-400 font-medium">
                Telefone
              </label>
              <input
                type="text"
                placeholder="(11) 99999-9999"
                value={newForm.telefone}
                onChange={(e) =>
                  setNewForm((prev) => ({ ...prev, telefone: e.target.value }))
                }
                className="w-full px-3 py-2 bg-gray-800/50 border border-gray-700 rounded-lg text-white text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/40 focus:border-cyan-500/50 transition-all"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs text-gray-400 font-medium">Bairro</label>
              <select
                value={newForm.bairro}
                onChange={(e) =>
                  setNewForm((prev) => ({ ...prev, bairro: e.target.value }))
                }
                className="w-full px-3 py-2 bg-gray-800/50 border border-gray-700 rounded-lg text-white text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/40 focus:border-cyan-500/50 transition-all appearance-none"
              >
                <option value="" disabled>
                  Selecione o bairro
                </option>
                {bairrosSP.map((b) => (
                  <option key={b} value={b}>
                    {b}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-1.5">
              <label className="text-xs text-gray-400 font-medium">Tipo</label>
              <select
                value={newForm.tipo}
                onChange={(e) =>
                  setNewForm((prev) => ({
                    ...prev,
                    tipo: e.target.value as TipoReclamacao,
                  }))
                }
                className="w-full px-3 py-2 bg-gray-800/50 border border-gray-700 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/40 focus:border-cyan-500/50 transition-all appearance-none"
              >
                {tipos.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-1.5 sm:col-span-2">
              <label className="text-xs text-gray-400 font-medium">
                Descrição
              </label>
              <textarea
                placeholder="Descreva o problema..."
                rows={3}
                value={newForm.descricao}
                onChange={(e) =>
                  setNewForm((prev) => ({ ...prev, descricao: e.target.value }))
                }
                className="w-full px-3 py-2 bg-gray-800/50 border border-gray-700 rounded-lg text-white text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/40 focus:border-cyan-500/50 transition-all resize-none"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs text-gray-400 font-medium">
                Prioridade
              </label>
              <select
                value={newForm.prioridade}
                onChange={(e) =>
                  setNewForm((prev) => ({
                    ...prev,
                    prioridade: e.target.value as Prioridade,
                  }))
                }
                className="w-full px-3 py-2 bg-gray-800/50 border border-gray-700 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/40 focus:border-cyan-500/50 transition-all appearance-none"
              >
                {prioridades.map((p) => (
                  <option key={p} value={p}>
                    {p.charAt(0).toUpperCase() + p.slice(1)}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button
              onClick={() => setShowNewForm(false)}
              className="px-4 py-2 text-sm text-gray-400 hover:text-white transition-all"
            >
              Cancelar
            </button>
            <button
              onClick={handleNewFormSubmit}
              disabled={
                formSubmitting ||
                !newForm.nome.trim() ||
                !newForm.bairro.trim() ||
                !newForm.descricao.trim()
              }
              className="flex items-center gap-2 px-5 py-2 bg-cyan-500/10 text-cyan-400 rounded-lg border border-cyan-500/20 hover:bg-cyan-500/20 transition-all text-sm font-medium disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {formSubmitting ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Zap className="w-4 h-4" />
              )}
              {formSubmitting ? 'Registrando...' : 'Registrar'}
            </button>
          </div>
        </div>
      </div>

      {/* ─── Main Grid ─── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* ─── Left: Complaint Feed (2/3) ─── */}
        <div className="lg:col-span-2 space-y-4">
          {/* ─── Filter bar ─── */}
          <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-4 space-y-3">
            {/* Tabs */}
            <div className="flex gap-1 bg-gray-800/50 rounded-lg p-1 overflow-x-auto">
              {statusTabs.map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setActiveStatusTab(tab.key)}
                  className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all whitespace-nowrap ${
                    activeStatusTab === tab.key
                      ? 'bg-cyan-500/20 text-cyan-400 shadow-sm'
                      : 'text-gray-400 hover:text-white'
                  }`}
                >
                  {tab.label}
                  {tab.key !== 'todas' && (
                    <span className="ml-1.5 text-[10px] opacity-60">
                      ({complaints.filter((c) => c.status === tab.key).length})
                    </span>
                  )}
                </button>
              ))}
            </div>

            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input
                type="text"
                placeholder="Buscar reclamações por bairro, tipo, descrição..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-4 py-2 bg-gray-800/50 border border-gray-700 rounded-lg text-white text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/40 focus:border-cyan-500/50 transition-all"
              />
            </div>
          </div>

          {/* ─── Feed ─── */}
          <div className="space-y-3 max-h-[calc(100vh-420px)] overflow-y-auto pr-1 scrollbar-thin">
            {filteredComplaints.length === 0 ? (
              <div className="flex flex-col items-center py-16 text-gray-500">
                <MessageSquare className="w-10 h-10 mb-3 opacity-40" />
                <p className="text-sm">Nenhuma reclamação encontrada</p>
              </div>
            ) : (
              filteredComplaints.map((complaint, index) => {
                const sConfig = statusConfig[complaint.status];
                const pConfig = prioridadeConfig[complaint.prioridade];
                const tConfig = tipoConfig[complaint.tipo];
                return (
                  <div
                    key={complaint.id}
                    className="bg-gray-900/60 border border-gray-800 rounded-xl p-4 hover:border-gray-700 transition-all group animate-in"
                    style={{
                      animation: `slideFadeIn 0.35s ease-out forwards`,
                      animationDelay: `${index * 0.05}s`,
                      opacity: 0,
                    }}
                  >
                    {/* Top row: id + status + prioridade */}
                    <div className="flex items-center justify-between gap-3 mb-3">
                      <div className="flex items-center gap-2 min-w-0">
                        <span className="text-xs font-mono text-gray-500 shrink-0">
                          {complaint.id}
                        </span>
                        <span className={`w-1.5 h-1.5 rounded-full ${sConfig.dot} shrink-0`} />
                        <span
                          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium border ${sConfig.bg} ${sConfig.color}`}
                        >
                          {sConfig.label}
                        </span>
                        <span
                          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium border ${pConfig.bg} ${pConfig.color}`}
                        >
                          {pConfig.label}
                        </span>
                      </div>
                      <span className="text-[10px] text-gray-500 shrink-0 flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {timeAgo(complaint.timestamp)}
                      </span>
                    </div>

                    {/* Description */}
                    <p className="text-sm text-gray-300 mb-3 leading-relaxed line-clamp-2">
                      {complaint.descricao}
                    </p>

                    {/* Bottom row: bairro, tipo, nome */}
                    <div className="flex items-center gap-3 flex-wrap text-[11px]">
                      <span className="flex items-center gap-1 text-gray-400">
                        <MapPin className="w-3 h-3" />
                        {complaint.bairro}
                      </span>
                      <span
                        className={`flex items-center gap-1 ${tConfig.color}`}
                      >
                        <Tag className="w-3 h-3" />
                        {complaint.tipo}
                      </span>
                      <span className="flex items-center gap-1 text-gray-400">
                        <User className="w-3 h-3" />
                        {complaint.nome}
                      </span>
                    </div>
                  </div>
                );
              })
            )}
          </div>

          {/* Feed count */}
          <div className="flex items-center justify-between text-xs text-gray-500 px-1">
            <span>
              Exibindo {filteredComplaints.length} de {complaints.length} reclamações
            </span>
            <span className="flex items-center gap-1">
              <Zap className="w-3 h-3 text-cyan-400" />
              Tempo real
            </span>
          </div>
        </div>

        {/* ─── Right: Send Panel (1/3) ─── */}
        <div
          className={`lg:block ${
            showSendPanel ? 'block' : 'hidden'
          } space-y-4`}
        >
          <div className="bg-gray-900/60 border border-gray-800 rounded-xl overflow-hidden">
            {/* Panel header */}
            <div className="p-4 border-b border-gray-800">
              <h2 className="text-sm font-semibold text-white flex items-center gap-2">
                <Send className="w-4 h-4 text-cyan-400" />
                Enviar Comunicação
              </h2>
            </div>

            {/* Tabs */}
            <div className="flex border-b border-gray-800">
              {(
                [
                  { key: 'whatsapp', label: 'WhatsApp', icon: MessageCircle },
                  { key: 'email', label: 'Email', icon: Mail },
                  { key: 'sms', label: 'SMS', icon: Smartphone },
                ] as const
              ).map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.key}
                    onClick={() => setCommsTab(tab.key)}
                    className={`flex-1 flex items-center justify-center gap-1.5 px-3 py-2.5 text-xs font-medium transition-all ${
                      commsTab === tab.key
                        ? 'text-cyan-400 border-b-2 border-cyan-400 bg-cyan-500/5'
                        : 'text-gray-500 hover:text-gray-300 border-b-2 border-transparent'
                    }`}
                  >
                    <Icon className="w-3.5 h-3.5" />
                    {tab.label}
                  </button>
                );
              })}
            </div>

            {/* Tab content */}
            <div className="p-4 space-y-3">
              {/* WhatsApp */}
              {commsTab === 'whatsapp' && (
                <div className="space-y-3">
                  <div className="space-y-1.5">
                    <label className="text-xs text-gray-400 font-medium">
                      Telefone
                    </label>
                    <input
                      type="text"
                      placeholder="(11) 99999-9999"
                      value={whatsPhone}
                      onChange={(e) => setWhatsPhone(e.target.value)}
                      className="w-full px-3 py-2 bg-gray-800/50 border border-gray-700 rounded-lg text-white text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/40 focus:border-cyan-500/50 transition-all"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-xs text-gray-400 font-medium">
                      Mensagem
                    </label>
                    <textarea
                      placeholder="Digite a mensagem..."
                      rows={4}
                      value={whatsMsg}
                      onChange={(e) => setWhatsMsg(e.target.value)}
                      className="w-full px-3 py-2 bg-gray-800/50 border border-gray-700 rounded-lg text-white text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/40 focus:border-cyan-500/50 transition-all resize-none"
                    />
                  </div>
                  <button
                    onClick={sendWhatsApp}
                    disabled={whatsSending || !whatsPhone.trim() || !whatsMsg.trim()}
                    className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-emerald-500/10 text-emerald-400 rounded-lg border border-emerald-500/20 hover:bg-emerald-500/20 transition-all text-sm font-medium disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    {whatsSending ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Send className="w-4 h-4" />
                    )}
                    {whatsSending ? 'Enviando...' : 'Enviar WhatsApp'}
                  </button>
                </div>
              )}

              {/* Email */}
              {commsTab === 'email' && (
                <div className="space-y-3">
                  <div className="space-y-1.5">
                    <label className="text-xs text-gray-400 font-medium">
                      Para (Email)
                    </label>
                    <input
                      type="email"
                      placeholder="email@exemplo.com"
                      value={emailTo}
                      onChange={(e) => setEmailTo(e.target.value)}
                      className="w-full px-3 py-2 bg-gray-800/50 border border-gray-700 rounded-lg text-white text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/40 focus:border-cyan-500/50 transition-all"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-xs text-gray-400 font-medium">
                      Assunto
                    </label>
                    <input
                      type="text"
                      placeholder="Assunto do e-mail"
                      value={emailSubject}
                      onChange={(e) => setEmailSubject(e.target.value)}
                      className="w-full px-3 py-2 bg-gray-800/50 border border-gray-700 rounded-lg text-white text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/40 focus:border-cyan-500/50 transition-all"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-xs text-gray-400 font-medium">
                      Mensagem
                    </label>
                    <textarea
                      placeholder="Corpo do e-mail..."
                      rows={4}
                      value={emailMsg}
                      onChange={(e) => setEmailMsg(e.target.value)}
                      className="w-full px-3 py-2 bg-gray-800/50 border border-gray-700 rounded-lg text-white text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/40 focus:border-cyan-500/50 transition-all resize-none"
                    />
                  </div>
                  <button
                    onClick={sendEmail}
                    disabled={
                      emailSending ||
                      !emailTo.trim() ||
                      !emailSubject.trim() ||
                      !emailMsg.trim()
                    }
                    className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-purple-500/10 text-purple-400 rounded-lg border border-purple-500/20 hover:bg-purple-500/20 transition-all text-sm font-medium disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    {emailSending ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Send className="w-4 h-4" />
                    )}
                    {emailSending ? 'Enviando...' : 'Enviar E-mail'}
                  </button>
                </div>
              )}

              {/* SMS */}
              {commsTab === 'sms' && (
                <div className="space-y-3">
                  <div className="space-y-1.5">
                    <label className="text-xs text-gray-400 font-medium">
                      Telefone
                    </label>
                    <input
                      type="text"
                      placeholder="(11) 99999-9999"
                      value={smsPhone}
                      onChange={(e) => setSmsPhone(e.target.value)}
                      className="w-full px-3 py-2 bg-gray-800/50 border border-gray-700 rounded-lg text-white text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/40 focus:border-cyan-500/50 transition-all"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-xs text-gray-400 font-medium">
                      Mensagem
                    </label>
                    <textarea
                      placeholder="Digite a mensagem SMS..."
                      rows={4}
                      value={smsMsg}
                      onChange={(e) => setSmsMsg(e.target.value)}
                      className="w-full px-3 py-2 bg-gray-800/50 border border-gray-700 rounded-lg text-white text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/40 focus:border-cyan-500/50 transition-all resize-none"
                    />
                  </div>
                  <button
                    onClick={sendSMS}
                    disabled={smsSending || !smsPhone.trim() || !smsMsg.trim()}
                    className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-blue-500/10 text-blue-400 rounded-lg border border-blue-500/20 hover:bg-blue-500/20 transition-all text-sm font-medium disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    {smsSending ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Send className="w-4 h-4" />
                    )}
                    {smsSending ? 'Enviando...' : 'Enviar SMS'}
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* ─── Recent Sends ─── */}
          <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-4">
            <h3 className="text-xs font-semibold text-white mb-3 flex items-center gap-2">
              <Clock className="w-3.5 h-3.5 text-gray-500" />
              Envios Recentes
            </h3>
            <div className="space-y-2 max-h-[280px] overflow-y-auto">
              {envioHistory.map((envio) => {
                const StatusIcon = envioStatusConfig[envio.status].icon;
                const sColor = envioStatusConfig[envio.status].color;
                const tipoIcon =
                  envio.tipo === 'whatsapp'
                    ? MessageCircle
                    : envio.tipo === 'email'
                      ? Mail
                      : Smartphone;
                const TipoIcon = tipoIcon;
                return (
                  <div
                    key={envio.id}
                    className="flex items-start gap-2.5 p-2.5 rounded-lg bg-gray-800/30 border border-gray-800/50"
                  >
                    <div className="shrink-0 mt-0.5">
                      <TipoIcon className="w-3.5 h-3.5 text-gray-500" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-1.5 mb-0.5">
                        <span className="text-[10px] font-medium text-white truncate">
                          {envio.destino}
                        </span>
                        <StatusIcon
                          className={`w-3 h-3 shrink-0 ${sColor} ${
                            envio.status === 'pendente' ? 'animate-spin' : ''
                          }`}
                        />
                      </div>
                      <p className="text-[10px] text-gray-500 truncate">
                        {envio.mensagem}
                      </p>
                      <p className="text-[9px] text-gray-600 mt-0.5">
                        {timeAgo(envio.timestamp)}
                      </p>
                    </div>
                  </div>
                );
              })}
              {envioHistory.length === 0 && (
                <p className="text-xs text-gray-500 text-center py-4">
                  Nenhum envio realizado
                </p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* ─── Keyframes for animations ─── */}
      <style jsx>{`
        @keyframes slideFadeIn {
          from {
            opacity: 0;
            transform: translateY(16px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .scrollbar-thin::-webkit-scrollbar {
          width: 4px;
        }
        .scrollbar-thin::-webkit-scrollbar-track {
          background: transparent;
        }
        .scrollbar-thin::-webkit-scrollbar-thumb {
          background: rgba(75, 85, 99, 0.5);
          border-radius: 4px;
        }
        .scrollbar-thin::-webkit-scrollbar-thumb:hover {
          background: rgba(75, 85, 99, 0.8);
        }
      `}</style>
    </div>
  );
}
