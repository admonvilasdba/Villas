import os

import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible

IMGBB_UPLOAD_URL = 'https://api.imgbb.com/1/upload'


@deconstructible
class ImgBBStorage(Storage):
    """Storage de Django que sube imágenes a ImgBB y guarda la URL directa."""

    def _save(self, name, content):
        api_key = getattr(settings, 'IMGBB_API_KEY', '')
        if not api_key:
            raise ImproperlyConfigured(
                'Falta IMGBB_API_KEY. Defínela en tu .env o en las variables de entorno.'
            )

        content.seek(0)
        response = requests.post(
            IMGBB_UPLOAD_URL,
            params={'key': api_key},
            files={'image': (os.path.basename(name), content.read())},
            timeout=30,
        )

        try:
            result = response.json()
        except ValueError as exc:
            raise RuntimeError(
                f'ImgBB respondió algo que no es JSON (HTTP {response.status_code}).'
            ) from exc

        if response.status_code == 200 and result.get('success') is True:
            return result['data']['url']

        raise RuntimeError(f'Error al subir la imagen a ImgBB: {result}')

    def _open(self, name, mode='rb'):
        raise NotImplementedError('ImgBBStorage no permite leer archivos.')

    def exists(self, name):
        return False

    def url(self, name):
        return name

    def delete(self, name):
        pass
