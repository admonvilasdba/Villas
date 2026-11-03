from urllib.parse import quote

from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
from storages.utils import clean_name


class SupabaseS3Storage(S3Boto3Storage):
    """Storage compatible con Supabase S3. Mantiene compatibilidad con URLs antiguas."""

    location = 'dishes'
    file_overwrite = False
    default_acl = None
    querystring_auth = False

    def url(self, name):
        if name and (name.startswith('http://') or name.startswith('https://')):
            return name

        public_url = getattr(settings, 'SUPABASE_STORAGE_PUBLIC_URL', '')
        if public_url:
            key = self._normalize_name(clean_name(name))
            return f'{public_url.rstrip("/")}/{quote(key, safe="/")}'

        return super().url(name)
