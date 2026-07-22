# POLIS — RELATÓRIO DE IMPLANTAÇÃO
## Versão: MVP 0.1.0 | Data: 22/07/2026

---

## 1. INFRAESTRUTURA CRIADA

### DNS e Subdomínio
- **Subdomínio:** polis.miraitohope.com ✅
- **Tipo:** CNAME → Cloudflare Tunnel
- **Status:** Ativo e propagado

### Docker Compose
- PostgreSQL 15 + PostGIS
- Redis 7
- MinIO (S3-compatible)
- pgvector (embeddings)

### Estrutura de Diretórios
```
/opt/data/polis/
├── backend/src/        → 6.212 linhas, 55 arquivos
├── frontend/           → Scaffold Next.js
├── infra/              → Docker, nginx, scripts
├── database/           → Migrations, seeds
├── docs/               → Arquitetura, roadmap, backlog
└── agents/             → Agentes especializados
```

---

## 2. BACKEND — FastAPI (6.212 linhas)

### Módulos Implementados (14/14)

| Módulo | Status | Endpoints |
|--------|--------|-----------|
| Auth | ✅ | login, register, refresh, change-password, me |
| Tenants | ✅ | CRUD multi-tenant completo |
| Users | ✅ | CRUD + RBAC + perfis |
| Contacts | ✅ | CRUD + tags + consentimentos |
| Conversations | ✅ | CRUD + status + atribuição |
| Messages | ✅ | Envio + histórico + mídia |
| Channels | ✅ | CRUD + providers + webhook |
| Campaigns | ✅ | CRUD + disparo + métricas + aprovação |
| Agents | ✅ | CRUD + prompts + configuração IA |
| Knowledge | ✅ | CRUD + RAG pipeline |
| Territorial | ✅ | Eventos + mapa + rankings + stats |
| Tasks | ✅ | CRUD + Kanban + prioridades |
| Protocols | ✅ | CRUD + numeração automática |
| Audit | ✅ | Logging completo de ações |

### Stack
- Python 3.12 + FastAPI
- SQLAlchemy 2.0 async + PostgreSQL
- JWT (python-jose) + bcrypt (passlib)
- Pydantic v2
- Soft delete em todos os modelos
- Tenant isolation (tenant_id em todas as entidades)

---

## 3. MODELO DE DADOS — 15 tabelas

```
tenants, users, roles, contacts, conversations, messages,
channels, campaigns, agents, knowledge_bases, territorial_events,
protocols, tasks, audit_logs, api_keys
```

### Características
- UUIDs como PKs
- tenant_id FK em todas as tabelas (CASCADE on delete)
- created_at, updated_at, deleted_at (soft delete)
- JSONB para campos flexíveis
- Índices em todas as FKs

---

## 4. PRÓXIMOS PASSOS

### Fase 0 — Fundação (PRONTA) ✅
- [x] Subdomínio criado
- [x] Docker Compose configurado
- [x] Backend FastAPI implementado
- [x] Banco de dados modelado
- [x] Autenticação multi-tenant
- [x] RBAC básico

### Fase 1 — MVP Implantação (PRÓXIMA)
- [ ] Subir Docker Compose (PostgreSQL + Redis + MinIO)
- [ ] Executar migrations
- [ ] Testar API com uvicorn
- [ ] Configurar deploy via Docker/Traefik
- [ ] Frontend Next.js com login + dashboard

### Fase 2 — Providers
- [ ] WhatsApp Cloud API
- [ ] Z-API
- [ ] Evolution API
- [ ] Email (SES/Resend/SMTP)
- [ ] SMS (Zenvia/Twilio)

### Fase 3 — Inteligência Territorial
- [ ] Classificação de mensagens via IA
- [ ] Geocodificação de endereços
- [ ] Mapa interativo
- [ ] Agrupamento semântico de eventos

---

## 5. COMPONENTES REAPROVEITADOS DO ECOSSISTEMA

| Componente | Origem | Status |
|------------|--------|--------|
| JWT Auth | Mirai App | Adaptado |
| Multi-tenant | Media Factory | Adaptado |
| FastAPI patterns | Arca API | Reutilizado |
| PostgreSQL + Redis | Infra comum | Reutilizado |
| Docker Compose | Templates da Mirai | Reutilizado |
| Agent Builder | MCP Gateway | Inspiração |
| WhatsApp providers | Media Factory | Inspiração |
| File upload (MinIO) | Media Factory | Adaptado |

---

## 6. RISCOS TÉCNICOS

1. **Cloudflare DNS token expirado** — Token atual precisa ser renovado
2. **Docker não está rodando** — Servidor precisa de rebuild
3. **PostgreSQL + PostGIS** — Precisa de ~2GB de disco adicional
4. **Dependências Python** — Precisam ser instaladas no .venv
5. **GPU para embeddings** — Usar API (OpenAI/Anthropic) em vez de local
