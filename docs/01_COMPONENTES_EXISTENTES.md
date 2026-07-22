# Diagnóstico de Componentes Reaproveitáveis — Ecossistema Mirai → Projeto Polis

> **Data:** 2026-07-22
> **Propósito:** Auditoria completa dos sistemas existentes (Arca, Media Factory, Mirai Hub, Pathfinder, Vestcasa) para identificar o que pode ser reutilizado no Polis (plataforma política SaaS).
> **Stack principal:** Python (FastAPI), Python (scripts/plugins), TypeScript (NestJS + Next.js), SQLite/PostgreSQL, Redis, Docker

---

## Sumário das Classificações

| Componente | Classificação |
|---|---|
| **Arca API** — Modelos de negócio (Document, Meeting, Task, etc.) | ✅ Reaproveitável |
| **Arca API** — Autenticação e multi-tenant | ❌ Não existe |
| **Arca API** — Sistema de permissões | ❌ Não existe |
| **Arca API** — Rotas REST (memória, contexto, projetos) | 🔧 Com modificações |
| **Arca API** — Mirai Bridge (sessões, decisões) | 🔧 Com modificações |
| **Media Factory** — Pipeline Orchestrator | 🔧 Com modificações |
| **Media Factory** — Multi-Tenant completo (UserRegistry, PerUserDB, Vault) | ✅ Reaproveitável |
| **Media Factory** — Tier/Subscription (Stripe, rate limiting) | ✅ Reaproveitável |
| **Media Factory** — Bot Telegram (onboarding, comandos) | 🔧 Com modificações |
| **Media Factory** — Integrações IA (Gemini, Higgsfield, Suno, Kling) | 🔧 Com modificações |
| **Media Factory** — YouTube upload/integration | 🔧 Com modificações |
| **Mirai Hub / MCP Center** — Registry de serviços | ✅ Reaproveitável |
| **Pathfinder** — Estrutura Next.js (layout, sidebar, iframes) | 🔧 Com modificações |
| **Vestcasa** — Backend NestJS/Prisma (arquitetura) | 🔧 Com modificações |
| **Vestcasa** — Modelo de assinatura/contrato | ❌ Não reaproveitável |
| **Vestcasa** — CRM (inexistente) | ❌ Não existe |

---

# 1. 🔵 Arca API (`/opt/data/arca/`)

## 1.1 Modelos de Dados (SQLAlchemy)

**Arquivo:** `api/app/core/database.py`

Tabelas existentes:

| Modelo | Tabela | Campos | Classificação |
|---|---|---|---|
| `Memory` | `memories` | id, content, user_id, categories, extra_data, created_at | ✅ **Reaproveitável** — modelo genérico de memória |
| `Person` | `people` | id, name, email, phone, role, company_id, tags, created_at | 🔧 **Modificações** — adicionar campos políticos (partido, cargo_publico, etc.) |
| `Company` | `companies` | id, name, tax_id, segment, tags, created_at | ✅ **Reaproveitável** — modelo de organização/partido |
| `Project` | `projects` | id, name, description, company_id, status, created_at | ✅ **Reaproveitável** — campanha = projeto |
| `Document` | `documents` | id, titulo, tipo, source, caminho, conteudo, resumo, tags | ✅ **Reaproveitável** — genérico, serve para propostas, leis, etc. |
| `Decision` | `decisions` | id, category, title, content, priority, project, outcome | ✅ **Reaproveitável** — decisões estratégicas |
| `Meeting` | `meetings` | id, project, meeting_type, title, description, date, attendees | ✅ **Reaproveitável** — reuniões de campanha |
| `Task` | `tasks` | id, title, description, project, deadline, status, priority, kpis, assignee | ✅ **Reaproveitável** — tarefas de campanha |
| `Risk` | `risks` | id, title, description, project, probability, impact, severity, mitigation | ✅ **Reaproveitável** — riscos políticos |
| `Opportunity` | `opportunities` | id, title, description, project, potential_value, effort, priority | ✅ **Reaproveitável** — oportunidades |
| `Relationship` | `relationships` | id, source, relation, target, confidence | ✅ **Reaproveitável** — grafos de relacionamento político |
| `Activity` | `activities` | id, project, activity_type, title, description, actor, target | ✅ **Reaproveitável** — timeline de campanha |

