# API v1

All endpoints require a Django-authenticated superuser. The interactive schema is at `/api/docs/`.

`GET/POST /api/v1/projects/`; detail GET/PATCH/DELETE `/api/v1/projects/{id}/`.
`POST /api/v1/projects/{id}/approve/`, `POST /api/v1/projects/{id}/activate/`.
`GET/POST /api/v1/knowledge/` (multipart file or JSON source_text), `POST /api/v1/knowledge/{id}/reprocess/`.
`GET/POST /api/v1/ai-config/`, `/api/v1/playbooks/`.
`POST /api/v1/ai/test/` payload `{"project":1,"question":"..."}`.
`GET/POST /api/v1/prospects/`; `POST /api/v1/prospects/{id}/score/`, `/opt_out/`.
`GET/POST /api/v1/campaigns/`; `POST /api/v1/campaigns/{id}/pause/`, `/record_analysis/`.
`GET/POST /api/v1/conversations/`; `POST /api/v1/conversations/{id}/handoff/`, `/take_over/`, `/reply/`.
`GET/POST /api/v1/leads/`.
`GET /api/v1/analytics/overview/`, `/api/v1/analytics/prospects.csv`.

Project-scoped listings accept `?project=ID`. POST/PATCH operations require CSRF token for browser-based session auth. API does not transmit live Instagram messages.

GET /api/v1/analytics/prospects.xlsx exports an Excel workbook. Browser workflows include /inbox/, /prospects/import/ and /admin/core/aitrainingtest/. GET and signed POST /integrations/instagram/webhook/ handle verification and deduplicated event receipts. Receipts do not trigger live delivery.
