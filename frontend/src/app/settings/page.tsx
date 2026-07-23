'use client';

import { useState } from 'react';
import {
  User,
  Bell,
  Key,
  Settings as SettingsIcon,
  Users,
  Palette,
  Globe,
  AlertTriangle,
  Save,
  Copy,
  CheckCircle,
  XCircle,
  ExternalLink,
} from 'lucide-react';

// ── Mock Data ──────────────────────────────────────────────

const userProfile = {
  name: 'Rafael Torres',
  email: 'rafael.torres@polis.ai',
  role: 'Administrador',
};

const notificationsConfig = [
  { id: 'email', label: 'Notificações por Email', desc: 'Resumo diário de alertas e relatórios' },
  { id: 'push', label: 'Push Notifications', desc: 'Alertas em tempo real no navegador' },
  { id: 'sms', label: 'SMS de Emergência', desc: 'Apenas incidentes críticos' },
  { id: 'alerts', label: 'Alertas do Sistema', desc: 'Mudanças de status nos serviços' },
];

const apiKey = 'sk-7f3a9b2c1d8e4f5a6b7c8d9e0f1a2b3c';
const maskedKey = apiKey.slice(0, 12) + '...' + apiKey.slice(-4);

const preferences = {
  theme: 'dark' as const,
  language: 'pt-BR' as const,
  timezone: '-03:00' as const,
};

const teamMembers = [
  { name: 'Rafael Torres', role: 'Admin', initials: 'RT', status: 'online' as const, color: 'from-cyan-500 to-blue-600' },
  { name: 'Ana Oliveira', role: 'DevOps', initials: 'AO', status: 'online' as const, color: 'from-emerald-400 to-teal-500' },
  { name: 'Lucas Mendes', role: 'Backend', initials: 'LM', status: 'away' as const, color: 'from-violet-500 to-purple-600' },
  { name: 'Carla Souza', role: 'Frontend', initials: 'CS', status: 'offline' as const, color: 'from-pink-500 to-rose-600' },
  { name: 'Diego Rocha', role: 'QA', initials: 'DR', status: 'online' as const, color: 'from-amber-400 to-orange-500' },
  { name: 'Juliana Costa', role: 'ML Engineer', initials: 'JC', status: 'away' as const, color: 'from-indigo-500 to-blue-600' },
];

// ── Toggle Component ───────────────────────────────────────

function Toggle({ enabled, onChange }: { enabled: boolean; onChange: () => void }) {
  return (
    <button
      type="button"
      onClick={onChange}
      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-all duration-300 ${
        enabled ? 'bg-cyan-500 shadow-[0_0_10px_rgba(6,182,212,0.3)]' : 'bg-gray-700'
      }`}
    >
      <span
        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-all duration-300 ${
          enabled ? 'translate-x-6' : 'translate-x-1'
        }`}
      />
    </button>
  );
}

// ── Status Dot ─────────────────────────────────────────────

const statusConfig = {
  online: { label: 'Online', dot: 'bg-emerald-500', pulse: 'bg-emerald-400' },
  away: { label: 'Ausente', dot: 'bg-amber-500', pulse: 'bg-amber-400' },
  offline: { label: 'Offline', dot: 'bg-gray-500', pulse: 'bg-gray-400' },
};

// ── Avatar with Gradient Initials ──────────────────────────

function AvatarInitials({ initials, color, size = 'md' }: { initials: string; color: string; size?: 'sm' | 'md' }) {
  const sizeClasses = size === 'sm' ? 'w-8 h-8 text-xs' : 'w-12 h-12 text-sm';
  return (
    <div
      className={`${sizeClasses} rounded-full bg-gradient-to-br ${color} flex items-center justify-center font-bold text-white shrink-0`}
    >
      {initials}
    </div>
  );
}

// ── Card Wrapper ───────────────────────────────────────────

function SectionCard({ title, icon: Icon, children }: { title: string; icon: React.ElementType; children: React.ReactNode }) {
  return (
    <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-6 hover:border-gray-700 transition-all">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20">
          <Icon className="w-4 h-4 text-cyan-400" />
        </div>
        <h2 className="text-sm font-semibold text-white">{title}</h2>
      </div>
      {children}
    </div>
  );
}

// ── Page Component ─────────────────────────────────────────

