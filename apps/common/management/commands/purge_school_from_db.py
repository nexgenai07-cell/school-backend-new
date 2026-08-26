"""
FINAL step of a sharding cutover: deletes one school's rows from a database
they no longer live on.

SAFETY RULES (do not bypass):
- DRY-RUN BY DEFAULT: without --confirm this only PRINTS what would be
  deleted, per model.
- Refuses to run against the database the school currently routes to — flip
  School.database_alias first and test the new home before purging.
- Deletion happens in REVERSE FK-dependency order via raw deletes, so no
  cascade can ever reach another school's rows.
- The School row itself is NEVER deleted here (it lives on 'default' and is
  the tenant registry).

Typical flow after a verified cutover:
    python manage.py purge_school_from_db --slug=school-b --database=default            # dry run
    python manage.py purge_school_from_db --slug=school-b --database=default --confirm  # real
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import connections

from apps.tenants.models import School
from .shard_school import tenant_models_in_dependency_order


class Command(BaseCommand):
    help = ('Delete a school\'s rows from one database (dry-run unless '
            '--confirm). Only run AFTER a verified sharding cutover.')

    def add_arguments(self, parser):
        parser.add_argument('--slug', required=True,
                            help='School slug whose old rows should be removed')
        parser.add_argument('--database', default='default',
                            help='Database to purge from (default: default)')
        parser.add_argument('--confirm', action='store_true',
                            help='Actually delete. Without this flag: dry-run only.')

    def handle(self, *args, **options):
        slug = options['slug'].strip().lower()
        database = options['database']
        confirm = options['confirm']

        if database not in connections:
            raise CommandError(f"Database '{database}' is not configured.")

        try:
            school = School.objects.get(slug=slug)
        except School.DoesNotExist:
            raise CommandError(f"No school with slug '{slug}'.")

        # Hard safety gate: never purge the DB the school is actively routed to.
        current_home = school.database_alias or 'default'
        if current_home == database:
            raise CommandError(
                f"'{slug}' currently routes to '{database}'. Flip "
                f"School.database_alias to its new home and verify BEFORE "
                f"purging this database."
            )

        self.stdout.write(self.style.MIGRATE_HEADING(
            f"Purging {school.name} ({school.slug}) from '{database}' "
            f"({'CONFIRMED' if confirm else 'DRY RUN'})"
        ))

        total = 0
        skipped_empty = 0
        for model in reversed(tenant_models_in_dependency_order()):
            qs = model.all_objects.filter(school=school).using(database)
            count = qs.count()
            if count == 0:
                skipped_empty += 1
                continue
            if confirm:
                deleted = qs._raw_delete(using=database)
                self.stdout.write(f"  ✓ {model.__name__:<24} -{deleted}")
                total += deleted
            else:
                self.stdout.write(f"  · {model.__name__:<24} {count} (would delete)")

        if confirm:
            self.stdout.write(self.style.SUCCESS(
                f"\n✅ Deleted {total} rows across models "
                f"({skipped_empty} already empty) from '{database}'."
            ))
            self.stdout.write(
                "Final verification: re-run WITHOUT --confirm — every line "
                "should report 0."
            )
        else:
            self.stdout.write(self.style.WARNING(
                f"\nDRY RUN — nothing deleted. Re-run with --confirm when "
                f"you have verified everything above."
            ))
