# Modelo de Dados Inicial — Polis (Political OS)

> **Versão:** 0.1.0  
> **Data:** 2026-07-22  
> **Banco:** PostgreSQL 16 + PostGIS 3.5  
> **ORM:** Prisma 6.x (schema-first)

---

## Convenções

### Colunas comuns a todas as tabelas

```sql
id          UUID PRIMARY KEY DEFAULT gen_random_uuid()
tenant_id   UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE
created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
deleted_at  TIMESTAMPTZ DEFAULT NULL       -- soft delete
```

### Soft Delete

- `deleted_at IS NULL` → registro ativo
- `deleted_at IS NOT NULL` → registro "apagado" (recuperável por 30 dias)
- Todas as queries da aplicação incluem `AND deleted_at IS NULL`
- Job diário purga registros com `deleted_at > 30 dias`

### RLS (Row-Level Security)

- Todas as tabelas de dados (exceto `tenants` e `users` globais) têm política RLS filtrando por `tenant_id`
- A política usa `current_setting('app.current_tenant_id')` setado pelo middleware

### Índices

- `idx_{tabela}_tenant_id` em `tenant_id` em todas as tabelas
- `idx_{tabela}_created_at` para consultas temporais
- `idx_{tabela}_deleted_at` para consultas de soft delete
- Índices adicionais documentados em cada tabela

---

## 1. Tenants & Configuração

### `tenants`

Organizações políticas (partidos, candidaturas, assessorias) que usam a plataforma.

```sql
CREATE TABLE tenants (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL,
    slug            VARCHAR(100) NOT NULL UNIQUE,       -- subdomínio: slug.polis.miraitohope.com
    logo_url        TEXT,
    primary_color   VARCHAR(7) DEFAULT '#2563EB',        -- hex
    document_cnpj   VARCHAR(18),                         -- CPF/CNPJ do responsável
    email           VARCHAR(255),
    phone           VARCHAR(20),
    status          VARCHAR(20) NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active', 'suspended', 'trial', 'cancelled')),
    plan_type       VARCHAR(50) NOT NULL DEFAULT 'free'
                    CHECK (plan_type IN ('free', 'starter', 'professional', 'enterprise')),
    max_contacts    INTEGER NOT NULL DEFAULT 500,
    max_users       INTEGER NOT NULL DEFAULT 5,
    max_campaigns   INTEGER NOT NULL DEFAULT 10,
    features        JSONB NOT NULL DEFAULT '{}',          -- feature flags: {"whatsapp": true, "agents": false}
    settings        JSONB NOT NULL DEFAULT '{}',          -- tenant-specific settings
    dpo_contact     JSONB,                                -- {"name": "...", "email": "...", "phone": "..."}
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ DEFAULT NULL
);

CREATE UNIQUE INDEX idx_tenants_slug ON tenants(slug) WHERE deleted_at IS NULL;
CREATE INDEX idx_tenants_status ON tenants(status);
```

### `tenant_settings`

Configurações extensíveis por tenant (chave-valor).

```sql
CREATE TABLE tenant_settings (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    key             VARCHAR(100) NOT NULL,
    value           JSONB NOT NULL,
    description     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ DEFAULT NULL,

    UNIQUE(tenant_id, key)
);

CREATE INDEX idx_tenant_settings_tenant ON tenant_settings(tenant_id);
```

---

## 2. Usuários, Roles & Permissões

### `users`

Usuários da plataforma (login na aplicação).

```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    email           VARCHAR(255) NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    name            VARCHAR(255) NOT NULL,
    avatar_url      TEXT,
    phone           VARCHAR(20),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    is_verified     BOOLEAN NOT NULL DEFAULT FALSE,
    last_login_at   TIMESTAMPTZ,
    two_factor_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    two_factor_secret VARCHAR(255),
    preferences     JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ DEFAULT NULL,

    UNIQUE(tenant_id, email)
);

CREATE INDEX idx_users_tenant ON users(tenant_id);
CREATE INDEX idx_users_email ON users(email);
```

### `roles`

Papéis do sistema RBAC.

```sql
CREATE TABLE roles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name            VARCHAR(100) NOT NULL,
    slug            VARCHAR(100) NOT NULL,
    description     TEXT,
    is_system       BOOLEAN NOT NULL DEFAULT FALSE,   -- true para roles padrão (admin, gestor...)
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ DEFAULT NULL,

    UNIQUE(tenant_id, slug)
);

CREATE INDEX idx_roles_tenant ON roles(tenant_id);
```

