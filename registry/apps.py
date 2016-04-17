from django.apps import AppConfig
from django.db import migrations


class RegistryConfig(AppConfig):
    name = 'registry'

    def ready(self):
        if not getattr(migrations, 'MIGRATION_OPERATION_IN_PROGRESS', False):
            from registry.utility.parsing import parse_conditions
            parse_conditions('conditions.xml')
