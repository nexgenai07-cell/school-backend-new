# Smart School Management System — Complete Backend (68 Tables)

Production-level Django + DRF project — ALL 68 tables, models, serializers,
views, urls complete across 17 apps.

## Multi-tenancy

All school-owned records are isolated by `School`. Existing API paths are
unchanged; resolve a tenant through its configured custom domain or send the
`X-Tenant-Slug` header (for example `X-Tenant-Slug: default-school`) with every
API request, including login and registration. The migration creates a
`Default School` and assigns existing records to it.

Platform superusers manage schools at `/api/tenants/schools/`; authenticated
users can inspect the resolved tenant at `/api/tenants/current/`.

## Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements/dev.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Coverage — 68/68 tables
| App | Tables |
|---|---|
| users | users, students, teachers, staff, parents |
| academics | classes, sections, subjects, class_subjects, timetable, rooms |
| assignments | assignments, submissions |
| exams | exams, questions, student_answers, results, ai_auto_checking, grade_scale |
| attendance | attendance, behavior_logs |
| ptm | ptm, ptm_meetings, ptm_attendees |
| communication | messages, notifications, notification_log |
| finance | fee_structures, fees, payments, expenses, fee_history |
| hr | departments, employees, leaves, payroll, salary_history, leave_history |
| transport | buses, routes, bus_stops, bus_students, transport_attendance |
| library | books, book_issues, book_issue_history |
| canteen | categories, menu_items, order_items |
| security | visitors, access_logs, entry_exit_logs |
| events | events, event_participation |
| documents | documents, document_types |
| analytics | predictions, recommendations, student_goals, skill_mapping, student_skills, parent_engagement, automation_rules, automation_logs, analytics_snapshots |
| logs | activity_logs, login_logs, error_logs |

Total = 68 tables ✅

## Every table has
- Model extending `apps.common.models.BaseModel` (id, created_at, updated_at, is_active, is_deleted, soft-delete)
- ModelSerializer
- ModelViewSet with role-based permission_classes (from `apps/common/permissions.py`)
- Router-registered urls.py

## Still needed before running
- `config/settings/base.py` — double-check `INSTALLED_APPS` lists all 17 apps (already done)
- Run migrations
- Create a superuser and test each endpoint in Postman