### Roles Padrão (Seed)

| Slug | Nome | Descrição |
|------|------|-----------|
| `admin` | Administrador | Acesso total ao tenant |
| `gestor` | Gestor | Gerencia campanhas, contatos, equipe |
| `analista` | Analista | Visualiza dados, cria relatórios |
| `atendente` | Atendente | Acesso apenas à caixa de entrada |

### `permissions`

Catálogo de permissões disponíveis no sistema.

```sql
CREATE TABLE permissions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    module          VARCHAR(50) NOT NULL,               -- auth, crm, campaigns, agents, territorial, analytics
    action          VARCHAR(50) NOT NULL,               -- create, read, update, delete, send, export
    description     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(module, action)
);
```

### `role_permissions`

Associação entre roles e permissões.

```sql
CREATE TABLE role_permissions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_id         UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id   UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(role_id, permission_id)
);

CREATE INDEX idx_role_permissions_role ON role_permissions(role_id);
```

### `user_roles`

Usuários podem ter múltiplos roles.

```sql
CREATE TABLE user_roles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id         UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(user_id, role_id)
);

CREATE INDEX idx_user_roles_user ON user_roles(user_id);
CREATE INDEX idx_user_roles_role ON user_roles(role_id);
```

---

## 3. Canais & Credenciais

### `channels`

Canais de comunicação configurados por tenant.

```sql
CREATE TABLE channels (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    type            VARCHAR(20) NOT NULL
                    CHECK (type IN ('whatsapp', 'sms', 'email', 'telegram', 'instagram')),
    name            VARCHAR(255) NOT NULL,
    phone_number    VARCHAR(20),                        -- para WhatsApp/SMS
    email_from      VARCHAR(255),                       -- para Email
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    is_default      BOOLEAN NOT NULL DEFAULT FALSE,
    config          JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX idx_channels_tenant ON channels(tenant_id);
CREATE INDEX idx_channels_type ON channels(type);
```

### `channel_credentials`

Credenciais dos provedores para cada canal (armazenadas com segurança).

```sql
CREATE TABLE channel_credentials (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    channel_id      UUID NOT NULL REFERENCES channels(id) ON DELETE CASCADE,
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    provider        VARCHAR(50) NOT NULL,               -- evolution_api, cloud_api, twilio, resend, sendgrid
    credentials     JSONB NOT NULL,                     -- criptografado em nível de aplicação
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    last_used_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ DEFAULT NULL,

    UNIQUE(channel_id, provider)
);

CREATE INDEX idx_channel_creds_channel ON channel_credentials(channel_id);
CREATE INDEX idx_channel_creds_tenant ON channel_credentials(tenant_id);
```

---

## 4. Contatos & Consentimento

### `contacts`

Eleitores, apoiadores e leads políticos.

```sql
CREATE TABLE contacts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name            VARCHAR(255) NOT NULL,
    email           VARCHAR(255),
    phone           VARCHAR(20),
    document        VARCHAR(18),                        -- CPF
    birth_date      DATE,
    gender          VARCHAR(20),
    address_street  VARCHAR(255),
    address_number  VARCHAR(20),
    address_complement VARCHAR(100),
    address_neighborhood VARCHAR(100),
    address_city    VARCHAR(100),
    address_state   VARCHAR(2),
    address_zip     VARCHAR(10),
    address_lat     DECIMAL(10, 7),                     -- latitude (PostGIS)
    address_lng     DECIMAL(10, 7),                     -- longitude
    location        GEOGRAPHY(POINT, 4326),             -- PostGIS point
    electoral_zone  VARCHAR(20),                        -- zona eleitoral
    electoral_section VARCHAR(20),                      -- seção eleitoral
    notes           TEXT,
    custom_fields   JSONB NOT NULL DEFAULT '{}',
    source          VARCHAR(50) DEFAULT 'manual',        -- manual, import, whatsapp, api
    status          VARCHAR(20) NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active', 'inactive', 'blocked', 'unsubscribed')),
    unsubscribed_at TIMESTAMPTZ,
    anonymized_at   TIMESTAMPTZ,
    last_contact_at TIMESTAMPTZ,
    total_messages  INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX idx_contacts_tenant ON contacts(tenant_id);
CREATE INDEX idx_contacts_phone ON contacts(phone);
CREATE INDEX idx_contacts_email ON contacts(email);
CREATE INDEX idx_contacts_status ON contacts(status);
CREATE INDEX idx_contacts_neighborhood ON contacts(address_neighborhood);
CREATE INDEX idx_contacts_electoral_zone ON contacts(electoral_zone);
CREATE INDEX idx_contacts_location ON contacts USING GIST(location);
CREATE INDEX idx_contacts_tenant_status ON contacts(tenant_id, status);
```

