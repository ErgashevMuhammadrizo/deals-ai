# Ma’lumotlar bazasi
core/0001_initial asosiy savdo jadvallarini, core/0002_chunkvector esa hujjat bo‘laklari vektorlarini yaratadi. Yangi o‘rnatishda migrate yetarli. Avvalgi ZIP --run-syncdb bilan jadval yaratgan bo‘lsa, bazaning va media papkasining nusxasini oling. Sxema 0001 bilan mosligini nusxada tekshirgandan so‘ng migrate --fake-initial ishlating. Django bu rejimda barcha ustun turlarining mosligini tekshirmaydi.

Project → ProjectKnowledge → KnowledgeChunk → ChunkVector. Project → Prospect → Conversation → Message/Handoff. Project → Campaign → CampaignActivity. Project → Lead, AIConfiguration, SalesPlaybook, AITrainingTest va AIUsage. PostgreSQL ishchi muhit uchun, SQLite lokal tekshiruv uchun.
