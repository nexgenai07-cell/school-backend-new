"""
School portal views — web login, role dashboards, read-only module lists
and detail pages for students, teachers, staff and parents.

The whole surface is read-only: mutations stay in the existing DRF APIs so the
current permission model is not bypassed. Every page is tenant-scoped via the
BaseModel manager (current_tenant is resolved by TenantMiddleware from the
logged-in user's own school).
"""

from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from . import portal_panel as reg


# ------------------------------------------------------------------
# Small helpers
# ------------------------------------------------------------------

def _fmt(value):
    """Human-friendly cell value for lists/details."""
    if value is None:
        return ''
    if isinstance(value, str):
        return value
    if hasattr(value, 'strftime'):          # datetime / date / time
        return value.strftime('%Y-%m-%d %H:%M' if hasattr(value, 'hour') else '%Y-%m-%d')
    if hasattr(value, 'pk'):                # FK model instance
        return str(value)
    return str(value)


def _deny():
    return HttpResponseForbidden('You do not have access to this portal area.')


def _check_role(request, role):
    """Returns True if the request user may view this role's portal pages."""
    if not reg.role_allowed(role):
        raise Http404('Unknown portal.')
    return getattr(request.user, 'role', None) == role


# ------------------------------------------------------------------
# Authentication
# ------------------------------------------------------------------

@require_http_methods(['GET', 'POST'])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('portal_home')
    error = None
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        user = authenticate(request, username=email, password=password)
        if user is None:
            error = 'Invalid email or password.'
        elif not reg.role_allowed(user.role):
            error = 'Your account does not have portal access.'
        elif getattr(user, 'status', 'active') != 'active':
            error = 'Your account is inactive. Contact your school office.'
        else:
            auth_login(request, user)
            return redirect('portal_home')
    return render(request, 'portal/login.html', {'error': error})


@require_POST
def logout_view(request):
    auth_logout(request)
    return redirect('portal_login')


@login_required
def portal_home(request):
    role = getattr(request.user, 'role', None)
    if not reg.role_allowed(role):
        return redirect('portal_login')
    return redirect('portal_dashboard', role=role)


# ------------------------------------------------------------------
# Role dashboards
# ------------------------------------------------------------------

def _student_dashboard(request):
    exams = reg.student_exams(request)
    assignments = reg.student_assignments(request)
    attendance = reg.student_attendance(request)
    fees = reg.student_fees(request)

    total_attendance = attendance.count()
    present = attendance.filter(status='present').count()
    attendance_pct = round((present / total_attendance) * 100, 1) if total_attendance else 0
    fees_due = sum((f.amount for f in fees.filter(status__in=['unpaid', 'pending'])), 0)

    kpis = [
        {'label': 'My Classes', 'value': reg.student_classes(request).count(), 'icon': 'layout-grid', 'color': '#0EA5E9'},
        {'label': 'Upcoming Exams', 'value': exams.filter(date__gte=timezone.localdate()).count(), 'icon': 'file-text', 'color': '#8B5CF6'},
        {'label': 'Pending Assignments', 'value': assignments.filter(status='pending').count(), 'icon': 'clipboard-list', 'color': '#F59E0B'},
        {'label': 'Attendance', 'value': f'{attendance_pct}%', 'icon': 'calendar-check', 'color': '#10B981'},
    ]
    return {
        'kpis': kpis,
        'upcoming_exams': exams.filter(date__gte=timezone.localdate())[:6],
        'recent_assignments': assignments.order_by('-due_date')[:6],
        'fees_due': fees_due,
    }


def _teacher_dashboard(request):
    classes = reg.teacher_classes(request)
    submissions = reg.teacher_submissions(request)
    exams = reg.teacher_exams(request)
    assignments = reg.teacher_assignments(request)

    kpis = [
        {'label': 'My Classes', 'value': classes.count(), 'icon': 'layout-grid', 'color': '#8B5CF6'},
        {'label': 'My Subjects', 'value': reg.teacher_subjects(request).count(), 'icon': 'book-open', 'color': '#0EA5E9'},
        {'label': 'Upcoming Exams', 'value': exams.filter(date__gte=timezone.localdate()).count(), 'icon': 'file-text', 'color': '#F59E0B'},
        {'label': 'Ungraded Submissions', 'value': submissions.filter(status='submitted').count(), 'icon': 'upload', 'color': '#10B981'},
    ]
    return {
        'kpis': kpis,
        'upcoming_exams': exams.filter(date__gte=timezone.localdate())[:6],
        'recent_assignments': assignments.order_by('-due_date')[:6],
        'recent_submissions': submissions[:6],
    }


def _parent_dashboard(request):
    children = reg.parent_children(request)
    fees = reg.parent_fees(request)
    ptm = reg.parent_ptm(request)

    fees_due = sum((f.amount for f in fees.filter(status__in=['unpaid', 'pending'])), 0)
    kpis = [
        {'label': 'My Children', 'value': children.count(), 'icon': 'users', 'color': '#10B981'},
        {'label': 'Fees Due', 'value': f'{float(fees_due):,.0f}', 'icon': 'wallet', 'color': '#F59E0B'},
        {'label': 'Upcoming PTM', 'value': ptm.count(), 'icon': 'handshake', 'color': '#8B5CF6'},
        {'label': 'Unread Notifications', 'value': reg.s_notifications(request).filter(is_read=False).count(), 'icon': 'bell', 'color': '#0EA5E9'},
    ]
    return {
        'kpis': kpis,
        'children': children[:6],
        'upcoming_exams': reg.parent_exams(request).filter(date__gte=timezone.localdate())[:6],
    }


