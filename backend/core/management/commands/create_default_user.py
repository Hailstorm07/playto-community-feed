from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Creates a default user if none exists'

    def handle(self, *args, **options):
        if not User.objects.exists():
            User.objects.create_user(username='testuser', password='testpass')
            self.stdout.write(self.style.SUCCESS('✓ Default user created'))
        else:
            self.stdout.write(self.style.WARNING('✓ Users already exist'))
