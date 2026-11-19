import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
BASE_DIR=Path(__file__).resolve().parent.parent
ROOT_DIR=BASE_DIR.parent
from dotenv import load_dotenv
load_dotenv(ROOT_DIR / ".env", override=False)
DEBUG=os.getenv('DEBUG','false').lower()=='true'
SECRET_KEY=os.getenv('DJANGO_SECRET_KEY','')
if not DEBUG and (len(SECRET_KEY)<50 or SECRET_KEY.startswith('REPLACE_')):
 raise ImproperlyConfigured('Set a unique DJANGO_SECRET_KEY of at least 50 characters in deals-ai/.env')
if not SECRET_KEY:
 if not DEBUG: raise ImproperlyConfigured('DJANGO_SECRET_KEY required when DEBUG=false')
 SECRET_KEY='DEV-ONLY-REPLACE-'+('0'*44)
ALLOWED_HOSTS=[s.strip() for s in os.getenv('ALLOWED_HOSTS','localhost,127.0.0.1').split(',') if s.strip()]
CSRF_TRUSTED_ORIGINS=[s.strip() for s in os.getenv('CSRF_TRUSTED_ORIGINS','').split(',') if s.strip()]
INSTALLED_APPS=['django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','rest_framework','drf_spectacular','apps.core']
MIDDLEWARE=['django.middleware.security.SecurityMiddleware','whitenoise.middleware.WhiteNoiseMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.locale.LocaleMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware']
ROOT_URLCONF='config.urls'
TEMPLATES=[{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[ROOT_DIR/'frontend'/'templates'],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.debug','django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages']}}]
WSGI_APPLICATION='config.wsgi.application'
DB_ENGINE=os.getenv('DB_ENGINE','postgres')
if DB_ENGINE=='sqlite':
 DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':os.getenv('SQLITE_PATH',str(BASE_DIR/'db.sqlite3'))}}
else:
 DATABASES={'default':{'ENGINE':'django.db.backends.postgresql','NAME':os.getenv('POSTGRES_DB','deals_ai'),'USER':os.getenv('POSTGRES_USER','deals'),'PASSWORD':os.getenv('POSTGRES_PASSWORD',''),'HOST':os.getenv('POSTGRES_HOST','db'),'PORT':os.getenv('POSTGRES_PORT','5432'),'CONN_MAX_AGE':60}}
AUTH_PASSWORD_VALIDATORS=[{'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},{'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator','OPTIONS':{'min_length':12}},{'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},{'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'}]
LANGUAGE_CODE='uz'
LANGUAGES=[('uz','O‘zbek'),('ru','Русский')]
TIME_ZONE='Asia/Tashkent'
USE_I18N=True
USE_TZ=True
STATIC_URL='/static/'
STATIC_ROOT=BASE_DIR/'staticfiles'
STATICFILES_DIRS=[ROOT_DIR/'frontend'/'static']
STORAGES={'default':{'BACKEND':'django.core.files.storage.FileSystemStorage'},'staticfiles':{'BACKEND':'whitenoise.storage.CompressedManifestStaticFilesStorage'}}
MEDIA_ROOT=BASE_DIR/'media'
MEDIA_URL='/media/'
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
LOGIN_URL='/login/'
LOGIN_REDIRECT_URL='/'
LOGOUT_REDIRECT_URL='/login/'
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SECURE=not DEBUG
CSRF_COOKIE_SECURE=not DEBUG
SESSION_COOKIE_SAMESITE='Lax'
SESSION_COOKIE_AGE=3600*8
SESSION_EXPIRE_AT_BROWSER_CLOSE=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_REFERRER_POLICY='strict-origin-when-cross-origin'
SECURE_SSL_REDIRECT=os.getenv('SECURE_SSL_REDIRECT','false').lower()=='true'
SECURE_HSTS_SECONDS=31536000 if os.getenv('ENABLE_HSTS','false').lower()=='true' else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS=SECURE_HSTS_SECONDS>0
X_FRAME_OPTIONS='DENY'
REST_FRAMEWORK={'DEFAULT_AUTHENTICATION_CLASSES':['rest_framework.authentication.SessionAuthentication'],'DEFAULT_PERMISSION_CLASSES':['apps.core.permissions.IsSuperAdmin'],'DEFAULT_PAGINATION_CLASS':'rest_framework.pagination.PageNumberPagination','PAGE_SIZE':25,'DEFAULT_SCHEMA_CLASS':'drf_spectacular.openapi.AutoSchema','DEFAULT_THROTTLE_CLASSES':['rest_framework.throttling.AnonRateThrottle','rest_framework.throttling.UserRateThrottle'],'DEFAULT_THROTTLE_RATES':{'anon':'10/min','user':'300/hour'}}
SPECTACULAR_SETTINGS={'TITLE':'DEALS AI API','VERSION':'1.0.0','SERVE_INCLUDE_SCHEMA':False}
CELERY_BROKER_URL=os.getenv('REDIS_URL','redis://redis:6379/0')
CELERY_RESULT_BACKEND=os.getenv('REDIS_URL','redis://redis:6379/0')
CELERY_TASK_TIME_LIMIT=180
CELERY_TASK_SOFT_TIME_LIMIT=160
FILE_UPLOAD_MAX_MEMORY_SIZE=10*1024*1024
DATA_UPLOAD_MAX_MEMORY_SIZE=12*1024*1024

from datetime import timedelta
INSTALLED_APPS.append('axes')
MIDDLEWARE.append('axes.middleware.AxesMiddleware')
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'apps.core.auth.AdminBackend',
]
AXES_FAILURE_LIMIT = 6
AXES_COOLOFF_TIME = timedelta(minutes=15)
AXES_LOCKOUT_PARAMETERS = [['username', 'ip_address']]