**Veredito:** Os 12 modelos de negócio são **diretamente reaproveitáveis** com ajustes mínimos de nomenclatura. O schema é genérico, bem projetado, e cobre 80% das necessidades de uma plataforma política (campanhas = projetos, tarefas, reuniões, decisões, riscos, relacionamentos).

## 1.2 Autenticação / Multi-Tenant

- ❌ **Não existe sistema de autenticação.** Zero. O `user_id` nos modelos é uma string fixa (`"marcos"`).
- ❌ **Não existe middleware de auth.** Nenhuma rota tem proteção.
- ❌ **Não existe multi-tenant real.** Apenas `company_id` como FK conceitual.
- ❌ **Não existe JWT, OAuth, API keys, ou sessão.**
- ❌ **Não existe gerenciamento de usuários** (login, registro, roles).

**Veredito:** Sistema de auth e tenant DEVE ser **criado do zero** para o Polis. Nada para reusar aqui.

## 1.3 Rotas REST

**Rotas principais** (todas em `main.py` ou `routers/`):

| Rota | Método | Função | Classificação |
|---|---|---|---|
| `/` | GET | Landing page + lista endpoints | ❌ Não reaproveitável |
| `/health` | GET | Health check | ❌ Não reaproveitável |
| `/docs` | GET | Swagger | ✅ Reaproveitável |
| `/documentacao` | GET | Página de documentação | ❌ Não reaproveitável |
| `/memory` | POST | Armazenar memória | 🔧 Modificações — servir para anotações de campanha |
| `/memory/search` | GET | Buscar memórias | 🔧 Modificações — search genérico |
| `/context` | GET | Contexto completo | ✅ Reaproveitável — search multi-entity |
| `/project/{name}` | GET | Contexto de projeto | ✅ Reaproveitável — adaptar para campanha |
| `/timeline/{project}` | GET | Timeline de eventos | ✅ **Reaproveitável diretamente** |
| `/executive-brief` | GET | Briefing executivo | ✅ **Reaproveitável** — dashboard de campanha |
| `/mirai-bridge/*` | Vários | Bridge MF ↔ Arca | 🔧 Modificações — adaptar bridge pattern |
| `routers/memory.py` | CRUD | Memórias via service layer | ✅ Reaproveitável — padrão de CRUD |
| `routers/entities.py` | CRUD | Pessoas, empresas, projetos | 🔧 Modificações — schema de contatos políticos |
| `routers/documents.py` | CRUD | Documentos | ✅ Reaproveitável |
| `routers/search.py` | GET | Busca multi-entity | ✅ Reaproveitável |
| `routers/ingestion.py` | POST | Ingestão de arquivos | ❌ Não reaproveitável (Google Drive) |

## 1.4 Sistema de Permissões

- ❌ **Inexistente.** Nada implementado.
- **Necessário criar do zero** para Polis: roles (admin, gestor, analista, viewer), permissions (CRUD por módulo), RBAC ou ABAC.

## 1.5 Esquema do Banco (SQLite/PostgreSQL)

- Schema dual (PostgreSQL primário + SQLite fallback) com `create_all()`.
- ✅ Padrão de `execute_write()` / `fetch_all()` com detecção automática de DB.
- ✅ Backup automático via scripts (`backup_complete.py`) → Google Drive.
- 🔧 O padrão de dual-DB é útil para desenvolvimento/testes.

---

# 2. 🟢 Media Factory (`/opt/data/media-factory/`)

## 2.1 Engine de Pipeline

**Arquivos:** `engine/controllers/pipeline.py`, `engine/controllers/tenant_pipeline.py`

**Arquitetura:**
- `NewsPipeline`: Orquestrador com 6 etapas (collect_news → thumbnails → music → build_video → seo → upload)
- `PipelineRunner`: Wrapper CLI/API do pipeline
- `TenantPipelineRunner`: Pipeline multi-tenant que carrega API keys do vault por usuário
- `Flow` models: Pipeline configurável com módulos (Observador, Roteiro, Thumbnail, Suno, Kling, Montagem, YouTube_Upload)
- `Schedule`: Agendamento cron para execução automática

**Classificação:**
- ✅ **Padrão de orquestração de pipeline** (PipelineResult, etapas ordenadas, tratamento de erros) é um pattern reaproveitável
- ✅ **TenantPipelineRunner** — mecanismo de executar pipeline com keys isoladas por tenant
- ✅ **Flow/Schedule** — modelo de workflows agendados
- 🔧 **Pipeline de conteúdo específico** (notícias, thumbnails, música) precisa ser substituído por tasks políticas
- ❌ **NewsPipeline** como está — não serve para Polis (domínio diferente)

