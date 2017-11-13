import os

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/


STATIC_URL = os.environ.get('STATIC_URL', '/static/')
GS_BUCKET_NAME = os.environ.get('GS_BUCKET_NAME')
GS_PROJECT_ID = os.environ.get('GS_PROJECT_ID')
STATICFILES_STORAGE = os.environ.get('STATICFILES_STORAGE', 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage')
