# Arquitetura Técnica — Polis (Political OS)

> **Versão:** 0.1.0  
> **Data:** 2026-07-22  
> **Status:** Rascunho  
> **Subdomínio:** `polis.miraitohope.com`

---

## 1. Stack Tecnológica

| Camada | Tecnologia | Versão | Finalidade |
|--------|-----------|--------|------------|
| **Frontend** | Next.js (App Router) | 15.x | Interface SPA + SSR + Páginas públicas |
| **Linguagem** | TypeScript | 5.8+ | Tipagem segura front/back |
| **Backend** | Next.js API Routes | 15.x | API REST monolítica modular |
| **ORM** | Prisma | 6.x | Type-safe schema + migrations |
| **Banco Relacional** | PostgreSQL | 16.x | Dados estruturados da plataforma |
| **Banco Geoespacial** | PostGIS | 3.5+ | Dados territoriais (mapas, zonas eleitorais) |
| **Cache / Filas** | Redis | 7.x | Cache, sessões, BullMQ, rate-limit |
| **Job Queue** | BullMQ | 5.x | Processamento assíncrono (campanhas, envio) |
| **Containerização** | Docker + Compose | latest | Ambiente dev/prod replicável |
| **Proxy** | Nginx / Caddy | latest | Reverso, SSL, rate-limit |
| **LLM** | Gemini / OpenAI API | — | Agentes IA, classificação, RAG |
| **Embeddings** | Qdrant / pgvector | — | RAG, busca semântica de conhecimento |
| **Monitoria** | Sentry / Prometheus | — | Logs, métricas, tracing |

### Justificativas

- **Next.js 15 App Router**: monolito modular com Server Components, React Server Actions para operações leves, e API Routes para a camada REST. Um único deploy gerencia UI + API.
- **PostgreSQL + PostGIS**: dados geoespaciais são requisito central (zonas eleitorais, mapas de calor, distribuição territorial).
- **Prisma sobre SQLAlchemy**: o ecossistema Next.js se beneficia de Prisma (schema-first, migrations, type safety nativo). O SQLAlchemy do Arca não será portado.
- **BullMQ + Redis**: campanhas de disparo em massa (WhatsApp, SMS, Email) precisam de filas confiáveis com retry, rate-limit e agendamento.
- **pgvector**: extensão nativa do PostgreSQL para ANN (approximate nearest neighbor) — evita um serviço Qdrant separado em versões iniciais.

---

## 2. Diagrama de Módulos

