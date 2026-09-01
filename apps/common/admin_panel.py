"""
Config-driven Super Admin Panel (read/CRUD over every module).

Purely additive: nothing here touches the existing DRF APIs or the built-in
Django admin at /admin/. Every view is restricted to platform superusers.
"""

from collections import OrderedDict

# Each module drives list + create + update + soft-delete pages.
#   model         -> "app.Model"
#   icon          -> Lucide icon name (https://lucide.dev/icons)
#   list_fields   -> table columns (FK fields render as __str__)
#   form_fields   -> editable fields on the add/edit form
#   search_fields -> simple icontains lookups for the ?q= box
#   read_only     -> hide add/edit/delete (audit/log style modules)

MODULES = {
    # â”€â”€ ORGANIZATION â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    'schools': dict(
        label='Schools', icon='school', model='tenants.School',
        list_fields=['id', 'name', 'slug', 'database_alias', 'is_active'],
        form_fields=['name', 'slug', 'domain', 'database_alias', 'is_active'],
        search_fields=['name', 'slug'],
    ),
    'classes': dict(
        label='Classes', icon='layout-grid', model='academics.Class',
        list_fields=['id', 'name', 'academic_year'],
        form_fields=['name', 'description', 'academic_year'],
        search_fields=['name'],
    ),
    'sections': dict(
        label='Sections', icon='columns-3', model='academics.Section',
        list_fields=['id', 'name', 'class_obj', 'capacity'],
        form_fields=['class_obj', 'name', 'capacity'],
        search_fields=['name'],
    ),
    'subjects': dict(
        label='Subjects', icon='book-open', model='academics.Subject',
        list_fields=['id', 'name', 'code'],
        form_fields=['name', 'code'],
        search_fields=['name', 'code'],
    ),
    'rooms': dict(
        label='Rooms', icon='door-open', model='academics.Room',
        list_fields=['id', 'name'],
        form_fields=['name'],
        search_fields=['name'],
    ),
    'class-subjects': dict(
        label='Class Subjects', icon='book-copy', model='academics.ClassSubject',
        list_fields=['id', 'class_obj', 'subject', 'teacher'],
        form_fields=['class_obj', 'subject', 'teacher'],
        search_fields=[],
    ),
    'timetable': dict(
        label='Timetable', icon='calendar-clock', model='academics.Timetable',
        list_fields=['id', 'class_obj', 'section', 'subject', 'teacher', 'room', 'day', 'start_time', 'end_time'],
        form_fields=['class_obj', 'section', 'subject', 'teacher', 'room', 'day', 'start_time', 'end_time'],
        search_fields=[],
    ),

    # â”€â”€ PEOPLE â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    'students': dict(
        label='Students', icon='graduation-cap', model='users.Student',
        list_fields=['id', 'admission_no', 'user', 'class_obj', 'parent', 'gender', 'phone'],
        form_fields=['user', 'class_obj', 'parent', 'admission_no', 'dob', 'gender', 'address', 'phone', 'admission_date', 'blood_group'],
        search_fields=['admission_no'],
    ),
    'teachers': dict(
        label='Teachers', icon='presentation', model='users.Teacher',
        list_fields=['id', 'user', 'qualification', 'experience', 'phone', 'status'],
        form_fields=['user', 'employee', 'qualification', 'experience', 'join_date', 'subject_specialization', 'phone', 'status'],
        search_fields=['qualification', 'phone'],
    ),
    'staff': dict(
        label='Staff', icon='id-card', model='users.Staff',
        list_fields=['id', 'user', 'designation', 'department', 'status'],
        form_fields=['user', 'employee', 'designation', 'department', 'join_date', 'phone', 'status'],
        search_fields=['designation', 'department'],
    ),
    'parents': dict(
        label='Parents', icon='users', model='users.Parent',
        list_fields=['id', 'user', 'occupation', 'phone'],
        form_fields=['user', 'occupation', 'phone', 'address'],
        search_fields=['occupation', 'phone'],
    ),
}



