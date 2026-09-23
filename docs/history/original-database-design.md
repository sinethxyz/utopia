For a **serious private Utopia system**, I would not design the database as “one big notes table plus embeddings.”  
That would kill the product.

Utopia needs a **typed memory architecture** with clear separation between:

* directional truth  
* live execution state  
* evidence about the operator  
* physiological priors  
* extracted knowledge  
* reasoning artifacts  
* action traces  
* calibration and policy learning  
* integration and audit infrastructure

The right mental model is:

**Postgres as canonical truth**  
**vector index for semantic recall**  
**graph edges for explicit conceptual relationships**  
**event log for replay/audit/triggering**  
**object store for raw artifacts**  
**time-series for dense physiological / behavioral telemetry**

That is the serious shape.

---

# **1\. Core storage strategy**

I would split the system into five storage roles.

## **A. Relational core**

This is the source of truth for all canonical entities.

Use it for:

* missions  
* threads  
* states  
* blockers  
* re-entry artifacts  
* rules  
* traces  
* decision briefs  
* sources  
* extractions  
* concepts  
* mechanisms  
* lens packs  
* permissions  
* OAuth connections  
* review records

This should be PostgreSQL.

## **B. Vector retrieval layer**

This exists for semantic retrieval across:

* extracted concepts  
* cases  
* prior traces  
* source chunks  
* decision briefs  
* rules  
* diagnostic questions

Keep this close to the relational core unless scale forces separation.  
For a private serious system, I would start with **pgvector inside Postgres**, not an external vector database.

## **C. Graph layer**

Use this for explicit relationships, not as the primary store.

Graph is useful for:

* concept → mechanism  
* mechanism → failure mode  
* lens → question  
* rule → applies\_to  
* case → pattern  
* pattern → intervention  
* contradiction → corrected\_by

You can model this in relational first with an `edges` table.  
Only move to a dedicated graph database if traversal actually becomes central.

## **D. Event / telemetry layer**

This captures:

* user actions  
* thread touches  
* failed starts  
* trigger firings  
* AI orchestration events  
* webhook receipts  
* provider calls  
* policy decisions

This can still live in Postgres initially as append-only event tables.

## **E. Object storage**

Use for:

* raw source files  
* PDFs  
* original imported documents  
* extraction snapshots  
* large JSON payload archives  
* encrypted export bundles

That should not be the operational DB.

---

# **2\. Database design principles**

The entire schema should obey a few principles.

## **Typed over generic**

Do not store everything in `notes`.  
Use separate typed tables for distinct cognitive objects.

## **Append where truth unfolds**

Traces, estimates, webhook receipts, and orchestration runs should often be append-only.

## **Current-state views over mutable sludge**

Keep immutable history, then materialize current state via views or snapshot tables.

## **JSONB for edges, not for the core**

Use JSONB for flexible payloads, model outputs, or provider-specific metadata.  
Do not hide core product semantics inside JSON blobs.

## **Single-user first, multi-tenant safe**

Even if Utopia is private and single-user, design tables with `operator_id` or `workspace_id` so the system is structurally clean.

## **Explicit confidence everywhere**

Any inferred object should store:

* confidence  
* evidence\_count  
* provenance  
* last\_validated\_at

Because Utopia is a reasoning system, not just a CRUD app.

---

# **3\. Logical schema namespaces**

I would separate the database into logical schemas like this:

* `core`  
* `vector`  
* `evidence`  
* `physiology`  
* `vector_ctrl`  
* `aether`  
* `reasoning`  
* `execution`  
* `integration`  
* `system`

That gives you clean domain boundaries.

---

# **4\. Global conventions**

Every major object should have:

* `id` as UUIDv7  
* `operator_id`  
* `created_at`  
* `updated_at`  
* `archived_at` nullable  
* `version`  
* `source_kind`  
* `provenance`  
* `confidence` where applicable

Suggested enums:

* `status`  
* `state_kind`  
* `blocker_kind`  
* `source_kind`  
* `memory_class`  
* `evidence_kind`  
* `intervention_kind`  
* `decision_kind`

Use UUIDv7 or time-ordered UUIDs because Utopia is event-heavy and benefits from sortable IDs.

---

# **5\. Core identity and system tables**

Even for a private system, you want these.

## **`core.operators`**

Represents the human operator the system is modeling.

create table core.operators (  
  id uuid primary key,  
  display\_name text not null,  
  timezone text not null,  
  locale text,  
  created\_at timestamptz not null default now(),  
  updated\_at timestamptz not null default now()  
);

## **`core.devices`**

Tracks trusted devices for local-first syncing.

create table core.devices (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  device\_name text not null,  
  device\_type text not null,  
  public\_key\_fingerprint text,  
  last\_seen\_at timestamptz,  
  created\_at timestamptz not null default now()  
);

