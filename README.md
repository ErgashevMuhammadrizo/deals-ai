# DEALS AI

## Noutbukda ishga tushirish

Python 3.12+ kerak. Buyruqlarni arxivdan chiqarilgan deals-ai papkasida bajaring.

1. Virtual muhit va kutubxonalarni o‘rnating.

       python3 -m venv .venv
       source .venv/bin/activate
       python -m pip install -r backend/requirements.txt
       cp .env.example .env

2. Lokal ish uchun .env ichida DEBUG=true va DB_ENGINE=sqlite belgilang. Django kalitini quyidagi buyruq bilan yarating va DJANGO_SECRET_KEY maydoniga yozing.

       python -c "import secrets; print(secrets.token_urlsafe(64))"

3. Yangi bazani tayyorlang va administrator yarating.

       python backend/manage.py check
       python backend/manage.py migrate
       python backend/manage.py createsuperuser
       python backend/manage.py runserver

4. http://127.0.0.1:8000/ manzilini oching. .env loyiha ildizidan avtomatik o‘qiladi. Avvalgi bazani o‘tkazish uchun docs/DATABASE.md ga qarang.

## Docker

.env ichida DB_ENGINE=postgres, POSTGRES_HOST=db, POSTGRES_PASSWORD va DJANGO_SECRET_KEY ni belgilang. Lokal HTTP sinov uchun DEBUG=true. Internetga chiqarishda DEBUG=false, HTTPS va o‘z domeningizga mos ALLOWED_HOSTS hamda CSRF_TRUSTED_ORIGINS kerak.

    docker compose up -d --build
    docker compose exec web python manage.py createsuperuser

Lokal manzil http://localhost:8080/.

## Savdo oqimini tekshirish

Loyiha yarating, bilimlar bazasiga fayl yoki matn qo‘shing, AI sozlamalarini saqlang va savdo strategiyasini kiriting. Gemini uchun GEMINI_API_KEY, GEMINI_MODEL hamda tanlangan modelning million token uchun kirish va chiqish narxlarini belgilang. AI sinov oynasida savol bering. Javob bilan birga ishlatilgan manbalar saqlanadi. “Javoblarni baholash” orqali testlarni ko‘rib chiqing. Django admin orqali loyiha holatini testing qiling, loyihalar jadvalidan tasdiqlang va faollashtiring.

170 ta qo‘shimcha baholash savolini yaratish uchun quyidagi buyruqdagi SLUG o‘rniga loyihangiz slugini yozing. Savollar 10 soha uchun 17 xil vaziyatdan tuzilgan. Admin testlarni beshtadan ishga tushiradi va javobni baholaydi. Ular avtomatik ravishda muvaffaqiyatli hisoblanmaydi.

    python backend/manage.py seed_sales_tests SLUG

Prospectni qo‘lda yoki CSV orqali kiriting. “Suhbatlar → Operator suhbatlari” orqali test kanalida yozishing, operatorga qabul qilish va AI’ni qayta yoqish mumkin. Hisobotlar Analitika oynasida. Instagram webhook manzili /integrations/instagram/webhook/. Jonli yetkazish uchun keyingi OAuth integratsiyasi kerak.

## Tekshiruv

    DEBUG=true DB_ENGINE=sqlite python backend/manage.py collectstatic --noinput
    DEBUG=true DB_ENGINE=sqlite python -m pytest -q

ZIP ichida real kalitlar, foydalanuvchilar bazasi va yuklangan mijoz fayllari yo‘q. Sinovlar Gemini HTTP javobini imitatsiya qiladi. PostgreSQL parallel yuklama, Docker muhiti, jonli Gemini javob sifati va Meta akkaunti alohida tekshirilishi kerak.