### `contact_consents`

Registro de consentimento LGPD por contato.

```sql
CREATE TABLE contact_consents (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    contact_id      UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    type            VARCHAR(50) NOT NULL,                -- marketing, communication, research, official
    status          VARCHAR(20) NOT NULL DEFAULT 'granted'
                    CHECK (status IN ('granted', 'revoked', 'expired')),
    granted_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    revoked_at      TIMESTAMPTZ,
    source          VARCHAR(50) NOT NULL,                -- whatsapp, form, import, api, manual
    source_ip       VARCHAR(45),
    user_agent      TEXT,
    channel         VARCHAR(20),                         -- canal onde foi coletado
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_contact_consents_contact ON contact_consents(contact_id);
CREATE INDEX idx_contact_consents_tenant ON contact_consents(tenant_id);
CREATE INDEX idx_contact_consents_type ON contact_consents(type, status);
```

### `contact_tags`

Tags para segmentação de contatos.

```sql
CREATE TABLE contact_tags (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name            VARCHAR(100) NOT NULL,
    color           VARCHAR(7) DEFAULT '#6366F1',
    description     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ DEFAULT NULL,

    UNIQUE(tenant_id, name)
);

CREATE INDEX idx_contact_tags_tenant ON contact_tags(tenant_id);
```

### `contact_tag_assignments`

Associação N:N entre contatos e tags.

```sql
CREATE TABLE contact_tag_assignments (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_id      UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    tag_id          UUID NOT NULL REFERENCES contact_tags(id) ON DELETE CASCADE,
    assigned_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    assigned_by     UUID REFERENCES users(id),

    UNIQUE(contact_id, tag_id)
);

CREATE INDEX idx_cta_contact ON contact_tag_assignments(contact_id);
CREATE INDEX idx_cta_tag ON contact_tag_assignments(tag_id);
```

---

## 5. Conversas & Mensagens

### `conversations`

Thread de mensagens entre a plataforma e um contato em um canal.

```sql
CREATE TABLE conversations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    contact_id      UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    channel_id      UUID REFERENCES channels(id),
    channel_type    VARCHAR(20) NOT NULL,                -- whatsapp, sms, email, telegram, instagram
    external_id     VARCHAR(255),                        -- ID externo no provedor (ex: remoteJid)
    status          VARCHAR(20) NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active', 'waiting', 'resolved', 'archived', 'spam')),
    assigned_to     UUID REFERENCES users(id),           -- atendente responsável
    agent_id        UUID REFERENCES agents(id),          -- agente IA ativo (se houver)
    protocol_number VARCHAR(50),                         -- protocolo único de atendimento
    subject         VARCHAR(255),
    last_message_at TIMESTAMPTZ,
    message_count   INTEGER NOT NULL DEFAULT 0,
    unread_count    INTEGER NOT NULL DEFAULT 0,
    is_priority     BOOLEAN NOT NULL DEFAULT FALSE,
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX idx_conversations_tenant ON conversations(tenant_id);
CREATE INDEX idx_conversations_contact ON conversations(contact_id);
CREATE INDEX idx_conversations_channel ON conversations(channel_id);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_assigned ON conversations(assigned_to);
CREATE INDEX idx_conversations_protocol ON conversations(protocol_number);
CREATE INDEX idx_conversations_last_msg ON conversations(last_message_at DESC);
```

### `messages`

Cada mensagem individual dentro de uma conversa.