## **`integration.oauth_connections`**

Stores external integration connections.

create table integration.oauth\_connections (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  provider text not null,                \-- whoop, openai, anthropic, etc.  
  provider\_user\_id text,  
  scopes text\[\] not null default '{}',  
  status text not null,                  \-- active, revoked, expired  
  encrypted\_access\_token bytea,  
  encrypted\_refresh\_token bytea,  
  token\_expires\_at timestamptz,  
  metadata jsonb not null default '{}',  
  created\_at timestamptz not null default now(),  
  updated\_at timestamptz not null default now()  
);

## **`integration.permissions`**

Fine-grained permissions ledger.

create table integration.permissions (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  provider text not null,  
  permission\_key text not null,  
  granted boolean not null,  
  granted\_at timestamptz,  
  revoked\_at timestamptz,  
  details jsonb not null default '{}'  
);

---

# **6\. Vector schema: direction and control plane**

This is where Utopia stores what matters.

## **`vector_ctrl.life_arcs`**

Top-level directional framing.

create table vector\_ctrl.life\_arcs (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  title text not null,  
  description text,  
  status text not null,                  \-- active, dormant, archived  
  horizon\_start date,  
  horizon\_end date,  
  success\_definition text,  
  anti\_goals text\[\] not null default '{}',  
  created\_at timestamptz not null default now(),  
  updated\_at timestamptz not null default now()  
);

## **`vector_ctrl.seasons`**

A season is a bounded phase of focus.

create table vector\_ctrl.seasons (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  life\_arc\_id uuid references vector\_ctrl.life\_arcs(id),  
  title text not null,  
  thesis text,  
  start\_date date not null,  
  end\_date date,  
  priority\_stack jsonb not null default '\[\]',  
  status text not null,                  \-- planned, active, closed  
  created\_at timestamptz not null default now(),  
  updated\_at timestamptz not null default now()  
);

## **`vector_ctrl.missions`**

Strategically meaningful objectives.

create table vector\_ctrl.missions (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  season\_id uuid references vector\_ctrl.seasons(id),  
  title text not null,  
  description text,  
  mission\_kind text not null,            \-- strategic, technical, personal, recovery, etc.  
  priority\_score numeric(6,3),  
  status text not null,                  \-- active, paused, completed, abandoned  
  success\_definition text,  
  failure\_definition text,  
  drift\_definition text,  
  created\_at timestamptz not null default now(),  
  updated\_at timestamptz not null default now()  
);

## **`vector_ctrl.threads`**

Live lines of work within missions.

create table vector\_ctrl.threads (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  mission\_id uuid not null references vector\_ctrl.missions(id),  
  parent\_thread\_id uuid references vector\_ctrl.threads(id),  
  title text not null,  
  description text,  
  thread\_kind text not null,             \-- build, research, decision, admin, etc.  
  status text not null,                  \-- active, blocked, paused, closed  
  complexity\_score numeric(6,3),  
  ambiguity\_score numeric(6,3),  
  reentry\_risk\_score numeric(6,3),  
  last\_meaningful\_touch\_at timestamptz,  
  next\_edge\_summary text,  
  created\_at timestamptz not null default now(),  
  updated\_at timestamptz not null default now()  
);

## **`vector_ctrl.thread_constraints`**

Explicit constraints on a thread.

create table vector\_ctrl.thread\_constraints (  
  id uuid primary key,  
  thread\_id uuid not null references vector\_ctrl.threads(id),  
  constraint\_type text not null,         \-- time, dependency, budget, skill, legal  
  description text not null,  
  hardness text not null,                \-- hard, soft, assumed  
  created\_at timestamptz not null default now()  
);

## **`vector_ctrl.anti_goals`**

What must not happen.

create table vector\_ctrl.anti\_goals (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  scope\_type text not null,              \-- life\_arc, season, mission, thread  
  scope\_id uuid not null,  
  description text not null,  
  created\_at timestamptz not null default now()  
);

---

# **7\. Evidence schema: subjective, behavioral, contextual**

This is the live sensing layer.

## **`evidence.subjective_checkins`**

create table evidence.subjective\_checkins (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  thread\_id uuid references vector\_ctrl.threads(id),  
  energy smallint check (energy between 0 and 100),  
  clarity smallint check (clarity between 0 and 100),  
  resistance smallint check (resistance between 0 and 100),  
  overwhelm smallint check (overwhelm between 0 and 100),  
  emotional\_load smallint check (emotional\_load between 0 and 100),  
  perceived\_urgency smallint check (perceived\_urgency between 0 and 100),  
  free\_text text,  
  recorded\_at timestamptz not null,  
  created\_at timestamptz not null default now()  
);

## **`evidence.behavior_events`**

