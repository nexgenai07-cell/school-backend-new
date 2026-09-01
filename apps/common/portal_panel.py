"""
Role-based School Portal — dashboards + read-only lists & details for
Students, Teachers and Parents.

Purely additive: nothing here touches the existing DRF APIs, the built-in
Django admin or the super-admin panel. Every portal module is role-scoped
(read-only) by construction, and every queryset is scoped to the logged-in
user's own school via the tenant manager on BaseModel.

Module config keys:
    label          -> sidebar + page title
    icon           -> Lucide icon name (https://lucide.dev/icons)
    model          -> "app.Model"
    list_fields    -> table columns on the list page
    detail_fields  -> key/value rows on the detail page
    search_fields  -> simple icontains lookups for the ?q= box
"""

from django.db.models import Q


# ------------------------------------------------------------------
# Shared / school-wide read-only catalogs (scoped by the tenant manager)
# ------------------------------------------------------------------

def s_books(request):
    from apps.library.models import Book
    return Book.objects.all()


def s_menu(request):
    from apps.canteen.models import MenuItem
    return MenuItem.objects.filter(is_available=True)


def s_events(request):
    from apps.events.models import Event
    return Event.objects.all()


def s_routes(request):
    from apps.transport.models import Route
    return Route.objects.all()


def s_messages(request):
    from apps.communication.models import Message
    return Message.objects.filter(
        Q(receiver=request.user) | Q(sender=request.user)
    ).order_by('-sent_at')


def s_notifications(request):
    from apps.communication.models import Notification
    return Notification.objects.filter(user=request.user)


# ------------------------------------------------------------------
# STUDENT scope helpers (the logged-in student's own data)
# ------------------------------------------------------------------

def student_classes(request):
    from apps.academics.models import Class
    return Class.objects.filter(students__user=request.user)


def student_sections(request):
    from apps.academics.models import Section
    return Section.objects.filter(class_obj__students__user=request.user).distinct()


def student_subjects(request):
    from apps.academics.models import Subject
    return Subject.objects.filter(
        class_subjects__class_obj__students__user=request.user
    ).distinct()


def student_class_subjects(request):
    from apps.academics.models import ClassSubject
    return ClassSubject.objects.filter(class_obj__students__user=request.user).distinct()


def student_timetable(request):
    from apps.academics.models import Timetable
    return Timetable.objects.filter(class_obj__students__user=request.user).order_by('day', 'start_time')


def student_exams(request):
    from apps.exams.models import Exam
    return Exam.objects.filter(class_obj__students__user=request.user).order_by('date')


def student_results(request):
    from apps.exams.models import Result
    return Result.objects.filter(student__user=request.user).order_by('-exam__date')


def student_assignments(request):
    from apps.assignments.models import Assignment
    return Assignment.objects.filter(class_obj__students__user=request.user)


def student_submissions(request):
    from apps.assignments.models import Submission
    return Submission.objects.filter(student__user=request.user).order_by('-submission_date')


def student_attendance(request):
    from apps.attendance.models import Attendance
    return Attendance.objects.filter(student__user=request.user).order_by('-date')


def student_behavior(request):
    from apps.attendance.models import BehaviorLog
    return BehaviorLog.objects.filter(student__user=request.user).order_by('-date')


def student_fees(request):
    from apps.finance.models import Fee
    return Fee.objects.filter(student__user=request.user)


def student_fee_structures(request):
    from apps.finance.models import FeeStructure
    return FeeStructure.objects.filter(class_obj__students__user=request.user)


def student_payments(request):
    from apps.finance.models import Payment
    return Payment.objects.filter(fee__student__user=request.user).order_by('-payment_date')


def student_book_issues(request):
    from apps.library.models import BookIssue
    return BookIssue.objects.filter(student__user=request.user)


def student_orders(request):
    from apps.canteen.models import OrderItem
    return OrderItem.objects.filter(student__user=request.user)


def student_bus(request):
    from apps.transport.models import BusStudent
    return BusStudent.objects.filter(student__user=request.user)


def student_events(request):
    from apps.events.models import EventParticipation
    return EventParticipation.objects.filter(student__user=request.user)


def student_goals(request):
    from apps.analytics.models import StudentGoal
    return StudentGoal.objects.filter(student__user=request.user)


def student_skills(request):
    from apps.analytics.models import StudentSkill
    return StudentSkill.objects.filter(student__user=request.user)


