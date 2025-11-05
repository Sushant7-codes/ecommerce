from django.core.management.base import BaseCommand
from accounts.models import CustomUser


class Command(BaseCommand):
    help = "Seed staff"

    def handle(self, *args, **kwargs):
        
        self.stdout.write(self.style.SUCCESS("Seed staff"))
        
        for i in range(100):
            CustomUser.objects.create_user(
                username=f"staff{i}",
                first_name=f"staff{i}",
                last_name=f"staff{i}",
                email=f"staff{i}@localhost",
                address=f"staff{i} address",
                phone_number="1234567890",
                password="password1",
                role=CustomUser.Roles.STAFF,
            )
        
        self.stdout.write(self.style.SUCCESS("Staff seeded"))