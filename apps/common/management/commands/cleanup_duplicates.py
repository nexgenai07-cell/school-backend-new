"""
One-off cleanup for duplicate rows that block unique-constraint migrations.

Default mode is a REPORT (dry-run): it only prints what it found.
Pass --confirm to actually fix: for every duplicate group the OLDEST row
(id order) is kept, all FK references pointing to the newer duplicates are
reassigned to the keeper, and the newer duplicates are deleted.

Usage:
    python manage.py cleanup_duplicates            # report only
    python manage.py cleanup_duplicates --confirm  # fix duplicates
"""

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db.models import Count

# (model_label, unique_fields, filter_kwargs, exclude_kwargs)
DUP_SPECS = [
    ("academics.Class", ["school", "name", "academic_year"], None, None),
    ("academics.Section", ["class_obj", "name"], None, None),
    ("academics.Room", ["school", "name"], None, None),
    ("academics.Subject", ["school", "code"], None, None),
    ("academics.ClassSubject", ["class_obj", "subject"], {"teacher__isnull": True}, None),
    ("exams.Result", ["exam", "student"], None, None),
    ("exams.StudentAnswer", ["exam", "student", "question"], None, None),
    ("exams.GradeScale", ["grade"], None, None),
    ("finance.Fee", ["student", "fee_structure"], None, None),
    ("finance.FeeStructure", ["class_obj", "title"], None, None),
    ("finance.Payment", ["transaction_id"], None, {"transaction_id": ""}),
    ("hr.Payroll", ["employee", "month"], None, None),
    ("hr.Department", ["school", "name"], None, None),
    ("analytics.AutomationRule", ["school", "rule_name"], None, None),
    ("analytics.AutomationLog", ["rule", "triggered_at"], None, None),
    ("analytics.AnalyticsSnapshot", ["school", "metric_name", "date"], None, None),
    ("analytics.Prediction", ["student", "prediction_type", "prediction_date"], None, None),
    ("analytics.Recommendation", ["student", "type", "content"], None, None),
    ("analytics.StudentGoal", ["student", "goal_type", "target"], None, None),
    ("analytics.StudentSkill", ["student", "skill"], None, None),
    ("analytics.SkillMapping", ["school", "name"], None, None),
    ("security.EntryExitLog", ["student", "entry_time"], None, None),
    ("ptm.PTM", ["class_obj", "name"], None, None),
    ("canteen.Category", ["school", "name"], None, None),
    ("canteen.MenuItem", ["school", "name"], None, None),
    ("documents.Document", ["user", "doc_type"], None, None),
    ("events.EventParticipation", ["event", "student"], None, None),
    ("transport.Route", ["school", "name"], None, None),
    ("transport.BusStop", ["route", "name"], None, None),
    ("transport.BusStudent", ["student"], None, None),
    ("transport.Bus", ["school", "bus_no"], None, None),
    ("library.Book", ["school", "isbn"], None, None),
    ("users.Student", ["school", "admission_no"], None, None),
]


class Command(BaseCommand):
    help = "Find (and optionally fix) duplicate rows that block unique-constraint migrations."

    def add_arguments(self, parser):
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Actually reassign references and delete duplicates (default: report only).",
        )

    def handle(self, *args, **options):
        confirm = options["confirm"]
        total_groups = 0
        total_deleted = 0

        for model_label, fields, filter_kwargs, exclude_kwargs in DUP_SPECS:
            model = apps.get_model(model_label)
            # _base_manager: soft-deleted rows (is_deleted=True) MUST be included,
            # because a DB unique index covers every row regardless of the flag.
            qs = model._base_manager.all()
            if filter_kwargs:
                qs = qs.filter(**filter_kwargs)
            if exclude_kwargs:
                qs = qs.exclude(**exclude_kwargs)

            dup_groups = (
                qs.values(*fields)
                .annotate(cnt=Count("id"))
                .filter(cnt__gt=1)
                .order_by(*fields)
            )

            for group in dup_groups:
                total_groups += 1
                # Keep the OLDEST ACTIVE row (non-deleted preferred, then lowest id).
                group_qs = qs.filter(**{f: group[f] for f in fields}).order_by("is_deleted", "id")
                rows = list(group_qs)
                keeper, dups = rows[0], rows[1:]
                self.stdout.write(
                    self.style.WARNING(
                        f"{model_label} {({f: group[f] for f in fields})} -> "
                        f"keep id={keeper.id}, delete ids={[d.id for d in dups]}"
                    )
                )

                if not confirm:
                    continue

                for dup in dups:
                    # Reassign every FK/OneToOne pointing at this duplicate.
                    # _base_manager: soft-deleted children must be reassigned too,
                    # otherwise the hard delete below would CASCADE into them.
                    for rel in dup._meta.related_objects:
                        if rel.field.many_to_many:
                            continue  # no M2M targets in this project's dup models
                        rel_model = rel.related_model
                        fixed = (
                            rel_model._base_manager.filter(**{rel.field.name: dup})
                            .update(**{rel.field.name: keeper})
                        )
                        if fixed:
                            self.stdout.write(
                                f"    reassigned {fixed} x {rel_model.__name__}.{rel.field.name}"
                            )
                    # HARD delete: BaseModel.delete() is a soft delete (sets
                    # is_deleted via save -> full_clean), and soft-deleted rows
                    # still violate DB unique indexes. Physically remove instead.
                    model._base_manager.filter(pk=dup.pk).delete()
                    total_deleted += 1

        if total_groups == 0:
            self.stdout.write(self.style.SUCCESS("No duplicates found. Safe to migrate."))
            return

        if confirm:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Done. {total_groups} duplicate group(s) resolved, {total_deleted} row(s) deleted."
                )
            )
        else:
            self.stdout.write(
                "REPORT ONLY. Re-run with --confirm to fix the duplicates above."
            )