```
┌─────────────────────────────────────────────────────────────┐
│                        POLIS PLATFORM                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Auth    │  │  Tenants  │  │   CRM    │  │   Mapa   │   │
│  │  Module   │  │  Module   │  │  Module  │  │  Module  │   │
│  ├──────────┤  ├──────────┤  ├──────────┤  ├──────────┤   │
│  │• JWT/OAuth│  │• Multi-  │  │• Contatos│  │• Zonas   │   │
│  │• 2FA     │  │  tenant   │  │• Segment.│  │  eleitor.│   │
│  │• RBAC    │  │• Onboard  │  │• Pipeline│  │• Mapas   │   │
│  │• Sessões │  │• Settings │  │• Tags    │  │  calor   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  WhatsApp │  │ Campanhas│  │  Agentes  │  │ Analytics│   │
│  │  Module   │  │  Module  │  │IA Module │  │  Module  │   │
│  ├──────────┤  ├──────────┤  ├──────────┤  ├──────────┤   │
│  │• Caixa   │  │• Criação │  │• Chatbot │  │• Dados   │   │
│  │  entrada  │  │• Disparo │  │• RAG     │  │• Grafos  │   │
│  │• Template│  │• Filas   │  │• Classif.│  │• Reports │   │
│  │• Mídia   │  │• Tracking│  │• Workflows│  │• Copilot │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                   │
│  │  Tasks/  │  │  Protocol │  │  Audit   │                   │
│  │  Kanban  │  │  Module   │  │  Module  │                   │
│  ├──────────┤  ├──────────┤  ├──────────┤                   │
│  │• Tarefas │  │• Atend.  │  │• Logs    │                   │
│  │• Projetos│  │  público  │  │• LGPD    │                   │
│  │• Metas   │  │• Números │  │• Retenção│                   │
│  │• Equipe  │  │• Docs    │  │• Exports  │                   │
│  └──────────┘  └──────────┘  └──────────┘                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    INFRAESTRUTURA COMPARTILHADA              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │PostgreSQL│  │  Redis   │  │  Filestore│  │   LLM    │   │
│  │ +PostGIS │  │ +BullMQ  │  │  (S3)    │  │ Gateway  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Arquitetura de Serviços (Monolito Modular)

### Princípios

1. **Monolito modular** — todo o backend em um único processo Next.js (API Routes + Server Actions), organizado em módulos internos bem delimitados.
2. **Separação por domínio** — cada módulo tem seu próprio schema Prisma, services, validators e rotas.
3. **Filas para operações pesadas** — disparo em massa, processamento de mídia, campanhas → BullMQ + Redis workers.
4. **Providers para canais** — WhatsApp, SMS, Email, Push → interface de provedor com implementações plugáveis.
5. **Middleware chain** — auth → tenant → rate-limit → log em cada rota.

### Estrutura de Módulos

```
polis/
├── src/
│   ├── app/                          # Next.js App Router (páginas)
│   │   ├── (auth)/                   # Login, registro, senha
│   │   ├── (dashboard)/              # Painel principal
│   │   │   ├── crm/                  # Páginas do CRM
│   │   │   ├── campanhas/            # Páginas de campanhas
│   │   │   ├── whatsapp/            # Caixa de entrada
│   │   │   ├── agentes/             # Agentes IA
│   │   │   ├── mapa/                # Mapa eleitoral
│   │   │   ├── analytics/           # Dashboards
│   │   │   └── configuracoes/       # Settings
│   │   └── api/                      # API Routes (REST)
│   │       ├── auth/                 # POST login, refresh, logout
│   │       ├── tenants/              # CRUD tenants
│   │       ├── contacts/             # CRUD contatos
│   │       ├── conversations/        # Mensagens
│   │       ├── campaigns/            # Campanhas
│   │       ├── agents/               # Agentes IA
│   │       ├── whatsapp/             # Webhook + envio
│   │       ├── territorial/          # Eventos + mapa
│   │       ├── tasks/                # Tarefas
│   │       ├── protocols/            # Protocolos
│   │       └── analytics/            # Métricas
│   │
│   ├── lib/                          # Core compartilhado
│   │   ├── prisma.ts                 # Singleton PrismaClient
│   │   ├── redis.ts                  # Redis client + BullMQ
│   │   ├── auth.ts                   # JWT, sessões, middleware
│   │   ├── tenant.ts                 # Tenant resolution
│   │   ├── permissions.ts           # RBAC checker
│   │   └── audit.ts                 # Audit logger
│   │
│   ├── modules/                      # Módulos de negócio
│   │   ├── auth/
│   │   │   ├── auth.service.ts
│   │   │   ├── auth.validator.ts
│   │   │   ├── providers/           # OAuth providers
│   │   │   └── utils.ts
│   │   ├── crm/
│   │   │   ├── contact.service.ts
│   │   │   ├── segment.service.ts
│   │   │   └── import.service.ts
│   │   ├── whatsapp/
│   │   │   ├── whatsapp.service.ts
│   │   │   ├── webhook.handler.ts
│   │   │   └── providers/           # Evolution API, WWebJS, Cloud API
│   │   ├── campaigns/
│   │   │   ├── campaign.service.ts
│   │   │   ├── dispatch.service.ts
│   │   │   └── campaign.worker.ts   # BullMQ worker
│   │   ├── agents/
│   │   │   ├── agent.service.ts
│   │   │   ├── rag.service.ts
│   │   │   ├── classification.service.ts
│   │   │   └── llm.client.ts        # Gemini/OpenAI client
│   │   ├── territorial/
│   │   │   ├── event.service.ts
│   │   │   ├── map.service.ts
│   │   │   └── ranking.service.ts
│   │   ├── tasks/
│   │   │   └── task.service.ts
│   │   └── analytics/
│   │       ├── dashboard.service.ts
│   │       └── report.service.ts
│   │
│   ├── providers/                    # Camada de provedores
│   │   ├── whatsapp/
│   │   │   ├── evolution-api.ts
│   │   │   ├── cloud-api.ts
│   │   │   └── types.ts
│   │   ├── sms/
│   │   │   ├── twilio.ts
│   │   │   └── types.ts
│   │   ├── email/
│   │   │   ├── resend.ts
│   │   │   ├── sendgrid.ts
│   │   │   └── types.ts
│   │   └── storage/
│   │       ├── s3.ts
│   │       └── local.ts
│   │
│   ├── workers/                      # BullMQ workers (processo separado)
│   │   ├── campaign.worker.ts       # Disparo de campanhas
│   │   ├── message.worker.ts        # Processamento de mensagens
│   │   ├── import.worker.ts         # Importação de contatos
│   │   └── media.worker.ts          # Processamento de mídia
│   │
│   └── shared/                       # Tipos, utils, constantes
│       ├── types/
│       ├── utils/
│       └── constants/
│
├── prisma/
│   ├── schema.prisma                 # Schema completo
│   └── migrations/                   # Migrations versionadas
│
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── nginx.conf
│
├── scripts/
│   ├── seed.ts                       # Dados iniciais
│   └── migrate.ts                    # Scripts de migração
│
└── .env.example
```

---

## 4. Sistema Multi-Tenant

### Modelo de Isolamento

```
┌──────────────────────────────────────────────────────┐
│                     POLIS GLOBAL                       │
│                                                        │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐ │
│  │   Tenant A   │   │   Tenant B   │   │   Tenant C   │ │
│  │ (Partido X)  │   │ (Candidato Y)│   │ (Assessoria)│ │
│  ├─────────────┤   ├─────────────┤   ├─────────────┤ │
│  │ Usuários    │   │ Usuários    │   │ Usuários    │ │
│  │ Contatos    │   │ Contatos    │   │ Contatos    │ │
│  │ Campanhas   │   │ Campanhas   │   │ Campanhas   │ │
│  │ Mensagens   │   │ Mensagens   │   │ Mensagens   │ │
│  │ Agentes     │   │ Agentes     │   │ Agentes     │ │
│  │ Config      │   │ Config      │   │ Config      │ │
│  └─────────────┘   └─────────────┘   └─────────────┘ │
│                                                        │
│  Banco Único (PostgreSQL) com tenant_id em toda        │
│  entidade. Isolamento via RLS (Row-Level Security).    │
└──────────────────────────────────────────────────────┘
```

### Estratégia

- **Banco único com tenant_id**: todas as tabelas de dados (contacts, campaigns, messages, etc.) possuem `tenant_id UUID NOT NULL REFERENCES tenants(id)`.
- **Row-Level Security (RLS)**: política no PostgreSQL que automaticamente filtra por `tenant_id` no `current_setting('app.current_tenant_id')`.
- **Middleware de tenant**: extrai tenant do subdomínio (`${tenant}.polis.miraitohope.com`) ou header `X-Tenant-ID` → seta na sessão → seta no Redis para o BullMQ worker.
- **Workers**: recebem `tenant_id` no payload do job — isolamento é explícito no código do worker.
- **Settings por tenant**: tabela `tenant_settings` com JSONB para configurações flexíveis (cores, logo, canais ativos, limites).

### Fluxo de Resolução de Tenant

```
Request → subdomain.polis.miraitohope.com
  ↓