MODULES.update({
    # â”€â”€ ACADEMIC OPS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    'exams': dict(
        label='Exams', icon='file-text', model='exams.Exam',
        list_fields=['id', 'name', 'class_obj', 'subject', 'exam_type', 'date', 'total_marks'],
        form_fields=['name', 'class_obj', 'subject', 'teacher', 'exam_type', 'date', 'total_marks', 'description'],
        search_fields=['name'],
    ),
    'assignments': dict(
        label='Assignments', icon='clipboard-list', model='assignments.Assignment',
        list_fields=['id', 'title', 'class_obj', 'subject', 'teacher', 'due_date', 'total_marks', 'status'],
        form_fields=['class_obj', 'subject', 'teacher', 'title', 'description', 'due_date', 'status', 'total_marks'],
        search_fields=['title'],
    ),
    'attendance': dict(
        label='Attendance', icon='calendar-check', model='attendance.Attendance',
        list_fields=['id', 'student', 'date', 'status', 'teacher'],
        form_fields=['student', 'teacher', 'date', 'status'],
        search_fields=[],
    ),
    'behavior-logs': dict(
        label='Behavior Logs', icon='smile', model='attendance.BehaviorLog',
        list_fields=['id', 'student', 'date', 'type', 'severity', 'description'],
        form_fields=['student', 'teacher', 'date', 'type', 'severity', 'description', 'action_taken'],
        search_fields=['description'],
    ),

    # â”€â”€ FINANCE â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    'fee-structures': dict(
        label='Fee Structures', icon='receipt-text', model='finance.FeeStructure',
        list_fields=['id', 'title', 'class_obj', 'amount', 'frequency'],
        form_fields=['class_obj', 'title', 'amount', 'frequency', 'description'],
        search_fields=['title'],
    ),
    'fees': dict(
        label='Fees', icon='wallet', model='finance.Fee',
        list_fields=['id', 'student', 'fee_structure', 'amount', 'due_date', 'status'],
        form_fields=['student', 'fee_structure', 'amount', 'due_date'],
        search_fields=[],
    ),
    'payments': dict(
        label='Payments', icon='credit-card', model='finance.Payment',
        list_fields=['id', 'fee', 'amount_paid', 'payment_date', 'payment_method', 'transaction_id', 'receipt_no'],
        form_fields=['fee', 'amount_paid', 'payment_date', 'payment_method', 'transaction_id', 'receipt_no'],
        search_fields=['transaction_id', 'receipt_no'],
    ),
    'expenses': dict(
        label='Expenses', icon='receipt', model='finance.Expense',
        list_fields=['id', 'category', 'amount', 'date', 'paid_by', 'payment_method'],
        form_fields=['category', 'description', 'amount', 'date', 'paid_by', 'payment_method'],
        search_fields=['category'],
    ),

    # â”€â”€ HR â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    'employees': dict(
        label='Employees', icon='briefcase', model='hr.Employee',
        list_fields=['id', 'user', 'designation', 'department', 'salary', 'status', 'leave_balance'],
        form_fields=['user', 'designation', 'department', 'salary', 'join_date', 'status', 'leave_balance'],
        search_fields=['designation'],
    ),
    'leaves': dict(
        label='Leaves', icon='calendar-off', model='hr.Leave',
        list_fields=['id', 'employee', 'leave_type', 'start_date', 'end_date', 'status'],
        form_fields=['employee', 'leave_type', 'start_date', 'end_date', 'reason', 'status'],
        search_fields=['leave_type'],
    ),
    'payroll': dict(
        label='Payroll', icon='banknote', model='hr.Payroll',
        list_fields=['id', 'employee', 'month', 'basic_salary', 'allowances', 'deductions', 'net_salary'],
        form_fields=['employee', 'month', 'basic_salary', 'allowances', 'deductions', 'paid_date'],
        search_fields=['month'],
    ),
})

