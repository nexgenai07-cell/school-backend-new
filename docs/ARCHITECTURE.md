# 🏗️ ARCHITECTURE — Multi-Tenant + Hybrid Sharding

**Project:** Smart School Management System (NexGen)
**Stack:** Django 5.2 + DRF + PostgreSQL (Neon shared + VPS dedicated) + Vercel
**Pattern:** Shared-DB row-level isolation + optional per-school physical shards

---

## 1️⃣ ARCHITECTURE OVERVIEW

```
                    ┌─────────────────────────────┐
                    │   Vercel (Django App)       │
                    │   Single deployment         │
                    └──────────┬──────────────────┘
           TenantMiddleware resolves tenant per-request
           (custom domain → X-Tenant-Slug fallback)
                               │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
 schoola.nxgenai.pro    schoolc.nxgenai.pro    schoolb.nxgenai.pro
        │                      │                      │
        ▼                      ▼                      ▼
 ┌────────────────────┐              ┌──────────────────┐
 │ Neon Postgres      │              │ VPS Postgres 16  │
 │ (default)          │              │ (vps_shard_1) 🎯 │
 │ School A ✓, C ✓    │              │ School B (sharded)│
 │ Platform tables 🔒 │              └──────────────────┘
 └────────────────────┘
```

**Design principle:** Application code kabhi nahi jaanta kis physical DB se baat ho rahi hai — `TenantDatabaseRouter` transparently route karta hai. Naya shard add karna = sirf settings entry + ek School row ka alias change.

---

## 2️⃣ TENANT FOUNDATION

### Core Components

| Component | File | Kaam |
|---|---|---|
| `School` model | `apps/tenants/models.py` | Tenant boundary — slug, domain, `database_alias`, `is_active` |
| `TenantMiddleware` | `apps/tenants/middleware.py` | Domain → header fallback resolution; bina tenant `/api/*` = 400 |
| `current_tenant` | `apps/tenants/context.py` | `ContextVar` — thread-safe/async-safe tenant context |
| `BaseModel` | `apps/common/models.py` | Abstract base: `school` FK + auto-bind on save + cross-tenant write rejection |
| `SoftDeleteManager` | `apps/common/models.py` | Querysets auto-filtered by current tenant + soft-delete hidden |
| `TenantModelViewSet` | `apps/common/views.py` | Base viewset: queryset filter + forced school assignment |
| `TenantModelSerializer` | `apps/common/serializers.py` | FK relations validate karta hai same-school |

### Defense in Depth (5 Layers)
```
1. Middleware   → bina tenant request reject (400)
2. ORM Manager  → har query auto-filtered by current_tenant
3. BaseModel.save() → school bind + cross-tenant write ValidationError
4. ViewSet      → queryset.filter(school=tenant) + perform_create(school=tenant)
5. Serializer   → related objects ka school verify
```

### User Model Specifics
- `UserManager.get_queryset()` — tenant-scoped + soft-delete filtered
- Platform superusers: **no school** (tenant management only)
- Regular users: school mandatory (`ValueError` otherwise)
- `User.email` globally unique → emails domain-prefixed (`admin@schoola.nxgenai.pro`)

---

## 3️⃣ FEATURE FLAG SYSTEM

### Models (`apps/tenants/models.py`)
```python
Feature         # key (unique), name, default_enabled
SchoolFeature   # school + feature + is_enabled (unique together)
```

### Resolution Logic (`School.has_feature(key)`)
```python
override = self.feature_overrides.filter(feature__key=key).first()
if override: return override.is_enabled
feature = Feature.objects.filter(key=key).first()
return feature.default_enabled if feature else False
```

### Gated Field Pattern (Demo: `blood_group`)
```python
# apps/users/serializers.py
FEATURE_GATED_FIELDS = {'blood_group': 'student-blood-group'}

class StudentSerializer(ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tenant = getattr(self.context.get('request'), 'tenant', None)
        for field_name, feature_key in FEATURE_GATED_FIELDS.items():
            if tenant is None or not tenant.has_feature(feature_key):
                self.fields.pop(field_name, None)   # API se field gayab
```

**Rules:**
- Naya feature = sirf ek `Feature.objects.create(...)` row — **koi migration nahi**
- DB column sab schools ke liye exist karta hai — sirf **API visibility** gated
- Column rename per-school **kabhi nahi**
- Toggle Django Admin se: `FeatureAdmin`, `SchoolFeatureAdmin`

---

## 4️⃣ SHARDING INTERNALS

### `database_alias` Field
```python
class School(models.Model):
    database_alias = models.CharField(max_length=50, default='default')
    # 'default' = Neon | 'vps_shard_1' = dedicated VPS
```

