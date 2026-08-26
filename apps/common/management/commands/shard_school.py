"""
One-time data-migration tool for hybrid sharding.

Copies one school tenant's rows from its current database to a target
database alias, preserving primary keys so FK relationships stay intact.

Safety properties:
- IDEMPOTENT: uses bulk_create(update_conflicts=True) — safe to re-run after
  an interrupted copy; rows are upserted, never duplicated.
- NON-DESTRUCTIVE: never deletes anything from the source. Deletion from the
  source is a separate, manual step (purge_school_from_db) that runs only
  after cutover verification.
- SCHEMA-IDENTICAL: run `migrate --database=<target>` (or migrate_all_shards)
  first; this command refuses to run if the target has no migrations applied.
- FK-SAFE: copies the School row itself into the target first, because every
  row's school_id references it.
- SEQUENCE-SAFE: resets each table's id sequence on the target afterwards, or
  the first new insert after cutover would fail with duplicate-key errors.

Usage:
    python manage.py shard_school --slug=school-b --target=vps_shard_1
    # delta re-sync of recently changed rows only:
    python manage.py shard_school --slug=school-b --target=vps_shard_1 \
        --since=2026-08-26T10:00:00Z
"""
from datetime import datetime

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import connections, models, transaction

from apps.common.models import BaseModel
from apps.tenants.models import School


def tenant_models_in_dependency_order():
    """Every BaseModel subclass, FK-dependency ordered via topo sort.

    Parents (referenced models) come before children so inserts satisfy FKs
    without deferrable constraints. Unknown/missing deps raise loudly rather
    than silently copying in a broken order.
    """
    model_set = [m for m in apps.get_models() if issubclass(m, BaseModel)]

    deps = {}
    for m in model_set:
        targets = set()
        for field in m._meta.get_fields():
            # Only FORWARD FK columns constrain insert order. Reverse
            # relations (children pointing at us) must NOT count as
            # dependencies, or every parent would depend on every child.
            if isinstance(field, models.ForeignKey):
                rel_model = field.related_model
                if rel_model is not None and rel_model is not m and rel_model in model_set:
                    targets.add(rel_model)
        # M2M through tables are auto-created; their rows are not copied.
        deps[m] = targets

    ordered, resolved = [], set()
    pending = set(model_set)
    while pending:
        ready = [m for m in pending if deps[m] <= resolved]
        if not ready:
            cycle = ', '.join(sorted(m.__name__ for m in pending))
            raise CommandError(
                f"Circular or unresolvable FK dependencies between: {cycle}"
            )
        for m in sorted(ready, key=lambda x: x._meta.db_table):
            ordered.append(m)
            resolved.add(m)
        pending -= set(ready)
    return ordered