def _staff_dashboard(request):
    employee = reg.staff_employee(request).first()
    leaves = reg.staff_leaves(request)
    payroll = reg.staff_payroll(request).order_by('-paid_date')
    visitors = reg.s_visitors(request)

    latest_payroll = payroll.first()
    kpis = [
        {'label': 'Leave Balance', 'value': getattr(employee, 'leave_balance', 0), 'icon': 'calendar-days', 'color': '#F59E0B'},
        {'label': 'Pending Leaves', 'value': leaves.filter(status='pending').count(), 'icon': 'calendar-off', 'color': '#8B5CF6'},
        {'label': 'Latest Net Salary', 'value': f'{float(latest_payroll.net_salary):,.0f}' if latest_payroll else '—', 'icon': 'banknote', 'color': '#10B981'},
        {'label': 'Visitors Logged', 'value': visitors.count(), 'icon': 'door-closed', 'color': '#0EA5E9'},
    ]
    return {
        'kpis': kpis,
        'employee': employee,
        'recent_leaves': leaves.order_by('-start_date')[:6],
        'recent_visitors': visitors.order_by('-in_time')[:6],
    }


@login_required
def dashboard(request, role):
    if not _check_role(request, role):
        return _deny()
    builder = {
        'student': _student_dashboard,
        'teacher': _teacher_dashboard,
        'parent': _parent_dashboard,
        'staff': _staff_dashboard,
    }.get(role)
    if builder is None:
        raise Http404
    ctx = builder(request)
    ctx.update(reg.portal_context(role, 'dashboard'))
    return render(request, f'portal/dashboard_{role}.html', ctx)


# ------------------------------------------------------------------
# Read-only module list + detail (shared by all roles)
# ------------------------------------------------------------------

@login_required
def module_list(request, role, module):
    if not _check_role(request, role):
        return _deny()
    scope = reg.get_scope(role, module)
    cfg = reg.get_module(role, module)
    if scope is None or cfg is None:
        raise Http404('Unknown module.')
    qs = scope(request)
    q = request.GET.get('q', '').strip()
    if q and cfg.get('search_fields'):
        cond = Q()
        for f in cfg['search_fields']:
            cond |= Q(**{f'{f}__icontains': q})
        qs = qs.filter(cond)
    qs = qs.distinct()
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page'))
    rows = []
    for obj in page.object_list:
        cells = [_fmt(getattr(obj, f, None)) for f in cfg['list_fields']]
        rows.append({'pk': obj.pk, 'cells': cells})
    ctx = reg.portal_context(role, module)
    ctx.update({'cfg': cfg, 'module': module, 'headers': cfg['list_fields'],
                'rows': rows, 'page': page, 'q': q, 'count': paginator.count})
    return render(request, 'portal/list.html', ctx)


RELATED = {
    'assignments': [('Submissions', 'assignments.Submission', 'assignment_id')],
    'exams': [('Results', 'exams.Result', 'exam_id'), ('Questions', 'exams.Question', 'exam_id')],
    'events': [('Participants', 'events.EventParticipation', 'event_id')],
    'classes': [('Students', 'users.Student', 'class_obj_id'), ('Sections', 'academics.Section', 'class_obj_id')],
    'children': [('Fees', 'finance.Fee', 'student_id'), ('Attendance', 'attendance.Attendance', 'student_id'),
                ('Results', 'exams.Result', 'student_id'), ('Submissions', 'assignments.Submission', 'student_id'),
                ('Book Issues', 'library.BookIssue', 'student_id'), ('Bus', 'transport.BusStudent', 'student_id'),
                ('PTM Meetings', 'ptm.PTMMeeting', 'student_id'), ('Events', 'events.EventParticipation', 'student_id')],
    'fees': [('Payments', 'finance.Payment', 'fee_id'), ('History', 'finance.FeeHistory', 'fee_id')],
    'ptm': [('Meetings', 'ptm.PTMMeeting', 'ptm_id')],
    'book-issues': [('History', 'library.BookIssueHistory', 'book_issue_id')],
    'bus': [('Transport Attendance', 'transport.TransportAttendance', 'bus_student_id')],
    'my-profile': [('Leaves', 'hr.Leave', 'employee_id'), ('Payroll', 'hr.Payroll', 'employee_id')],
    'notifications': [('Logs', 'communication.NotificationLog', 'notification_id')],
    'leaves': [('History', 'hr.LeaveHistory', 'leave_id')],
    'submissions': [('History', 'assignments.Submission', 'assignment_id')],
}


def _related_rows(role, obj, cfg_key):
    from django.apps import apps
    rows = []
    for label, path, fk in RELATED.get(cfg_key, [])[:6]:
        try:
            Model = apps.get_model(path)
            related_qs = Model._base_manager.filter(**{fk: obj})
        except Exception:
            continue
        count = related_qs.count()
        if not count:
            continue
        items = [str(x) for x in related_qs[:6]]
        rows.append({'label': label, 'count': count, 'items': items})
    return rows


@login_required
def module_detail(request, role, module, pk):
    if not _check_role(request, role):
        return _deny()
    scope = reg.get_scope(role, module)
    cfg = reg.get_module(role, module)
    if scope is None or cfg is None:
        raise Http404('Unknown module.')
    obj = get_object_or_404(scope(request).distinct(), pk=pk)
    fields = [{
        'label': f.replace('_', ' ').title(),
        'value': _fmt(getattr(obj, f, None)),
    } for f in cfg['detail_fields']]
    related = _related_rows(role, obj, module)
    ctx = reg.portal_context(role, module)
    ctx.update({'cfg': cfg, 'module': module, 'obj': obj, 'fields': fields, 'related': related})
    return render(request, 'portal/detail.html', ctx)