create table evidence.behavior\_events (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  thread\_id uuid references vector\_ctrl.threads(id),  
  event\_type text not null,              \-- thread\_opened, action\_started, action\_abandoned, etc.  
  event\_at timestamptz not null,  
  duration\_ms bigint,  
  metadata jsonb not null default '{}'  
);

## **`evidence.context_snapshots`**

create table evidence.context\_snapshots (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  thread\_id uuid references vector\_ctrl.threads(id),  
  local\_time timestamptz not null,  
  environment\_label text,  
  interruption\_count int,  
  obligation\_load smallint,  
  available\_minutes int,  
  active\_window text,                    \-- morning, afternoon, evening  
  metadata jsonb not null default '{}'  
);

## **`evidence.derived_features`**

Computed features from raw evidence.

create table evidence.derived\_features (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  thread\_id uuid references vector\_ctrl.threads(id),  
  feature\_name text not null,  
  feature\_value numeric,  
  feature\_json jsonb,  
  feature\_window text,                   \-- last\_2h, last\_24h, last\_7d  
  confidence numeric(5,4),  
  observed\_at timestamptz not null,  
  created\_at timestamptz not null default now()  
);

This is where you store things like:

* failed\_start\_rate\_24h  
* thread\_decay\_hours  
* drift\_probability  
* completion\_aversion\_score  
* ambiguity\_candidate\_score

---

# **8\. Physiology schema: WHOOP as a first-class subsystem**

