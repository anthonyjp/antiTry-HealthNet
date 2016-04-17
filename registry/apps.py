from django.apps import AppConfig
from django.db.models.signals import pre_migrate, post_migrate
from django.dispatch import receiver

_is_migrating = False


@receiver(pre_migrate)
def migrate_happening(**kwargs):
    global _is_migrating
    _is_migrating = True


@receiver(post_migrate)
def migrate_ended(**kwargs):
    global _is_migrating
    _is_migrating = False


class RegistryConfig(AppConfig):
    name = 'registry'

    def ready(self):
        if not _is_migrating:
            from registry.utility.parsing import parse_conditions
            parse_conditions('conditions.xml')
        else:
            @receiver(post_migrate)
            def exec(**kwargs):
                from registry.utility.parsing import parse_conditions
                parse_conditions('conditions.xml')