```sql
CREATE TABLE messages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    sender_type     VARCHAR(10) NOT NULL
                    CHECK (sender_type IN ('contact', 'user', 'agent', 'system')),
    sender_id       UUID,                                -- contact.id, user.id, agent.id, NULL p/ system
    direction       VARCHAR(10) NOT NULL
                    CHECK (direction IN ('inbound', 'outbound')),
    content_type    VARCHAR(20) NOT NULL DEFAULT 'text'
                    CHECK (content_type IN ('text', 'image', 'audio', 'video', 'document', 'location', 'template', 'system')),
    content         TEXT,
    media_url       TEXT,
    media_mime_type VARCHAR(100),
    media_size      INTEGER,
    external_id     VARCHAR(255),                        -- message ID no provedor
    status          VARCHAR(20) NOT NULL DEFAULT 'sent'
                    CHECK (status IN ('queued', 'sent', 'delivered', 'read', 'failed')),
    status_updated_at TIMESTAMPTZ,
    error_message   TEXT,
    metadata        JSONB DEFAULT '{}',                  -- {"intent": "...", "sentiment": "..."}
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_tenant ON messages(tenant_id);
CREATE INDEX idx_messages_created ON messages(conversation_id, created_at);
CREATE INDEX idx_messages_status ON messages(status);
CREATE INDEX idx_messages_content_type ON messages(content_type);
CREATE INDEX idx_messages_external ON messages(external_id);
```

### `message_attachments`

Anexos de mídia das mensagens.

```sql
CREATE TABLE message_attachments (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    message_id      UUID NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    file_name       VARCHAR(255) NOT NULL,
    file_size       INTEGER NOT NULL,
    mime_type       VARCHAR(100) NOT NULL,
    storage_url     TEXT NOT NULL,                        -- URL no S3/local
    storage_key     VARCHAR(255) NOT NULL,                -- chave no bucket
    thumbnail_url   TEXT,
    width           INTEGER,
    height          INTEGER,
    duration_seconds DECIMAL(10, 2),
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX idx_attachments_message ON message_attachments(message_id);
CREATE INDEX idx_attachments_tenant ON message_attachments(tenant_id);
```

---

## 6. Campanhas

### `campaigns`

Campanhas de disparo em massa.

```sql
CREATE TABLE campaigns (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    channel_type    VARCHAR(20) NOT NULL
                    CHECK (channel_type IN ('whatsapp', 'sms', 'email')),
    channel_id      UUID REFERENCES channels(id),
    template_id     UUID,                                 -- se usar template de mensagem
    content         JSONB NOT NULL,                       -- {"text": "...", "media_url": "..."}
    variables       JSONB DEFAULT '[]',                   -- ["nome", "bairro"]
    status          VARCHAR(20) NOT NULL DEFAULT 'draft'
                    CHECK (status IN ('draft', 'scheduled', 'sending', 'paused', 'completed', 'cancelled', 'failed')),
    scheduled_at    TIMESTAMPTZ,
    sent_at         TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    total_recipients   INTEGER NOT NULL DEFAULT 0,
    sent_count         INTEGER NOT NULL DEFAULT 0,
    delivered_count    INTEGER NOT NULL DEFAULT 0,
    read_count         INTEGER NOT NULL DEFAULT 0,
    failed_count       INTEGER NOT NULL DEFAULT 0,
    created_by      UUID NOT NULL REFERENCES users(id),
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX idx_campaigns_tenant ON campaigns(tenant_id);
CREATE INDEX idx_campaigns_status ON campaigns(status);
CREATE INDEX idx_campaigns_scheduled ON campaigns(scheduled_at);
CREATE INDEX idx_campaigns_created_by ON campaigns(created_by);
```

### `campaign_segments`

Segmentos de contatos que a campanha atinge (filtros).

```sql
CREATE TABLE campaign_segments (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id     UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    filters         JSONB NOT NULL,                       -- [{"field": "tags", "operator": "in", "value": ["eleitores"]}]
    contact_count   INTEGER,                              -- resultado da query de contatos
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_campaign_segments_campaign ON campaign_segments(campaign_id);
CREATE INDEX idx_campaign_segments_tenant ON campaign_segments(tenant_id);
```

### `campaign_recipients`

Contatos individuais que receberão a campanha.

