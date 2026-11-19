# Architecture / Arxitektura

Browser -> nginx -> Gunicorn / Django -> PostgreSQL. Redis/Celery services are provisioned for async expansion. Django views provide bilingual server-rendered UI; DRF routers provide `/api/v1/` JSON CRUD. Data is keyed by project, including knowledge chunks and conversations; APIs are restricted to superadmin for this MVP. Meta is an explicit disabled provider and has no outbound authorization. Gemini only operates on bounded, retrieved project-specific reference snippets and is invoked inside the admin testing endpoint.

## Data entities

Project <- ProjectKnowledge <- KnowledgeChunk
Project <- AIConfiguration / SalesPlaybook / AITrainingTest
Project <- Prospect <- Conversation <- Message
Project <- Campaign <- CampaignActivity -> Prospect
Project <- Lead -> Prospect
Conversation <- Handoff
Project <- AIUsage / IntegrationAccount / OptOutRecord
Project <- AuditLog

## Known gaps

No production migration scripts, pgvector embedding, independent claim verifier, robust asynchronous extraction, real Meta OAuth, official messages, structured lead import, full frontend per-entity editor, or user/operator ACL in this version. Database backups, TLS, monitoring and deployment secrets need production configuration.

The local index stores hashed word and character-trigram vectors per chunk. Search combines cosine similarity with literal term matches within the selected project. This works offline and needs no additional database extension. It does not learn semantic equivalence or translate between languages. Larger deployments can move the vector storage and nearest-neighbor lookup to pgvector. Files uploaded before vector storage was introduced are embedded on read until reprocessed.
