# 📖 SHARDING RUNBOOK — Complete Method With Commands

**Project:** NexGen School Management | **Pattern:** Hybrid Multi-Tenant Sharding
**Flow:** `Seeder → Neon → shard_school → VPS → Alias Flip → Live → Purge Neon`

---

## 🗺️ METHOD OVERVIEW (Data Ka Safar)

```
[1] Naya School create/seed  ──→  NEON (default DB) pe rehta hai
[2] Domain + DNS setup        ──→  schoolX.nxgenai.pro live
[3] Jab load/need ho:
    shard_school command      ──→  NEON se READ → VPS pe WRITE
    (same PKs, idempotent, verified)
[4] database_alias flip       ──→  ab requests VPS pe jayengi
[5] Live test                 ──→  Postman/browser se confirm
[6] Purge Neon                ──→  purana copy delete (LAST step!)
```

---

## 📋 SCENARIO A: Naya School Onboard Karna (Default/Neon Pe)

Naye schools **hamesha pehle default (Neon) pe aate hain** — sharding optional baad ki decision hai.

### A1. School Create + Seed
```bash
cd C:\Users\momina\Documents\GitHub\Nexgen-projects\nexgen_ai_school_project_backend\nexgen_school

# Test/demo data ke saath:
venv\Scripts\python.exe manage.py seed --school=school-d --label-prefix="School D"

# Feature enable karni ho to:
venv\Scripts\python.exe manage.py seed --school=school-d --label-prefix="School D" --enable-feature student-blood-group
```
> Real school ho to seed skip karein — data APIs/admin se aayega. Sirf School row chahiye:
> ```bash
> venv\Scripts\python.exe manage.py shell -c "from apps.tenants.models import School; School.objects.create(name='School D', slug='school-d', domain='schoold.nxgenai.pro')"
> ```

### A2. Domain Setup
```
Vercel Dashboard → Project → Settings → Domains → Add: schoold.nxgenai.pro
DNS Provider   → CNAME schoold → cname.vercel-dns.com
SSL            → Vercel automatic ✅
ALLOWED_HOSTS  → '.nxgenai.pro' already covered ✅
```

### A3. Verify
```bash
# Postman:
POST https://schoold.nxgenai.pro/api/token/
{"email": "admin@schoold.nxgenai.pro", "password": "admin123"}
```
*(Real school ka admin user admin panel/API se banayen)*

---

## 📤 SCENARIO B: Existing School Ko VPS Pe Shard Karna

### B0. Prerequisites Checklist
- [ ] VPS accessible (`ssh root@<IP>`)
- [ ] PostgreSQL installed + running on VPS
- [ ] Vercel env var add hogi: `VPS_SHARD_1_URL` (ya naye shard ke liye `VPS_SHARD_2_URL` + settings update + deploy)
- [ ] Local `.env` mein bhi connection string set
- [ ] Code pushed & deployed (router + commands included)

### B1. VPS Pe Database Create
```bash
sudo -u postgres psql <<'EOF'
CREATE DATABASE school_d_db;
CREATE USER school_d_user WITH PASSWORD 'STRONG_SIMPLE_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE school_d_db TO school_d_user;
ALTER DATABASE school_d_db OWNER TO school_d_user;
\c school_d_db
GRANT ALL ON SCHEMA public TO school_d_user;
EOF

# Remote access (Postgres 16):
echo "listen_addresses = '*'" >> /etc/postgresql/16/main/postgresql.conf
echo "hostssl  school_d_db  school_d_user  0.0.0.0/0  scram-sha-256" >> /etc/postgresql/16/main/pg_hba.conf
systemctl restart postgresql
ss -tulpn | grep 5432          # 0.0.0.0:5432 dikhna chahiye
ufw allow OpenSSH && ufw allow 5432/tcp
```
> ⚠️ Password mein `@ ! # $` use na karein — URL break hota hai!

### B2. Settings Mein Naya Connection Register
```bash
# Local .env:
VPS_SHARD_2_URL=postgresql://school_d_user:PASSWORD@VPS_IP:5432/school_d_db?sslmode=require

# config/settings/prod.py + dev.py mein pattern:
if os.environ.get('VPS_SHARD_2_URL'):
    DATABASES['vps_shard_2'] = env.db('VPS_SHARD_2_URL')
```
→ **Commit + Push → Vercel redeploy Ready**