```sql
CREATE TABLE campaign_recipients (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id     UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    contact_id      UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    recipient_phone VARCHAR(20),                          -- snapshot do contato no momento do envio
    recipient_name  VARCHAR(255),
    message_id      UUID REFERENCES messages(id),         -- message gerada
    status          VARCHAR(20) NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'sent', 'delivered', 'read', 'failed')),
    error_message   TEXT,
    attempted_at    TIMESTAMPTZ,
    sent_at         TIMESTAMPTZ,
    delivered_at    TIMESTAMPTZ,
    read_at         TIMESTAMPTZ,
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(campaign_id, contact_id)
);

CREATE INDEX idx_campaign_recip_campaign ON campaign_recipients(campaign_id);
CREATE INDEX idx_campaign_recip_tenant ON campaign_recipients(tenant_id);
CREATE INDEX idx_campaign_recip_status ON campaign_recipients(status);
CREATE INDEX idx_campaign_recip_contact ON campaign_recipients(contact_id);
```

---

## 7. Agentes IA

### `agents`

Agentes de inteligência artificial configurados por tenant.

```sql
CREATE TABLE agents (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    personality     TEXT NOT NULL,                        -- descrição da personalidade
    instructions    TEXT NOT NULL,                        -- instruções de comportamento
    tone_of_voice   VARCHAR(50) DEFAULT 'formal'
                    CHECK (tone_of_voice IN ('formal', 'informal', 'friendly', 'professional', 'empatico')),
    model           VARCHAR(100) DEFAULT 'gemini-2.0-flash',
    temperature     DECIMAL(3, 2) DEFAULT 0.7,
    max_tokens      INTEGER DEFAULT 1024,
    is_active       BOOLEAN NOT NULL DEFAULT FALSE,
    auto_respond    BOOLEAN NOT NULL DEFAULT FALSE,       -- responder automaticamente
    channels        JSONB DEFAULT '["whatsapp"]',         -- canais onde atua
    working_hours   JSONB,                                -- {"start": "08:00", "end": "18:00", "timezone": "America/Sao_Paulo"}
    fallback_to_human BOOLEAN NOT NULL DEFAULT TRUE,
    classification_rules JSONB DEFAULT '{}',              -- regras de classificação customizadas
    metadata        JSONB DEFAULT '{}',
    created_by      UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX idx_agents_tenant ON agents(tenant_id);
CREATE INDEX idx_agents_active ON agents(tenant_id, is_active);
```

### `agent_versions`

Histórico de versões das configurações dos agentes.

```sql
CREATE TABLE agent_versions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id        UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    version         INTEGER NOT NULL,
    personality     TEXT NOT NULL,
    instructions    TEXT NOT NULL,
    tone_of_voice   VARCHAR(50),
    model           VARCHAR(100),
    changelog       TEXT,
    created_by      UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(agent_id, version)
);

CREATE INDEX idx_agent_versions_agent ON agent_versions(agent_id);
CREATE INDEX idx_agent_versions_tenant ON agent_versions(tenant_id);
```

### `knowledge_bases`

Documentos e textos que alimentam o RAG do agente.

```sql
CREATE TABLE knowledge_bases (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    agent_id        UUID REFERENCES agents(id) ON DELETE SET NULL,
    title           VARCHAR(255) NOT NULL,
    content         TEXT NOT NULL,                        -- texto extraído do documento
    content_type    VARCHAR(50) DEFAULT 'manual'
                    CHECK (content_type IN ('manual', 'document', 'faq', 'law', 'regulation', 'script')),
    source_file     TEXT,                                 -- nome original do arquivo
    source_url      TEXT,
    file_type       VARCHAR(50),                          -- pdf, docx, txt, md
    chunk_index     INTEGER,                              -- se o doc foi chunked
    embedding       vector(1536),                         -- pgvector embedding
    metadata        JSONB DEFAULT '{}',
    created_by      UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX idx_kb_tenant ON knowledge_bases(tenant_id);
CREATE INDEX idx_kb_agent ON knowledge_bases(agent_id);
CREATE INDEX idx_kb_embedding ON knowledge_bases USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);
CREATE INDEX idx_kb_content_type ON knowledge_bases(content_type);
```

---

## 8. Categorias & Eventos Territoriais

### `categories`

Categorias para eventos e conteúdos.

```sql
CREATE TABLE categories (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name            VARCHAR(100) NOT NULL,
    slug            VARCHAR(100) NOT NULL,
    description     TEXT,
    color           VARCHAR(7) DEFAULT '#6B7280',
    icon            VARCHAR(50),
    parent_id       UUID REFERENCES categories(id),
    sort_order      INTEGER DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ DEFAULT NULL,

    UNIQUE(tenant_id, slug)
);

CREATE INDEX idx_categories_tenant ON categories(tenant_id);
CREATE INDEX idx_categories_parent ON categories(parent_id);
```

