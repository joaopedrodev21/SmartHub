"""
Cria (ou atualiza) o superusuário administrador a partir das variáveis
de ambiente DJANGO_ADMIN_USERNAME, DJANGO_ADMIN_PASSWORD e DJANGO_ADMIN_EMAIL.

Uso:
    python manage.py create_admin

Ideal para rodar no Shell do Render (ou como comando do deploy) logo após
as migrações, para garantir acesso ao /admin em produção.
"""
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Cria ou atualiza o superusuário a partir das variáveis de ambiente.'

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.getenv('DJANGO_ADMIN_USERNAME')
        password = os.getenv('DJANGO_ADMIN_PASSWORD')
        email = os.getenv('DJANGO_ADMIN_EMAIL', '')

        if not username or not password:
            self.stderr.write(self.style.ERROR(
                'Variáveis DJANGO_ADMIN_USERNAME e DJANGO_ADMIN_PASSWORD '
                'são obrigatórias (defina-as no ambiente ou no .env).'
            ))
            raise SystemExit(1)

        user, created = User.objects.update_or_create(
            username=username,
            defaults={
                'email': email,
                'is_staff': True,
                'is_superuser': True,
            },
        )
        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(
                f'Superusuário "{username}" criado com sucesso.'
            ))
        else:
            self.stdout.write(self.style.WARNING(
                f'Superusuário "{username}" já existia — senha e dados atualizados.'
            ))
