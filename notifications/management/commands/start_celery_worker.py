from django.core.management.base import BaseCommand
from django.conf import settings
import subprocess
import sys


class Command(BaseCommand):
    help = 'Start Celery worker for notifications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--queue',
            type=str,
            default='notifications',
            help='Queue name to process (default: notifications)'
        )
        parser.add_argument(
            '--concurrency',
            type=int,
            default=2,
            help='Number of worker processes (default: 2)'
        )
        parser.add_argument(
            '--loglevel',
            type=str,
            default='info',
            choices=['debug', 'info', 'warning', 'error'],
            help='Log level (default: info)'
        )

    def handle(self, *args, **options):
        queue = options['queue']
        concurrency = options['concurrency']
        loglevel = options['loglevel']

        self.stdout.write(
            self.style.SUCCESS(
                f'Starting Celery worker for queue: {queue} with {concurrency} processes'
            )
        )

        try:
            # Start Celery worker
            cmd = [
                'celery', '-A', 'orderflow', 'worker',
                '-Q', queue,
                '-l', loglevel,
                '--concurrency', str(concurrency)
            ]
            
            subprocess.run(cmd, check=True)
            
        except subprocess.CalledProcessError as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to start Celery worker: {e}')
            )
            sys.exit(1)
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('Celery worker stopped by user')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Unexpected error: {e}')
            )
            sys.exit(1)

