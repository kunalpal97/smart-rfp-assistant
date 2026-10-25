# ProposIQ — Backend

**AI-Powered Proposal Intelligence Platform**

ProposIQ is a full-stack Request for Proposal (RFP) intelligence application that helps teams manage reference documents, retrieve relevant organizational knowledge, and generate evidence-backed proposal responses.

This directory contains the **FastAPI backend**, which manages document ingestion, retrieval-augmented generation (RAG), RFP workflows, authentication, authorization, and persistent application data.

The backend uses a **provider-based architecture** that supports local development services and provides integration paths for Azure cloud services.

## 1. Overview

ProposIQ provides a centralized API for:

- Uploading, processing, listing, and deleting reference documents.
- Extracting text and structured document content.
- Retrieving relevant knowledge through keyword, vector, or hybrid retrieval.
- Generating AI-assisted answers with supporting citations.
- Managing RFP-related workflows.
- Saving, searching, and deleting generated answer history.
- Providing dashboard statistics and authenticated user information.
- Enforcing authentication and role-based access controls.

The React frontend communicates with the backend through REST APIs. External AI services, document storage, search indexes, and database operations remain behind the backend.

## 2. Technology Stack

The application supports different service providers depending on the environment.

| Component | Local development configuration | Azure / cloud option |
|---|---|---|
| API framework | FastAPI | FastAPI hosted on Azure |
| LLM | Groq | Azure OpenAI |
| Embeddings | Sentence Transformers | Azure OpenAI embeddings |
| Document extraction | PyPDF | Azure Document Intelligence |
| File storage | Local filesystem | Azure Blob Storage |
| Vector / search storage | ChromaDB | Azure AI Search |
| Relational database | PostgreSQL | Azure Database for PostgreSQL |
| Authentication | Microsoft Entra ID | Microsoft Entra ID |
| ORM | SQLAlchemy | SQLAlchemy |
| Data validation | Pydantic | Pydantic |

**Current `.env` selection:** Groq, local embeddings, PyPDF, local file storage, ChromaDB, and PostgreSQL.

The repository also contains Azure integrations and alternative retrieval implementations. Provider availability does not automatically establish that every configuration has been fully tested.

## 3. System Architecture

```text
                       USER
                        |
                        v
                React Frontend
                        |
                Bearer Access Token
                        |
                        v
                 FastAPI Backend
                        |
               Authentication Layer
                Microsoft Entra ID
                        |
                Permission / RBAC
                        |
                        v
                    API Routes
                        |
          +-------------+-------------+
          |             |             |
          v             v             v
      Documents      Questions      RFPs
          |             |             |
          v             v             v
       Ingestion    RAG Pipeline   RFP Services
          |             |
          v             v
      Extraction     Retrieval
          |             |
          v             v
      File Storage   Vector / Search Store
          |             |
          |             v
          |         LLM Generation
          |             |
          |             v
          |       Answer + Citations
          |             |
          +-------------+-------------+
                        |
                        v
                    PostgreSQL
             Metadata / History / Stats
```

### Architectural layers

| Layer | Responsibility |
|---|---|
| API | HTTP endpoints, dependencies, request handling |
| Core | Configuration, security, permissions, logging, exceptions |
| Schemas | Request and response validation |
| Services | Business logic, ingestion, retrieval, generation |
| Integrations | External AI, embedding, extraction, and storage providers |
| Storage | Database repositories, document registry, vector/search stores |
| Utilities | Chunking, citation formatting, content normalization |

The separation allows provider implementations to change without requiring the frontend to directly interact with external services.

## 4. Project Structure

The following structure reflects the backend files present in the repository.