## 2.2 Módulo de Atendimento (Bot)

**Arquivo:** `bot/telegram_bot.py`

**Funcionalidades:**
- Bot Telegram com `python-telegram-bot` v20+
- Onboarding multi-step (nome → email → completo)
- Comandos: `/start`, `/daily`, `/status`, `/connect`, `/flows`, `/schedule`, `/services`, `/link`, `/help`
- Conversational AI mode via Verboo API
- MCP integration para linking de contas
- Multi-tenant aware (chat_id ↔ user_id ↔ tenant_id)

**Classificação:**
- 🟢 **Arquitetura do bot** (ApplicationBuilder, handlers, conversation) → ✅ **Reaproveitável como template**
- 🟢 **Onboarding flow** → 🔧 **Modificações** (adaptar onboarding político)
- 🟢 **MCP Client** → ✅ **Reaproveitável diretamente** para integrações
- 🔴 **Handlers específicos** (daily, flows, schedule, connect) → ❌ **Não reaproveitáveis** (substituir por comandos Polis)
- 🔴 **Conversational mode** → ❌ **Não reaproveitável** (substituir por engine Polis de IA)

## 2.3 Integrações existentes

| Serviço | Arquivo | Tipo | Classificação |
|---|---|---|---|
| **Google Gemini** | `services/gemini.py` | LLM | ✅ **Reaproveitável** — interface genérica |
| **Higgsfield** | `services/higgsfield.py` | Image gen | 🔧 Modificações — adaptar para geração de conteúdo político |
| **Google Imagen** | `services/imagen.py` | Image gen | 🔧 Modificações |
| **Kling** | `services/kling_native.py`, `services/kling_auth.py` | Video gen | 🔧 Modificações |
| **Suno** | `services/suno.py` | Music gen | ❌ Não reaproveitável (fora de escopo Polis) |
| **Edge TTS / ElevenLabs** | `config.toml` | Voice/TTS | ✅ **Reaproveitável** — TTS para campanhas |
| **YouTube Data API** | `services/youtube.py` | Upload | 🔧 Modificações — adaptar para publicação política |
| **Pexels/Pixabay** | `config.toml` | Stock media | ❌ Fora de escopo |
| **Telegram** | `services/telegram.py`, `bot/` | Notificação | ✅ **Reaproveitável** como notificador |
| **Observador** | `services/observador.py` | News discovery | ❌ Fora de escopo |
| **Magnific** | `services/magnific.py` | Image upscale | ❌ Fora de escopo |
| **Live Research** | `services/live_research.py` | Web research | ✅ **Reaproveitável** — pesquisa de conteúdo político |
| **Video Editor** | `services/video_editor.py` | FFmpeg | 🔧 Modificações — útil para montagem de vídeos políticos |

## 2.4 Geração de Conteúdo IA

- `services/gemini.py` — serviço de LLM para gerar roteiros, SEO, descrições
- `services/higgsfield.py` — geração de thumbnails via MCP local + Pillow fallback

**Classificação:** 🔧 **Reaproveitável com modificações.** O padrão de chamar LLM + image gen pode ser adaptado para geração de conteúdo político (textos de campanha, artigos, posts).

## 2.5 Processamento de Mensagens

- Bot processa mensagens de texto do Telegram para onboarding e modo conversacional
- Usa `bot/lib/conversation.py` com Verboo API para respostas

**Classificação:** 🔧 **Reaproveitável.** Arquitetura de processamento de mensagens (inbound → MCP → response) pode ser base para o módulo de atendimento do Polis.

---

# 3. 🟡 Mirai Hub / MCP Center (`/opt/data/mirai-hub/`)

## 3.1 Registro de Serviços

**Arquivo:** `mcp_center.py`

**Schema SQL:** (`schema.sql`)

| Tabela | Finalidade | Classificação |
|---|---|---|
| `mcps` | Registro centralizado de MCPs (id, name, transport, url, auth_type, locations, status) | ✅ **Reaproveitável diretamente** |
| `sync_log` | Log de sincronização | ✅ **Reaproveitável** |
| `apis` | Registro de APIs (id, name, service, provider, has_key, locations) | ✅ **Reaproveitável** |

