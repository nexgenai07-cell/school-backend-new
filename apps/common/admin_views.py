"""
Super Admin Panel views — dashboard + generic CRUD for every module.

Superuser-only. Server-rendered Django templates (no DRF involvement),
so the existing REST APIs and built-in /admin/ are completely untouched.
"""

import json
from datetime import timedelta

from django import forms
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Sum, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.decorators import decorator_from_middleware
from django.views.decorators.http import require_POST

from . import admin_panel as reg

superuser_required = staff_member_required


# ── dynamic ModelForm factory ────────────────────────────────────

def build_form(model, field_names):
    meta = type('Meta', (), {'model': model, 'fields': list(field_names) or []})
    return type(f'{model.__name__}PanelForm', (forms.ModelForm,), {'Meta': meta})


# ── shared context: sidebar groups ───────────────────────────────

def panel_context(active_key=''):
    groups = []
    for title, keys in reg.GROUPS:
        items = [{'key': k, 'label': reg.MODULES[k]['label'], 'icon': reg.MODULES[k]['icon']}
                 for k in keys if k in reg.MODULES]
        if title == 'Overview':
            items.insert(0, {'key': 'dashboard', 'label': 'Dashboard', 'icon': 'layout-dashboard'})
        groups.append({'title': title, 'items': items})
    return {'nav_groups': groups, 'active_module': active_key}


def _schools():
    from apps.tenants.models import School
    return School.objects.all()


def _base(path):
    return reg.get_model({'model': path})._base_manager


# ── dashboard ────────────────────────────────────────────────────

@superuser_required
def dashboard(request):
    student_m = _base('users.Student')
    payment_m = _base('finance.Payment')
    exam_m = _base('exams.Exam')
    user_m = _base('users.User')

    total_fee = payment_m.aggregate(total=Sum('amount_paid'))['total'] or 0

    students_per_school = [
        {'label': s['school__name'] or '—', 'value': s['c']}
        for s in student_m.values('school__name').annotate(c=Count('id')).order_by('-c')
    ]
    roles_split = [
        {'label': r['role'], 'value': r['c']}
        for r in user_m.values('role').annotate(c=Count('id')).order_by('role')
    ]
    exams_by_type = [
        {'label': e['exam_type'], 'value': e['c']}
        for e in exam_m.values('exam_type').annotate(c=Count('id')).order_by('exam_type')
    ]

    fee_trend, labels = [], []
    today = timezone.localdate()
    for i in range(5, -1, -1):
        d = today - timedelta(days=30 * i)
        total = payment_m.filter(payment_date__year=d.year, payment_date__month=d.month).aggregate(
            t=Sum('amount_paid'))['t'] or 0
        labels.append(f'{d.year}-{d.month:02d}')
        fee_trend.append(float(total))

    kpis = [
        {'label': 'Schools', 'value': _schools().count(), 'icon': 'school', 'color': '#6366F1'},
        {'label': 'Total Users', 'value': user_m.count(), 'icon': 'users', 'color': '#0EA5E9'},
        {'label': 'Students', 'value': student_m.count(), 'icon': 'graduation-cap', 'color': '#10B981'},
        {'label': 'Fee Collected', 'value': f'{float(total_fee):,.0f}', 'icon': 'wallet', 'color': '#F59E0B'},
    ]

    ctx = panel_context('dashboard')
    ctx.update({
        'kpis': kpis,
        'students_per_school': json.dumps(students_per_school),
        'roles_split': json.dumps(roles_split),
        'exams_by_type': json.dumps(exams_by_type),
        'fee_trend_labels': json.dumps(labels),
        'fee_trend_values': json.dumps(fee_trend),
        'schools': _schools(),
    })
    return render(request, 'admin_panel/dashboard.html', ctx)


# ── generic module CRUD ──────────────────────────────────────────