def student_recommendations(request):
    from apps.analytics.models import Recommendation
    return Recommendation.objects.filter(student__user=request.user)


# ------------------------------------------------------------------
# TEACHER scope helpers (the logged-in teacher's own data)
# ------------------------------------------------------------------

def teacher_classes(request):
    from apps.academics.models import Class
    return Class.objects.filter(class_subjects__teacher__user=request.user).distinct()


def teacher_sections(request):
    from apps.academics.models import Section
    return Section.objects.filter(class_obj__class_subjects__teacher__user=request.user).distinct()


def teacher_subjects(request):
    from apps.academics.models import Subject
    return Subject.objects.filter(class_subjects__teacher__user=request.user).distinct()


def teacher_class_subjects(request):
    from apps.academics.models import ClassSubject
    return ClassSubject.objects.filter(teacher__user=request.user)


def teacher_timetable(request):
    from apps.academics.models import Timetable
    return Timetable.objects.filter(teacher__user=request.user).order_by('day', 'start_time')


def teacher_assignments(request):
    from apps.assignments.models import Assignment
    return Assignment.objects.filter(teacher__user=request.user)


def teacher_submissions(request):
    from apps.assignments.models import Submission
    return Submission.objects.filter(assignment__teacher__user=request.user).order_by('-submission_date')


def teacher_exams(request):
    from apps.exams.models import Exam
    return Exam.objects.filter(teacher__user=request.user).order_by('date')


def teacher_results(request):
    from apps.exams.models import Result
    return Result.objects.filter(exam__teacher__user=request.user).select_related('exam', 'student')


def teacher_attendance(request):
    from apps.attendance.models import Attendance
    return Attendance.objects.filter(
        Q(marked_by__user=request.user) |
        Q(student__class_obj__class_subjects__teacher__user=request.user)
    ).distinct().order_by('-date')


def teacher_behavior(request):
    from apps.attendance.models import BehaviorLog
    return BehaviorLog.objects.filter(
        Q(teacher__user=request.user) |
        Q(student__class_obj__class_subjects__teacher__user=request.user)
    ).distinct().order_by('-date')


def student_predictions(request):
    from apps.analytics.models import Prediction
    return Prediction.objects.filter(student__user=request.user)


def teacher_fee_structures(request):
    from apps.finance.models import FeeStructure
    return FeeStructure.objects.filter(class_obj__class_subjects__teacher__user=request.user).distinct()


def teacher_ptm(request):
    from apps.ptm.models import PTMMeeting
    return PTMMeeting.objects.filter(teacher__user=request.user).order_by('meeting_date', 'start_time')


def teacher_book_issues(request):
    from apps.library.models import BookIssue
    return BookIssue.objects.filter(student__class_obj__class_subjects__teacher__user=request.user).distinct()


def teacher_employee(request):
    from apps.hr.models import Employee
    return Employee.objects.filter(user=request.user)


def teacher_leaves(request):
    from apps.hr.models import Leave
    return Leave.objects.filter(employee__user=request.user)


def teacher_payroll(request):
    from apps.hr.models import Payroll
    return Payroll.objects.filter(employee__user=request.user)


# ------------------------------------------------------------------
# STAFF scope helpers (the logged-in staff member's own data)
# ------------------------------------------------------------------

def staff_employee(request):
    from apps.hr.models import Employee
    return Employee.objects.filter(user=request.user)


def staff_leaves(request):
    from apps.hr.models import Leave
    return Leave.objects.filter(employee__user=request.user)


def staff_payroll(request):
    from apps.hr.models import Payroll
    return Payroll.objects.filter(employee__user=request.user)


def s_visitors(request):
    from apps.security.models import Visitor
    return Visitor.objects.all()


# ------------------------------------------------------------------
# PARENT scope helpers (the logged-in parent's children's data)
# ------------------------------------------------------------------

def parent_children(request):
    from apps.users.models import Student
    return Student.objects.filter(parent__user=request.user)


def parent_sections(request):
    from apps.academics.models import Section
    return Section.objects.filter(class_obj__students__parent__user=request.user).distinct()


def parent_subjects(request):
    from apps.academics.models import Subject
    return Subject.objects.filter(
        class_subjects__class_obj__students__parent__user=request.user
    ).distinct()


def parent_class_subjects(request):
    from apps.academics.models import ClassSubject
    return ClassSubject.objects.filter(class_obj__students__parent__user=request.user).distinct()


