"""
Database routing for hybrid sharding.

All schools share the 'default' database until one is explicitly sharded by
setting School.database_alias to another DATABASES entry (e.g. 'vps_shard_1').
The router then transparently sends every read/write for that school's models
to its own database — application/view code never needs to know or care.

Non-negotiable routing rules:
1. Platform tables (the whole 'tenants' app: School, Feature, SchoolFeature)
   ALWAYS live in 'default'. Tenant resolution must hit one central location;
   shards carry an identical-but-copied schools row purely to satisfy FKs.
2. No tenant in context (Django admin superuser, migrations, management
   commands outside a tenant scope) -> 'default'.
3. allow_migrate returns True everywhere so the schema stays identical across
   every database — only row-level data location differs.
"""
from apps.tenants.context import current_tenant


class TenantDatabaseRouter:
    def _alias(self, model):
        # Rule 1: platform tables are pinned to the central database.
        if model._meta.app_label == 'tenants':
            return 'default'

        # Rule 2: without an active tenant everything falls back to default.
        tenant = current_tenant.get()
        if tenant is None:
            return 'default'

        # Rule 3: route to whatever physical DB this school calls home.
        return getattr(tenant, 'database_alias', None) or 'default'

    def db_for_read(self, model, **hints):
        return self._alias(model)

    def db_for_write(self, model, **hints):
        return self._alias(model)

    def allow_relation(self, obj1, obj2, **hints):
        # Same-school relations always live in the same database.
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Every database carries the identical schema.
        return True
