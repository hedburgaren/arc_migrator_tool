# ARC Migrator Tool

A local, dockerized, visual data migration framework for moving business‑critical data between **ERP, CRM and e‑commerce systems** without CSV/Excel hell or cloud lock‑in.

---

## 1. Overview

**ARC Migrator Tool** is a pluggable migration engine that:

- Runs **entirely locally** (Docker / on‑prem)
- Connects to **source systems** (e.g. Zoho CRM/Books, HubSpot, Shopify, WooCommerce)
- Connects to **target systems** (e.g. Odoo, WooCommerce, Shopify)
- Lets users design **field mappings visually** (n8n/Node‑RED style UI)
- Executes migrations in **preview**, **dry‑run**, and **commit** modes
- Preserves **complete historical context** (activities, emails, invoices, notes, etc.)

Primary goal:  
Turn “spreadsheet migration hell” into a **repeatable, auditable and transparent** process.

---

## 2. Core Concepts

- **Connectors**  
  Pluggable adapters for specific systems (Zoho, Odoo, Shopify, etc.) that:
  - Discover schemas
  - Extract data (via API or exported CSV/Excel)
  - Push transformed data to target systems

- **Schema Inspection Engine**  
  Analyses source and target schemas:
  - Infers data types (string, number, date, enum candidates)
  - Detects lookup/relational candidates (columns with few unique values)
  - Builds an internal representation for mapping (models + fields)

- **Mapping Workspace (ArcFlow UI)**  
  Node‑based editor (ReactFlow-style):
  - Source fields (left), target fields (right), transform/lookup nodes (middle)
  - Users “draw edges” between fields
  - Supports 1→1, 1→N, N→1, constants, and transform chains
  - Stores mappings as versioned JSON profiles

- **Processing & Validation Engine**
  - Applies transform rules on dataframes
  - Resolves lookups (e.g. suppliers, users, categories)
  - Matches or creates related records
  - Validates required fields & constraints before import

- **Execution & Logging**
  - **Preview**: counts, sample records, warnings
  - **Dry run**: generate import datasets without writing to target
  - **Commit**: push to target (API/CSV) and create rollback bundles
  - Detailed logs & audit trail per migration run

---

## 3. Full-History CRM/ERP Migration Mode

Specialized mode for scenarios like **Zoho → Odoo** where the priority is **complete history**, not just current master data.

- **Record‑centric view**  
  For a given account/partner, show:
  - Contacts, deals, tasks, calls, emails, notes, documents
  - Invoices, payments, balances (from CRM + Books)
  - “Before” (source system view) vs “After” (simulated target view)

- **History Profiles**
  - Configurable profiles that define:
    - Which source modules are treated as “history” (e.g. tasks, events, deal stage logs, invoices)
    - How they map to target entities (e.g. Odoo `mail.message`, `mail.activity`, `account.move`, etc.)

- **Interactive lookup resolution**
  - When a column looks like a lookup list (few unique values), the engine prompts:
    - “Create new target records?”
    - “Match to existing records?”
    - “Ignore / map to constant?”

- **Excel‑free workflow**
  - Users configure and iterate mappings in the visual UI
  - Output is ready‑to‑import CSVs or direct API calls, **no manual Excel massaging required**

---

## 4. High-Level Architecture

- **Frontend (UI)**
  - React + ReactFlow (or similar)
  - Node‑based mapping workspace
  - Project wizard (“From system?” / “To system?” / “What to migrate?”)

- **Backend**
  - Python + FastAPI
  - Pandas for dataframe operations
  - Mapping/transform engine
  - Connector abstraction layer

- **Persistence**
  - SQLite for:
    - Projects
    - Mapping profiles
    - Lookup dictionaries
    - Execution history

- **Deployment**
  - Docker (single-compose stack)
  - Everything runs locally; no external cloud services are required by design

---

## 5. Example Use Case: Zoho → Odoo (with full history)