def parent_timetable(request):
    from apps.academics.models import Timetable
    return Timetable.objects.filter(
        class_obj__students__parent__user=request.user
    ).distinct().order_by('day', 'start_time')


def parent_exams(request):
    from apps.exams.models import Exam
    return Exam.objects.filter(class_obj__students__parent__user=request.user).distinct().order_by('date')


def parent_results(request):
    from apps.exams.models import Result
    return Result.objects.filter(student__parent__user=request.user).select_related('exam', 'student')


def parent_assignments(request):
    from apps.assignments.models import Assignment
    return Assignment.objects.filter(class_obj__students__parent__user=request.user).distinct()


def parent_submissions(request):
    from apps.assignments.models import Submission
    return Submission.objects.filter(student__parent__user=request.user).select_related('assignment', 'student')


def parent_attendance(request):
    from apps.attendance.models import Attendance
    return Attendance.objects.filter(student__parent__user=request.user).select_related('student').order_by('-date')


def parent_behavior(request):
    from apps.attendance.models import BehaviorLog
    return BehaviorLog.objects.filter(student__parent__user=request.user).select_related('student').order_by('-date')


def parent_fees(request):
    from apps.finance.models import Fee
    return Fee.objects.filter(student__parent__user=request.user).select_related('student')


def parent_fee_structures(request):
    from apps.finance.models import FeeStructure
    return FeeStructure.objects.filter(class_obj__students__parent__user=request.user).distinct()


def parent_payments(request):
    from apps.finance.models import Payment
    return Payment.objects.filter(fee__student__parent__user=request.user).select_related('fee__student')


def parent_book_issues(request):
    from apps.library.models import BookIssue
    return BookIssue.objects.filter(student__parent__user=request.user).select_related('student')


def parent_orders(request):
    from apps.canteen.models import OrderItem
    return OrderItem.objects.filter(student__parent__user=request.user).select_related('student')


def parent_bus(request):
    from apps.transport.models import BusStudent
    return BusStudent.objects.filter(student__parent__user=request.user).select_related('student')


def parent_ptm(request):
    from apps.ptm.models import PTMMeeting
    return PTMMeeting.objects.filter(student__parent__user=request.user).distinct()


def parent_ptm_attendees(request):
    from apps.ptm.models import PTMAttendee
    return PTMAttendee.objects.filter(parent__user=request.user)


def parent_engagement(request):
    from apps.analytics.models import ParentEngagement
    return ParentEngagement.objects.filter(parent__user=request.user)


def parent_predictions(request):
    from apps.analytics.models import Prediction
    return Prediction.objects.filter(student__parent__user=request.user).select_related('student')


def parent_events(request):
    from apps.events.models import EventParticipation
    return EventParticipation.objects.filter(student__parent__user=request.user).select_related('event', 'student')


# ------------------------------------------------------------------
# Role metadata (branding + sidebar identity)
# ------------------------------------------------------------------

ROLE_META = {
    'student': dict(label='Student', icon='graduation-cap', color='#0EA5E9'),
    'teacher': dict(label='Teacher', icon='presentation', color='#8B5CF6'),
    'parent': dict(label='Parent', icon='users', color='#10B981'),
    'staff': dict(label='Staff', icon='id-card', color='#F59E0B'),
}

# ------------------------------------------------------------------
# Module catalog (label, icon, model, list + detail column hints,
# searchable fields). The scope for each (role, module) pair lives in
# SCOPES below — a module can be shared by several roles.
# ------------------------------------------------------------------