**Funcionalidades:**
- 🔄 Scan automático de Hermes config, MCP Gateway, Media Factory DB
- 📊 Relatório de status (online/offline/enabled)
- 🔀 Merge de entradas duplicadas
- 🔑 Gerenciamento de auth config (OAuth2, tokens)

**Veredito:** O MCP Center é o componente **mais maduro e mais diretamente reaproveitável** de todo o ecossistema para o Polis. O schema de registro de serviços, o padrão de scanners e o gerenciamento de auth são exatamente o que o Polis precisa para seu módulo de integrações.

---

# 4. 🟠 Pathfinder (`/opt/data/pathfinder-app/`)

## 4.1 Estrutura Next.js

**Stack:** Next.js 15.3.1 + React 19.1 + TypeScript 5.8

**Arquivos principais:**
- `app/page.tsx` — Server component que carrega config do disco
- `app/ClientHome.tsx` — Client component com sidebar + dashboard + iframes
- `services.json` — Configuração dos serviços (13 serviços registrados)
- `next.config.mjs`, `tsconfig.json`, `package.json`

**Arquitetura:**
- Server/Client split (Server carrega config.json, Client renderiza UI)
- Sidebar dinâmica com navegação entre serviços
- Serviços podem ser: `dashboard` (nativo), `local` (iframe interno), `external` (iframe externo), `placeholder` (em breve)
- Dashboard com métricas mock, gráficos de tendência, atividade recente, top conteúdo

**Serviços registrados:**
Hub, Intelligence Dashboard, YouTube Intelligence, Competitive Matrix, AI Insights, Performance Agents, GSC Social Posts, GEO Audit, SEO Autônomo, Campanhas, Conteúdo, Relatórios, Config

**Classificação:**
- ✅ **Estrutura Next.js + React 19** → diretamente utilizável como base do frontend Polis
- ✅ **Sidebar pattern** → reusável para navegação de módulos Polis
- ✅ **Iframe-based micro-frontends** → útil para integrar subsistemas Polis
- ✅ **Serviço config via JSON** → pattern reusável para configuração dinâmica de módulos
- 🔧 **Dashboard UI** → base para o dashboard político, mas precisa de dados reais
- ❌ **Dados mock** → substituir por dados reais da API Polis
- ❌ **Serviços específicos** (GSC, GEO, SEO, YouTube Intelligence) → não relevantes para Polis

---

# 5. 🟤 Vestcasa (`/opt/data/vestcasa/` + `/opt/data/vestcasa-backend/`)

## 5.1 CRM Básico

**Realidade:** Vestcasa **não é um CRM.** É um formulário de assinatura de clube de compras.

**Backend:** NestJS 10 + Prisma 5 + PostgreSQL
- Modelo único: `Subscription` (CPF, plano, dados pessoais, pagamento, status)
- CRUD básico: POST/GET `/subscriptions`
- Sem autenticação
- Sem multi-tenant
- Sem pipeline de vendas
- Sem leads
- Sem contatos (além do assinante)

## 5.2 Modelo de Contatos

**Modelo Subscription:**
- CPF (unique), planType, planValue, email, name, birthdate, phone, postcode, address, paymentMethod, cardNumber (4 últimos), status, paymentStatus

**Classificação:**
- 🔧 **Arquitetura NestJS + Prisma** é um bom template para microsserviços Polis
- ✅ **Padrão Prisma** (schema, migrations, service layer) é reusável
- ✅ **Validação DTO** com class-validator é reusável
- ❌ **Modelo Subscription** não serve para Polis (domínio diferente)
- ❌ **CRM inexistente** — precisa ser criado do zero para Polis (contatos, leads, pipeline, campanhas eleitorais)

---

# 6. 📊 Matriz de Reaproveitamento por Módulo Polis

## Módulo de Autenticação e Usuários
| Componente | Origem | Classificação |
|---|---|---|
| Sistema de auth (JWT/OAuth2) | — | ❌ Criar do zero |
| Registro de usuários | Media Factory (UserRegistry) | ✅ Reaproveitar padrão |
| Multi-tenant isolation | Media Factory (PerUserDB, Vault) | ✅ Reaproveitar diretamente |
| Roles e permissões (RBAC) | — | ❌ Criar do zero |