```text
backend/
└── app/
    ├── main.py
    │
    ├── api/
    │   ├── dependencies.py
    │   └── routes/
    │       ├── dashboard.py
    │       ├── documents.py
    │       ├── health.py
    │       ├── history.py
    │       ├── questions.py
    │       ├── rfps.py
    │       └── users.py
    │
    ├── core/
    │   ├── config.py
    │   ├── exceptions.py
    │   ├── logging.py
    │   ├── permissions.py
    │   └── security.py
    │
    ├── integrations/
    │   ├── azure_blob.py
    │   ├── azure_document_intelligence.py
    │   ├── azure_embeddings.py
    │   ├── azure_openai.py
    │   ├── document_intelligence.py
    │   ├── embedding_factory.py
    │   ├── groq_client.py
    │   ├── llm_factory.py
    │   └── local_embeddings.py
    │
    ├── schemas/
    │   ├── dashboard.py
    │   ├── document.py
    │   ├── history.py
    │   ├── question.py
    │   ├── response.py
    │   └── user.py
    │
    ├── services/
    │   ├── azure_search_retrieval.py
    │   ├── document_service.py
    │   ├── evidence_assessment.py
    │   ├── generation.py
    │   ├── history_service.py
    │   ├── hybrid_retrieval.py
    │   ├── ingestion.py
    │   ├── keyword_retrieval.py
    │   ├── rag.py
    │   ├── retrieval.py
    │   ├── rfp_extraction.py
    │   └── rfp_service.py
    │
    ├── storage/
    │   ├── azure_search_store.py
    │   ├── dashboard_repository.py
    │   ├── database.py
    │   ├── db_engine.py
    │   ├── document_registry.py
    │   ├── file_storage.py
    │   ├── history_repository.py
    │   ├── models.py
    │   ├── structured_content_repository.py
    │   └── vector_store.py
    │
    └── utils/
        ├── chunking.py
        ├── citations.py
        ├── content_normalizer.py
        ├── content_types.py
        └── structured_content.py
```

Python package `__init__.py` files are omitted for readability.

## 5. Application Workflows

### 5.1 Document ingestion

When a user uploads a reference document, the backend processes it into retrievable knowledge.

```text
          User uploads document
                    |
                    v
       POST /api/documents/upload
                    |
                    v
          Validate request
          + authenticate user
                    |
                    v
             Store document
          Local / Azure Blob
                    |
                    v
           Extract document
       PyPDF / Document Intelligence
                    |
                    v
        Normalize extracted content
                    |
                    v
          Chunk document content
                    |
                    v
          Generate embeddings
        Local / Azure OpenAI
                    |
                    v
         Index searchable content
        ChromaDB / Azure AI Search
                    |
                    v
        Persist document metadata
                    |
                    v
          Return upload result
```

**Key implementation areas:** `services/ingestion.py`, `services/document_service.py`, `utils/chunking.py`, `utils/content_normalizer.py`, `integrations/`, and `storage/`.

The exact order of storage and processing operations, along with rollback behavior, depends on the ingestion implementation.

### 5.2 AI question answering

The RAG pipeline uses retrieved document evidence to support generated responses.

```text
             User asks question
                      |
                      v
         POST /api/questions/ask
                      |
                      v
           Authentication + validation
                      |
                      v
               Query processing
                      |
                      v
                Retrieval layer
          Keyword / Vector / Hybrid
                      |
                      v
             Relevant document chunks
                      |
                      v
              Evidence assessment
                      |
                      v
                LLM generation
              Groq / Azure OpenAI
                      |
                      v
           Answer + Source Citations
                      |
             +--------+--------+
             |                 |
             v                 v
       React Frontend     PostgreSQL History
```

**Key implementation areas:** `services/rag.py`, `services/retrieval.py`, `services/hybrid_retrieval.py`, `services/evidence_assessment.py`, `services/generation.py`, and `utils/citations.py`.

The objective is to generate responses using retrieved organizational knowledge while preserving source traceability.

### 5.3 Saved answer history

Previously generated answers are stored in PostgreSQL and can be retrieved without rerunning the generation pipeline.

```text
         Generated Answer
                |
                v
       History Service
                |
                v
       History Repository
                |
                v
          PostgreSQL
                |
       +--------+---------+
       |        |         |
       v        v         v
     Search   Retrieve   Delete
              Detail
```

History supports text search, source-based filtering, sorting, pagination, statistics, and individual record deletion.

## 6. API Reference

FastAPI provides interactive OpenAPI documentation at:

```text
http://127.0.0.1:8000/docs
```

### Verified application endpoints

These routes are visible in the supplied Swagger interface or confirmed from the History route implementation.

| Module | Method | Endpoint | Functionality |
|---|---|---|---|
| Health | GET | `/health` | Application health check |
| Root | GET | `/` | Root endpoint |
| Questions | POST | `/api/questions/ask` | Submit a question to the AI Assistant |
| Documents | POST | `/api/documents/upload` | Upload a document |
| Documents | GET | `/api/documents` | List documents |
| Documents | DELETE | `/api/documents/{document_id}` | Delete a document |
| Users | GET | `/api/users/me` | Retrieve authenticated user profile |
| History | GET | `/api/history` | List, search, filter, and paginate answers |
| History | GET | `/api/history/stats` | Retrieve history statistics |
| History | GET | `/api/history/{history_id}` | Retrieve a saved answer |
| History | DELETE | `/api/history/{history_id}` | Delete a saved answer |

The repository also includes `dashboard.py` and `rfps.py`. Their exact endpoint paths and request methods should be taken from their route decorators rather than inferred from filenames.