MODULES = {
    'dashboard': dict(label='Dashboard', icon='layout-dashboard'),
    'classes': dict(label='My Classes', icon='layout-grid', model='academics.Class',
                    list_fields=['id', 'name', 'academic_year'],
                    detail_fields=['name', 'academic_year', 'description', 'created_at'],
                    search_fields=['name']),
    'children': dict(label='My Children', icon='users', model='users.Student',
                    list_fields=['id', 'admission_no', 'user', 'class_obj', 'gender'],
                    detail_fields=['admission_no', 'user', 'class_obj', 'gender', 'dob', 'address', 'phone', 'admission_date'],
                    search_fields=['admission_no', 'user__name']),
    'sections': dict(label='My Sections', icon='columns-3', model='academics.Section',
                     list_fields=['id', 'class_obj', 'name', 'capacity'],
                     detail_fields=['class_obj', 'name', 'capacity'],
                     search_fields=['name']),
    'subjects': dict(label='My Subjects', icon='book-open', model='academics.Subject',
                     list_fields=['id', 'code', 'name'],
                     detail_fields=['code', 'name', 'description'],
                     search_fields=['name', 'code']),
    'class-subjects': dict(label='My Class Subjects', icon='book-copy', model='academics.ClassSubject',
                           list_fields=['id', 'class_obj', 'subject', 'teacher'],
                           detail_fields=['class_obj', 'subject', 'teacher'],
                           search_fields=[]),
    'timetable': dict(label='Timetable', icon='calendar-clock', model='academics.Timetable',
                      list_fields=['id', 'class_obj', 'section', 'subject', 'teacher', 'day', 'start_time', 'end_time'],
                      detail_fields=['class_obj', 'section', 'subject', 'teacher', 'room', 'day', 'start_time', 'end_time'],
                      search_fields=[]),
    'exams': dict(label='Exams', icon='file-text', model='exams.Exam',
                  list_fields=['id', 'name', 'class_obj', 'subject', 'exam_type', 'date', 'total_marks'],
                  detail_fields=['name', 'class_obj', 'subject', 'teacher', 'exam_type', 'date', 'total_marks', 'description'],
                  search_fields=['name']),
    'results': dict(label='Results', icon='badge-check', model='exams.Result',
                    list_fields=['id', 'exam', 'marks_obtained', 'percentage', 'grade', 'gpa'],
                    detail_fields=['exam', 'marks_obtained', 'percentage', 'grade', 'gpa'],
                    search_fields=[]),
    'assignments': dict(label='Assignments', icon='clipboard-list', model='assignments.Assignment',
                        list_fields=['id', 'title', 'class_obj', 'subject', 'due_date', 'total_marks', 'status'],
                        detail_fields=['title', 'class_obj', 'subject', 'teacher', 'description', 'due_date', 'total_marks', 'status'],
                        search_fields=['title']),
    'submissions': dict(label='Submissions', icon='upload', model='assignments.Submission',
                        list_fields=['id', 'assignment', 'student', 'status', 'marks_obtained', 'submission_date'],
                        detail_fields=['assignment', 'student', 'status', 'marks_obtained', 'submission_date'],
                        search_fields=[]),
    'attendance': dict(label='Attendance', icon='calendar-check', model='attendance.Attendance',
                       list_fields=['id', 'student', 'date', 'status'],
                       detail_fields=['student', 'date', 'status', 'teacher'],
                       search_fields=[]),
    'behavior-logs': dict(label='Behavior Logs', icon='smile', model='attendance.BehaviorLog',
                          list_fields=['id', 'student', 'date', 'type', 'severity', 'description'],
                          detail_fields=['student', 'teacher', 'date', 'type', 'severity', 'description', 'action_taken'],
                          search_fields=['description']),
    'fees': dict(label='Fees', icon='wallet', model='finance.Fee',
                 list_fields=['id', 'student', 'fee_structure', 'amount', 'due_date', 'status'],
                 detail_fields=['student', 'fee_structure', 'amount', 'due_date', 'status'],
                 search_fields=[]),
    'fee-structures': dict(label='Fee Structures', icon='receipt-text', model='finance.FeeStructure',
                           list_fields=['id', 'title', 'class_obj', 'amount', 'frequency'],
                           detail_fields=['title', 'class_obj', 'amount', 'frequency', 'description'],
                           search_fields=['title']),
    'payments': dict(label='Payments', icon='credit-card', model='finance.Payment',
                     list_fields=['id', 'fee', 'amount_paid', 'payment_date', 'payment_method'],
                     detail_fields=['fee', 'amount_paid', 'payment_date', 'payment_method', 'transaction_id', 'receipt_no'],
                     search_fields=[]),
    'book-issues': dict(label='Book Issues', icon='book-user', model='library.BookIssue',
                        list_fields=['id', 'book', 'student', 'due_date', 'return_date', 'fine', 'status'],
                        detail_fields=['book', 'student', 'due_date', 'return_date', 'fine', 'status'],
                        search_fields=[]),
    'books': dict(label='Books', icon='library', model='library.Book',
                  list_fields=['id', 'title', 'author', 'isbn', 'total_copies', 'available_copies'],
                  detail_fields=['title', 'author', 'isbn', 'category', 'total_copies', 'available_copies', 'description'],
                  search_fields=['title', 'author', 'isbn']),
    'menu-items': dict(label='Canteen Menu', icon='utensils', model='canteen.MenuItem',
                       list_fields=['id', 'name', 'category', 'price'],
                       detail_fields=['name', 'category', 'price', 'is_available'],
                       search_fields=['name']),
    'orders': dict(label='My Orders', icon='shopping-cart', model='canteen.OrderItem',
                   list_fields=['id', 'student', 'menu_item', 'quantity', 'price', 'total_amount', 'order_date', 'status'],
                   detail_fields=['student', 'menu_item', 'quantity', 'price', 'total_amount', 'order_date', 'status'],
                   search_fields=[]),
    'bus': dict(label='My Bus', icon='bus', model='transport.BusStudent',
                list_fields=['id', 'student', 'bus', 'pickup_stop', 'drop_stop'],
                detail_fields=['student', 'bus', 'pickup_stop', 'drop_stop'],
                search_fields=[]),
    'routes': dict(label='Transport Routes', icon='route', model='transport.Route',
                   list_fields=['id', 'name', 'start_point', 'end_point'],
                   detail_fields=['name', 'start_point', 'end_point', 'description'],
                   search_fields=['name']),
    'my-events': dict(label='My Events', icon='party-popper', model='events.EventParticipation',
                      list_fields=['id', 'event', 'student'],
                      detail_fields=['event', 'student'],
                      search_fields=[]),
    'events': dict(label='Events', icon='party-popper', model='events.Event',
                   list_fields=['id', 'name', 'event_type', 'event_date', 'location'],
                   detail_fields=['name', 'event_type', 'event_date', 'location', 'organizer', 'max_participants', 'description'],
                   search_fields=['name', 'location']),
    'goals': dict(label='My Goals', icon='target', model='analytics.StudentGoal',
                  list_fields=['id', 'goal_type', 'target', 'target_date', 'progress', 'status'],
                  detail_fields=['goal_type', 'target', 'target_date', 'progress', 'status'],
                  search_fields=['target']),
    'skills': dict(label='My Skills', icon='sparkles', model='analytics.StudentSkill',
                   list_fields=['id', 'skill', 'proficiency_level', 'acquired_on'],
                   detail_fields=['skill', 'proficiency_level', 'acquired_on'],
                   search_fields=[]),
    'recommendations': dict(label='Recommendations', icon='lightbulb', model='analytics.Recommendation',
                            list_fields=['id', 'type', 'content', 'status'],
                            detail_fields=['type', 'content', 'status'],
                            search_fields=['content']),
    'predictions': dict(label='AI Predictions', icon='brain-circuit', model='analytics.Prediction',
                        list_fields=['id', 'student', 'prediction_type', 'value', 'risk_score', 'prediction_date'],
                        detail_fields=['student', 'prediction_type', 'value', 'risk_score', 'prediction_date', 'details'],
                        search_fields=[]),
    'messages': dict(label='Messages', icon='mail', model='communication.Message',
                     list_fields=['id', 'sender', 'receiver', 'subject', 'sent_at', 'is_read'],
                     detail_fields=['sender', 'receiver', 'subject', 'message', 'sent_at', 'is_read'],
                     search_fields=['subject']),
    'notifications': dict(label='Notifications', icon='bell', model='communication.Notification',
                          list_fields=['id', 'title', 'type', 'is_read'],
                          detail_fields=['title', 'type', 'message', 'is_read'],
                          search_fields=['title']),
    'ptm': dict(label='PTM Meetings', icon='handshake', model='ptm.PTMMeeting',
                list_fields=['id', 'ptm', 'student', 'teacher', 'meeting_date', 'start_time', 'end_time', 'status'],
                detail_fields=['ptm', 'student', 'teacher', 'meeting_date', 'start_time', 'end_time', 'location', 'status', 'notes'],
                search_fields=[]),
    'ptm-attendees': dict(label='My PTM Attendance', icon='user-check', model='ptm.PTMAttendee',
                          list_fields=['id', 'ptm_meeting', 'attended', 'joined_at'],
                          detail_fields=['ptm_meeting', 'attended', 'joined_at'],
                          search_fields=[]),
    'my-profile': dict(label='My Profile', icon='user-round', model='hr.Employee',
                       list_fields=['id', 'user', 'designation', 'department', 'salary', 'join_date', 'status'],
                       detail_fields=['user', 'designation', 'department', 'salary', 'join_date', 'leave_balance', 'status'],
                       search_fields=['designation']),
    'leaves': dict(label='My Leaves', icon='calendar-days', model='hr.Leave',
                   list_fields=['id', 'employee', 'leave_type', 'start_date', 'end_date', 'status'],
                   detail_fields=['employee', 'leave_type', 'start_date', 'end_date', 'reason', 'status'],
                   search_fields=['leave_type', 'status']),
    'payroll': dict(label='My Payroll', icon='banknote', model='hr.Payroll',
                    list_fields=['id', 'month', 'basic_salary', 'allowances', 'deductions', 'net_salary', 'paid_date'],
                    detail_fields=['month', 'basic_salary', 'allowances', 'deductions', 'net_salary', 'paid_date'],
                    search_fields=['month']),
    'engagement': dict(label='My Engagement', icon='heart-handshake', model='analytics.ParentEngagement',
                       list_fields=['id', 'engagement_score', 'ptm_attendance', 'response_rate', 'interaction_score'],
                       detail_fields=['engagement_score', 'ptm_attendance', 'response_rate', 'interaction_score'],
                       search_fields=[]),
    'visitors': dict(label='Visitors', icon='door-closed', model='security.Visitor',
                     list_fields=['id', 'name', 'phone', 'purpose', 'in_time', 'out_time', 'approved_by'],
                     detail_fields=['name', 'phone', 'purpose', 'in_time', 'out_time', 'approved_by'],
                     search_fields=['name', 'phone', 'purpose']),
}