### Router (`apps/tenants/router.py`) — Teen Non-Negotiable Rules
```python
def _alias(self, model):
    if model._meta.app_label == 'tenants':   # RULE 1: platform tables pinned
        return 'default'
    tenant = current_tenant.get()
    if tenant is None:                        # RULE 2: no context -> default
        return 'default'
    return getattr(tenant, 'database_alias', None) or 'default'  # RULE 3

def allow_migrate(self, ...):
    return True   # schema har DB pe identical
```

### Settings Pattern
```python
DATABASE_ROUTERS = ['apps.tenants.router.TenantDatabaseRouter']

# Connection SIRF tab jab URL set ho (deploy-safe):
if os.environ.get('VPS_SHARD_1_URL'):
    DATABASES['vps_shard_1'] = env.db('VPS_SHARD_1_URL')

ALLOWED_HOSTS += ['.nxgenai.pro']   # domain-based resolution
```

### Management Commands

| Command | Kaam |
|---|---|
| `migrate_all_shards` | Har referenced alias pe schema sync (har deploy pe) |
| `shard_school --slug --target [--since]` | Idempotent copy engine |
| `purge_school_from_db --slug --database [--confirm]` | Dry-run default; reverse-FK deletion |

### `shard_school` Safety Engineering
1. **Auto-discovery:** Saare `BaseModel` subclasses (68) topological FK-order (forward-FK only)
2. **School-row FK fix:** Pehle School row target mein copy (`school_id` FK ke liye)
3. **Idempotent upsert:** `bulk_create(update_conflicts=True)` + `.using(target)` router override
4. **Timestamp freeze:** Copy ke doran `auto_now/auto_now_add` disabled
5. **Sequence reset:** `setval(pg_get_serial_sequence(...))` per table
6. **Parity verify:** Per-model count + Sum(id) dono DBs pe; mismatch = abort
7. **Delta mode:** `--since=<ISO>` sirf changed rows re-copy

### Purge Safety Gates
- Dry-run by default; `--confirm` mandatory
- Active-routed DB purge refuse karta hai
- Reverse-FK-order `_raw_delete` — cascade doosre school tak nahi jata

---

## 5️⃣ SEEDED DATA STRATEGY

Command: `python manage.py seed --school=<slug> --label-prefix="School X" [--enable-feature <key>]`

- Labels har record mein: `"School A - Ahmed Khan"` (visual isolation testing)
- Globally-unique columns prefixed: emails, admissions (`SCH-A-001`), codes, ISBNs
- `current_tenant.set(school)` wrap → auto school tagging via `BaseModel.save()`
- Idempotent (`get_or_create`)
- Per school: 12 users, 5 students, 3 teachers, 2 parents + academics/fees/exams/transport/canteen/library

---

## 6️⃣ SCHOOL-B CUTOVER RECORD (Aug 2026)

| # | Step | Result |
|---|------|--------|
| 1 | Vercel env var `VPS_SHARD_1_URL` + redeploy | ✅ |
| 2 | Schema migrate: 80/80 tables identical | ✅ |
| 3 | Practice run School-C se | ✅ 68 models, parity pass |
| 4 | Practice cleanup (purge C from shard) | ✅ |
| 5 | Real copy School-B → shard | ✅ All parity pass |
| 6 | Routing proof (marker-on-shard test) | ✅ SHARD HIT |
| 7 | Alias flip → vps_shard_1 | ✅ Persisted |
| 8 | Live Postman test (login + students) | ✅ Production verified |
| 9 | Neon purge | ✅ B rows = 0 |
| 10 | Final verify: A/C untouched, B intact on shard | ✅ ALL GREEN |

**Issues hit & fixed:** listen_addresses nano-edit not applied (sed fix), PG15+ schema grants missing (owner+grant fix), mis-tagged LoginLog FK block (ORM delete), topo-sort reverse-relation cycles (forward-FK-only), bulk_create router bypass (.using(target)).

---

## 7️⃣ CURRENT STATE

| Item | Value |
|---|---|
| Schools | A: Neon, **B: VPS shard**, C: Neon |
| Tables per DB | 80 (identical schema everywhere) |
| Features enabled | `student-blood-group` (School-A only) |
| Deployments | Vercel single app, wildcard domains |

---

## 8️⃣ SECURITY NOTES / PENDING

1. ⚠️ Rotate shard DB password (exposed during setup):
   ```sql
   ALTER USER school_b_user WITH PASSWORD '<naya-strong-password>';
   ```
   → Vercel env var + local `.env` update (URL-encoded!)
2. pg_hba.conf cleanup: loose `host all all md5` lines comment karein, sirf `hostssl ... scram-sha-256`
3. VPS Postgres backups: `pg_dump` cron recommended:
   ```bash
   # crontab -e (VPS)
   0 2 * * * sudo -u postgres pg_dump school_b_db > /opt/backups/school_b_db_$(date +\%F).sql
   ```

---

*See `docs/SHARDING_RUNBOOK.md` for step-by-step operational commands.*

