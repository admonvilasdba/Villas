from decouple import config
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Crea el superusuario en producción desde las variables DJANGO_SUPERUSER_*.'

    def handle(self, *args, **options):
        username = config('DJANGO_SUPERUSER_USERNAME', default='')
        email = config('DJANGO_SUPERUSER_EMAIL', default='')
        password = config('DJANGO_SUPERUSER_PASSWORD', default='')

        if not username or not password:
            self.stdout.write(
                'create_admin: DJANGO_SUPERUSER_USERNAME/PASSWORD no definidos; se omite.'
            )
            return

        User = get_user_model()
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(
                    f'create_admin: el usuario "{username}" ya existe; no se modifica.'
                )
            )
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(
            self.style.SUCCESS(f'create_admin: superusuario "{username}" creado.')
        )
