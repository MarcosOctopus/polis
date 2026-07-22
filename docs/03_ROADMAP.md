# Roadmap e Backlog — Polis (Political OS)

> **Versão:** 0.1.0  
> **Data:** 2026-07-22  
> **Status:** Planejamento  
> **Estratégia:** Entregas incrementais com valor real a cada fase

---

## Filosofia do Roadmap

Cada fase é independente e entregável em produção. Fases posteriores **não bloqueiam** fases anteriores — o MVP (Fase 0 + Fase 1) já é uma plataforma funcional para gestão de campanhas políticas.

```
Fase 0 ─► Fase 1 ─► Fase 2 ─► Fase 3 ─► Fase 4 ─► Fase 5
Fundação    CRM      IA       Mapa     Analytics  Expansão
 ─────────────────────────────────────────────────────────► Tempo
```

**Priorização:**
- Funcionalidades core (auth, tenant, contatos, WhatsApp)
- Dados reais o mais cedo possível
- IA progressiva (começa com classificação simples, evolui para RAG + agentes)
- Mapa e analytics consomem dados das fases anteriores

---

## Fase 0: Fundação (Semanas 1–3)

### Objetivo
Base sólida da plataforma: autenticação, multi-tenant, RBAC, infraestrutura Docker, schema do banco.

### Entregáveis

| # | Entregável | Descrição | Critério de Aceitação |
|---|-----------|-----------|----------------------|
| 0.1 | Setup Docker | docker-compose.yml + Dockerfile para Next.js, PostgreSQL+PostGIS, Redis | `docker compose up` sobe tudo |
| 0.2 | Schema Prisma | Todas as tabelas do MVP (04_DADOS.md) com migrations | Prisma migrate aplica sem erros |
| 0.3 | Auth (JWT) | Login, registro, refresh token, logout | POST /api/auth/login retorna tokens |
| 0.4 | Multi-Tenant | Subdomain resolution, RLS, tenant isolation | Tenant A não vê dados de Tenant B |
| 0.5 | RBAC | Roles (admin, gestor, analista, atendente), permissions por módulo | Usuário sem permissão recebe 403 |
| 0.6 | Middleware chain | Auth → Tenant → Rate-Limit → Audit | Todas as rotas passam pelo pipeline |
| 0.7 | Seed inicial | Tenant padrão, admin user, roles base | `npm run seed` cria dados iniciais |
| 0.8 | CI/CD | GitHub Actions: lint, typecheck, build | PR passa no CI |
| 0.9 | Deploy básico | Deploy em subdomínio + HTTPS | polis.miraitohope.com responde |

### Tarefas Detalhadas (Backlog)

```
[POL-001] Instalar Next.js 15 + TypeScript + App Router scaffold
[POL-002] Configurar Prisma + PostgreSQL + PostGIS
[POL-003] Criar schema de tenants + users + roles (Prisma)
[POL-004] Implementar login com JWT (access + refresh)
[POL-005] Implementar middleware de autenticação
[POL-006] Implementar resolução de tenant por subdomínio
[POL-007] Criar políticas RLS no PostgreSQL
[POL-008] Implementar RBAC checker (permissões por módulo)
[POL-009] Configurar Redis (cache + sessão + rate-limit)
[POL-010] Implementar rate-limiting por tenant (sliding window)
[POL-011] Implementar audit_logs (middleware)
[POL-012] Configurar BullMQ (Redis backend)
[POL-013] Dockerizar app (Next.js + worker)
[POL-014] docker-compose.yml completo
[POL-015] Nginx/Caddy reverse proxy + SSL
[POL-016] Seed script (admin + roles + tenant)
[POL-017] GitHub Actions workflow
[POL-018] Deploy em polis.miraitohope.com
[POL-019] Testes de isolamento multi-tenant
[POL-020] Documentação de setup para devs
```

---

## Fase 1: CRM e Comunicação (Semanas 4–7)

### Objetivo
Núcleo operacional: gestão de contatos, integração WhatsApp, caixa de entrada unificada.

### Entregáveis

| # | Entregável | Descrição | Critério de Aceitação |
|---|-----------|-----------|----------------------|
| 1.1 | CRUD Contatos | Cadastro, edição, busca, tags, segmentação | API REST + UI funcional |
| 1.2 | Importar contatos | CSV, XLSX, Google Sheets | 10k contatos em < 30s |
| 1.3 | Integração WhatsApp | Evolution API (self-hosted) | Enviar e receber mensagens |
| 1.4 | Webhook WhatsApp | Receber mensagens → criar conversas | Mensagem chega na caixa de entrada |
| 1.5 | Caixa de Entrada | Lista de conversas, busca, filtros | UI similar a Telegram Web |
| 1.6 | Envio de mensagens | Texto, imagem, áudio, documento | Envio por provider |
| 1.7 | Templates de mensagem | Mensagens pré-definidas com variáveis | {{nome}} substituído no envio |
| 1.8 | Consentimento LGPD | Registrar consentimento, opt-out, link descadastro | Contato descadastrado não recebe mais |
| 1.9 | Protocolo de atendimento | Número de protocolo por conversa | Protocolo único por tenant |

