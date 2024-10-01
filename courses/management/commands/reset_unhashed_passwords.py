from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password, identify_hasher
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Reset unhashed passwords for all users'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        users = User.objects.all()

        unhashed_count = 0
        for user in users:
            try:
                # Check if the password is already hashed
                identify_hasher(user.password)
            except ValueError:
                # If it's not hashed, reset it
                unhashed_count += 1
                new_password = 'default_password123'  # Set a default password
                user.set_password(new_password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Reset password for user: {user.email}'))
        
        if unhashed_count == 0:
            self.stdout.write(self.style.SUCCESS('No unhashed passwords found.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Successfully reset {unhashed_count} passwords.'))