### History API example

```http
GET /api/history?limit=10&offset=0&search=security&source_filter=with_sources&sort=newest
Authorization: Bearer <access-token>
```

Response structure:

```json
{
  "items": [],
  "total": 0,
  "limit": 10,
  "offset": 0
}
```

| Parameter | Description |
|---|---|
| `limit` | Page size, 1–100 |
| `offset` | Pagination offset |
| `search` | Search saved questions and answers |
| `source_filter` | `all`, `with_sources`, `without_sources` |
| `sort` | `newest`, `oldest` |

The History API uses authenticated tenant and user identifiers for ownership filtering.

## 7. Authentication and Role-Based Access Control

ProposIQ uses **Microsoft Entra ID** for identity and authentication.

The backend contains dedicated security and permission modules:

- `core/security.py` — authentication and user identity handling.
- `core/permissions.py` — route-level permission dependencies.
- `api/dependencies.py` — shared API dependencies.

### Authentication flow

```text
             User signs in
                    |
                    v
           Microsoft Entra ID
                    |
                    v
          Frontend receives token
                    |
                    v
          Authorization: Bearer
                    |
                    v
              FastAPI Security
                    |
                    v
           Validate access token
                    |
                    v
           Resolve user identity
                    |
                    v
            Permission checks
                    |
             +------+------+
             |             |
             v             v
          Allowed        Denied
             |             |
             v             v
         API Handler    401 / 403
```

### User and admin access

The application is organized to support role-based permissions, including **User** and **Admin** responsibilities.

| Role | Intended responsibility |
|---|---|
| User | Access permitted document, question-answering, profile, and personal history operations |
| Admin | Perform authorized administrative or management operations in addition to permitted user workflows |

**Important:** The exact permissions for each role must be verified against `core/permissions.py` and the dependencies declared on individual routes. The presence of an Admin role does not imply unrestricted access to every endpoint.

Authentication establishes identity; authorization determines which operations that identity may perform.

## 8. Data Storage

ProposIQ separates document files, searchable knowledge, and relational application records.

| Data | Local provider | Cloud option |
|---|---|---|
| Uploaded document files | Local filesystem | Azure Blob Storage |
| Document embeddings / search index | ChromaDB | Azure AI Search |
| Document metadata | PostgreSQL-backed application storage | Azure Database for PostgreSQL |
| Saved answer history | PostgreSQL | Azure Database for PostgreSQL |

### Answer history model

The existing history model includes:

| Field | Purpose |
|---|---|
| `id` | Unique history entry |
| `tenant_id` | Tenant ownership |
| `user_id` | User ownership |
| `question` | Submitted question |
| `answer` | Generated answer |
| `sources_json` | Saved citation and evidence data |
| `created_at` | Creation timestamp |

Search indexes are used for retrieval; PostgreSQL stores application records and saved answers.

## 9. Environment Configuration

The backend uses environment-based configuration to select providers and configure external services.

### Local development example

```dotenv
# Application
APP_ENV=development
LOG_LEVEL=INFO

# Providers
LLM_PROVIDER=groq
EMBEDDING_PROVIDER=local
DOCUMENT_EXTRACTOR=pypdf
FILE_STORAGE_PROVIDER=local
VECTOR_STORE_PROVIDER=chroma

# Groq
GROQ_API_KEY=<your-groq-api-key>
GROQ_MODEL=<supported-groq-model>

# Local embeddings
LOCAL_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# ChromaDB
CHROMA_MODE=local
CHROMA_PERSIST_DIRECTORY=./storage/chroma
CHROMA_HOST=localhost
CHROMA_PORT=8001

# Application API
BACKEND_API_URL=http://127.0.0.1:8000

# Microsoft Entra ID
ENTRA_TENANT_ID=<tenant-id>
ENTRA_CLIENT_ID=<application-client-id>
ENTRA_API_AUDIENCE=<api-audience>
ENTRA_REQUIRED_SCOPE=access_as_user

# PostgreSQL
DATABASE_PROVIDER=postgresql
DATABASE_URL=<postgresql-connection-url>
```

The example reflects the provider choices in the supplied configuration. Use a valid, currently supported Groq model identifier.

### Azure integration variables

The backend also defines configuration for Azure integrations:

| Service | Environment variables |
|---|---|
| Azure OpenAI | `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_API_VERSION`, `AZURE_OPENAI_CHAT_DEPLOYMENT`, `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` |
| Azure Document Intelligence | `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT`, `AZURE_DOCUMENT_INTELLIGENCE_KEY` |
| Azure Blob Storage | `AZURE_STORAGE_CONNECTION_STRING`, `AZURE_STORAGE_CONTAINER_NAME` |
| Azure AI Search | `AZURE_SEARCH_ENDPOINT`, `AZURE_SEARCH_API_KEY`, `AZURE_SEARCH_INDEX_NAME` |

Do not commit `.env` files containing credentials. Keep Azure API keys, database passwords, and other secrets exclusively in trusted backend environments.

## 10. Local Development Setup

### Prerequisites

- Python version compatible with the project dependencies.
- PostgreSQL database.
- Required provider credentials.
- Microsoft Entra ID application configuration.
- Network access to the selected external services.

### Installation

From the repository root:

```bash
cd backend

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

The installation command assumes the project maintains a `requirements.txt` file.

### Configure environment

Create the environment file supported by `core/config.py` and populate it with the required settings.

Ensure PostgreSQL is accessible and the configured document, embedding, vector-store, and LLM providers are available.

### Run the API

From the `backend/` directory:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Access the application at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

## 11. Azure Cloud Migration

The provider-based design makes it possible to replace local infrastructure with managed Azure services.

### Recommended migration mapping

| Local component | Azure replacement |
|---|---|
| Locally hosted FastAPI | Azure App Service or Azure Container Apps |
| Local file storage | Azure Blob Storage |
| PyPDF extraction | Azure Document Intelligence |
| Local embeddings | Azure OpenAI embedding deployment |
| Groq generation | Azure OpenAI chat deployment |
| ChromaDB | Azure AI Search |
| PostgreSQL | Azure Database for PostgreSQL — Flexible Server |
| Local secret configuration | Azure Key Vault |
| Local application logs | Azure Monitor / Application Insights |

### Cloud architecture

```text
                React Frontend
                       |
                       v
              Microsoft Entra ID
                       |
                       v
              FastAPI on Azure
                       |
          +------------+------------+
          |            |            |
          v            v            v
      Azure Blob    Azure AI     Azure Database
       Storage       Search      for PostgreSQL
          |            ^
          v            |
    Azure Document     |
     Intelligence      |
          |            |
          +--> Content Processing
                       |
                       v
                  Azure OpenAI
                       |
                       v
              Answer + Citations
```

### Migration considerations

Moving to Azure requires more than changing provider environment variables.

The migration should include:

1. Provisioning Azure resources and configuring identity, permissions, and networking.
2. Uploading existing documents to Azure Blob Storage.
3. Reprocessing or migrating document content into the Azure AI Search index.
4. Selecting and validating Azure OpenAI chat and embedding deployments.
5. Migrating PostgreSQL data with an appropriate backup and migration procedure.
6. Configuring production secrets, HTTPS, CORS, monitoring, and access controls.
7. Testing the complete document-upload and RAG workflow after migration.

Embeddings generated by different models are not necessarily interchangeable. Changing embedding providers may require rebuilding the vector index.

Provider values for the Azure deployment must match those actually supported by the application's configuration factories.

## 12. Security and Production Considerations

The backend should enforce the following controls:

- Validate Microsoft Entra ID access tokens for protected endpoints.
- Apply route-level permission checks for User and Admin operations.
- Scope tenant-specific and user-specific database queries appropriately.
- Keep service credentials outside source control.
- Restrict CORS to approved frontend origins.
- Use HTTPS in deployed environments.
- Avoid logging access tokens, secrets, and confidential document content.
- Apply file validation and resource limits to document uploads.
- Maintain PostgreSQL backups and monitor cloud service failures.

For production deployments, use managed secrets and monitoring, and test failure recovery across storage, extraction, retrieval, and generation services.

## 13. Testing and Validation

Validate the application through the following end-to-end scenarios:

| Workflow | Expected behavior |
|---|---|
| Authentication | Valid tokens are accepted; invalid tokens are rejected |
| Authorization | Users cannot access operations outside their permissions |
| Document upload | Document is stored, processed, and indexed |
| Document retrieval | Relevant indexed evidence can be retrieved |
| AI question answering | Answer is generated with available citations |
| Answer history | Generated answers can be saved and retrieved |
| History filters | Search, sorting, and pagination return correct results |
| History deletion | Only authorized records can be deleted |
| Provider migration | Configured provider integrations work end-to-end |

Verify Python syntax:

```bash
python -m compileall -q app
```

Use the project's configured automated test runner where available. FastAPI's `/docs` interface can be used for authenticated API testing during development.

---

**ProposIQ — Proposal Intelligence**

*Transforming organizational knowledge into evidence-backed proposal responses.*