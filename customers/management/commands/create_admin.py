from django.core.management.base import BaseCommand
from notifications.admin_service import AdminService


class Command(BaseCommand):
    help = 'Create a new admin user'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Admin email address')
        parser.add_argument('first_name', type=str, help='First name')
        parser.add_argument('last_name', type=str, help='Last name')
        parser.add_argument('password', type=str, help='Password')
        parser.add_argument(
            '--role',
            type=str,
            default='admin',
            choices=['admin', 'super_admin', 'manager'],
            help='Admin role (default: admin)'
        )
        parser.add_argument(
            '--permissions',
            type=str,
            default='{}',
            help='JSON string of permissions'
        )

    def handle(self, *args, **options):
        email = options['email']
        first_name = options['first_name']
        last_name = options['last_name']
        password = options['password']
        role = options['role']
        permissions = options['permissions']

        try:
            # Parse permissions if provided
            import json
            if permissions:
                permissions = json.loads(permissions)
            else:
                permissions = {}

            # Create admin service
            admin_service = AdminService()

            # Create admin user
            admin = admin_service.create_admin_user(
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
                role=role,
                permissions=permissions
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created admin user: {admin.email} (Role: {admin.role})'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to create admin user: {e}')
            )