### Tarefas Detalhadas (Backlog)

```
[POL-101] Schema de contacts + contact_tags + contact_consents
[POL-102] API CRUD de contatos (GET, POST, PUT, DELETE)
[POL-103] UI de listagem de contatos (tabela + busca)
[POL-104] UI de cadastro/edição de contato (formulário)
[POL-105] Importador CSV/XLSX (worker BullMQ)
[POL-106] Mapeamento de colunas na importação
[POL-107] Tags: CRUD + atribuição em lote a contatos
[POL-108] Segmentação: filtros combinados (tag + bairro + data)
[POL-109] Provider WhatsApp: interface abstrata
[POL-110] Provider Evolution API: implementação
[POL-111] Provider Cloud API (Meta): implementação
[POL-112] Webhook handler: receber mensagens WhatsApp
[POL-113] Schema de conversations + messages + message_attachments
[POL-114] API de conversas (listar, buscar, abrir)
[POL-115] UI Caixa de Entrada (sidebar conversas + chat)
[POL-116] Envio de mensagem pela UI
[POL-117] Suporte a mídia (upload S3 + thumbnail)
[POL-118] Templates de mensagem (CRUD + variáveis)
[POL-119] Consentimento: registro + opt-out automático
[POL-120] Link de descadastro em mensagens
[POL-121] Protocolo único por conversa
[POL-122] Export de dados do contato (portabilidade)
[POL-123] Testes de fluxo completo (WhatsApp → Caixa de Entrada → Resposta)
```

---

## Fase 2: Inteligência (Semanas 8–11)

### Objetivo
Agentes IA para atendimento automático, classificação de mensagens, RAG com base de conhecimento.

### Entregáveis

| # | Entregável | Descrição | Critério de Aceitação |
|---|-----------|-----------|----------------------|
| 2.1 | Agente IA básico | Atendimento automático em conversas | Agente responde com personalidade configurável |
| 2.2 | Base de Conhecimento | CRUD de KB + upload de documentos | FAQ, documentos, leis indexados |
| 2.3 | RAG | Busca semântica na KB para responder | Respostas citam fontes da KB |
| 2.4 | Classificador de intenção | Categorizar mensagens (pergunta, reclamação, sugestão, spam) | Dashboard mostra distribuição |
| 2.5 | Classificador de sentimento | Positivo, neutro, negativo, urgente | Alerta para sentimento negativo |
| 2.6 | Workflow de agente | Regras: se X então Y (ex: se urgente → task) | Regras executam automaticamente |
| 2.7 | Histórico de agentes | Log de interações e decisões do agente | Auditável e exportável |

### Tarefas Detalhadas (Backlog)

```
[POL-201] Schema de agents + agent_versions + knowledge_bases
[POL-202] CRUD de agentes (personalidade, instruções, tom)
[POL-203] LLM client unificado (Gemini / OpenAI)
[POL-204] Implementar RAG com pgvector
[POL-205] UI de configuração do agente
[POL-206] Upload de documentos para KB (PDF, DOCX, TXT)
[POL-207] Chunking + embedding de documentos
[POL-208] Classificador de intenção (prompt engineering + few-shot)
[POL-209] Classificador de sentimento
[POL-210] Worker de processamento de mensagens com IA
[POL-211] Streaming de resposta (SSE) na Caixa de Entrada
[POL-212] Workflow engine (regras if/then)
[POL-213] Histórico de decisões do agente
[POL-214] Fallback humano (quando agente não sabe responder)
[POL-215] Métricas do agente (taxa de resolução, tempo médio)
[POL-216] Testes com massas de mensagens reais simuladas
```

---

## Fase 3: Territorial (Semanas 12–14)

### Objetivo
Inteligência territorial: mapa interativo, zonas eleitorais, eventos, rankings.

### Entregáveis

