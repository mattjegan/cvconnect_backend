from cvconnect_backend.cvconnect_backend.settings import *
# Parse database configuration from $DATABASE_URL
HEROKU = True

if not os.environ.get('LOCAL', False):
    import dj_database_url
    DATABASES['default'] = dj_database_url.config()

STATIC_ROOT = 'staticfiles'