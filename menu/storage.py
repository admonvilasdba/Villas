from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class SupabaseS3Storage(S3Boto3Storage):
    """Storage compatible con Supabase S3. Mantiene compatibilidad con URLs antiguas."""

    location = 'dishes'
    file_overwrite = False
    default_acl = None
    querystring_auth = False

    def url(self, name):
        if name and (name.startswith('http://') or name.startswith('https://')):
            return name
        return super().url(name)