# ------------------------------------------------------------------
# SCOPES: role -> {module_key: scope_callable}. Determines who sees what.
# ------------------------------------------------------------------

SCOPES = {
    'student': {
        'classes': student_classes,
        'sections': student_sections,
        'subjects': student_subjects,
        'class-subjects': student_class_subjects,
        'timetable': student_timetable,
        'exams': student_exams,
        'results': student_results,
        'assignments': student_assignments,
        'submissions': student_submissions,
        'attendance': student_attendance,
        'behavior-logs': student_behavior,
        'fees': student_fees,
        'fee-structures': student_fee_structures,
        'payments': student_payments,
        'book-issues': student_book_issues,
        'books': s_books,
        'menu-items': s_menu,
        'orders': student_orders,
        'bus': student_bus,
        'routes': s_routes,
        'my-events': student_events,
        'events': s_events,
        'goals': student_goals,
        'skills': student_skills,
        'recommendations': student_recommendations,
        'predictions': student_predictions,
        'messages': s_messages,
        'notifications': s_notifications,
    },
    'teacher': {
        'classes': teacher_classes,
        'sections': teacher_sections,
        'subjects': teacher_subjects,
        'class-subjects': teacher_class_subjects,
        'timetable': teacher_timetable,
        'exams': teacher_exams,
        'results': teacher_results,
        'assignments': teacher_assignments,
        'submissions': teacher_submissions,
        'attendance': teacher_attendance,
        'behavior-logs': teacher_behavior,
        'fee-structures': teacher_fee_structures,
        'book-issues': teacher_book_issues,
        'books': s_books,
        'menu-items': s_menu,
        'routes': s_routes,
        'events': s_events,
        'ptm': teacher_ptm,
        'messages': s_messages,
        'notifications': s_notifications,
        'my-profile': teacher_employee,
        'leaves': teacher_leaves,
        'payroll': teacher_payroll,
    },
    'staff': {
        'my-profile': staff_employee,
        'leaves': staff_leaves,
        'payroll': staff_payroll,
        'visitors': s_visitors,
        'events': s_events,
        'messages': s_messages,
        'notifications': s_notifications,
    },
    'parent': {
        'classes': parent_children,
        'sections': parent_sections,
        'subjects': parent_subjects,
        'class-subjects': parent_class_subjects,
        'timetable': parent_timetable,
        'exams': parent_exams,
        'results': parent_results,
        'assignments': parent_assignments,
        'submissions': parent_submissions,
        'attendance': parent_attendance,
        'behavior-logs': parent_behavior,
        'fees': parent_fees,
        'fee-structures': parent_fee_structures,
        'payments': parent_payments,
        'book-issues': parent_book_issues,
        'books': s_books,
        'menu-items': s_menu,
        'orders': parent_orders,
        'bus': parent_bus,
        'routes': s_routes,
        'my-events': parent_events,
        'events': s_events,
        'predictions': parent_predictions,
        'ptm': parent_ptm,
        'ptm-attendees': parent_ptm_attendees,
        'engagement': parent_engagement,
        'messages': s_messages,
        'notifications': s_notifications,
    },
}