Middleware → extrai subdomain → busca tenant por slug
  ↓
Tenant encontrado → seta tenant_id no contexto (async local storage)
  ↓
Seta app.current_tenant_id na sessão do PostgreSQL (para RLS)
  ↓
Rota executa com tenant_id implícito
```

---

## 5. Camada de Providers

### Interface Abstrata

```typescript
// providers/types.ts
interface MessageProvider {
  send(to: string, content: MessageContent): Promise<MessageResult>;
  sendBulk(to: string[], content: MessageContent): Promise<MessageResult[]>;
  getStatus(messageId: string): Promise<MessageStatus>;
  webhookHandler(payload: unknown): Promise<WebhookEvent>;
}

interface MediaProvider {
  upload(file: Buffer, options: UploadOptions): Promise<string>;
  getUrl(mediaId: string): Promise<string>;
  delete(mediaId: string): Promise<void>;
}
```

### Provedores de WhatsApp

| Provedor | Tipo | Indicação | Custo |
|----------|------|-----------|-------|
| **Evolution API** | Self-hosted | Produção, liberdade total | Servidor próprio |
| **Cloud API (Meta)** | SaaS | Produção, oficial | Por conversa |
| **WhatsApp Web JS** | Bridge | Desenvolvimento / testes | Gratuito |

### Provedores de SMS

| Provedor | Indicação |
|----------|-----------|
| **Twilio** | Provedor principal (confiável, API madura) |
| **AWS SNS** | Fallback para alto volume |

### Provedores de Email

| Provedor | Indicação |
|----------|-----------|
| **Resend** | Transacional (principal) |
| **SendGrid** | Disparo em massa (campanhas) |

---

## 6. Fluxos Principais

### 6.1 Fluxo de Mensagem Recebida (WhatsApp → Polis)

```
WhatsApp → Webhook (Evolution API / Cloud API)
  ↓
