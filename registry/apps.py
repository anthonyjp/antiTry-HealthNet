from django.apps import AppConfig
from django.db import migrations
import sys


class RegistryConfig(AppConfig):
    name = 'registry'

    def ready(self):
        if not getattr(migrations, 'MIGRATION_OPERATION_IN_PROGRESS', False) \
                and 'makemigrations' not in sys.argv and 'migrate' not in sys.argv:
            from registry.utility.parsing import parse_conditions
            parse_conditions('conditions.xml')