# Human-facing module labels per role (override the shared catalog label).
LABELS = {
    'student': {'classes': 'My Classes'},
    'teacher': {'classes': 'My Classes'},
    'parent': {'classes': 'My Children'},
}
# ------------------------------------------------------------------
# GROUPS: role -> [(group_title, [module keys])] for the sidebar.
# 'dashboard' is special-cased in portal_context.
# ------------------------------------------------------------------

GROUPS = {
    'student': [
        ('Overview', ['dashboard']),
        ('Academics', ['classes', 'sections', 'subjects', 'class-subjects', 'timetable']),
        ('Assessments', ['exams', 'results', 'assignments', 'submissions']),
        ('Attendance', ['attendance', 'behavior-logs']),
        ('Finance', ['fees', 'fee-structures', 'payments']),
        ('Campus', ['books', 'book-issues', 'menu-items', 'orders', 'bus', 'routes', 'events', 'my-events']),
        ('My Growth', ['goals', 'skills', 'recommendations', 'predictions']),
        ('Communication', ['messages', 'notifications']),
    ],
    'teacher': [
        ('Overview', ['dashboard']),
        ('Academics', ['classes', 'sections', 'subjects', 'class-subjects', 'timetable']),
        ('Assessments', ['exams', 'results', 'assignments', 'submissions']),
        ('Attendance', ['attendance', 'behavior-logs']),
        ('Finance', ['fee-structures']),
        ('Campus', ['books', 'book-issues', 'menu-items', 'routes', 'events']),
        ('Meetings', ['ptm']),
        ('HR', ['my-profile', 'leaves', 'payroll']),
        ('Communication', ['messages', 'notifications']),
    ],
    'staff': [
        ('Overview', ['dashboard']),
        ('HR', ['my-profile', 'leaves', 'payroll']),
        ('Front Desk', ['visitors']),
        ('Campus', ['events']),
        ('Communication', ['messages', 'notifications']),
    ],
    'parent': [
        ('Overview', ['dashboard']),
        ('Children', ['classes']),
        ('Academics', ['sections', 'subjects', 'class-subjects', 'timetable']),
        ('Assessments', ['exams', 'results', 'assignments', 'submissions']),
        ('Attendance', ['attendance', 'behavior-logs']),
        ('Finance', ['fees', 'fee-structures', 'payments']),
        ('Campus', ['books', 'book-issues', 'menu-items', 'orders', 'bus', 'routes', 'events']),
        ('Meetings', ['ptm', 'ptm-attendees']),
        ('Insights', ['predictions', 'engagement']),
        ('Communication', ['messages', 'notifications']),
    ],
}