## Módulo de Campanhas
| Componente | Origem | Classificação |
|---|---|---|
| Modelo de Projeto/Campanha | Arca (Project model) | ✅ Reaproveitar |
| Tasks/Kanban | Arca (Task model) | ✅ Reaproveitar |
| Timeline de eventos | Arca (timeline endpoint) | ✅ Reaproveitar |
| Decisões estratégicas | Arca (Decision model) | ✅ Reaproveitar |
| Riscos e oportunidades | Arca (Risk, Opportunity) | ✅ Reaproveitar |

## Módulo de Contatos/CRM
| Componente | Origem | Classificação |
|---|---|---|
| Modelo de Pessoa | Arca (Person model) | 🔧 Adaptar |
| Modelo de Organização | Arca (Company model) | ✅ Reaproveitar |
| Relacionamentos | Arca (Relationship model) | ✅ Reaproveitar |
| Pipeline de vendas/leads | — | ❌ Criar do zero |
| Segmentação de contatos | — | ❌ Criar do zero |
| Importação de contatos | — | ❌ Criar do zero |

## Módulo de Conteúdo Político
| Componente | Origem | Classificação |
|---|---|---|
| LLM para geração de texto | MF (GeminiService) | ✅ Reaproveitar |
| Geração de imagens | MF (HiggsfieldService) | 🔧 Adaptar |
| TTS / Áudio | MF (Edge TTS config) | ✅ Reaproveitar |
| Editor de vídeo | MF (video_editor.py) | 🔧 Adaptar |
| Agendamento de publicação | MF (Schedule/Flow) | ✅ Reaproveitar |
| SEO de conteúdo | MF (SEO engine) | 🔧 Adaptar |

## Módulo de Integrações
| Componente | Origem | Classificação |
|---|---|---|
| Registro de serviços | MCP Center (mcps table) | ✅ Reaproveitar |
| Gerenciamento de API keys | MF (Credential Vault) | ✅ Reaproveitar |
| Bot Telegram | MF (telegram_bot.py) | 🔧 Adaptar |
| YouTube API | MF (youtube.py) | 🔧 Adaptar |
| WhatsApp integration | — | ❌ Criar do zero |
| Instagram/TikTok | — | ❌ Criar do zero |

## Módulo de Dashboard/UI
| Componente | Origem | Classificação |
|---|---|---|
| Next.js scaffold | Pathfinder | ✅ Reaproveitar |
| Sidebar navigation | Pathfinder (ClientHome) | ✅ Reaproveitar |
| Iframe embedding | Pathfinder | ✅ Reaproveitar |
| Dashboard widgets | Pathfinder (mock data) | 🔧 Adaptar |
| Serviço config | Pathfinder (services.json) | ✅ Reaproveitar |

## Módulo de Assinaturas/Billing
| Componente | Origem | Classificação |
|---|---|---|
| Stripe integration | MF (stripe_integration.py) | ✅ Reaproveitar |
| Tier system | MF (tiers/db.py, models.py) | ✅ Reaproveitar |
| Rate limiting | MF (rate_limiter.py) | ✅ Reaproveitar |
| Usage tracking | MF (usage_monthly table) | ✅ Reaproveitar |

---

# 7. 📋 Resumo Final

## O que PEGAR (reaproveitar diretamente)
1. **Arca**: Models de negócio (Document, Decision, Meeting, Task, Risk, Opportunity, Relationship, Activity, Project, Company, Person) — 12 tabelas genéricas
2. **Arca**: Endpoints de contexto, timeline, executive-brief
3. **Media Factory**: Sistema multi-tenant completo (UserRegistry, PerUserDB, Credential Vault)
4. **Media Factory**: Tier/Subscription system (Stripe, rate limits, usage)
5. **Media Factory**: Serviços de LLM (Gemini) e Image Gen (Higgsfield, Imagen)
6. **Media Factory**: YouTube API integration
7. **Media Factory**: Config management (config.toml loader)
8. **Mirai Hub**: MCP Center registry (mcps, apis tables + scanners)
9. **Pathfinder**: Next.js scaffold, sidebar, iframe pattern, services.json config

## O que ADAPTAR (reaproveitar com modificações)
1. **Arca**: Rotas CRUD de entidades (adaptar para contatos políticos)
2. **Arca**: Mirai Bridge pattern (adaptar para bridge Polis ↔ módulos)
3. **Media Factory**: Pipeline orchestration (substituir etapas de notícias por políticas)
4. **Media Factory**: Bot Telegram (adaptar comandos e onboarding para Polis)
5. **Media Factory**: SEO engine (adaptar para conteúdo político)
6. **Pathfinder**: Dashboard (substituir dados mock por APIs reais)
7. **Vestcasa**: NestJS/Prisma architecture (template para microsserviços)
8. **MCP Center**: Scanners (adaptar para scan de serviços Polis)