| # | Entregável | Descrição | Critério de Aceitação |
|---|-----------|-----------|----------------------|
| 3.1 | Mapa base | Mapa com Leaflet/Mapbox, zoom a nível de bairro | Mapa carrega com dados do tenant |
| 3.2 | Zonas eleitorais | GeoJSON com zonas, seções, endereços | Import de shapefile funcional |
| 3.3 | Heatmap de contatos | Densidade de contatos no mapa | Cores por concentração |
| 3.4 | Eventos territoriais | Cadastro de eventos com geolocalização | Pin no mapa com detalhes |
| 3.5 | Rankings | Ranking de regiões por engajamento, contatos, reuniões | Tabela ordenável no dashboard |
| 3.6 | Cruzamento geográfico | Contatos em raio X de um ponto | Lista de contatos filtrados por região |

### Tarefas Detalhadas (Backlog)

```
[POL-301] Schema territorial (territorial_events, categories, reports)
[POL-302] Setup PostGIS + índices geoespaciais
[POL-303] API de pontos geográficos (ST_Contains, ST_DWithin)
[POL-304] Import de shapefile/zona eleitoral
[POL-305] Integração Leaflet/Mapbox no frontend
[POL-306] Heatmap layer (contatos por área)
[POL-307] CRUD de eventos territoriais
[POL-308] Eventos com geolocalização (lat/lng) + pin no mapa
[POL-309] Modal de detalhe do evento
[POL-310] Rankings: contatos, eventos, atividades por região
[POL-311] Filtro geográfico de contatos (bairro, zona, raio)
[POL-312] Worker de cruzamento (evento → contatos próximos)
[POL-313] Export de dados territoriais (GeoJSON)
```

---

## Fase 4: Analytics (Semanas 15–17)

### Objetivo
Dashboard inteligente com métricas da campanha, relatórios exportáveis e copiloto IA.

### Entregáveis

| # | Entregável | Descrição | Critério de Aceitação |
|---|-----------|-----------|----------------------|
| 4.1 | Dashboard geral | Cards com KPIs, gráficos de tendência, atividade recente | Dados reais, não mock |
| 4.2 | Relatórios | Relatórios exportáveis (PDF, CSV) — resumo de campanha, evolução de contatos | Download funcional |
| 4.3 | Gráfico de crescimento | Evolução de contatos, engajamento, mensagens | Timeline interativa |
| 4.4 | Funil de comunicação | Recebida → Lida → Respondida → Convertida | Por campanha e período |
| 4.5 | Copiloto IA | Perguntas em linguagem natural sobre dados | "Quantos contatos novos este mês?" responde |
| 4.6 | Métricas de agente | Taxa de automação, sentimento, tempo de resposta | Dashboard de performance do agente |

### Tarefas Detalhadas (Backlog)

```
[POL-401] Schema de analytics (materialized views para métricas)
[POL-402] Dashboard service (agregações, queries otimizadas)
[POL-403] UI Dashboard: cards + gráficos (Recharts / Nivo)
[POL-404] Timeline de crescimento de contatos
[POL-405] Funil de comunicação (etapas + conversão)
[POL-406] Relatório de campanha (PDF com resumo)
[POL-407] Relatório de contatos (CSV export)
[POL-408] Relatório de agente (desempenho, sentimento)
[POL-409] Copiloto IA: query → LLM → resposta + gráfico
[POL-410] Copiloto: seleção automática de período e métrica
[POL-411] Agendamento de relatórios (email periódico)
[POL-412] Refresh automático de métricas (cron + worker)
```

---

## Fase 5: Expansão (Semanas 18–22)

### Objetivo
Canais adicionais, API pública, recursos avançados de comunicação.

### Entregáveis

| # | Entregável | Descrição | Critério de Aceitação |
|---|-----------|-----------|----------------------|
| 5.1 | Canal Instagram | Integração com Instagram DM (Meta API) | Enviar e receber mensagens |
| 5.2 | Canal Telegram | Bot Telegram para campanhas | Mensagens via bot |
| 5.3 | Voz / Áudio | Mensagens de voz + TTS para responder | Áudio gravado → texto → resposta |
| 5.4 | Avatar digital | Avatar com IA (geração de vídeo/speech) | Vídeo curto com avatar falando |
| 5.5 | API Pública | REST API com API keys para terceiros | Documentação Swagger completa |
| 5.6 | Webhooks de saída | Notificar sistemas externos sobre eventos | POST para URL configurada |
| 5.7 | Scheduler de conteúdo | Post agendado em redes sociais | Publicar em data/hora futura |
| 5.8 | App mobile (PWA) | PWA com push notifications | Instalável, notifica offline |

### Tarefas Detalhadas (Backlog)

