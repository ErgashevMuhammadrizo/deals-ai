# Security status

Enabled: password hashing via Django, CSRF middleware, session-only DRF authentication, superadmin permissions, safe ORM, escaped HTML templates, security headers, no keys in browser, max 10MB document processing, no public outbound providers, project-level source filtering, opt-out record, uniqueness on external message IDs.

Not yet complete: login rate limiting with abuse monitoring, external file MIME checking, malware scanner and sandboxed document parsers, secret vault for OAuth tokens, rigorous SSRF controls for any future URL ingestion, full independent AI output verifier, audit of every read/write path, production-focused penetration tests, backup/restore validation, rate limiting per project and official Meta permission verification. Public launch is blocked on these requirements.

Production HTTPS termination and forwarded scheme must be configured and tested at the ingress. Never enable `DEBUG=true` in production. Rotate any credentials that were shared in chats or uploaded to untrusted storage.