### `territorial_events`

Eventos com relevância territorial (comícios, reuniões, panfletagem, eventos da cidade).

```sql
CREATE TABLE territorial_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    category_id     UUID REFERENCES categories(id),
    title           VARCHAR(255) NOT NULL,
    description     TEXT,
    event_type      VARCHAR(50) NOT NULL
                    CHECK (event_type IN ('rally', 'meeting', 'canvassing', 'city_event', 'debate', 'other')),
    event_date      TIMESTAMPTZ NOT NULL,
    end_date        TIMESTAMPTZ,
    location_name   VARCHAR(255),
    address         TEXT,
    lat             DECIMAL(10, 7),
    lng             DECIMAL(10, 7),
    location_point  GEOGRAPHY(POINT, 4326),               -- PostGIS
    electoral_zone  VARCHAR(20),
    neighborhood    VARCHAR(100),
    city            VARCHAR(100),
    state           VARCHAR(2),
    expected_public INTEGER,
    real_public     INTEGER,
    status          VARCHAR(20) NOT NULL DEFAULT 'scheduled'
                    CHECK (status IN ('scheduled', 'confirmed', 'ongoing', 'completed', 'cancelled')),
    created_by      UUID REFERENCES users(id),
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX idx_te_tenant ON territorial_events(tenant_id);
CREATE INDEX idx_te_date ON territorial_events(event_date);
CREATE INDEX idx_te_type ON territorial_events(event_type);
CREATE INDEX idx_te_status ON territorial_events(status);
CREATE INDEX idx_te_location ON territorial_events USING GIST(location_point);
CREATE INDEX idx_te_neighborhood ON territorial_events(neighborhood);
CREATE INDEX idx_te_electoral_zone ON territorial_events(electoral_zone);
```

### `territorial_reports`

Relatórios territoriais gerados (por zona, bairro, período).

```sql
CREATE TABLE territorial_reports (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    title           VARCHAR(255) NOT NULL,
    report_type     VARCHAR(50) NOT NULL
                    CHECK (report_type IN ('zone_summary', 'neighborhood_ranking', 'event_density', 'contact_distribution')),
    filters         JSONB NOT NULL DEFAULT '{}',           -- filtros aplicados
    data            JSONB NOT NULL,                        -- resultado do relatório
    generated_by    UUID REFERENCES users(id),
    generated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at      TIMESTAMPTZ,                           -- cache expira
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX idx_tr_tenant ON territorial_reports(tenant_id);
CREATE INDEX idx_tr_type ON territorial_reports(report_type);
CREATE INDEX idx_tr_generated ON territorial_reports(generated_at);
```

---

## 9. Tarefas & Projetos

### `tasks`

Tarefas operacionais da campanha (reaproveitando modelo do Arca).

```sql
CREATE TABLE tasks (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    title           VARCHAR(255) NOT NULL,
    description     TEXT,
    task_type       VARCHAR(50) DEFAULT 'general'
                    CHECK (task_type IN ('general', 'call', 'meeting', 'delivery', 'content', 'event', 'follow_up')),
    status          VARCHAR(20) NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled', 'blocked')),
    priority        VARCHAR(10) NOT NULL DEFAULT 'medium'
                    CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    assigned_to     UUID REFERENCES users(id),
    created_by      UUID REFERENCES users(id),
    due_date        TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    related_to_type VARCHAR(50),                          -- campaign, contact, conversation, event
    related_to_id   UUID,
    kpis            JSONB DEFAULT '{}',                   -- {"calls_made": 5, "contacts_reached": 50}
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX idx_tasks_tenant ON tasks(tenant_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_assigned ON tasks(assigned_to);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_related ON tasks(related_to_type, related_to_id);
```

### `protocols`

Registro de protocolos de atendimento (por lei, cada interação com cidadão gera protocolo).

