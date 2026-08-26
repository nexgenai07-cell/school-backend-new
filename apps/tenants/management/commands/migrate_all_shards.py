"""Apply migrations to every database referenced by any School.database_alias.

Run this after EVERY deploy (or before/after a sharding cutover) so the schema
stays identical across all databases — only row-level data location differs.

Usage:
    python manage.py migrate_all_shards
"""
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connections

from apps.tenants.models import School


class Command(BaseCommand):
    help = 'Migrate every database alias referenced by any school tenant.'

    def handle(self, *args, **options):
        aliases = ['default']
        for alias in (
            School.objects
            .exclude(database_alias='default')
            .exclude(database_alias='')
            .values_list('database_alias', flat=True)
            .distinct()
        ):
            if alias not in aliases:
                aliases.append(alias)

        failures = []
        for alias in aliases:
            if alias not in connections:
                self.stdout.write(self.style.WARNING(
                    f"⚠ '{alias}' is not in DATABASES — skipped "
                    f"(is VPS_SHARD_1_URL configured?)"
                ))
                continue
            self.stdout.write(f"Migrating '{alias}'...")
            try:
                call_command('migrate', database=alias, interactive=False)
                self.stdout.write(self.style.SUCCESS(f"✓ '{alias}' up to date"))
            except Exception as exc:  # keep migrating the remaining DBs
                failures.append(alias)
                self.stdout.write(self.style.ERROR(f"✗ '{alias}' failed: {exc}"))

        if failures:
            raise SystemExit(f"Migration failed for: {', '.join(failures)}")
        self.stdout.write(self.style.SUCCESS('\nAll shard schemas are in sync.'))