MODULES.update({
    # â”€â”€ OPERATIONS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    'routes': dict(
        label='Transport Routes', icon='route', model='transport.Route',
        list_fields=['id', 'name', 'start_point', 'end_point'],
        form_fields=['name', 'description', 'start_point', 'end_point'],
        search_fields=['name'],
    ),
    'buses': dict(
        label='Buses', icon='bus', model='transport.Bus',
        list_fields=['id', 'bus_no', 'capacity', 'status'],
        form_fields=['bus_no', 'capacity', 'status'],
        search_fields=['bus_no'],
    ),
    'bus-stops': dict(
        label='Bus Stops', icon='map-pin', model='transport.BusStop',
        list_fields=['id', 'route', 'name', 'stop_order'],
        form_fields=['route', 'name', 'stop_order'],
        search_fields=['name'],
    ),
    'bus-students': dict(
        label='Bus Students', icon='bus-front', model='transport.BusStudent',
        list_fields=['id', 'bus', 'student', 'pickup_stop', 'drop_stop'],
        form_fields=['bus', 'student', 'pickup_stop', 'drop_stop'],
        search_fields=[],
    ),
    'books': dict(
        label='Books', icon='library', model='library.Book',
        list_fields=['id', 'title', 'author', 'isbn', 'category', 'total_copies', 'available_copies'],
        form_fields=['title', 'author', 'isbn', 'category', 'description', 'total_copies', 'available_copies'],
        search_fields=['title', 'author', 'isbn'],
    ),
    'book-issues': dict(
        label='Book Issues', icon='book-user', model='library.BookIssue',
        list_fields=['id', 'book', 'student', 'due_date', 'return_date', 'fine', 'status'],
        form_fields=['book', 'student', 'due_date', 'return_date', 'fine', 'status'],
        search_fields=[],
    ),
    'menu-items': dict(
        label='Canteen Menu', icon='utensils', model='canteen.MenuItem',
        list_fields=['id', 'name', 'category', 'price', 'is_available'],
        form_fields=['name', 'category', 'price', 'is_available'],
        search_fields=['name'],
    ),
    'ptm-meetings': dict(
        label='PTM Meetings', icon='handshake', model='ptm.PTMMeeting',
        list_fields=['id', 'ptm', 'student', 'teacher', 'meeting_date', 'start_time', 'end_time'],
        form_fields=['ptm', 'student', 'teacher', 'meeting_date', 'start_time', 'end_time'],
        search_fields=[],
    ),
    'events': dict(
        label='Events', icon='party-popper', model='events.Event',
        list_fields=['id', 'name', 'event_type', 'event_date', 'location', 'organizer', 'max_participants'],
        form_fields=['name', 'event_type', 'event_date', 'description', 'organizer', 'location', 'max_participants'],
        search_fields=['name', 'location'],
    ),
    'visitors': dict(
        label='Visitors', icon='door-closed', model='security.Visitor',
        list_fields=['id', 'name', 'phone', 'purpose', 'in_time', 'out_time', 'approved_by'],
        form_fields=['name', 'phone', 'purpose', 'in_time', 'out_time', 'approved_by'],
        search_fields=['name', 'phone', 'purpose'],
    ),
    'notifications': dict(
        label='Notifications', icon='bell', model='communication.Notification',
        list_fields=['id', 'user', 'title', 'is_read'],
        form_fields=['user', 'title', 'message', 'is_read'],
        search_fields=['title'],
    ),

    # â”€â”€ SYSTEM (read-only audit surfaces) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    'activity-logs': dict(
        label='Activity Logs', icon='scroll-text', model='logs.ActivityLog',
        list_fields=['id', 'user', 'action', 'created_at'],
        form_fields=[], search_fields=['action'], read_only=True,
    ),
    'login-logs': dict(
        label='Login Logs', icon='log-in', model='logs.LoginLog',
        list_fields=['id', 'user', 'created_at'],
        form_fields=[], search_fields=[], read_only=True,
    ),
})

# Sidebar grouping: (group title, [module keys}
GROUPS = [
    ('Overview', []),
    ('Organization', ['schools', 'classes', 'sections', 'subjects', 'rooms', 'class-subjects', 'timetable']),
    ('People', ['students', 'teachers', 'staff', 'parents']),
    ('Academic Ops', ['exams', 'assignments', 'attendance', 'behavior-logs']),
    ('Finance', ['fee-structures', 'fees', 'payments', 'expenses']),
    ('HR', ['employees', 'leaves', 'payroll']),
    ('Operations', ['routes', 'buses', 'bus-stops', 'bus-students', 'books', 'book-issues',
                    'menu-items', 'ptm-meetings', 'events', 'visitors', 'notifications']),
    ('System', ['activity-logs', 'login-logs']),
]


def get_module(key):
    return MODULES.get(key)


def get_model(module_cfg):
    from django.apps import apps
    return apps.get_model(module_cfg['model'])