```sql
CREATE TABLE protocols (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    contact_id      UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    protocol_number VARCHAR(50) NOT NULL,                 -- ex: POL-2026-0001
    subject         VARCHAR(255),
    description     TEXT,
    status          VARCHAR(30) NOT NULL DEFAULT 'open'
                    CHECK (status IN ('open', 'in_progress', 'resolved', 'closed', 'appealed')),
    priority        VARCHAR(10) DEFAULT 'normal'
                    CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    category        VARCHAR(100),                         -- type of demand
    channel         VARCHAR(20),                          -- canal de origem
    assigned_to     UUID REFERENCES users(id),
    resolved_at     TIMESTAMPTZ,
    resolution      TEXT,                                 -- descrição da resolução
    satisfaction    INTEGER CHECK (satisfaction BETWEEN 1 AND 5),
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ DEFAULT NULL,

    UNIQUE(tenant_id, protocol_number)
);

CREATE INDEX idx_protocols_tenant ON protocols(tenant_id);
CREATE INDEX idx_protocols_conversation ON protocols(conversation_id);
CREATE INDEX idx_protocols_contact ON protocols(contact_id);
CREATE INDEX idx_protocols_status ON protocols(status);
CREATE INDEX idx_protocols_protocol ON protocols(protocol_number);
CREATE INDEX idx_protocols_assigned ON protocols(assigned_to);
```

---

## 10. Auditoria & Logs

### `audit_logs`

Registro de todas as ações relevantes na plataforma (LGPD, segurança, operações).

```sql
CREATE TABLE audit_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID REFERENCES tenants(id),           -- pode ser NULL para ações globais
    user_id         UUID REFERENCES users(id),
    action          VARCHAR(100) NOT NULL,                  -- contact.created, campaign.sent, message.sent, user.login
    entity_type     VARCHAR(50),                            -- contact, campaign, message, user, agent
    entity_id       UUID,                                   -- ID da entidade afetada
    description     TEXT,
    metadata        JSONB DEFAULT '{}',                     -- payload da mudança, diferenças
    ip_address      VARCHAR(45),
    user_agent      TEXT,
    severity        VARCHAR(10) DEFAULT 'info'
                    CHECK (severity IN ('debug', 'info', 'warning', 'error', 'critical')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_tenant ON audit_logs(tenant_id);
CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_created ON audit_logs(created_at);
CREATE INDEX idx_audit_severity ON audit_logs(severity);
-- Tabela de auditoria NÃO tem soft delete nem update (append-only)
```

---

## 11. Tabelas de Apoio

### `sessions`

Sessões de usuário (refresh token tracking).

```sql
CREATE TABLE sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    refresh_token   VARCHAR(255) NOT NULL UNIQUE,
    device_info     TEXT,
    ip_address      VARCHAR(45),
    user_agent      TEXT,
    is_valid        BOOLEAN NOT NULL DEFAULT TRUE,
    expires_at      TIMESTAMPTZ NOT NULL,
    last_used_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sessions_user ON sessions(user_id);
CREATE INDEX idx_sessions_token ON sessions(refresh_token);
CREATE INDEX idx_sessions_expires ON sessions(expires_at);
```

### `templates`

Templates de mensagens para campanhas e respostas rápidas.

```sql
CREATE TABLE templates (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    channel_type    VARCHAR(20) NOT NULL
                    CHECK (channel_type IN ('whatsapp', 'sms', 'email')),
    content         JSONB NOT NULL,                        -- {"text": "Olá {{nome}}!", "media_url": null}
    variables       JSONB DEFAULT '[]',                    -- ["nome", "bairro"]
    category        VARCHAR(50) DEFAULT 'general',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_by      UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ DEFAULT NULL,

    UNIQUE(tenant_id, name)
);

CREATE INDEX idx_templates_tenant ON templates(tenant_id);
CREATE INDEX idx_templates_channel ON templates(channel_type);
```

---

## 12. Resumo das Tabelas