API Route: POST /api/whatsapp/webhook
  ↓
Middleware: autentica HMAC/Token → resolve tenant (do número)
  ↓
whatsapp.service.ts:
  1. Parse payload → extrai remetente, conteúdo, tipo (texto, imagem, áudio)
  2. Busca ou cria contato (contact.service.ts)
  3. Cria conversa se não existir
  4. Cria mensagem (messages table)
  5. Enfileira job: message.process
  ↓
BullMQ Worker (message.worker.ts):
  1. Atualiza status da mensagem (delivered → read)
  2. Se agente IA ativo → agent.service:processMessage()
     a. LLM classifica intent (pergunta, reclamação, sugestão, spam)
     b. Se pergunta → busca RAG na knowledge base
     c. Gera resposta → enfileira job: message.send
  3. Se regra de automação → executa (tag, mover, responder)
  4. Loga no audit_logs
```

### 6.2 Fluxo de Campanha

```
Usuário cria campanha no dashboard
  ↓
POST /api/campaigns
  ↓
campaign.service.ts:
  1. Valida dados (nome, canal, conteúdo, segmento)
  2. Cria campaign (status: draft)
  3. Cria campaign_segments (filtros de contatos)
  4. Calcula total de recipients (query em contacts)
  ↓
Usuário revisa e confirma → PATCH /api/campaigns/:id/send
  ↓
campaign.service.ts:
  1. Valida saldo/limite do tenant
  2. Atualiza status → sending
  3. Cria campaign_recipients (INSERT de N recipients)
  4. Enfileira job: campaign.dispatch
  ↓
BullMQ Worker (campaign.worker.ts) — paralelo por batch:
  1. Busca batch de campaign_recipients (status: pending)
  2. Para cada recipient:
     a. Personaliza conteúdo (handlebars: {{nome}}, {{bairro}}, etc.)
     b. Envia via provider (WhatsApp / SMS / Email)
     c. Atualiza status (sent / failed)
     d. Loga em audit_logs
  3. Atualiza progresso da campanha (sent_count, fail_count)
  ↓
Campanha finalizada → notifica webhook ou push ao usuário
```

### 6.3 Fluxo do Agente IA

```
Mensagem recebida (ou usuário inicia conversa no modal)
  ↓
agent.service.ts:
  1. Resolve agente ativo do tenant (agents WHERE tenant_id AND active=true)
  2. Carrega personalidade, instruções, tom de voz
  ↓
rag.service.ts:
  1. Embeddings da pergunta (pgvector)
  2. Busca top-K na knowledge_bases do tenant (threshold de similaridade)
  3. Monta contexto (texto da KB + histórico da conversa)
  ↓
llm.client.ts:
  1. Monta prompt: personalidade + instruções + contexto + pergunta
  2. Chama LLM (Gemini / OpenAI) com streaming
  3. Retorna resposta token a token (SSE para o usuário)
  ↓
agent.service.ts:
  1. Classifica intenção e sentimento da resposta
  2. Se promessa ou compromisso → cria task
  3. Salva mensagem do agente na conversa
  ↓
Resposta enviada ao usuário (mesmo canal da mensagem original)
```

### 6.4 Fluxo de Evento Territorial

```
Fonte externa (API TSE, API IBGE, input manual, scraper)
  ↓
POST /api/territorial/events
  ↓
event.service.ts:
  1. Valida dados geoespaciais (lat/lng, zona eleitoral, bairro)
  2. Geocodifica endereço → coordenadas (se necessário)
  3. Salva territorial_event com ponto geográfico (PostGIS)
  ↓
Worker (opcional):
  1. Cruza evento com contatos da região → notificação segmentada
  2. Atualiza ranking de regiões
  3. Se evento crítico → alerta via push/email
  ↓