def _module_or_404(key):
    cfg = reg.get_module(key)
    if cfg is None:
        raise LookupError(key)
    return cfg


def _model(cfg):
    return reg.get_model(cfg)

def _has_field(model, name):
    return any(f.name == name for f in model._meta.fields)

@superuser_required
def module_list(request, module):
    cfg = _module_or_404(module)
    model = _model(cfg)
    qs = model._base_manager.all()
    # School (tenants.School) is a plain models.Model without soft-delete;
    # only apply is_deleted filtering when the model actually has the field.
    if _has_field(model, 'is_deleted'):
        qs = qs.filter(is_deleted=False)

    q = request.GET.get('q', '').strip()
    if q and cfg.get('search_fields'):
        from django.db.models import Q
        cond = Q()
        for f in cfg['search_fields']:
            cond |= Q(**{f'{f}__icontains': q})
        qs = qs.filter(cond)

    qs = qs.order_by('-id')
    paginator = Paginator(qs, 25)
    page = paginator.get_page(request.GET.get('page'))

    rows = []
    for obj in page.object_list:
        cells = []
        for field in cfg['list_fields']:
            value = getattr(obj, field, None)
            if hasattr(value, 'pk'):
                value = str(value)
            cells.append('' if value is None else str(value))
        rows.append({'pk': obj.pk, 'cells': cells})

    ctx = panel_context(module)
    ctx.update({
        'module_key': module, 'cfg': cfg, 'headers': cfg['list_fields'],
        'rows': rows, 'page': page, 'q': q,
        'read_only': cfg.get('read_only', False),
    })
    return render(request, 'admin_panel/list.html', ctx)


def _save_with_school(request, form, model):
    instance = form.save(commit=False)
    if any(f.name == 'school' for f in model._meta.fields):
        school_id = request.POST.get('school') or None
        instance.school_id = int(school_id) if school_id else None
    instance.save()
    return instance


@superuser_required
def module_create(request, module):
    cfg = _module_or_404(module)
    if cfg.get('read_only'):
        return redirect('admin_panel_list', module=module)
    model = _model(cfg)
    Form = build_form(model, cfg.get('form_fields', []))

    form = Form(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        try:
            _save_with_school(request, form, model)
            return redirect('admin_panel_list', module=module)
        except Exception as exc:
            form.add_error(None, str(exc))

    ctx = panel_context(module)
    ctx.update({'module_key': module, 'cfg': cfg, 'form': form,
                'schools': _schools(), 'current_school_id': None})
    return render(request, 'admin_panel/form.html', ctx)


@superuser_required
def module_edit(request, module, pk):
    cfg = _module_or_404(module)
    if cfg.get('read_only'):
        return redirect('admin_panel_list', module=module)
    model = _model(cfg)
    obj = get_object_or_404(model, pk=pk)
    Form = build_form(model, cfg.get('form_fields', []))

    form = Form(request.POST or None, request.FILES or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        try:
            _save_with_school(request, form, model)
            return redirect('admin_panel_list', module=module)
        except Exception as exc:
            form.add_error(None, str(exc))

    ctx = panel_context(module)
    ctx.update({'module_key': module, 'cfg': cfg, 'form': form, 'obj': obj,
                'schools': _schools(), 'current_school_id': getattr(obj, 'school_id', None)})
    return render(request, 'admin_panel/form.html', ctx)


@superuser_required
def module_delete(request, module, pk):
    cfg = _module_or_404(module)
    if request.method == 'POST':
        model = _model(cfg)
        # Soft delete via direct update — bypasses model save()/full_clean()
        # overrides that could reject a legitimate delete.
        if _has_field(model, 'is_deleted'):
            model._base_manager.filter(pk=pk).update(is_deleted=True, deleted_at=timezone.now())
        else:
            # Non-soft-delete models (e.g. tenants.School) actually delete.
            model._base_manager.filter(pk=pk).delete()
    return redirect('admin_panel_list', module=module)