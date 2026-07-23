# 🏛️ ARQUITETURA DO MÓDULO DE COMUNICAÇÃO MULTICANAL — POLIS

> **Plataforma de Relacionamento com o Cidadão**
> Versão: 1.0 | Data: Julho 2026

---

## SUMÁRIO

1. [VISÃO GERAL](#1-visão-geral)
2. [O QUE JÁ EXISTE (REUSO)](#2-o-que-já-existe-reuso)
3. [O QUE PRECISA SER CRIADO](#3-o-que-precisa-ser-criado)
4. [FLUXO COMPLETO](#4-fluxo-completo)
5. [MODELO DE DADOS](#5-modelo-de-dados)
6. [ESTRUTURA DE PROVIDERS](#6-estrutura-de-providers)
7. [PIPELINE DE IA](#7-pipeline-de-ia)
8. [SEGMENTAÇÃO](#8-segmentação)
9. [CAMPANHAS MULTICANAIS](#9-campanhas-multicanais)
10. [GERAÇÃO DE MENSAGEM POR IA](#10-geração-de-mensagem-por-ia)
11. [APROVAÇÃO E GOVERNANÇA](#11-aprovação-e-governança)
12. [FILAS E WORKERS](#12-filas-e-workers)
13. [CONSENTIMENTO E OPT-OUT](#13-consentimento-e-opt-out)
14. [CUSTOS POR CANAL](#14-custos-por-canal)
15. [TELAS / FRONTEND](#15-telas--frontend)
16. [APIs](#16-apis)
17. [WEBHOOKS](#17-webhooks)
18. [BACKLOG E ORDEM DE IMPLEMENTAÇÃO](#18-backlog-e-ordem-de-implementação)
19. [RISCOS](#19-riscos)
20. [PRÓXIMO PASSO TÉCNICO](#20-próximo-passo-técnico)

---

## 1. VISÃO GERAL

```
┌─────────────────────────────────────────────────────────────┐
│                    POLIS PLATFORM                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐ │
│  │ INBOX    │  │ MAPA     │  │ SEGMENTOS│  │ CAMPANHAS  │ │
│  │ (Caixa   │  │ (Eventos │  │ (Públicos│  │ (Disparo   │ │
│  │  Entrada)│  │  Territ.)│  │  Alvo)   │  │  Multicanal)│ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┬─────┘ │
│       │              │              │               │       │
│  ┌────▼──────────────▼──────────────▼───────────────▼─────┐ │
│  │                  CORE ENGINE                            │ │
│  │  ┌────────┐ ┌──────────┐ ┌────────┐ ┌───────────────┐ │ │
│  │  │Classif.│ │Resolução │ │Segment.│ │Orquestrador   │ │ │
│  │  │ IA     │ │ Fluxo    │ │ Engine  │ │ de Canais     │ │ │
│  │  └────────┘ └──────────┘ └────────┘ └───────────────┘ │ │
│  └─────────────────────────────────────────────────────────┘ │
│                              │                               │
│  ┌───────────────────────────▼─────────────────────────────┐ │
│  │               PROVIDER ABSTRACTION LAYER                │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐ │ │
│  │  │ WhatsApp │ │  SMS     │ │  Email   │ │ Audio/Video│ │ │
│  │  │ Provider │ │ Provider │ │ Provider │ │ Provider   │ │ │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────────┘ │ │
│  └─────────────────────────────────────────────────────────┘ │
│                              │                               │
│  ┌───────────────────────────▼─────────────────────────────┐ │
│  │   CRM (Contact History + Territorial Events + Audit)    │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. O QUE JÁ EXISTE (REUSO)

### ✅ Backend — Providers

| Componente | Arquivo | Status |
|---|---|---|
| `MessageProvider` (ABC) | `src/providers/base.py` | ✅ Completo |
| `DeliveryStatus` / `MessageStatus` / `IncomingMessage` | `src/providers/base.py` | ✅ Completo |
| WhatsApp Provider (Meta Cloud API) | `src/providers/whatsapp/provider.py` | ✅ Completo |
| Email Provider (Resend + SMTP) | `src/providers/email/provider.py` | ✅ Completo |
| SMS Provider | `src/providers/sms/provider.py` | ✅ Existe (verificar) |
| `WhatsAppCloudService` | `src/modules/whatsapp/service.py` | ✅ Completo |

### ✅ Backend — Módulos

| Módulo | Função | Status |
|---|---|---|
| `channels` | Gerenciamento de conexões (CRUD) | ✅ Completo |
| `contacts` | Contatos (CRUD com localização) | ✅ Completo |
| `conversations` | Conversas (CRUD + atribuição) | ✅ Completo |
| `messages` | Mensagens (histórico) | ✅ Completo |
| `campaigns` | Campanhas (CRUD + send + métricas) | ✅ Completo |
| `protocols` | Protocolos de atendimento | ✅ Completo |
| `territorial` | Eventos territoriais (CRUD) | ✅ Completo |
| `agents` | Agentes IA configuráveis | ✅ Completo |
| `knowledge` | Base de conhecimento | ✅ Completo |
| `tasks` | Tarefas (vinculadas a eventos/protocolos) | ✅ Completo |
| `workflows` | Workflows | ✅ Completo |
| `webhooks` | Webhooks | ✅ Completo |
| `analytics` | Analytics | ✅ Completo |
| `audit` | Auditoria | ✅ Completo |
| `auth` | Autenticação/autorização | ✅ Completo |
| `tenants` | Multi-tenant | ✅ Completo |
| `users` | Usuários | ✅ Completo |
| `dashboard` | Dashboard | ✅ Completo |
| `billing` | Faturamento | ✅ Completo |

### ✅ Modelos de Dados

| Modelo | Tabela | Status |
|---|---|---|
| `Tenant` | tenants | ✅ |
| `User` | users | ✅ |
| `Role` | roles | ✅ |
| `Contact` | contacts | ✅ (já tem phone, email, city, state, neighborhood, address, lat, lon, tags) |
| `Channel` | channels | ✅ (já tem provider, credentials, webhook) |
| `Conversation` | conversations | ✅ (já tem contact_id, assigned_to, status, subject) |
| `Message` | messages | ✅ (já tem direction, type, content, provider_message_id, status) |
| `Campaign` | campaigns | ✅ (já tem segments, message_template, status, metrics) |
| `Protocol` | protocols | ✅ (já tem contact, status, event) |
| `TerritorialEvent` | territorial_events | ✅ (já tem location, severity, event_type) |
| `Task` | tasks | ✅ (já tem event_id, protocol_id) |
| `Agent` | agents | ✅ |
| `KnowledgeBase` | knowledge_bases | ✅ |
| `AuditLog` | audit_logs | ✅ |

### ✅ Frontend

| Página | Arquivo | Status |
|---|---|---|
| Dashboard | `app/page.tsx` | ✅ |
| Messages | `app/messages/page.tsx` | ✅ Parcial |
| Conversations | `app/conversations/page.tsx` | ✅ Parcial |
| Mapa | `app/mapa/page.tsx` | ✅ |
| Ranking | `app/ranking/page.tsx` | ✅ |
| Reports | `app/reports/page.tsx` | ✅ |
| Settings | `app/settings/page.tsx` | ✅ |
| Agents | `app/agents/page.tsx` | ✅ |
| Monitoring | `app/monitoring/page.tsx` | ✅ |
| Security | `app/security/page.tsx` | ✅ |
| Login | `app/login/page.tsx` | ✅ |
| API lib | `lib/api.ts` | ✅ |
| WhatsApp send | `lib/whatsapp-send.ts` | ✅ |
| MapaLeaflet | `components/MapaLeaflet.tsx` | ✅ |
| Sidebar | `components/Sidebar.tsx` | ✅ |

---

## 3. O QUE PRECISA SER CRIADO

### 🔴 Crítico (MVP - Fase 1)

| # | Componente | Descrição |
|---|---|---|
| 1 | **Pipeline de Classificação IA** | Classificar mensagens em: reclamação, elogio, sugestão, dúvida, denúncia, etc. Extrair endereço, bairro, cidade, sentimento, urgência. |
| 2 | **Caixa de Entrada Unificada** | Tela única com todas as conversas, classificação visível, filtros, ações rápidas. |
| 3 | **Geocodificação + Mapa** | Converter endereço extraído em lat/lon. Criar/associar evento territorial. Clustering no mapa. |
| 4 | **Fluxo de Resolução** | Marcar resolvido → identificar afetados → selecionar canal → gerar resposta → enviar. |
| 5 | **Segmentação de Públicos** | Criador de segmentos manuais, dinâmicos e por evento territorial. |

### 🟡 Importante (MVP - Fase 2)

| # | Componente | Descrição |
|---|---|---|
| 6 | **Geração de Mensagem por IA** | Texto personalizado com variáveis e tom escolhido. |
| 7 | **Campanhas Multicanal** | Suporte a WhatsApp + SMS + Email simultâneo ou sequencial. |
| 8 | **Consentimento / Opt-out** | Gerenciar permissões por canal por contato. |
| 9 | **Aprovação de Campanhas** | Draft → Revisão → Aprovação → Agendamento → Envio. |
| 10 | **Queue System** | Fila de processamento assíncrono para envio em lote. |

### 🟢 Desejável (Fases 3-5)

| # | Componente | Descrição |
|---|---|---|
| 11 | **Áudio Provider (ElevenLabs)** | Voz clonada, TTS, preview, envio via WhatsApp. |
| 12 | **Vídeo Provider (HeyGen)** | Avatar autorizado, geração de vídeo personalizado. |
| 13 | **Custos por Canal** | Tracking de créditos, custo por mensagem, estimativas. |
| 14 | **Dashboard de Comunicação** | KPIs específicos: entregues, lidas, respostas, conversão. |
| 15 | **E-mail Templates** | Editor visual com templates prontos. |

---

## 4. FLUXO COMPLETO

### 4.1 Fluxo de Mensagem Recebida

```
Cidadão envia WhatsApp
        │
        ▼
Webhook Meta Cloud API
        │
        ▼
process_webhook() → IncomingMessage
        │
        ▼
Criar/Atualizar Contact (by phone)
        │
        ▼
Criar/Atualizar Conversation (agrupar por contato)
        │
        ▼
Salvar Message (inbound)
        │
        ▼
=== PIPELINE DE IA (assíncrono) ===
        │
        ├─ Classificar tipo: reclamação | elogio | sugestão | dúvida | denúncia | etc.
        ├─ Extrair endereço, bairro, cidade
        ├─ Geocodificar endereço → lat/lon
        ├─ Detectar sentimento, urgência, risco
        ├─ Sugerir secretaria/órgão responsável
        ├─ Gerar resumo da mensagem
        ├─ Extrair palavras-chave
        └─ Tags automáticas
        │
        ▼
=== VINCULAÇÃO TERRITORIAL ===
        │
        ├─ Buscar TerritorialEvents próximos (mesma região + categoria)
        │   ├─ Se encontrou → associar mensagem ao evento existente
        │   │   ├─ Atualizar volume, sentimento, urgência
        │   │   └─ Atualizar cluster no mapa
        │   └─ Se NÃO encontrou → criar novo TerritorialEvent
        │       ├─ lat/lon, endereço, categoria
        │       └─ Primeiro relato
        │
        ▼
=== CRM & INBOX ===
        │
        ├─ Atualizar perfil do Contact
        ├─ Adicionar ao histórico do Contact
        ├─ Notificar na Caixa de Entrada
        ├─ Se urgente → destacar / alertar
        └─ Se classificado → mostrar badge na inbox
```

### 4.2 Fluxo de Resolução

```
Equipe marca TerritorialEvent como "resolvido"
        │
        ▼
Sistema identifica todos os contatos relacionados
        │
        ├─ Contacts que enviaram mensagens sobre este evento
        ├─ Filtro: apenas com consentimento
        └─ Filtro: apenas sem opt-out
        │
        ▼
Mostra público impactado (quantidade, perfil)
        │
        ▼
Equipe seleciona:
        ├─ Quem receberá retorno
        ├─ Canal(is): WhatsApp | SMS | Email | Combinação
        ├─ Tom da mensagem
        └─ Revisa/Aprova mensagem gerada por IA
        │
        ▼
Sistema envia mensagens (com fila)
        │
        ▼
Registra no CRM de cada contato
        │
        ▼
Registra no TerritorialEvent
        │
        ▼
Métricas de entrega → Dashboard
```

### 4.3 Fluxo de Campanha

```
Usuário cria Campanha
        │
        ├─ Nome, objetivo, canal(is), agendamento
        ├─ Seleciona Segmento (ou cria na hora)
        └─ Gera/escreve mensagem
        │
        ▼
Status: RASCUNHO
        │
        ▼
Revisão → Aprovação
        │
        ▼
Se aprovada → AGENDADA
        │
        ▼
No horário agendado → EM ENVIO
        │
        ▼
Queue System processa em lotes
        │
        ├─ Para cada contato no segmento:
        │   ├─ Verificar consentimento
        │   ├─ Verificar opt-out
        │   ├─ Personalizar mensagem (variáveis)
        │   ├─ Escolher provider (canal)
        │   ├─ Enviar
        │   ├─ Registrar Message + status
        │   └─ Atualizar métricas
        │
        ▼
Status: CONCLUÍDA (ou PAUSADA / COM ERRO)
        │
        ▼
Métricas: previstos, enviados, entregues, lidos, respondidos, erros, custos
```

---

## 5. MODELO DE DADOS (NOVOS/ESTENDIDOS)

### 5.1 Novas Tabelas

```sql
-- Classificação da mensagem pelo pipeline de IA
CREATE TABLE message_classifications (
    id UUID PRIMARY KEY,
    message_id UUID REFERENCES messages(id),
    tenant_id UUID REFERENCES tenants(id),
    type VARCHAR(50) NOT NULL,        -- complaint, praise, suggestion, doubt, denunciation, etc.
    category VARCHAR(100),             -- infrastructure, health, education, etc.
    subcategory VARCHAR(100),          -- pavement, lighting, garbage, etc.
    sentiment VARCHAR(20),             -- positive, negative, neutral
    sentiment_score FLOAT,
    urgency VARCHAR(20),               -- low, medium, high, emergency
    risk VARCHAR(20),                  -- low, medium, high
    address TEXT,                      -- endereço extraído
    neighborhood VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(50),
    latitude FLOAT,
    longitude FLOAT,
    reference_point TEXT,              -- ponto de referência
    suggested_department VARCHAR(255), -- secretaria/órgão sugerido
    summary TEXT,                      -- resumo gerado por IA
    keywords JSON,                     -- palavras-chave extraídas
    confidence FLOAT,                  -- confiança da classificação
    raw_prompt TEXT,                   -- prompt usado
    model VARCHAR(100),                -- modelo de IA usado
    processed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Segmentos de público
CREATE TABLE segments (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(50) NOT NULL,         -- manual, dynamic, imported, ai_generated, territorial
    filters JSON,                      -- critérios de filtro (dinâmico)
    contacts JSON,                     -- contatos fixos (manual)
    territorial_event_id UUID REFERENCES territorial_events(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- Consentimentos do contato por canal
CREATE TABLE consents (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    contact_id UUID REFERENCES contacts(id),
    channel VARCHAR(50) NOT NULL,      -- whatsapp, sms, email
    status VARCHAR(20) NOT NULL,       -- granted, denied, pending
    source VARCHAR(50),                -- opt_in_form, campaign, manual, import
    granted_at TIMESTAMP,
    denied_at TIMESTAMP,
    expires_at TIMESTAMP,
    metadata JSON,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    UNIQUE(contact_id, channel)
);

-- Campanhas (estendido com novos campos)
-- Campo strategy adicionado à tabela campaigns:
-- strategy: simultaneous, sequential, preference, consent
-- secondary_channel_id: UUID
-- tertiary_channel_id: UUID
-- approval_status: pending_review, approved, rejected
-- approved_by: UUID REFERENCES users(id)
-- approved_at: TIMESTAMP
-- tone: VARCHAR(50)
-- cost_estimate: JSON

-- Mensagens de campanha (estendido)
-- Campo campaign_id já existe
-- Adicionar: cost FLOAT, channel_failure_reason TEXT

-- Templates de mensagem
CREATE TABLE message_templates (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    name VARCHAR(255) NOT NULL,
    channel VARCHAR(50) NOT NULL,      -- whatsapp, sms, email
    type VARCHAR(50) NOT NULL,         -- text, html, template
    subject TEXT,                      -- para email
    body TEXT NOT NULL,
    variables JSON,                    -- lista de variáveis esperadas
    category VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- Log de aprovação
CREATE TABLE approval_logs (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    entity_type VARCHAR(50) NOT NULL,   -- campaign, message, audio, video
    entity_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL,        -- pending, approved, rejected
    reviewer_id UUID REFERENCES users(id),
    notes TEXT,
    version INT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 5.2 Campos Novos em Tabelas Existentes

**contacts** (adicionar):
- `consent_whatsapp` BOOLEAN DEFAULT FALSE
- `consent_sms` BOOLEAN DEFAULT FALSE
- `consent_email` BOOLEAN DEFAULT FALSE
- `communication_preference` VARCHAR(20) -- whatsapp, sms, email
- `last_interaction_at` TIMESTAMP
- `interaction_count` INTEGER DEFAULT 0
- `notes` TEXT
- `source` VARCHAR(100) -- origem do contato

**territorial_events** (adicionar):
- `report_count` INTEGER DEFAULT 1
- `unique_citizens` INTEGER DEFAULT 1
- `sentiment_score` FLOAT
- `dominant_type` VARCHAR(50)
- `photos` JSON
- `videos` JSON
- `audios` JSON
- `resolution_status` VARCHAR(20) DEFAULT 'open' -- open, in_progress, resolved, closed
- `resolved_at` TIMESTAMP
- `notified_count` INTEGER DEFAULT 0
- `responded_count` INTEGER DEFAULT 0

---

## 6. ESTRUTURA DE PROVIDERS

### 6.1 Hierarquia Atual

```
MessageProvider (ABC)
├── WhatsAppProvider (Meta Cloud API)     ✅
├── EmailProvider (Resend + SMTP)          ✅
└── SmsProvider                            ✅ (verificar)
```

### 6.2 Providers a Adicionar

```
MessageProvider (ABC)
├── WhatsAppProvider (Meta Cloud API)     ✅
├── ZApiProvider                           🔧 (wrapper)
├── EvolutionApiProvider                   🔧 (wrapper)
├── EmailProvider (Resend + SMTP)         ✅
├── SmsProvider                            ✅
│
AudioProvider (ABC)                       🔧 NOVO
├── ElevenLabsProvider                    🔧
└── (futuro: OpenAI TTS, Google TTS)
│
VideoAvatarProvider (ABC)                  🔧 NOVO
├── HeyGenProvider                        🔧
└── (futuro: D-ID, Synthesia)
│
LLMProvider (ABC)                          🔧 NOVO
├── OpenAIProvider
├── AnthropicProvider
└── (para classificação + geração de texto)
```

### 6.3 Interface WhatsAppProvider Estendida

```python
class WhatsAppProvider(MessageProvider):
    async def send_text(self, to, text) -> MessageStatus
    async def send_media(self, to, media_url, caption) -> MessageStatus
    async def send_template(self, to, template_name, params) -> MessageStatus
    async def send_audio(self, to, audio_url) -> MessageStatus       # NOVO
    async def send_video(self, to, video_url, caption) -> MessageStatus  # NOVO
    async def get_status(self, message_id) -> DeliveryStatus
    async def process_webhook(self, data) -> IncomingMessage
    async def get_account_health(self) -> dict                        # NOVO
    async def get_templates(self) -> list                             # NOVO
```

### 6.4 Interface AudioProvider

```python
class AudioProvider(ABC):
    async def list_voices(self) -> list[Voice]
    async def clone_voice(self, audio_sample, name) -> Voice
    async def generate_audio(self, text, voice_id, options) -> AudioResult
    async def get_cost_estimate(self, text, voice_id) -> float
```

### 6.5 Interface VideoAvatarProvider

```python
class VideoAvatarProvider(ABC):
    async def list_avatars(self) -> list[Avatar]
    async def generate_video(self, text, avatar_id, voice_id, options) -> VideoResult
    async def personalize_video(self, text, avatar_id, variables) -> VideoResult
    async def get_cost_estimate(self, text, avatar_id) -> float
```

---

## 7. PIPELINE DE IA

### 7.1 Arquitetura

```
Mensagem Recebida
        │
        ▼
┌─────────────────────────────────────┐
│         Orchestrator                │
│  (chama cada etapa em sequência     │
│   ou paralelo quando possível)      │
└──────┬──────────┬──────────┬────────┘
       │          │          │
       ▼          ▼          ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│Classifi- │ │Extração  │ │Geocodifi-│
│cação     │ │Territorial│ │cação     │
│(LLM)     │ │(LLM+NLP) │ │(API)     │
└──────────┘ └──────────┘ └──────────┘
       │          │          │
       └──────────┴──────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│         MessageClassification       │
│  Salvo no banco + vinculado à       │
│  mensagem original                  │
└─────────────────────────────────────┘
```

### 7.2 Prompt de Classificação

```python
SYSTEM_PROMPT = """
Você é um classificador de mensagens para uma plataforma de reclamações cidadãs.
Analise a mensagem abaixo e retorne UM JSON com:

{
  "type": "complaint" | "praise" | "suggestion" | "question" | "denunciation" | "support" | "criticism" | "emergency" | "general",
  "category": "infraestrutura" | "saude" | "educacao" | "seguranca" | "transporte" | "iluminacao" | "limpeza" | "meio_ambiente" | "habitacao" | "outro",
  "subcategory": "pavimentacao" | "buraco" | "esgoto" | "agua" | "luz" | "coleta_lixo" | "poda_arvore" | "outro",
  "sentiment": "positivo" | "negativo" | "neutro",
  "sentiment_score": 0.0 a 1.0,
  "urgency": "baixa" | "media" | "alta" | "emergencia",
  "risk": "baixo" | "medio" | "alto",
  "address": "endereço completo se encontrado",
  "neighborhood": "bairro",
  "city": "cidade",
  "state": "estado",
  "reference_point": "ponto de referência próximo",
  "suggested_department": "secretaria ou órgão responsável",
  "summary": "resumo de até 100 caracteres",
  "keywords": ["palavra1", "palavra2"],
  "confidence": 0.0 a 1.0
}

Mensagem:
{text}
"""
```

### 7.3 Modelo de IA Recomendado

| Tarefa | Modelo | Provider | Custo |
|---|---|---|---|
| Classificação | GPT-4o-mini / Claude 3 Haiku | OpenAI / Anthropic | ~$0.001/msg |
| Extração de endereço | GPT-4o-mini | OpenAI | ~$0.001/msg |
| Geração de texto | GPT-4o / Claude 3 Sonnet | OpenAI / Anthropic | ~$0.01/msg |
| Geração de áudio | ElevenLabs | ElevenLabs | ~$0.01/min |
| Geração de vídeo | HeyGen | HeyGen | ~$0.10/video |
| Geocodificação | Nominatim (OSM) ou Google Maps | Grátis/Pago | Grátis-~$0.005 |

---

## 8. SEGMENTAÇÃO

### 8.1 Tipos de Segmento

| Tipo | Descrição | Quando usar |
|---|---|---|
| **Manual** | Lista fixa de contatos selecionados um a um | Ações pontuais |
| **Dinâmico** | Filtros que são reavaliados a cada execução | Campanhas recorrentes |
| **Importado** | CSV/planilha subida pelo usuário | Base externa |
| **IA** | Segmento sugerido pelo sistema baseado em padrões | Descoberta |
| **Territorial** | Contatos vinculados a um evento no mapa | Resolução/notificação |

### 8.2 Filtros Disponíveis

```python
FILTERS = {
    "city": "string",                          # Cidade
    "neighborhood": "string",                   # Bairro
    "address": "string",                        # Rua/endereço
    "cep": "string",                            # CEP
    "region": "string",                         # Região administrativa
    "category": ["infraestrutura", "saude"],    # Categoria de reclamação
    "subcategory": ["pavimentacao"],            # Subcategoria
    "territorial_event_id": "uuid",             # Evento territorial específico
    "complained": True,                         # Pessoas que reclamaram
    "praised": True,                            # Pessoas que elogiaram
    "sent_media": True,                         # Pessoas que enviaram foto/vídeo
    "has_protocol": True,                       # Pessoas com protocolo
    "resolved": True,                           # Pessoas com problema resolvido
    "no_response": True,                        # Pessoas sem resposta
    "consent_whatsapp": True,                   # Consentimento WhatsApp
    "consent_sms": True,                        # Consentimento SMS
    "consent_email": True,                      # Consentimento Email
    "last_interaction_days": 30,                # Última interação em dias
    "interaction_count_min": 3,                 # Mínimo de interações
    "interaction_count_max": 10,                # Máximo de interações
    "tags": ["tag1", "tag2"],                   # Tags
    "channel": "whatsapp",                      # Canal de origem
    "assigned_to": "user_id",                   # Responsável
    "previous_campaign": "campaign_id",         # Campanha anterior
    "crm_status": "active",                     # Status no CRM
}
```

### 8.3 Regras de Consentimento

```
NUNCA enviar para canais sem consentimento explícito
NUNCA re-enviar após opt-out
Sempre registrar data/hora do opt-out
Opt-out em UM canal não cancela outros canais
Respeitar preferência do contato (communication_preference)
```

---

## 9. CAMPANHAS MULTICANAIS

### 9.1 Estratégias de Orquestração

| Estratégia | Comportamento |
|---|---|
| **Simultânea** | Envia WhatsApp + SMS + Email ao mesmo tempo |
| **Sequencial** | WhatsApp → se não entregar em X min → SMS → se não responder em Y dias → Email |
| **Preferência** | Usa o canal preferido do contato; fallback automático se falhar |
| **Consentimento** | Envia apenas pelos canais que o contato autorizou |

### 9.2 Canais Suportados (MVP)

| Canal | Provider | Status |
|---|---|---|
| WhatsApp | Meta Cloud API | ✅ |
| SMS | SmsProvider | ✅ |
| Email | EmailProvider | ✅ |
| WhatsApp + SMS | Orquestrador | 🔧 |
| WhatsApp + Email | Orquestrador | 🔧 |
| SMS + Email | Orquestrador | 🔧 |
| Todos | Orquestrador | 🔧 |

### 9.3 Status da Campanha

```
RASCUNHO → EM REVISÃO → APROVADA → AGENDADA → EM ENVIO → CONCLUÍDA
                                ↘ PAUSADA → EM ENVIO
                                ↘ CANCELADA
                                ↘ COM ERRO
```

---

## 10. GERAÇÃO DE MENSAGEM POR IA

### 10.1 Variáveis Disponíveis

```
{{primeiro_nome}}        → "Maria"
{{nome_completo}}        → "Maria da Silva"
{{bairro}}              → "Praia da Costa"
{{cidade}}              → "Vila Velha"
{{estado}}              → "ES"
{{tema}}                → "iluminação pública"
{{problema}}            → "poste queimado"
{{evento}}              → nome do TerritorialEvent
{{status}}              → status do evento
{{protocolo}}           → número do protocolo
{{acao_realizada}}      → "troca da lâmpada"
{{data}}                → "22/07/2026"
{{responsavel}}         → "Secretaria de Obras"
{{canal}}               → "WhatsApp"
```

### 10.2 Tons Disponíveis

| Tom | Descrição |
|---|---|
| `institucional` | Tom padrão do órgão público |
| `acolhedor` | Caloroso, empático |
| `próximo` | Informal, humano, sem burocracia |
| `formal` | Protocolar, impessoal |
| `informativo` | Objetivo, dados concretos |
| `celebrativo` | Comemorativo, positivo |
| `tranquilizador` | Calmo, seguro, resolve ansiedade |
| `urgente` | Direto, alerta, sem rodeios |
| `prestacao_contas` | Transparente, dados do que foi feito |
| `direto` | Enxuto, vai direto ao ponto |
| `inspirador` | Motivacional, engajamento |
| `personalizado` | Instrução livre do usuário |

### 10.3 Prompt de Geração

```python
SYSTEM_PROMPT = """
Você é um redator de comunicação pública.
Gere uma mensagem de {tone} para {channel}.

Destinatário: {first_name}
Bairro: {neighborhood}
Cidade: {city}
Tema: {topic}
Problema: {issue}
Protocolo: {protocol}
Ação realizada: {action}

Regras:
- Mínimo 50 caracteres, máximo 500
- Use o nome da pessoa naturalmente
- Não use jargão técnico
- Seja claro e direto
- A mensagem deve soar humana, não robotizada
- Não pareça propaganda política
- Mostre gratidão pela participação cidadã
"""
```

---

## 11. APROVAÇÃO E GOVERNANÇA

### 11.1 Fluxo de Aprovação

```
CRIADOR                     REVISOR                     APROVADOR
   │                          │                            │
   ├─ Cria rascunho           │                            │
   │                          │                            │
   ├─ Envia para revisão ─────► Revisa conteúdo            │
   │                          │   ├─ Aprova? ──────────────► Aprova final
   │                          │   ├─ Pede alterações ──►   Volta p/ criador
   │                          │   └─ Rejeita ──────────►   Arquivado
   │                          │                            │
   ├─ Recebe feedback         │                            │
   ├─ Ajusta                  │                            │
   └─ Reenvia ────────────────┘                            │
                                                           │
Campanha agendada ◄─────────────────── Aprovação final ───┘
```

### 11.2 Registro de Auditoria

```sql
-- Todo passo fica registrado em approval_logs e audit_logs
-- Quem criou, editou, aprovou, disparou
-- Conteúdo final, público, canal, data
-- Versão do conteúdo
-- Modelo e prompt de IA utilizados
```

---

## 12. FILAS E WORKERS

### 12.1 Arquitetura de Filas

```
[API]──nova campanha──►[Queue: campaigns_to_send]
                            │
                    [Worker: campaign_worker]
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
      [Queue: whatsapp] [Queue: sms] [Queue: email]
              │             │             │
      [Worker: wpp]  [Worker: sms]  [Worker: email]
              │             │             │
              ▼             ▼             ▼
         Provider API  Provider API  Provider API
```

### 12.2 Tecnologia Recomendada

| Opção | Prós | Contras |
|---|---|---|
| **Redis + RQ** | Simples, rápido, já temos Redis | Sem persistência |
| **Celery** | Maduro, agendamento, retry | Pesado para o escopo |
| **APScheduler + SQLite** | Zero dependências, persistente | Sem workers paralelos |
| **ARQ (Redis)** | Async nativo, simples, rápido | Precisa Redis |

**Recomendação MVP:** APScheduler + SQLite (já temos SQLite, zero novas dependências). Depois migrar para ARQ (Redis) quando escalar.

### 12.3 Rate Limiting

```python
# Meta Cloud API: ~80 req/s por número
# SMS: depende do provider
# Email: ~10 req/s (Resend free)

RATE_LIMITS = {
    "whatsapp": {"max_per_second": 50, "max_per_minute": 2000},
    "whatsapp_template": {"max_per_second": 10, "max_per_minute": 250},
    "sms": {"max_per_second": 10, "max_per_minute": 500},
    "email": {"max_per_second": 5, "max_per_minute": 100},
}
```

---

## 13. CONSENTIMENTO E OPT-OUT

### 13.1 Regras de Negócio

```
1. TODO envio deve verificar consentimento
2. Consentimento é POR CANAL (WhatsApp, SMS, Email)
3. Opt-out em UM canal NÃO afeta outros canais
4. Opt-out deve ser processado em até 24h
5. Mensagens transacionais (protocolo, resolução) têm regras diferentes
6. Contato pode revogar consentimento a qualquer momento
7. Registrar data/hora de TODAS as mudanças de consentimento
8. NUNCA enviar mensagem promocional sem consentimento
9. Mensagens de resolução de problema podem ser enviadas mesmo sem consentimento prévio (interesse legítimo)
```

### 13.2 Fluxo de Opt-out via WhatsApp

```
Usuário envia "SAIR" ou "PARE" ou "NÃO QUERO" no WhatsApp
        │
        ▼
Pipeline de IA detecta intenção de opt-out
        │
        ▼
Atualiza consents (status=denied, channel=whatsapp)
        │
        ▼
Registra timestamp e motivo
        │
        ▼
Envia confirmação: "Você não receberá mais mensagens pelo WhatsApp"
```

---

## 14. CUSTOS POR CANAL

### 14.1 Estimativas

| Canal | Custo Médio | Observação |
|---|---|---|
| **WhatsApp (Meta)** | ~$0.005/msg (Marketing) | Template messages |
| **WhatsApp (Meta)** | ~$0.001/msg (Utility) | Senhas, protocolos |
| **WhatsApp (Meta)** | Grátis (Service) | Resposta a conversas iniciadas |
| **SMS (Brasil)** | ~$0.02-0.05/SMS | Depende do volume |
| **Email (Resend)** | Grátis (primeiras 3k/mês) | Depois ~$0.001/email |
| **Email (SMTP)** | ~$0.001/email | Servidor próprio |
| **Áudio (ElevenLabs)** | ~$0.01/min | TTS |
| **Vídeo (HeyGen)** | ~$0.10/video | Avatar + TTS |

### 14.2 Tracking de Custos

```python
# Registrar por mensagem:
{
    "channel": "whatsapp",
    "provider": "meta_cloud_api",
    "message_type": "template",
    "cost": 0.005,
    "currency": "USD",
    "charged_to": "tenant_id",
    "campaign_id": "uuid"
}

# Agregado por campanha:
{
    "total_cost": 12.50,
    "cost_per_contact": 0.005,
    "cost_by_channel": {
        "whatsapp": 10.00,
        "sms": 2.50
    }
}
```

---

## 15. TELAS / FRONTEND

### 15.1 Telas do MVP (Fase 1)

| # | Tela | Descrição |
|---|---|---|
| 1 | **Configurações de WhatsApp** | Conectar número, ver status, templates |
| 2 | **Caixa de Entrada** | Lista de conversas com classificação, filtros, ações |
| 3 | **Conversa Detalhada** | Histórico completo, resposta manual/IA |
| 4 | **Contato Detalhado** | Perfil, consentimentos, histórico, segmentos |
| 5 | **Mapa** | Eventos territoriais com clustering |
| 6 | **Evento Territorial Detalhado** | Relatos, fotos, resolvidos, cidadãos |

### 15.2 Telas do MVP (Fase 2)

| # | Tela | Descrição |
|---|---|---|
| 7 | **Públicos e Segmentos** | Lista, criar, editar, visualizar contagens |
| 8 | **Criar Segmento** | Builder com filtros |
| 9 | **Campanhas** | Lista com status e métricas |
| 10 | **Nova Campanha** | Wizard: público → canal → mensagem → agendamento |
| 11 | **Editor de Mensagem** | Texto com variáveis e preview |
| 12 | **Aprovação de Campanha** | Revisão e aprovação |

### 15.3 Telas Futuras (Fases 3-5)

| # | Tela | Descrição |
|---|---|---|
| 13 | **Gerador de Áudio** | Voz, preview, aprovação |
| 14 | **Gerador de Vídeo** | Avatar, voz, preview |
| 15 | **Editor de Email** | HTML, visual, templates |
| 16 | **Editor de SMS** | Caracteres, partes, preview |
| 17 | **Histórico de Envios** | Auditoria por campanha/contato |
| 18 | **Métricas de Comunicação** | Dashboard especializado |
| 19 | **Templates** | Gerenciar templates de mensagem |
| 20 | **Consentimentos** | Gerenciar permissões em lote |

---

## 16. APIs

### 16.1 APIs Existentes (reuso)

| Endpoint | Módulo | Uso |
|---|---|---|
| `GET/POST /whatsapp/*` | whatsapp | Status, envio, webhook |
| `CRUD /contacts/*` | contacts | Contatos |
| `CRUD /conversations/*` | conversations | Conversas |
| `CRUD /messages/*` | messages | Mensagens |
| `CRUD /campaigns/*` | campaigns | Campanhas |
| `CRUD /territorial/*` | territorial | Eventos |
| `CRUD /protocols/*` | protocols | Protocolos |
| `CRUD /channels/*` | channels | Canais |

### 16.2 Novas APIs Necessárias

```
# Classificação
POST /api/ai/classify              ← Classificar mensagem manualmente
POST /api/ai/classify/batch         ← Reclassificar lote
GET  /api/classifications/{id}      ← Ver classificação

# Segmentos
CRUD /api/segments                  ← Gerenciar segmentos
POST /api/segments/{id}/preview     ← Ver contagem de contatos no segmento
POST /api/segments/{id}/export      ← Exportar lista

# Campanhas (estendido)
POST /api/campaigns/{id}/approve    ← Aprovar campanha
POST /api/campaigns/{id}/reject     ← Rejeitar
POST /api/campaigns/{id}/resend     ← Reenviar para falhas
GET  /api/campaigns/{id}/cost       ← Estimar custo

# Mensagens multicanal
POST /api/communication/send        ← Enviar para contato específico em canal específico
POST /api/communication/batch       ← Enviar para lote

# Consentimento
GET  /api/consents                  ← Listar consentimentos
POST /api/consents/grant            ← Conceder permissão
POST /api/consents/deny             ← Revogar
POST /api/consents/opt-out          ← Processar opt-out

# Templates
CRUD /api/templates                 ← Templates de mensagem

# Geração IA
POST /api/ai/generate-text          ← Gerar texto personalizado
POST /api/ai/generate-audio         ← Gerar áudio (futuro)
POST /api/ai/generate-video         ← Gerar vídeo (futuro)

# Fluxo de resolução
GET  /api/resolution/{event_id}/impacted  ← Ver cidadãos impactados
POST /api/resolution/{event_id}/notify    ← Notificar cidadãos sobre resolução

# Métricas
GET  /api/communication/metrics           ← Dashboard de comunicação
GET  /api/communication/metrics/export    ← Exportar relatório

# Workers
POST /api/admin/queue/status              ← Status da fila
POST /api/admin/queue/retry-failed        ← Reenviar mensagens com erro
```

---

## 17. WEBHOOKS

### 17.1 Webhook de Mensagem Recebida (WhatsApp)

```
POST /api/whatsapp/webhook
  └─ Meta Cloud API callback
  └─ Verificar assinatura
  └─ Parse → IncomingMessage
  └─ Pipeline de IA (async)
  └─ Criar/Atualizar Contact
  └─ Criar/Atualizar Conversation
  └─ Salvar Message
  └─ Associar a TerritorialEvent
  └─ Notificar na inbox
```

### 17.2 Webhook de Status de Mensagem

```
POST /api/whatsapp/webhook
  └─ Status: sent, delivered, read, failed
  └─ Atualizar Message.provider_status
  └─ Atualizar Campaign.sent_count/failed_count
  └─ Disparar estratégia sequencial se falhou
```

### 17.3 Webhook de Template Aprovado

```
POST /api/whatsapp/webhook
  └─ Template status update
  └─ Atualizar lista de templates do Channel
```

---

## 18. BACKLOG E ORDEM DE IMPLEMENTAÇÃO

### FASE 1 — Fundação do Fluxo Cidadão (MVP Essencial)

| Ordem | Tarefa | Esforço | Depende de |
|---|---|---|---|
| 1 | Pipeline de classificação IA (tipo, sentimento, endereço) | 2 dias | Agente IA configurado |
| 2 | Extração territorial + geocodificação | 1 dia | #1 |
| 3 | Vincular mensagem a TerritorialEvent (criar/se associar) | 1 dia | #2 |
| 4 | Caixa de entrada unificada (frontend) | 2 dias | #1, #3 |
| 5 | Conversa detalhada com classificação visível | 1 dia | #4 |
| 6 | Mapa com eventos territoriais e clustering | 1 dia | #3 |
| 7 | Fluxo de resolução: marcar resolvido → mostrar afetados | 1 dia | #3, #5 |
| 8 | Resposta manual com sugestão de IA | 1 dia | #1, #5 |
| 9 | Contact detail: perfil + consentimentos + histórico | 1 dia | #5 |
| 10 | Queue system (APScheduler + SQLite) | 1 dia | — |

**Total Fase 1: ~12 dias**

### FASE 2 — Campanhas e Segmentação

| Ordem | Tarefa | Esforço | Depende de |
|---|---|---|---|
| 11 | Segment builder (criar segmentos com filtros) | 2 dias | — |
| 12 | Preview de segmento (contagem de contatos) | 0.5 dia | #11 |
| 13 | Campanha multicanal (selecionar canais) | 2 dias | #10, #11 |
| 14 | Geração de mensagem com IA (tom, variáveis) | 1 dia | — |
| 15 | Personalização de mensagem (variáveis → valores) | 1 dia | #14 |
| 16 | Agendamento de campanha | 0.5 dia | #13 |
| 17 | Envio em lote com fila + rate limit | 2 dias | #10, #13 |
| 18 | Consentimento / opt-out | 1 dia | — |
| 19 | Métricas de campanha (entregues, lidos, respostas) | 1 dia | #17 |
| 20 | Aprovação de campanha (revisão antes do envio) | 1 dia | #13 |

**Total Fase 2: ~12 dias**

### FASE 3 — Email e SMS Avançados

| Ordem | Tarefa | Esforço |
|---|---|---|
| 21 | Templates de email (editor visual) | 2 dias |
| 22 | Estratégia sequencial de envio | 1 dia |
| 23 | Templates de SMS | 0.5 dia |
| 24 | Custo tracking por mensagem | 1 dia |
| 25 | Exportar relatório de comunicação | 1 dia |

**Total Fase 3: ~5.5 dias**

### FASE 4 — Áudio

| Ordem | Tarefa | Esforço |
|---|---|---|
| 26 | AudioProvider (ElevenLabs) | 1 dia |
| 27 | Geração de áudio com preview | 1 dia |
| 28 | Envio de áudio via WhatsApp | 0.5 dia |
| 29 | Aprovação de áudio antes do lote | 0.5 dia |

**Total Fase 4: ~3 dias**

### FASE 5 — Vídeo

| Ordem | Tarefa | Esforço |
|---|---|---|
| 30 | VideoAvatarProvider (HeyGen) | 1 dia |
| 31 | Geração de vídeo com preview | 1.5 dias |
| 32 | Personalização controlada (nome/bairro) | 1 dia |
| 33 | Aprovação de vídeo antes do lote | 0.5 dia |

**Total Fase 5: ~4 dias**

---

## 19. RISCOS

| Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|
| **Token WhatsApp expira** | Alta | Crítico | Monitorar health_check, alertar antes de expirar |
| **Rate limit do Meta** | Média | Alto | Implementar rate limiting interno, fila com backoff |
| **Custo de IA escala** | Média | Médio | Usar modelos mais baratos (GPT-4o-mini) para classificação |
| **Geocodificação falha** | Média | Médio | Fallback para endereço textual sem coordenadas |
| **ElevenLabs fora do ar** | Baixa | Médio | Cache de áudios gerados, fallback para TTS gratuito |
| **HeyGen fora do ar** | Baixa | Médio | Fallback para áudio + imagem estática |
| **SQLite concorrência** | Média | Alto | Migrar para PostgreSQL quando escalar (>10k msg/dia) |
| **Campanha enviada sem querer** | Baixa | Crítico | Dupla aprovação obrigatória, confirmação explícita |
| **Opt-out não respeitado** | Baixa | Crítico | Verificação dupla antes de cada envio |
| **Dados sensíveis expostos** | Baixa | Crítico | Criptografia das credenciais, nunca expor em logs |

---

## 20. PRÓXIMO PASSO TÉCNICO

### 🔨 Começar pela FASE 1, item 1: Pipeline de Classificação IA

**Implementação concreta:**

1. Criar `src/services/classification/` com:
   - `classifier.py` — Orquestrador que chama LLM
   - `schemas.py` — `MessageClassification` schema
   - `prompts.py` — Prompts de classificação e extração
   - `geocoding.py` — Serviço de geocodificação (Nominatim)
   - `matcher.py` — Busca de eventos territoriais próximos

2. Conectar ao webhook do WhatsApp:
   - Após `WhatsAppCloudService.parse_incoming_message()`
   - Disparar classificação assíncrona
   - Salvar `MessageClassification`
   - Vincular a `TerritorialEvent`

3. Criar endpoint `GET /api/whatsapp/messages` que retorna mensagens com classificação

---

> **Documento gerado por Mirai — Arca v2**
> Anexo Técnico: `polis/docs/arquitetura-comunicacao-multicanal.md`