export default function Settings() {
  const [profile, setProfile] = useState(userProfile);
  const [notifications, setNotifications] = useState<Record<string, boolean>>({
    email: true,
    push: true,
    sms: false,
    alerts: true,
  });
  const [selectedTheme, setSelectedTheme] = useState<'dark' | 'light' | 'system'>('dark');
  const [selectedLanguage, setSelectedLanguage] = useState<'pt-BR' | 'en-US'>('pt-BR');
  const [selectedTimezone, setSelectedTimezone] = useState(preferences.timezone);
  const [showFullKey, setShowFullKey] = useState(false);
  const [copied, setCopied] = useState(false);
  const [saved, setSaved] = useState(false);

  const toggleNotification = (id: string) => {
    setNotifications((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(apiKey);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleRegenerate = () => {
    // Mock regeneration
  };

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="p-6 lg:p-8 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Configurações</h1>
          <p className="text-sm text-gray-400 mt-1">
            Gerencie sua conta, preferências e integrações
          </p>
        </div>
        <button
          onClick={handleSave}
          className="flex items-center gap-2 px-4 py-2 bg-cyan-500/10 text-cyan-400 rounded-lg border border-cyan-500/20 text-sm font-medium hover:bg-cyan-500/20 transition-all"
        >
          {saved ? (
            <>
              <CheckCircle className="w-4 h-4" />
              Salvo
            </>
          ) : (
            <>
              <Save className="w-4 h-4" />
              Salvar Alterações
            </>
          )}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* ── 1) Perfil ── */}
        <SectionCard title="Perfil" icon={User}>
          <div className="flex items-start gap-4 mb-6">
            <AvatarInitials initials="RT" color="from-cyan-500 to-blue-600" />
            <div className="space-y-1">
              <p className="text-base font-semibold text-white">{profile.name}</p>
              <p className="text-sm text-gray-400">{profile.email}</p>
              <span className="inline-block text-xs px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                {profile.role}
              </span>
            </div>
          </div>
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-gray-400 uppercase tracking-wider mb-1.5">
                Nome
              </label>
              <input
                type="text"
                value={profile.name}
                onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                className="w-full bg-gray-800/50 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-cyan-500/50 focus:border-cyan-500/50"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-400 uppercase tracking-wider mb-1.5">
                Email
              </label>
              <input
                type="email"
                value={profile.email}
                onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                className="w-full bg-gray-800/50 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-cyan-500/50 focus:border-cyan-500/50"
              />
            </div>
          </div>
        </SectionCard>

        {/* ── 2) Notificações ── */}
        <SectionCard title="Notificações" icon={Bell}>
          <div className="space-y-4">
            {notificationsConfig.map((n) => (
              <div
                key={n.id}
                className="flex items-center justify-between py-3 px-4 rounded-lg bg-gray-800/30 border border-gray-800"
              >
                <div>
                  <p className="text-sm font-medium text-white">{n.label}</p>
                  <p className="text-xs text-gray-500 mt-0.5">{n.desc}</p>
                </div>
                <Toggle
                  enabled={notifications[n.id]}
                  onChange={() => toggleNotification(n.id)}
                />
              </div>
            ))}
          </div>
        </SectionCard>

        {/* ── 3) API ── */}
        <SectionCard title="API & Integrações" icon={Key}>
          <div className="space-y-5">
            <div>
              <label className="block text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">
                Chave de API
              </label>
              <div className="flex items-center gap-2">
                <div className="flex-1 bg-gray-800/50 border border-gray-700 rounded-lg px-3 py-2.5 text-xs font-mono text-gray-300 truncate">
                  {showFullKey ? apiKey : maskedKey}
                </div>
                <button
                  onClick={() => setShowFullKey(!showFullKey)}
                  className="p-2 rounded-lg bg-gray-800/50 border border-gray-700 text-gray-400 hover:text-white hover:border-gray-600 transition-all"
                  title={showFullKey ? 'Ocultar' : 'Mostrar'}
                >
                  <Key className="w-4 h-4" />
                </button>
                <button
                  onClick={handleCopy}
                  className="p-2 rounded-lg bg-gray-800/50 border border-gray-700 text-gray-400 hover:text-white hover:border-gray-600 transition-all"
                  title="Copiar"
                >
                  {copied ? (
                    <CheckCircle className="w-4 h-4 text-emerald-400" />
                  ) : (
                    <Copy className="w-4 h-4" />
                  )}
                </button>
              </div>
              <div className="flex items-center gap-2 mt-2">
                <button
                  onClick={handleRegenerate}
                  className="text-xs text-amber-400 hover:text-amber-300 transition-colors"
                >
                  Regenerar chave
                </button>
                <span className="text-gray-600">·</span>
                <span className="text-xs text-gray-500">Última rotação: 15/07/2026</span>
              </div>
            </div>

            <div className="border-t border-gray-800 pt-4">
              <label className="block text-xs font-medium text-gray-400 uppercase tracking-wider mb-3">
                Webhooks
              </label>
              <div className="space-y-3">
                {[
                  { url: 'https://hooks.polis.ai/events', event: 'Todos os eventos' },
                  { url: 'https://hooks.polis.ai/alerts', event: 'Apenas alertas' },
                ].map((wh, i) => (
                  <div key={i} className="flex items-center justify-between py-2 px-3 rounded-lg bg-gray-800/20 border border-gray-800">
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-mono text-gray-300 truncate">{wh.url}</p>
                      <p className="text-[10px] text-gray-500 mt-0.5">{wh.event}</p>
                    </div>
                    <ExternalLink className="w-3.5 h-3.5 text-gray-600 shrink-0 ml-2" />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </SectionCard>

        {/* ── 4) WhatsApp ── */}
        <SectionCard title="WhatsApp" icon={() => <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-emerald-400"><path d="M3 21l1.65-3.8a9 9 0 1 1 3.4 2.9L3 21"/><path d="M9 10a.5.5 0 0 0 1 0V9a.5.5 0 0 0-1 0v1a5 5 0 0 0 5 5h1a.5.5 0 0 0 0-1h-1a.5.5 0 0 0 0 1"/></svg>}>
          <div className="space-y-5">
            {/* Status */}
            <div>
              <label className="block text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">
                Status da Conexão
              </label>
              <div className="flex items-center gap-3 py-3 px-4 rounded-lg bg-gray-800/30 border border-gray-800">
                <span className="relative flex h-3 w-3">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500" />
                </span>
                <div>
                  <p className="text-sm font-medium text-white">WhatsApp Cloud API</p>
                  <p className="text-xs text-gray-500">Conectado e operacional</p>
                </div>
              </div>
            </div>

            {/* Config */}
            <div className="grid grid-cols-1 gap-4">
              <div>
                <label className="block text-xs font-medium text-gray-400 uppercase tracking-wider mb-1.5">
                  Phone Number ID
                </label>
                <input
                  type="text"
                  defaultValue="542510762287376"
                  readOnly
                  className="w-full bg-gray-800/50 border border-gray-700 rounded-lg px-3 py-2 text-sm font-mono text-gray-300 focus:outline-none cursor-default"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-400 uppercase tracking-wider mb-1.5">
                  Token de Acesso
                </label>
                <div className="flex items-center gap-2">
                  <input
                    type="password"
                    defaultValue="************EAAH"
                    readOnly
                    className="flex-1 bg-gray-800/50 border border-gray-700 rounded-lg px-3 py-2 text-sm font-mono text-gray-300 focus:outline-none cursor-default"
                  />
                  <button className="p-2 rounded-lg bg-gray-800/50 border border-gray-700 text-gray-400 hover:text-white transition-all" title="Copiar">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                  </button>
                </div>
              </div>
            </div>

            {/* Webhook */}
            <div className="border-t border-gray-800 pt-4">
              <label className="block text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">
                Webhook URL
              </label>
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  defaultValue="https://polis.miraitohope.com/api/whatsapp/webhook"
                  readOnly
                  className="flex-1 bg-gray-800/50 border border-gray-700 rounded-lg px-3 py-2 text-sm font-mono text-gray-300 focus:outline-none cursor-default"
                />
                <button className="p-2 rounded-lg bg-gray-800/50 border border-gray-700 text-gray-400 hover:text-white transition-all" title="Copiar">
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-1.5">
                Configure esta URL no Meta Developer Dashboard em <strong>Webhook → Callback URL</strong>. Use o verify token: <code className="text-cyan-400">polis_wa_verify_2026</code>
              </p>
            </div>

            {/* Números autorizados */}
            <div className="border-t border-gray-800 pt-4">
              <label className="block text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">
                Números Autorizados (Sandbox)
              </label>
              <div className="space-y-2">
                <div className="flex items-center justify-between py-2 px-3 rounded-lg bg-gray-800/20 border border-gray-800">
                  <span className="text-sm text-gray-300 font-mono">5511999999999</span>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-yellow-500/10 text-yellow-400 border border-yellow-500/20">Pendente</span>
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                Para testar, adicione seu número no <strong>Meta Business Settings → WhatsApp Accounts → Sandbox → Allowed Numbers</strong>
              </p>
            </div>
          </div>
        </SectionCard>

        {/* ── 5) Preferências ── */}
        <SectionCard title="Preferências" icon={Palette}>
          <div className="space-y-5">
            {/* Tema */}
            <div>
              <label className="flex items-center gap-2 text-xs font-medium text-gray-400 uppercase tracking-wider mb-2.5">
                <Palette className="w-3.5 h-3.5" />
                Tema
              </label>
              <div className="grid grid-cols-3 gap-2">
                {(['dark', 'light', 'system'] as const).map((t) => (
                  <button
                    key={t}
                    onClick={() => setSelectedTheme(t)}
                    className={`px-3 py-2 rounded-lg text-xs font-medium border transition-all ${
                      selectedTheme === t
                        ? 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400'
                        : 'bg-gray-800/30 border-gray-700 text-gray-400 hover:border-gray-600'
                    }`}
                  >
                    {t === 'dark' ? 'Dark' : t === 'light' ? 'Light' : 'Sistema'}
                  </button>
                ))}
              </div>
            </div>

            {/* Idioma */}
            <div>
              <label className="flex items-center gap-2 text-xs font-medium text-gray-400 uppercase tracking-wider mb-2.5">
                <Globe className="w-3.5 h-3.5" />
                Idioma
              </label>
              <div className="grid grid-cols-2 gap-2">
                {(['pt-BR', 'en-US'] as const).map((lang) => (
                  <button
                    key={lang}
                    onClick={() => setSelectedLanguage(lang)}
                    className={`px-3 py-2 rounded-lg text-xs font-medium border transition-all ${
                      selectedLanguage === lang
                        ? 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400'
                        : 'bg-gray-800/30 border-gray-700 text-gray-400 hover:border-gray-600'
                    }`}
                  >
                    {lang === 'pt-BR' ? '🇧🇷 Português (BR)' : '🇺🇸 English (US)'}
                  </button>
                ))}
              </div>
            </div>

            {/* Fuso Horário */}
            <div>
              <label className="flex items-center gap-2 text-xs font-medium text-gray-400 uppercase tracking-wider mb-2.5">
                <SettingsIcon className="w-3.5 h-3.5" />
                Fuso Horário
              </label>
              <select
                value={selectedTimezone}
                onChange={(e) => setSelectedTimezone(e.target.value as typeof selectedTimezone)}
                className="w-full bg-gray-800/50 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-1 focus:ring-cyan-500/50 focus:border-cyan-500/50"
              >
                <option value="-03:00">(GMT-3) Brasília</option>
                <option value="-02:00">(GMT-2) Fernando de Noronha</option>
                <option value="-04:00">(GMT-4) Manaus</option>
                <option value="-05:00">(GMT-5) Acre</option>
                <option value="+00:00">(GMT+0) UTC</option>
                <option value="-08:00">(GMT-8) Pacific Time</option>
                <option value="-05:00">(GMT-5) Eastern Time</option>
              </select>
            </div>
          </div>
        </SectionCard>
      </div>

      {/* ── 5) Time ── */}
      <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-6 hover:border-gray-700 transition-all">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20">
            <Users className="w-4 h-4 text-cyan-400" />
          </div>
          <h2 className="text-sm font-semibold text-white">Time</h2>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {teamMembers.map((member) => {
            const status = statusConfig[member.status];
            return (
              <div
                key={member.name}
                className="flex items-center gap-3 py-3 px-4 rounded-lg bg-gray-800/30 border border-gray-800 hover:bg-gray-800/50 transition-all"
              >
                <AvatarInitials initials={member.initials} color={member.color} size="sm" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-white truncate">{member.name}</p>
                  <p className="text-xs text-gray-500">{member.role}</p>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="relative flex h-2 w-2">
                    <span
                      className={`animate-ping absolute inline-flex h-full w-full rounded-full ${status.pulse} opacity-75 ${
                        member.status === 'offline' ? 'hidden' : ''
                      }`}
                    />
                    <span
                      className={`relative inline-flex rounded-full h-2 w-2 ${status.dot}`}
                    />
                  </span>
                  <span className="text-[10px] text-gray-500">{status.label}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* ── 6) Zona de Perigo ── */}
      <div className="bg-gray-900/60 border border-red-900/30 rounded-xl p-6 hover:border-red-800/40 transition-all">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 rounded-lg bg-red-500/10 border border-red-500/20">
            <AlertTriangle className="w-4 h-4 text-red-400" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-white">Zona de Perigo</h2>
            <p className="text-xs text-gray-500 mt-0.5">
              Ações irreversíveis — prossiga com cuidado
            </p>
          </div>
        </div>
        <div className="border-t border-red-900/20 pt-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-white">Desativar Conta</p>
              <p className="text-xs text-gray-500 mt-0.5">
                Remove permanentemente sua conta e todos os dados associados
              </p>
            </div>
            <button className="px-4 py-2 bg-red-500/10 text-red-400 rounded-lg border border-red-500/20 text-sm font-medium hover:bg-red-500/20 transition-all">
              Desativar Conta
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
