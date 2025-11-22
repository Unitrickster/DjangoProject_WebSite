from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from sales.models import Client, Lead
import random


class Command(BaseCommand):
    help = 'Create test leads for development'

    def handle(self, *args, **options):
        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR('No users found. Create a superuser first.'))
            return

        clients_data = [
            {'full_name': 'Иванов Иван', 'phone': '+79161234567', 'email': 'ivanov@mail.ru', 'source': 'website'},
            {'full_name': 'Петрова Анна', 'phone': '+79162345678', 'email': 'petrova@mail.ru', 'source': 'phone'},
            {'full_name': 'Сидоров Петр', 'phone': '+79163456789', 'email': 'sidorov@mail.ru', 'source': 'showroom'},
            {'full_name': 'Козлова Мария', 'phone': '+79164567890', 'email': 'kozlova@mail.ru',
             'source': 'recommendation'},
        ]

        for client_data in clients_data:
            client, created = Client.objects.get_or_create(
                phone=client_data['phone'],
                defaults=client_data
            )

            Lead.objects.get_or_create(
                client=client,
                assigned_manager=user,
                status=random.choice(['new', 'in_progress', 'presentation', 'test_drive']),
                priority=random.choice([1, 2, 3]),
                source=client.source
            )

        self.stdout.write(self.style.SUCCESS('Successfully created test leads'))