## O que CRIAR (não reaproveitável / não existe)
1. **Sistema de autenticação** (JWT/OAuth2 + login + registro)
2. **Sistema de permissões** (RBAC com roles: admin, gestor, analista, viewer)
3. **Multi-tenant real** (isolamento de dados por organização política)
4. **CRM político** (contatos, leads, pipeline, segmentação, histórico de interações)
5. **Módulo de campanhas eleitorais** (metas, indicadores, prestação de contas)
6. **Integração WhatsApp** (para comunicação com eleitores)
7. **Módulo de pesquisas/eleições** (votação, enquete, resultados)
8. **Módulo financeiro** (doações, prestação de contas eleitoral)
9. **Módulo de equipe** (gestão de voluntários, cargos, permissões por campanha)
10. **Módulo de comunicação** (mailing, disparo em massa, templates)
11. **Módulo de transparência** (gastos de campanha, relatórios públicos)
12. **Notificações multi-canal** (Telegram + WhatsApp + Email + Push)

---

## Anexo: Estrutura de Diretórios Auditados

```
/opt/data/
├── arca/                          # ✅ BACKEND — Memory API
│   ├── api/app/
│   │   ├── main.py               # FastAPI app (800 linhas, 20+ endpoints)
│   │   ├── core/database.py      # SQLAlchemy models (12 tabelas)
│   │   ├── core/config.py        # Config (Qdrant, Neo4j, Redis)
│   │   ├── routers/              # 6 routers (memory, entities, documents, search, ingestion)
│   │   └── services/             # 8 services (memory, entity, document, search, etc.)
│   ├── scripts/                  # 44 scripts (engines, backup, ingestão)
│   └── ARCA_V1_STATUS.md         # Status completo do sistema
│
├── media-factory/                # ✅ PIPELINE ENGINE + BOT
│   ├── config.toml               # Config central (272 linhas)
│   ├── engine/
│   │   ├── config.py             # Config loader (TOML + env)
│   │   ├── controllers/          # Pipeline, TenantPipeline
│   │   ├── models/               # Channel, NewsItem, VideoSpec, PipelineResult
│   │   ├── services/             # 13 services (Gemini, Higgsfield, Kling, Suno, YouTube, etc.)
│   │   ├── flows/                # Flow models, scheduler, DB
│   │   └── tiers/                # Subscription, rate limiter, Stripe
│   ├── bot/                      # Telegram bot completo
│   │   ├── telegram_bot.py       # Entrypoint (ApplicationBuilder)
│   │   ├── handlers/             # 8 handlers (start, daily, flows, services, etc.)
│   │   └── lib/                  # MCP client, conversation, onboarding
│   └── plugin/                   # User registry, per-user DB, multi-tenant
│       └── multi_tenant/         # Schema migration
│
├── mirai-hub/                    # ✅ MCP CENTER
│   ├── mcp_center.py             # CLI completo (505 linhas)
│   ├── schema.sql                # 3 tabelas (mcps, sync_log, apis)
│   └── mirai_hub.db              # SQLite database
│
├── pathfinder-app/               # ✅ FRONTEND
│   ├── app/
│   │   ├── page.tsx              # Server component
│   │   └── ClientHome.tsx        # Client UI (sidebar, dashboard, iframes)
│   ├── services.json             # 13 serviços configurados
│   ├── package.json              # Next.js 15.3.1 + React 19.1
│   └── next.config.mjs
│
├── vestcasa-backend/             # 🔧 REFERÊNCIA NESTJS
│   ├── prisma/schema.prisma      # Subscription model (PostgreSQL)
│   ├── src/
│   │   ├── app.module.ts         # NestJS module
│   │   ├── main.ts               # Bootstrap + CORS
│   │   ├── prisma/               # Prisma service
│   │   └── subscription/         # Subscription CRUD
│   └── package.json              # NestJS 10 + Prisma 5
│
└── vestcasa/                     # ❌ NÃO REAPROVEITÁVEL (WordPress scan)
```

---

*Relatório gerado automaticamente via auditoria de código fonte.*
*Nenhuma modificação foi feita nos sistemas auditados.*