### B3. Schema Migrate (Target DB Pe)
```bash
venv\Scripts\python.exe manage.py migrate --database=vps_shard_2 --plan     # preview
venv\Scripts\python.exe manage.py migrate --database=vps_shard_2            # apply
```

### B4. PRACTICE RUN (Pehle Dummy School Se — Kabhi Direct Real Nahi!)
```bash
# Practice: kisi minimal-data school se
venv\Scripts\python.exe manage.py shard_school --slug=school-c --target=vps_shard_2

# Log check karo: saare ✓ + "Copy complete and verified"
# Phir practice data saaf karo:
venv\Scripts\python.exe manage.py purge_school_from_db --slug=school-c --database=vps_shard_2           # dry-run
venv\Scripts\python.exe manage.py purge_school_from_db --slug=school-c --database=vps_shard_2 --confirm # real
```

### B5. REAL SHARDING — Copy
```bash
venv\Scripts\python.exe manage.py shard_school --slug=school-d --target=vps_shard_2
```
Command khud verify karti hai (68 models, count+checksum parity). **Agar "PARITY CHECK FAILED" aaye → alias flip MAT karo, command dobara chalao (idempotent hai).**

### B6. ALIAS FLIP (Cutover Point)
```bash
venv\Scripts\python.exe manage.py shell
```
```python
from apps.tenants.models import School
s = School.objects.get(slug='school-d')
print('before:', s.database_alias)          # default
s.database_alias = 'vps_shard_2'
s.save(update_fields=['database_alias'])
print('after :', s.database_alias)          # vps_shard_2
```

### B7. LIVE TEST (Purge Se PEHLE — Mandatory!)
```bash
POST https://schoold.nxgenai.pro/api/token/
{"email": "<real-admin-email>", "password": "..."}
→ 200 expected

GET https://schoold.nxgenai.pro/api/users/students/
Authorization: Bearer <token>
→ 200 expected, school-d ka data
```

### B8. PURGE — Purana Data Source Se Hatao
```bash
# Dry-run pehle (kya delete hoga):
venv\Scripts\python.exe manage.py purge_school_from_db --slug=school-d --database=default

# Confirm (sirf live test pass hone ke BAAD):
venv\Scripts\python.exe manage.py purge_school_from_db --slug=school-d --database=default --confirm

# Final verify (sab 0 hona chahiye):
venv\Scripts\python.exe manage.py purge_school_from_db --slug=school-d --database=default
```

---

## 🔧 TROUBLESHOOTING TABLE (Jo Humne Face Kiya)

| Problem | Wajah | Fix |
|---|---|---|
| Connection timeout | `listen_addresses` localhost tha / port blocked | `echo "listen_addresses = '*'" >> postgresql.conf` + restart + firewall/provider panel |
| Migrate permission denied | PG15+ public schema grant nahi | `ALTER DATABASE ... OWNER TO user` + `GRANT ALL ON SCHEMA public` |
| Purge FK violation (`login_logs`) | Mis-tagged log rows (school_id mismatch) | User-ids se log rows delete karo via ORM, phir purge |
| Parity fail after copy | Network interruption mid-copy | Bas `shard_school` dobara chalao — idempotent upsert hai |
| Postman 400 DisallowedHost | Domain ALLOWED_HOSTS mein nahi | prod.py mein `.nxgenai.pro` (already added) |

---

## ↩️ ROLLBACK (Agar Cutover Ke Baad Kuch Gale)

Alias flip **reversible hai** — data dono jagah tab tak safe hai jab tak purge na ho:
```bash
venv\Scripts\python.exe manage.py shell
>>> from apps.tenants.models import School
>>> s = School.objects.get(slug='school-d')
>>> s.database_alias = 'default'      # wapas Neon pe
>>> s.save(update_fields=['database_alias'])
```
⚠️ **Lekin purge ke BAAD rollback possible nahi** — is liye purge hamesha LAST hota hai.

---

## ✅ GOLDEN RULES SUMMARY

1. Seed sirf testing ke liye — real data direct APIs se
2. Practice run hamesha dummy school se pehle
3. Copy → Verify → Flip → Live Test → **Phir** Purge (order kabhi mat todo)
4. Purge dry-run ke baghair kabhi nahi
5. Har deploy ke baad `migrate_all_shards`
6. Naye shard ka env var **flip se pehle** Vercel pe hona chahiye

