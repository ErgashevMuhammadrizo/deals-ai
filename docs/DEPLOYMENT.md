# Deployment readiness

1. Create `.env` with unique secrets and correct domain/CSRF origins.
2. Apply committed migrations after verifying a restore on a staging copy.
3. Install valid TLS, verify correct proxy forwarding and set `SECURE_SSL_REDIRECT=true` and `ENABLE_HSTS=true` only once TLS is validated.
4. Enable tested backups and perform a restore rehearsal for PostgreSQL/media volumes.
5. Run Django checks and migrations in staging; run test suite and manual workflow from PROJECT_PLAN.md.
6. Add isolated file scanning, monitoring, alerts and server-side provider quota controls.
7. Only then consider enabling public traffic. Real Meta integration requires official permissions and separate verification.