1. **Create project**: Source = Zoho CRM/Books, Target = Odoo  
2. **Connect/extract**: API connection or CSV/Excel exports from Zoho  
3. **Inspect schemas**: Engine discovers Zoho modules & Odoo models  
4. **Configure mapping** in ArcFlow UI:
   - Accounts → `res.partner`
   - Contacts → `res.partner` (child contacts)
   - Deals → `crm.lead/opportunity`
   - Activities, calls, notes → `mail.activity` / `mail.message`
   - Invoices & payments → `account.move` and `account.payment`
5. **Resolve lookups** for owners, users, suppliers, categories  
6. **Preview & dry‑run** migration, fix conflicts  
7. **Commit** to Odoo and store an audit/rollback bundle

---

## 6. Project Backlog Structure (Epics, Stories, Tasks)

> Suggested GitHub issue hierarchy.  
> Convention:
> - Label **`type: epic`**, **`type: story`**, **`type: task`**
> - Optionally labels for area: `area:backend`, `area:frontend`, `area:connector`, etc.

### Epic 1: Core Framework & Infrastructure (`type: epic`)

**User goal:** Run ARC Migrator Tool locally in a consistent, reproducible way and support basic project management.

#### Story 1.1: Initialize project structure & base tooling (`type: story`)

- Task 1.1.1: Set up repository structure (`/backend`, `/frontend`, `/connectors`, `/docs`) (`type: task`)
- Task 1.1.2: Configure Python environment and dependency management (e.g. `poetry` or `pip + requirements.txt`) (`type: task`)
- Task 1.1.3: Configure frontend tooling (React + Vite/Next + TypeScript) (`type: task`)
- Task 1.1.4: Add basic CI checks (linting, formatting, tests) (`type: task`)

#### Story 1.2: Dockerize the stack (`type: story`)

- Task 1.2.1: Create Dockerfile for backend service (`type: task`)
- Task 1.2.2: Create Dockerfile for frontend service (`type: task`)
- Task 1.2.3: Add `docker-compose.yml` to run UI + backend + SQLite (`type: task`)
- Task 1.2.4: Document local run instructions (`README: Getting started`) (`type: task`)

---

### Epic 2: Connector Framework & Initial Connectors (`type: epic`)

**User goal:** Allow migrations between specific real systems (starting with Zoho and Odoo) via a generic connector abstraction.

#### Story 2.1: Design connector interface (`type: story`)

- Task 2.1.1: Define `ConnectorBase` interface (Python) for `get_schema`, `extract`, `push` (`type: task`)
- Task 2.1.2: Implement connector registration & discovery mechanism (`type: task`)
- Task 2.1.3: Define `metadata.json` format for connectors (`type: task`)

#### Story 2.2: Implement Zoho connector (read‑side) (`type: story`)

- Task 2.2.1: Support reading Zoho CRM via CSV exports (baseline) (`type: task`)
- Task 2.2.2: Optional: Implement Zoho CRM API extractor (`type: task`)
- Task 2.2.3: Parse Zoho modules (Accounts, Contacts, Deals, Activities) into dataframes (`type: task`)
- Task 2.2.4: Parse Zoho Books exports (Invoices, Payments, Products) into dataframes (`type: task`)

#### Story 2.3: Implement Odoo connector (write‑side) (`type: story`)

- Task 2.3.1: Implement Odoo schema discovery via `fields_get` (XML‑RPC/JSON‑RPC) (`type: task`)
- Task 2.3.2: Implement Odoo data push for core models (`res.partner`, `crm.lead`, `account.move`) (`type: task`)
- Task 2.3.3: Add CSV export mode for Odoo‑compatible imports (`type: task`)

---

### Epic 3: Schema Inspection & Mapping Model (`type: epic`)

**User goal:** Automatically understand source/target schemas and represent them in a way that supports visual mapping.

#### Story 3.1: Schema inspection engine (`type: story`)

- Task 3.1.1: Define internal `Field` and `Model` representations (name, type, stats) (`type: task`)
- Task 3.1.2: Implement type inference (string, numeric, date, enum candidates) (`type: task`)
- Task 3.1.3: Implement lookup detection based on unique value counts (`type: task`)
- Task 3.1.4: Store inspected schemas in SQLite linked to a `MigrationProject` (`type: task`)

#### Story 3.2: Mapping profile data model (`type: story`)