| # | Tabela | Tipo | Finalidade |
|---|--------|------|------------|
| 1 | `tenants` | Core | Organizações políticas |
| 2 | `tenant_settings` | Core | Configurações de tenant |
| 3 | `users` | Auth | Usuários da plataforma |
| 4 | `roles` | Auth | Papéis RBAC |
| 5 | `permissions` | Auth | Catálogo de permissões |
| 6 | `role_permissions` | Auth | Role ↔ Permission |
| 7 | `user_roles` | Auth | User ↔ Role |
| 8 | `sessions` | Auth | Sessões de usuário |
| 9 | `channels` | Comms | Canais de comunicação |
| 10 | `channel_credentials` | Comms | Credenciais dos canais |
| 11 | `contacts` | CRM | Contatos/eleitores |
| 12 | `contact_consents` | CRM | Consentimentos LGPD |
| 13 | `contact_tags` | CRM | Tags de segmentação |
| 14 | `contact_tag_assignments` | CRM | Contact ↔ Tag |
| 15 | `templates` | CRM | Templates de mensagem |
| 16 | `conversations` | Comms | Conversas |
| 17 | `messages` | Comms | Mensagens |
| 18 | `message_attachments` | Comms | Anexos |
| 19 | `campaigns` | Campaign | Campanhas de disparo |
| 20 | `campaign_segments` | Campaign | Segmentos de campanha |
| 21 | `campaign_recipients` | Campaign | Recipientes individuais |
| 22 | `agents` | IA | Agentes de IA |
| 23 | `agent_versions` | IA | Versões dos agentes |
| 24 | `knowledge_bases` | IA | Base de conhecimento RAG |
| 25 | `categories` | Geral | Categorias |
| 26 | `territorial_events` | Mapa | Eventos territoriais |
| 27 | `territorial_reports` | Mapa | Relatórios territoriais |
| 28 | `tasks` | Ops | Tarefas operacionais |
| 29 | `protocols` | Ops | Protocolos de atendimento |
| 30 | `audit_logs` | Seg | Logs de auditoria |

**Total: 30 tabelas** (todas com UUID PK, tenant_id, created_at, updated_at, soft delete onde aplicável)

---

## 13. Scripts de Migração (Seed)

### Permissões Padrão

```sql
-- Módulos e suas permissões base
INSERT INTO permissions (module, action, description) VALUES
    ('auth',     'create', 'Criar usuários'),
    ('auth',     'read',   'Visualizar usuários'),
    ('auth',     'update', 'Editar usuários'),
    ('auth',     'delete', 'Excluir usuários'),
    ('crm',      'create', 'Criar contatos'),
    ('crm',      'read',   'Visualizar contatos'),
    ('crm',      'update', 'Editar contatos'),
    ('crm',      'delete', 'Excluir contatos'),
    ('crm',      'import', 'Importar contatos'),
    ('crm',      'export', 'Exportar contatos'),
    ('campaigns','create', 'Criar campanhas'),
    ('campaigns','read',   'Visualizar campanhas'),
    ('campaigns','update', 'Editar campanhas'),
    ('campaigns','delete', 'Excluir campanhas'),
    ('campaigns','send',   'Enviar campanhas'),
    ('agents',   'create', 'Criar agentes IA'),
    ('agents',   'read',   'Visualizar agentes IA'),
    ('agents',   'update', 'Editar agentes IA'),
    ('agents',   'delete', 'Excluir agentes IA'),
    ('whatsapp', 'read',   'Visualizar mensagens'),
    ('whatsapp', 'send',   'Enviar mensagens'),
    ('whatsapp', 'manage', 'Gerenciar canais WhatsApp'),
    ('territorial','create','Criar eventos'),
    ('territorial','read',  'Visualizar mapa'),
    ('territorial','update','Editar eventos'),
    ('territorial','delete','Excluir eventos'),
    ('analytics','read',   'Visualizar dashboards'),
    ('analytics','export', 'Exportar relatórios'),
    ('settings', 'read',   'Visualizar configurações'),
    ('settings', 'update', 'Editar configurações');
```

### Roles Padrão com Permissões

```sql
-- Admin: todas as permissões
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p
WHERE r.slug = 'admin';

-- Gestor: exceto delete de auth e configurações críticas
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p
WHERE r.slug = 'gestor'
  AND NOT (p.module = 'auth' AND p.action IN ('delete', 'create'))
  AND NOT (p.module = 'settings');

-- Analista: apenas leitura + export
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p
WHERE r.slug = 'analista'
  AND p.action IN ('read', 'export');

-- Atendente: apenas WhatsApp
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p
WHERE r.slug = 'atendente'
  AND p.module IN ('whatsapp', 'crm')
  AND p.action IN ('read', 'send', 'update');
```

---

*Este schema deve ser migrado via Prisma (`prisma/schema.prisma`). O SQL acima serve como blueprint conceitual e referência para políticas RLS. Toda a migração deve ser versionada e revisada antes de aplicar em produção.*