class Command(BaseCommand):
    help = 'Copy one school tenant to another database alias (idempotent, non-destructive).'

    def add_arguments(self, parser):
        parser.add_argument('--slug', required=True,
                            help='School slug to move, e.g. school-b')
        parser.add_argument('--target', required=True,
                            help='Destination DATABASES alias, e.g. vps_shard_1')
        parser.add_argument('--source', default='default',
                            help='Source DATABASES alias (default: default)')
        parser.add_argument('--since', default=None,
                            help='Delta pass: only copy rows updated since this '
                                 'ISO timestamp, e.g. 2026-08-26T10:00:00Z')

    # ------------------------------------------------------------------
    def handle(self, *args, **options):
        slug = options['slug'].strip().lower()
        source = options['source']
        target = options['target']
        since = options['since']

        if source == target:
            raise CommandError('--source and --target must differ.')
        for alias in (source, target):
            if alias not in connections:
                raise CommandError(
                    f"Database '{alias}' is not configured in DATABASES "
                    f"(check VPS_SHARD_1_URL)."
                )

        # School table is pinned to 'default' by the router, so this lookup
        # always hits the central database regardless of alias state.
        try:
            school = School.objects.get(slug=slug)
        except School.DoesNotExist:
            raise CommandError(f"No school with slug '{slug}'.")

        if school.database_alias == target:
            raise CommandError(
                f"{slug} already lives on '{target}'. Nothing to do."
            )

        self._check_target_schema(target)

        since_dt = None
        if since:
            since_dt = datetime.fromisoformat(since.replace('Z', '+00:00'))
            self.stdout.write(self.style.WARNING(
                f"DELTA MODE: copying rows updated since {since_dt.isoformat()}"
            ))

        self.stdout.write(self.style.MIGRATE_HEADING(
            f"Sharding {school.name} ({school.slug}): {source} -> {target}"
        ))

        # ---- 0. School row itself (FK target must exist on the shard) ----
        self._copy_school_row(school, source, target)

        # ---- checkpoint BEFORE copying: safe lower bound for delta passes --
        from django.utils import timezone
        checkpoint = timezone.now()

        ordered_models = tenant_models_in_dependency_order()
        self.stdout.write(f"Discovered {len(ordered_models)} tenant-aware models.\n")

        # auto_now/auto_now_add would stamp copy-time values over the source
        # timestamps during bulk_create; disable them just for this process.
        stashed = self._freeze_timestamp_fields(ordered_models)
        try:
            report = {}
            for model in ordered_models:
                copied = self._copy_model(model, school, source, target, since_dt)
                report[model.__name__] = copied
                self.stdout.write(f"  {model.__name__:<24} {copied:>6} rows")
            self._reset_sequences(target, ordered_models)
        finally:
            self._restore_timestamp_fields(stashed)

        # ---- verification -------------------------------------------------
        self.stdout.write('\nVerifying source/target parity...')
        mismatches = []
        for model in ordered_models:
            ok, detail = self._verify_model(model, school, source, target)
            mark = '✓' if ok else '✗'
            self.stdout.write(f"  {mark} {model.__name__:<24} {detail}")
            if not ok:
                mismatches.append(model.__name__)

        if mismatches:
            raise CommandError(
                f"PARITY CHECK FAILED for: {', '.join(mismatches)}. "
                f"Do NOT flip school.database_alias. Re-run this command to repair."
            )

        self.stdout.write(self.style.SUCCESS(
            f"\n✅ Copy complete and verified. Checkpoint: {checkpoint.isoformat()}"
        ))
        self.stdout.write(
            "\nNEXT STEPS (manual, in order):\n"
            f"  1. Set School(slug='{slug}').database_alias = '{target}'\n"
            f"  2. Reactivate the school and test real operations against it\n"
            f"     (login, view a student, create an attendance record)\n"
            f"  3. Only after confirming, purge old rows:\n"
            f"       python manage.py purge_school_from_db --slug={slug} --database={source}\n"
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _check_target_schema(self, target):
        """Refuse to run unless the target DB has migrations applied."""
        with connections[target].cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM information_schema.tables "
                "WHERE table_schema = 'public'"
            )
            (table_count,) = cursor.fetchone()
        if table_count < 10:  # ~60 tables expected; a fresh DB has few
            raise CommandError(
                f"Target '{target}' looks unmigrated ({table_count} tables). "
                f"Run: python manage.py migrate --database={target}"
            )

    def _copy_school_row(self, school, source, target):
        """Copy this school's own row into the shard so school_id FKs resolve.
        .using(target) OVERRIDES the router (which pins School to 'default')."""
        School.objects.using(target).bulk_create(
            [school],
            batch_size=1,
            update_conflicts=True,
            unique_fields=['id'],
            update_fields=['name', 'slug', 'domain', 'database_alias',
                           'is_active', 'created_at', 'updated_at'],
        )
        self.stdout.write("  schools (platform row)   ✓")

    @staticmethod
    def _freeze_timestamp_fields(model_list):
        """Disable auto_now/auto_now_add so copied timestamps survive."""
        stashed = []
        for model in model_list:
            for field in model._meta.fields:
                if getattr(field, 'auto_now', False) or getattr(field, 'auto_now_add', False):
                    stashed.append((field, field.auto_now, field.auto_now_add))
                    field.auto_now = False
                    field.auto_now_add = False
        return stashed

    @staticmethod
    def _restore_timestamp_fields(stashed):
        for field, auto_now, auto_now_add in stashed:
            field.auto_now = auto_now
            field.auto_now_add = auto_now_add

    def _copy_model(self, model, school, source, target, since_dt):
        """Idempotent upsert of one model's rows for this school."""
        qs = (
            model.all_objects.filter(school=school)
            .using(source)
            .order_by('pk')
        )
        if since_dt is not None:
            qs = qs.filter(updated_at__gte=since_dt)

        update_fields = [
            f.name for f in model._meta.fields if f.name != 'id'
        ]
        copied = 0
        buffer = []
        for obj in qs.iterator(chunk_size=500):
            buffer.append(obj)
            if len(buffer) >= 500:
                copied += self._upsert_batch(model, buffer, update_fields, target)
                buffer = []
        copied += self._upsert_batch(model, buffer, update_fields, target)
        return copied

    def _upsert_batch(self, model, objs, update_fields, target):
        if not objs:
            return 0
        # .using(target) OVERRIDES the router: outside a request there is no
        # tenant in context, so the router alone would send everything to
        # 'default' instead of the shard we are filling.
        with transaction.atomic(using=target):
            model.objects.using(target).bulk_create(
                objs,
                batch_size=500,
                update_conflicts=True,
                unique_fields=['id'],
                update_fields=update_fields,
            )
        return len(objs)

    def _reset_sequences(self, target, model_list):
        """PK-preserving inserts leave Postgres id sequences stale; fix them
        or the first post-cutover insert fails with duplicate-key errors."""
        with connections[target].cursor() as cursor:
            for model in model_list:
                table = model._meta.db_table
                cursor.execute(f"""
                    SELECT setval(
                        pg_get_serial_sequence('{table}', 'id'),
                        GREATEST((SELECT COALESCE(MAX(id), 0) FROM {table}), 1)
                    )
                """)
        self.stdout.write("\nSequences reset on target.")

    def _verify_model(self, model, school, source, target):
        src = self._parity_aggregate(model, school, source)
        tgt = self._parity_aggregate(model, school, target)
        ok = src == tgt
        detail = f"count {src[0]}/{tgt[0]}, sum(id) {src[1]}/{tgt[1]}"
        return ok, detail

    @staticmethod
    def _parity_aggregate(model, school, alias):
        row = (
            model.all_objects.filter(school=school)
            .using(alias)
            .aggregate(
                count=models.Count('id'),
                id_sum=models.Sum('id'),
                max_updated=models.Max('updated_at'),
            )
        )
        return (row['count'], row['id_sum'], str(row['max_updated']))