# ------------------------------------------------------------------
# Lookup helpers used by the portal views and templates
# ------------------------------------------------------------------

def module_cfg(key):
    """Return the catalog config for a module key (across all roles)."""
    return MODULES.get(key)


def get_module(role, key):
    """Return config for (role, module) or None if the role cannot access it."""
    if role not in SCOPES or key not in SCOPES[role]:
        return None
    if key == 'classes' and role == 'parent':
        # Parent's "classes" slot actually shows children — use the students schema.
        key = 'children'
    return MODULES.get(key)


def get_scope(role, key):
    """Return the scope callable for (role, module) or None."""
    return SCOPES.get(role, {}).get(key)


def role_allowed(role):
    """True if `role` is one of the portal roles."""
    return role in ROLE_META


def portal_context(role, active_key='dashboard'):
    """Sidebar groups + branding, mirroring the super-admin panel context."""
    groups = []
    for title, keys in GROUPS.get(role, []):
        items = []
        for key in keys:
            if key == 'dashboard':
                continue
            cfg = MODULES.get(key)
            if cfg is None or get_scope(role, key) is None:
                continue
            label = LABELS.get(role, {}).get(key, cfg['label'])
            items.append({'key': key, 'label': label, 'icon': cfg.get('icon', 'circle')})
        if items:
            groups.append({'title': title, 'items': items})
    return {
        'nav_groups': groups,
        'active_module': active_key,
        'role_key': role,
        'meta': ROLE_META.get(role, {}),
    }