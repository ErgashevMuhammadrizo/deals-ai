# Meta Instagram adapter contract

`apps/core/integrations/instagram/provider.py` defines `InstagramProvider.send` and the fail-closed provider. `webhooks.py` defines HMAC SHA-256 signature verification helper. This is **not** an operational Instagram API integration. OAuth flow, callback processing, webhook routing and authorized session window checks must be implemented against the current official Meta documentation before enabling any delivery. Do not use scraping or unauthorized cold DMs. `.env.example` contains future Meta configuration names with empty values.