This domain should be explicit because WHOOP is not just metadata.  
WHOOP’s API provides OAuth-scoped data for recovery, cycles, sleep, workouts, profile, and body measurements, and its webhook model sends events such as `recovery.updated`, `sleep.updated`, and `workout.updated` with HMAC-verifiable signatures. Recovery is described by WHOOP as a daily 0–100 score derived from signals such as HRV and resting heart rate. ([WHOOP for Developers](https://developer.whoop.com/api/))

## **`physiology.whoop_connections`**

create table physiology.whoop\_connections (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  oauth\_connection\_id uuid not null references integration.oauth\_connections(id),  
  whoop\_user\_id bigint,  
  webhook\_secret\_fingerprint text,  
  status text not null,                  \-- active, revoked, errored  
  last\_sync\_at timestamptz,  
  created\_at timestamptz not null default now(),  
  updated\_at timestamptz not null default now()  
);

## **`physiology.whoop_body_measurements`**

create table physiology.whoop\_body\_measurements (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  measured\_at timestamptz not null,  
  height\_meter numeric(6,4),  
  weight\_kg numeric(6,3),  
  max\_heart\_rate int,  
  source\_payload jsonb not null default '{}',  
  created\_at timestamptz not null default now()  
);

## **`physiology.whoop_cycles`**

create table physiology.whoop\_cycles (  
  id uuid primary key,                   \-- internal UUID  
  operator\_id uuid not null references core.operators(id),  
  provider\_cycle\_id bigint not null unique,  
  whoop\_user\_id bigint,  
  cycle\_start timestamptz not null,  
  cycle\_end timestamptz,  
  timezone\_offset text,  
  score\_state text,                      \-- SCORED, PENDING\_SCORE, UNSCORABLE  
  strain numeric(8,4),  
  kilojoule numeric(12,3),  
  average\_heart\_rate int,  
  max\_heart\_rate int,  
  source\_payload jsonb not null default '{}',  
  created\_at timestamptz not null default now(),  
  updated\_at timestamptz not null default now()  
);

## **`physiology.whoop_sleeps`**

create table physiology.whoop\_sleeps (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  provider\_sleep\_id uuid not null unique,  
  provider\_cycle\_id bigint,  
  sleep\_start timestamptz,  
  sleep\_end timestamptz,  
  sleep\_performance\_pct numeric(5,2),  
  total\_in\_bed\_ms bigint,  
  total\_asleep\_ms bigint,  
  slow\_wave\_ms bigint,  
  rem\_ms bigint,  
  light\_ms bigint,  
  awake\_ms bigint,  
  source\_payload jsonb not null default '{}',  
  created\_at timestamptz not null default now(),  
  updated\_at timestamptz not null default now()  
);

## **`physiology.whoop_recoveries`**

Recovery objects should mirror WHOOP’s actual structure closely enough to avoid lossy mapping. WHOOP’s recovery docs describe fields including `cycle_id`, `sleep_id`, `user_id`, `created_at`, `updated_at`, `score_state`, and score values like `recovery_score`, `resting_heart_rate`, and `hrv_rmssd_milli`. ([WHOOP for Developers](https://developer.whoop.com/docs/developing/user-data/recovery/))

create table physiology.whoop\_recoveries (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  provider\_cycle\_id bigint not null,  
  provider\_sleep\_id uuid not null,  
  whoop\_user\_id bigint,  
  recorded\_at timestamptz not null,  
  updated\_at\_source timestamptz,  
  score\_state text not null,  
  recovery\_score smallint,  
  resting\_heart\_rate int,  
  hrv\_rmssd\_milli numeric(12,6),  
  spo2\_percentage numeric(6,3),  
  skin\_temp\_celsius numeric(6,3),  
  user\_calibrating boolean,  
  source\_payload jsonb not null default '{}',  
  created\_at timestamptz not null default now(),  
  unique (operator\_id, provider\_cycle\_id, provider\_sleep\_id)  
);

## **`physiology.whoop_workouts`**

create table physiology.whoop\_workouts (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  provider\_workout\_id uuid not null unique,  
  workout\_type text,  
  workout\_start timestamptz,  
  workout\_end timestamptz,  
  strain numeric(8,4),  
  average\_heart\_rate int,  
  max\_heart\_rate int,  
  source\_payload jsonb not null default '{}',  
  created\_at timestamptz not null default now(),  
  updated\_at timestamptz not null default now()  
);

## **`physiology.physiology_features`**

This is where raw WHOOP data becomes operational priors.

create table physiology.physiology\_features (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  feature\_date date not null,  
  feature\_name text not null,            \-- capacity\_envelope, fragility\_risk, sleep\_debt\_slope, etc.  
  feature\_value numeric,  
  feature\_json jsonb,  
  confidence numeric(5,4),  
  computed\_at timestamptz not null default now(),  
  unique (operator\_id, feature\_date, feature\_name)  
);

Useful features:

* recovery\_trend\_3d  
* recovery\_volatility\_7d  
* strain\_carryover  
* sleep\_regularity\_score  
* fragility\_risk  
* depth\_ceiling\_score  
* depletion\_prior  
* recovery\_mismatch\_score

## **`physiology.biomarker_panels`**

For Advanced Labs or any later biomarker layer, keep separate from wearable data.

create table physiology.biomarker\_panels (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  panel\_date date not null,  
  provider text not null,  
  panel\_type text not null,              \-- advanced\_labs, manual\_lab\_import  
  summary jsonb not null,  
  source\_payload jsonb not null default '{}',  
  created\_at timestamptz not null default now()  
);

## **`integration.webhook_receipts`**

WHOOP webhook bodies include fields like `user_id`, `id`, `type`, and `trace_id`, and WHOOP documents signature validation using `X-WHOOP-Signature` and `X-WHOOP-Signature-Timestamp`. ([WHOOP for Developers](https://developer.whoop.com/docs/developing/webhooks/))

create table integration.webhook\_receipts (  
  id uuid primary key,  
  provider text not null,  
  event\_type text not null,  
  provider\_user\_id text,  
  provider\_object\_id text,  
  trace\_id text,  
  received\_at timestamptz not null default now(),  
  signature\_valid boolean,  
  headers jsonb not null,  
  raw\_body jsonb not null,  
  processed\_at timestamptz,  
  processing\_status text not null default 'pending'  
);

---

# **9\. Aether schema: memory and extracted intelligence**

This is the most important part of the system.

Do not make Aether one table.  
It should be a family of typed memory objects.

## **`aether.sources`**

create table aether.sources (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  source\_kind text not null,             \-- book, paper, essay, transcript, note\_bundle, case\_file  
  title text not null,  
  author text,  
  published\_at date,  
  ingest\_status text not null,  
  canonical\_uri text,  
  storage\_uri text,  
  checksum text,  
  metadata jsonb not null default '{}',  
  created\_at timestamptz not null default now(),  
  updated\_at timestamptz not null default now()  
);

## **`aether.source_chunks`**

Only if you need chunk-level retrieval.

create table aether.source\_chunks (  
  id uuid primary key,  
  source\_id uuid not null references aether.sources(id),  
  chunk\_index int not null,  
  raw\_text text not null,  
  token\_count int,  
  semantic\_label text,  
  metadata jsonb not null default '{}'  
);

## **`aether.extractions`**

A structured distillation pass for a source.

create table aether.extractions (  
  id uuid primary key,  
  source\_id uuid not null references aether.sources(id),  
  extraction\_version text not null,  
  extraction\_status text not null,  
  thesis text,  
  summary text,  
  confidence numeric(5,4),  
  extracted\_at timestamptz not null default now(),  
  model\_run\_id uuid,  
  unique (source\_id, extraction\_version)  
);

## **`aether.concepts`**

create table aether.concepts (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  canonical\_name text not null,  
  definition text,  
  domain text,  
  source\_count int not null default 0,  
  confidence numeric(5,4),  
  created\_at timestamptz not null default now(),  
  updated\_at timestamptz not null default now(),  
  unique (operator\_id, canonical\_name)  
);

## **`aether.mechanisms`**

create table aether.mechanisms (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  name text not null,  
  description text not null,  
  causal\_logic text,  
  domain text,  
  confidence numeric(5,4),  
  created\_at timestamptz not null default now()  
);

## **`aether.tradeoffs`**

create table aether.tradeoffs (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  name text not null,  
  pole\_a text not null,  
  pole\_b text not null,  
  description text,  
  domain text,  
  created\_at timestamptz not null default now()  
);

## **`aether.failure_modes`**

create table aether.failure\_modes (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  name text not null,  
  description text not null,  
  early\_signals text\[\],  
  domain text,  
  severity text,  
  created\_at timestamptz not null default now()  
);

## **`aether.heuristics`**

create table aether.heuristics (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  statement text not null,  
  domain text,  
  applicability text,  
  failure\_conditions text,  
  confidence numeric(5,4),  
  created\_at timestamptz not null default now()  
);

## **`aether.diagnostic_questions`**

create table aether.diagnostic\_questions (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  question\_text text not null,  
  question\_class text not null,          \-- objective, constraint, risk, hidden\_variable, etc.  
  domain text,  
  usefulness\_score numeric(6,3),  
  created\_at timestamptz not null default now()  
);

## **`aether.protocols`**

Reusable reasoning flows.

create table aether.protocols (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  protocol\_name text not null,  
  domain text not null,  
  purpose text,  
  steps jsonb not null,                  \-- ordered protocol structure  
  applicability text,  
  created\_at timestamptz not null default now()  
);

## **`aether.lens_packs`**

create table aether.lens\_packs (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  name text not null,  
  domain text not null,  
  description text,  
  version text not null,  
  source\_basis jsonb not null default '\[\]',  
  created\_at timestamptz not null default now()  
);

## **`aether.lens_pack_items`**

create table aether.lens\_pack\_items (  
  id uuid primary key,  
  lens\_pack\_id uuid not null references aether.lens\_packs(id),  
  item\_kind text not null,               \-- concept, mechanism, question, heuristic, protocol, failure\_mode  
  item\_id uuid not null,  
  weight numeric(6,3),  
  metadata jsonb not null default '{}'  
);

## **`aether.cases`**

Internal or external cases.

create table aether.cases (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  title text not null,  
  case\_kind text not null,               \-- internal, external  
  summary text,  
  outcome text,  
  lessons jsonb not null default '\[\]',  
  created\_at timestamptz not null default now()  
);

## **`aether.rules`**

Durable truths that survived compression.

create table aether.rules (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  rule\_text text not null,  
  rule\_kind text not null,               \-- execution, reasoning, physiology, strategic, personal  
  evidence\_count int not null default 0,  
  confidence numeric(5,4),  
  first\_observed\_at timestamptz,  
  last\_validated\_at timestamptz,  
  active boolean not null default true,  
  created\_at timestamptz not null default now()  
);

## **`aether.patterns`**

create table aether.patterns (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  pattern\_name text not null,  
  description text,  
  pattern\_kind text not null,            \-- blocker, timing, physiology, narrative, execution  
  recurrence\_count int not null default 0,  
  confidence numeric(5,4),  
  created\_at timestamptz not null default now()  
);

## **`aether.edges`**

Relational graph layer.

create table aether.edges (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  src\_kind text not null,  
  src\_id uuid not null,  
  edge\_type text not null,               \-- supports, contradicts, applies\_to, predicts, resembles, etc.  
  dst\_kind text not null,  
  dst\_id uuid not null,  
  weight numeric(6,3),  
  provenance jsonb not null default '{}',  
  created\_at timestamptz not null default now()  
);

This table becomes surprisingly powerful if kept clean.

---

# **10\. Reasoning schema: problem room and decision artifacts**

This is where Utopia turns live problems into structured thinking.

## **`reasoning.problems`**

create table reasoning.problems (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  title text not null,  
  raw\_prompt text not null,  
  problem\_kind text,                     \-- strategic, technical, social, legal, execution, etc.  
  urgency\_score numeric(6,3),  
  stakes\_score numeric(6,3),  
  uncertainty\_score numeric(6,3),  
  state\_at\_creation text,  
  thread\_id uuid references vector\_ctrl.threads(id),  
  created\_at timestamptz not null default now()  
);

## **`reasoning.problem_structures`**

create table reasoning.problem\_structures (  
  id uuid primary key,  
  problem\_id uuid not null references reasoning.problems(id),  
  objective text,  
  stakes text,  
  actors jsonb not null default '\[\]',  
  incentives jsonb not null default '\[\]',  
  constraints jsonb not null default '\[\]',  
  assumptions jsonb not null default '\[\]',  
  unknowns jsonb not null default '\[\]',  
  irreversibilities jsonb not null default '\[\]',  
  bottlenecks jsonb not null default '\[\]',  
  observable\_facts jsonb not null default '\[\]',  
  narrative\_layer jsonb not null default '\[\]',  
  distortion\_candidates jsonb not null default '\[\]',  
  confidence numeric(5,4),  
  generated\_at timestamptz not null default now()  
);

## **`reasoning.interrogations`**

create table reasoning.interrogations (  
  id uuid primary key,  
  problem\_id uuid not null references reasoning.problems(id),  
  interrogation\_kind text not null,      \-- initial, followup, contradiction, pressure\_test  
  questions jsonb not null,              \-- ordered high-leverage questions  
  rationale jsonb not null default '{}',  
  generated\_at timestamptz not null default now()  
);

## **`reasoning.decision_briefs`**

create table reasoning.decision\_briefs (  
  id uuid primary key,  
  problem\_id uuid not null references reasoning.problems(id),  
  classification text,  
  summary text,  
  key\_unknowns jsonb not null default '\[\]',  
  blind\_spots jsonb not null default '\[\]',  
  risks jsonb not null default '\[\]',  
  relevant\_lens\_pack\_ids uuid\[\] not null default '{}',  
  recommendation\_summary text,  
  confidence numeric(5,4),  
  generated\_at timestamptz not null default now()  
);

## **`reasoning.option_paths`**

create table reasoning.option\_paths (  
  id uuid primary key,  
  decision\_brief\_id uuid not null references reasoning.decision\_briefs(id),  
  option\_label text not null,            \-- conservative, aggressive, asymmetric  
  description text not null,  
  expected\_upside text,  
  expected\_downside text,  
  reversibility text,  
  risk\_score numeric(6,3),  
  recommendation\_rank int,  
  created\_at timestamptz not null default now()  
);

## **`reasoning.contradiction_reports`**

create table reasoning.contradiction\_reports (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  problem\_id uuid references reasoning.problems(id),  
  contradiction\_kind text not null,      \-- narrative\_vs\_behavior, physiology\_vs\_claim, vector\_vs\_action  
  description text not null,  
  evidence jsonb not null default '\[\]',  
  severity numeric(6,3),  
  created\_at timestamptz not null default now()  
);

---

# **11\. Execution schema: Schrödinger, re-entry, traces**

This is the action layer.

## **`execution.state_estimates`**

create table execution.state\_estimates (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  thread\_id uuid references vector\_ctrl.threads(id),  
  state\_kind text not null,              \-- recover, preserve, orient, clarify, execute, etc.  
  confidence numeric(5,4) not null,  
  contributing\_factors jsonb not null default '\[\]',  
  generated\_at timestamptz not null default now()  
);

## **`execution.blocker_estimates`**

create table execution.blocker\_estimates (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  thread\_id uuid references vector\_ctrl.threads(id),  
  blocker\_kind text not null,  
  confidence numeric(5,4) not null,  
  supporting\_evidence jsonb not null default '\[\]',  
  generated\_at timestamptz not null default now()  
);

## **`execution.reentry_artifacts`**

create table execution.reentry\_artifacts (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  thread\_id uuid not null references vector\_ctrl.threads(id),  
  last\_completed\_step text,  
  unresolved\_edge text,  
  next\_smallest\_move text,  
  trap\_to\_avoid text,  
  relevant\_context jsonb not null default '{}',  
  freshness\_score numeric(6,3),  
  created\_at timestamptz not null default now(),  
  superseded\_by uuid references execution.reentry\_artifacts(id)  
);

## **`execution.policy_decisions`**

This is the actual Schrödinger output record.

create table execution.policy\_decisions (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  thread\_id uuid references vector\_ctrl.threads(id),  
  problem\_id uuid references reasoning.problems(id),  
  state\_estimate\_id uuid references execution.state\_estimates(id),  
  blocker\_estimate\_id uuid references execution.blocker\_estimates(id),  
  mode text not null,                    \-- recover, preserve, re-enter, clarify, ask, execute, close\_loop, review  
  intervention\_kind text not null,  
  action\_depth text not null,            \-- tiny, narrow, moderate, deep  
  next\_move text not null,  
  rationale text,  
  confidence numeric(5,4),  
  caution\_flags jsonb not null default '\[\]',  
  created\_at timestamptz not null default now()  
);

## **`execution.traces`**

create table execution.traces (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  thread\_id uuid references vector\_ctrl.threads(id),  
  policy\_decision\_id uuid references execution.policy\_decisions(id),  
  trace\_kind text not null,              \-- action, question, preserve, recovery, closure  
  action\_taken text,  
  outcome text,  
  truth\_revealed text,  
  next\_edge text,  
  completion\_score numeric(6,3),  
  subjective\_after jsonb not null default '{}',  
  created\_at timestamptz not null default now()  
);

## **`execution.closures`**

create table execution.closures (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  thread\_id uuid not null references vector\_ctrl.threads(id),  
  closure\_type text not null,            \-- complete, archive, pause, merge  
  summary text,  
  lessons jsonb not null default '\[\]',  
  created\_at timestamptz not null default now()  
);

---

# **12\. Review and calibration schema**

This is the immune system.

## **`execution.review_sessions`**

create table execution.review\_sessions (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  review\_scope text not null,            \-- micro, daily, weekly, monthly  
  started\_at timestamptz not null,  
  completed\_at timestamptz,  
  summary text,  
  metadata jsonb not null default '{}'  
);

## **`execution.rule_promotions`**

create table execution.rule\_promotions (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  rule\_id uuid references aether.rules(id),  
  source\_trace\_ids uuid\[\] not null default '{}',  
  promotion\_reason text,  
  created\_at timestamptz not null default now()  
);

## **`execution.pattern_updates`**

create table execution.pattern\_updates (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  pattern\_id uuid references aether.patterns(id),  
  supporting\_trace\_ids uuid\[\] not null default '{}',  
  recurrence\_delta int not null default 1,  
  created\_at timestamptz not null default now()  
);

## **`execution.calibration_records`**

create table execution.calibration\_records (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  policy\_decision\_id uuid references execution.policy\_decisions(id),  
  predicted\_outcome text,  
  actual\_outcome text,  
  calibration\_error numeric(6,3),  
  lesson text,  
  created\_at timestamptz not null default now()  
);

## **`execution.physiology_calibrations`**

Critical for personal WHOOP learning.

create table execution.physiology\_calibrations (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  feature\_date date not null,  
  physiology\_summary jsonb not null,  
  realized\_capacity\_score numeric(6,3),  
  work\_type text,                        \-- deep, narrow, admin, recovery, exploratory  
  mismatch\_score numeric(6,3),  
  lesson text,  
  created\_at timestamptz not null default now()  
);

This is how Utopia learns that low recovery may still permit narrow deterministic work, while open-ended work collapses.

---

# **13\. AI orchestration schema**

If this is a serious private system, you need auditability around model behavior.

## **`system.model_providers`**

create table system.model\_providers (  
  id uuid primary key,  
  provider text not null unique,  
  capability\_profile jsonb not null,  
  active boolean not null default true,  
  created\_at timestamptz not null default now()  
);

## **`system.model_runs`**

create table system.model\_runs (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  provider text not null,  
  model\_name text not null,  
  task\_kind text not null,               \-- extraction, routing, reasoning, compression  
  input\_object\_kind text,  
  input\_object\_id uuid,  
  output\_object\_kind text,  
  output\_object\_id uuid,  
  latency\_ms int,  
  prompt\_tokens int,  
  completion\_tokens int,  
  cache\_hit boolean,  
  success boolean not null,  
  error\_text text,  
  created\_at timestamptz not null default now()  
);

## **`system.retrieval_runs`**

create table system.retrieval\_runs (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  query\_text text not null,  
  query\_kind text not null,              \-- problem, reentry, lens, contradiction  
  retrieved\_objects jsonb not null,  
  created\_at timestamptz not null default now()  
);

## **`system.event_log`**

create table system.event\_log (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  event\_type text not null,  
  aggregate\_kind text,  
  aggregate\_id uuid,  
  payload jsonb not null,  
  occurred\_at timestamptz not null default now()  
);

## **`system.outbox_events`**

For reliable async processing.

create table system.outbox\_events (  
  id uuid primary key,  
  event\_type text not null,  
  aggregate\_kind text,  
  aggregate\_id uuid,  
  payload jsonb not null,  
  created\_at timestamptz not null default now(),  
  processed\_at timestamptz  
);

---

# **14\. Vector / embedding schema**

Use this only for semantic recall, not as truth storage.

## **`vector.embeddings`**

create table vector.embeddings (  
  id uuid primary key,  
  operator\_id uuid not null references core.operators(id),  
  object\_kind text not null,             \-- source\_chunk, concept, rule, case, brief, trace  
  object\_id uuid not null,  
  embedding vector(1536),                \-- or chosen dimension  
  model\_name text not null,  
  created\_at timestamptz not null default now()  
);

Index with HNSW or IVF depending on scale.  
For a private system, HNSW is usually fine.

---

# **15\. Materialized views / derived read models**

You should not compute everything on the fly.

I would create these derived views:

## **`execution.current_thread_state_mv`**

Current effective state per active thread.

Contains:

* last state estimate  
* last blocker  
* last touch  
* re-entry risk  
* current next edge  
* last policy decision

## **`physiology.daily_capacity_mv`**

Daily physiology summary.

Contains:

* latest recovery  
* latest sleep summary  
* derived fragility risk  
* depth ceiling  
* recent strain carryover

## **`vector.active_focus_mv`**

What matters now.

Contains:

* active season  
* active missions  
* neglected high-value threads  
* drift candidates

## **`reasoning.latest_briefs_mv`**

Latest problem-room outputs.

Contains:

* open problem  
* classification  
* key unknowns  
* current recommendation  
* unresolved questions

These views make the product fast and legible.

---

# **16\. Recommended indexes**

At minimum:

* `(operator_id, created_at desc)` on almost every append-heavy table  
* `unique` on provider object IDs  
* `btree` on active status columns  
* `gin` on JSONB fields that need querying  
* vector index on embeddings  
* `(thread_id, created_at desc)` on traces, policy decisions, checkins  
* `(feature_date, feature_name)` on physiology features  
* `(problem_id)` on all reasoning children  
* `(source_id)` on all extraction children

For event tables:

* `(processing_status, received_at)`  
* `(event_type, occurred_at desc)`

---

# **17\. Data lifecycle and retention**

A serious private system needs explicit retention policy.

## **Hot operational data**

Keep immediately accessible:

* active missions  
* active threads  
* latest states  
* latest recoveries  
* recent traces  
* current re-entry artifacts  
* active rules

## **Warm memory**

Frequently retrievable but not in the cockpit:

* past decision briefs  
* old traces  
* historical patterns  
* old problems  
* lens-pack history

## **Cold archive**

Store encrypted and compressed:

* raw source payloads  
* old webhook bodies  
* raw import snapshots  
* superseded extraction runs

Do not delete what might matter for calibration, but do aggressively archive what should not clutter runtime.

---

# **18\. What the actual core aggregates are**

If I compress the entire schema into true product aggregates, they are:

## **Directional aggregates**

* LifeArc  
* Season  
* Mission  
* Thread

## **Evidence aggregates**

* SubjectiveCheckin  
* BehaviorEvent  
* ContextSnapshot  
* PhysiologyDay

## **Knowledge aggregates**

* Source  
* Extraction  
* Concept  
* Mechanism  
* Rule  
* LensPack  
* Case  
* Pattern

## **Reasoning aggregates**

* Problem  
* ProblemStructure  
* Interrogation  
* DecisionBrief  
* OptionPath

## **Execution aggregates**

* StateEstimate  
* BlockerEstimate  
* ReentryArtifact  
* PolicyDecision  
* Trace  
* Closure

## **Learning aggregates**

* ReviewSession  
* CalibrationRecord  
* PhysiologyCalibration  
* RulePromotion  
* PatternUpdate

## **System aggregates**

* OAuthConnection  
* WebhookReceipt  
* ModelRun  
* RetrievalRun  
* EventLog

That is the serious internal shape.

---

# **19\. The most important non-obvious design choice**

The most important design choice is this:

**Do not store only conclusions. Store the chain between evidence, inference, policy, and outcome.**

That means for every serious recommendation, you want to be able to recover:

* what evidence existed  
* what state was inferred  
* what blocker was inferred  
* which rules/lenses were retrieved  
* what policy was selected  
* what action was actually taken  
* what happened afterward  
* what got updated

That chain is the real moat.

Because that is how Utopia compounds judgment instead of becoming a smart-looking black box.

---

# **20\. If I had to reduce this to the minimum serious v1 schema**

If you want the smallest schema that is still architecturally correct, build these first:

**core**

* operators  
* oauth\_connections

**vector\_ctrl**

* seasons  
* missions  
* threads

**evidence**

* subjective\_checkins  
* behavior\_events  
* context\_snapshots

**physiology**

* whoop\_recoveries  
* whoop\_sleeps  
* physiology\_features

**aether**

* sources  
* extractions  
* concepts  
* mechanisms  
* rules  
* lens\_packs  
* edges

**reasoning**

* problems  
* problem\_structures  
* interrogations  
* decision\_briefs  
* option\_paths

**execution**

* state\_estimates  
* blocker\_estimates  
* reentry\_artifacts  
* policy\_decisions  
* traces  
* calibration\_records

**system**

* model\_runs  
* webhook\_receipts  
* event\_log

That is enough to build a real Utopia, not a toy.

---

# **21\. Final compression**

The database for Utopia should not look like “notes \+ tasks \+ embeddings.”

It should look like a **typed cognitive architecture**:

* Vector stores what matters  
* Evidence stores what is true about the moment  
* Physiology stores body-state priors, including WHOOP recovery/sleep/cycle/workout-derived signals and webhook events. ([WHOOP for Developers](https://developer.whoop.com/api/))  
* Aether stores durable truth and extracted intelligence  
* Reasoning stores problem structures and decision artifacts  
* Execution stores state, blockers, policy, re-entry, and traces  
* Review stores calibration and learning  
* System tables store orchestration, integrations, and audit

That is the serious private system as a whole.

The next correct step is to turn this into:

1. exact enum definitions,  
2. Pydantic or TypeScript domain models,  
3. SQL migration files,  
4. event contracts,  
5. and the service boundaries for the API.