```
[POL-501] Provider Instagram (Meta Graph API)
[POL-502] Caixa de entrada unificada (WhatsApp + Instagram + Telegram)
[POL-503] Provider Telegram (Bot API)
[POL-504] Mensagens de voz: gravação + envio
[POL-505] TTS (ElevenLabs / Edge TTS) para respostas
[POL-506] Avatar IA: geração de vídeo com texto falado
[POL-507] API Keys: CRUD + middleware de autenticação
[POL-508] Rate limits por API key
[POL-509] Documentação OpenAPI/Swagger
[POL-510] Webhooks de saída: registro + disparo
[POL-511] Fila de webhooks com retry
[POL-512] Scheduler de conteúdo (BullMQ cron jobs)
[POL-513] PWA: manifest, service worker, push notifications
[POL-514] Testes de carga na API pública
[POL-515] Onboarding de terceiros (documentação + exemplos)
```

---

## MVP (Produto Mínimo Viável)

### Definição

O MVP do Polis é **Fase 0 + Fase 1** — uma plataforma funcional que permite a um político/partido:

1. **Criar conta** e configurar seu espaço (tenant)
2. **Convidar equipe** com diferentes permissões (admin, gestor, analista, atendente)
3. **Importar contatos** de eleitores via CSV (nome, telefone, bairro, tags)
4. **Conectar WhatsApp** (Evolution API auto-hospedada)
5. **Receber mensagens** de eleitores na Caixa de Entrada
6. **Responder mensagens** individualmente
7. **Enviar campanhas** em massa pelo WhatsApp para segmentos de contatos
8. **Criar protocolos** de atendimento
9. **Respeitar LGPD** (consentimento, descadastro, portabilidade)

### O que NÃO está no MVP

- ❌ Agentes IA com RAG (Fase 2)
- ❌ Mapa interativo (Fase 3)
- ❌ Dashboards analíticos complexos (Fase 4)
- ❌ Instagram, Telegram, Voz, Avatar (Fase 5)
- ❌ API pública (Fase 5)
- ❌ Scheduler de conteúdo (Fase 5)

### Estimativa de Esforço MVP

| Fase | Estimativa | Recursos |
|------|-----------|----------|
| Fase 0 | 3 semanas | 1 fullstack sênior |
| Fase 1 | 4 semanas | 1 fullstack + 1 frontend |
| **Total MVP** | **7 semanas** | **2 devs** |

### Marcos (Milestones)

```
M0 — Setup (Fim Semana 1)
  ├── Docker + Next.js + DB rodando
  └── Prisma schema aplicado

M1 — Auth (Fim Semana 2)
  ├── Login/registro funcional
  └── Multi-tenant isolado

M2 — RBAC (Fim Semana 3)
  ├── Roles e permissões
  ├── Middleware completo
  └── Deploy em produção

M3 — Contatos (Fim Semana 5)
  ├── CRUD + importação
  ├── Tags + segmentação
  └── Consentimento LGPD

M4 — WhatsApp (Fim Semana 6)
  ├── Provider integrado
  ├── Webhook recebendo mensagens
  └── Envio funcional

M5 — Caixa de Entrada (Fim Semana 7)
  ├── UI de conversas
  ├── Envio de mídia
  └── MVP pronto para uso REAL
```

---

## Matriz de Dependências

```
Fase 0 ─────────────────────────────────────────────► Todas as fases
  │
  ├──► Fase 1 (CRM) ──► Fase 2 (IA) ──► Fase 4 (Analytics)
  │       │                  │
  │       └──► Fase 3 (Territorial)
  │
  └──► Fase 5 (Expansão) ── pode começar em paralelo após Fase 0
```

- **Fase 2** depende de Fase 1 (precisa de conversas reais para classificar)
- **Fase 3** pode começar após Fase 1 (precisa de contatos com endereço)
- **Fase 4** depende de Fase 1 + Fase 2 (precisa de dados + classificações)
- **Fase 5** depende apenas de Fase 0 (pode iniciar paralelamente)

---

## Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Complexidade de multi-tenant RLS | Média | Alto | Protótipo de isolamento antes de começar outras features |
| WhatsApp bloqueio de número | Alta | Alto | Usar Evolution API + hot swapping de números |
| LGPD multa por vazamento | Baixa | Crítico | Auditoria + criptografia + DPO configurado |
| Escopo crescer (scope creep) | Alta | Médio | MVP rigidamente definido; novas ideias vão para backlog de fases futuras |
| Performance de campanhas massivas | Média | Médio | Testar com 50k contatos antes do deploy |
| Dependência de LLM externo | Média | Baixo | Fallback para regras locais quando LLM estiver offline |
| Adoção por usuários não-técnicos | Média | Alto | UI focada em simplicidade; onboarding guiado |

---

*Este roadmap deve ser revisado a cada sprint. Estimativas são aproximadas e serão refinadas com dados reais de desenvolvimento.*