- Task 3.2.1: Define `MappingProfile` and `MappingEdge` models (Python + SQLite schema) (`type: task`)
- Task 3.2.2: Support 1→1, 1→N, N→1 mappings in the data model (`type: task`)
- Task 3.2.3: Add transform and lookup resolver references on mapping edges (`type: task`)

---

### Epic 4: Visual Mapping UI (ArcFlow Editor) (`type: epic`)

**User goal:** Allow users to map fields and configure transformations without touching Excel or writing code.

#### Story 4.1: Basic node‑based editor (`type: story`)

- Task 4.1.1: Integrate ReactFlow (or equivalent) in the frontend (`type: task`)
- Task 4.1.2: Render source models/fields as nodes in left column (`type: task`)
- Task 4.1.3: Render target models/fields as nodes in right column (`type: task`)
- Task 4.1.4: Allow drawing edges from source fields to target fields (`type: task`)

#### Story 4.2: Transform & lookup nodes (`type: story`)

- Task 4.2.1: Implement transform node types (concat, split, lowercase, trim, constant) (`type: task`)
- Task 4.2.2: Implement lookup node UI for value mappings (source value list → target entities) (`type: task`)
- Task 4.2.3: Persist mapping graph and node layout to backend (`type: task`)
- Task 4.2.4: Load and render existing mapping profiles into the editor (`type: task`)

---

### Epic 5: Processing, Validation & Execution (`type: epic`)

**User goal:** Run a migration end‑to‑end with preview, validation, and safe commit.

#### Story 5.1: Transformation pipeline (`type: story`)

- Task 5.1.1: Implement pipeline to apply mapping edges to source dataframes (`type: task`)
- Task 5.1.2: Implement transform rule execution (e.g. Python functions or DSL) (`type: task`)
- Task 5.1.3: Integrate lookup resolution into the pipeline (`type: task`)

#### Story 5.2: Validation and preview (`type: story`)

- Task 5.2.1: Implement required‑field validation based on target schema (`type: task`)
- Task 5.2.2: Implement conflict detection (duplicate keys, ambiguous matches) (`type: task`)
- Task 5.2.3: Build preview endpoint + UI (counts, sample rows, warnings) (`type: task`)

#### Story 5.3: Execution & logging (`type: story`)

- Task 5.3.1: Implement dry‑run mode (no writes, only simulated operations) (`type: task`)
- Task 5.3.2: Implement commit mode with per‑record result logging (`type: task`)
- Task 5.3.3: Generate rollback bundles (raw inputs + transformed outputs + mapping profile) (`type: task`)
- Task 5.3.4: Store execution history in SQLite and expose basic run list UI (`type: task`)

---

### Epic 6: Full-History CRM/ERP Migration Mode (`type: epic`)

**User goal:** Migrate **complete customer history** (activities, emails, invoices, etc.) from systems like Zoho CRM/Books to Odoo without manual Excel work.

#### Story 6.1: Record-centric history view (`type: story`)

- Task 6.1.1: Define “history entities” concept (activities, notes, emails, invoices) in the data model (`type: task`)
- Task 6.1.2: Implement backend endpoint to fetch all related records for a given account/contact (`type: task`)
- Task 6.1.3: Build UI to display “source history” vs “simulated target view” for a single customer (`type: task`)

#### Story 6.2: History Profiles (`type: story`)

- Task 6.2.1: Define `HistoryProfile` model (which modules/fields are treated as history) (`type: task`)
- Task 6.2.2: Implement mapping logic from history profile to target entities (`type: task`)
- Task 6.2.3: Expose history profile selection/configuration in the project wizard (`type: task`)

#### Story 6.3: Interactive lookup resolution for history data (`type: story`)

- Task 6.3.1: Detect lookup columns (owners, users, categories) in historical tables (`type: task`)
- Task 6.3.2: Implement guided UI dialogs for “create / match / ignore” decisions (`type: task`)
- Task 6.3.3: Persist lookup mappings and reuse them across runs (`type: task`)

---

## 7. Status

This repository currently contains:

- ✅ High-level system design  
- ✅ Planned architecture and backlog (this document)  
- ⏳ Implementation in progress

Contributions welcome – especially connectors, UI improvements, and migration profiles for specific source/target pairs.