Dashboard de mapa (frontend):
  1. Query PostGIS: eventos nos últimos N dias, agrupados por zona
  2. Renderiza heatmap + pins no mapa (Mapbox / Leaflet)
  3. Sidebar com lista de eventos ordenados por data
```

---

## 7. Segurança e LGPD

### Controles de Segurança

| Camada | Controle | Implementação |
|--------|----------|---------------|
| **Rede** | HTTPS obrigatório | Caddy/Nginx com Let's Encrypt |
| **API** | Rate limiting | Redis + sliding window por tenant |
| **API** | CORS restrito | Whitelist de origins por tenant |
| **Auth** | JWT com refresh token | Access: 15min, Refresh: 7d (rotação) |
| **Auth** | 2FA opcional | TOTP (speakeasy) |
| **Auth** | Senha forte | Argon2id, min 8 chars, breach check |
| **RBAC** | Permissões granulares | role_permissions: CRUD por módulo |
| **Input** | Validação | Zod schemas em todas as rotas |
| **DB** | SQL Injection | Prisma (parameterized queries nativas) |
| **DB** | RLS | Row-Level Security por tenant_id |

### LGPD (Lei Geral de Proteção de Dados)

| Requisito | Implementação |
|-----------|---------------|
| **Consentimento** | Tabela `contact_consents` com tipo, data, origem, ip |
| **Finalidade** | Cada consentimento vinculado a uma finalidade (marketing, comunicação oficial, pesquisa) |
| **Opt-out** | Link de descadastro em toda comunicação (unsubscribe_hash) |
| **Anonimização** | Campo `anonymized_at` — quando preenchido, dados pessoais são substituídos por hash |
| **Portabilidade** | Export de dados do contato em JSON (todos os consentimentos + interações) |
| **Eliminação** | Soft delete + job de purga física após período de retenção |
| **Registro** | `audit_logs` com timestamp, tenant, usuário, ação, payload |
| **DPO** | Config de contato do DPO por tenant (tenant_settings.dpo_contact) |
| **Incidente** | Fluxo de notificação de violação com template de email ao DPO |

### Política de Retenção

| Dado | Retenção Ativa | Arquivo Morto | Purga |
|------|---------------|---------------|-------|
| Mensagens | 2 anos | +3 anos (anônimo) | Após 5 anos |
| Contatos ativos | Indeterminado | — | Após 2 anos sem interação |
| Contatos descadastrados | — | 90 dias | Após 90 dias |
| Logs de auditoria | 1 ano | +4 anos | Após 5 anos |
| Sessões | 7 dias | — | Após 7 dias |
| Campanhas | Indeterminado | — | Sob demanda |

---

## 8. Infraestrutura Docker

```yaml
# docker-compose.yml (resumo dos serviços)
services:
  polis-web:
    build: .
    ports: ["3000:3000"]
    depends_on: [postgres, redis]
    env_file: .env

  postgres:
    image: postgis/postgis:16-3.5
    volumes: ["pgdata:/var/lib/postgresql/data"]
    ports: ["5432:5432"]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  bullmq-worker:
    build: .
    command: npx tsx src/workers/index.ts
    depends_on: [postgres, redis]
    env_file: .env
    deploy:
      replicas: 2  # horizontal scaling

  evolution-api:      # WhatsApp provider (opcional)
    image: atendai/evolution-api:v2.1.1
    ports: ["8080:8080"]
    depends_on: [postgres, redis]
    env_file: .env.evolution
```

---

## 9. Considerações de Escalabilidade

| Cenário | Estratégia |
|---------|-----------|
| **Alto volume de mensagens** | Workers BullMQ horizontais (N replicas consumindo mesma fila) |
| **Muitos tenants** | RLS no PostgreSQL + índices parciais por tenant |
| **Campanhas massivas** | Batch processing (INSERT de 1000 recipients por transação) |
| **Busca de contatos** | Índices GIN em JSONB + pg_trgm para fuzzy search |
| **Mapa com muitos pontos** | PostGIS clustering (ST_SnapToGrid) + tile server |
| **Mídia pesada** | Upload direto para S3 (presigned URLs) + workers de thumbnail |
| **Custos LLM** | Cache de respostas frequentes no Redis + rate-limit por tenant |

---

*Este documento é o blueprint arquitetural do Polis. Deve ser revisado e aprovado antes do início do desenvolvimento da Fase 0.*
