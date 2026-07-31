from rest_framework.permissions import BasePermission, SAFE_METHODS


# ---- Base role checks ----------------------------------------------------
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'teacher'


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'student'


class IsParent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'parent'


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'staff'


class IsAdminOrTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'teacher']


class IsAdminOrStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'staff']


# ---- Combined role checks -----------------------------------------
class IsAdminOrTeacherOrParent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'teacher', 'parent']


class IsAdminOrTeacherOrStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'teacher', 'student']


class IsAdminOrTeacherOrStudentOrParent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'teacher', 'student', 'parent']


class IsAdminOrTeacherOrStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'teacher', 'staff']


class IsAdminOrParent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'parent']


class IsAdminOrStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'student']


# ---- Read/Write ------------------------------------------------------------
class ReadOnlyOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role == 'admin'


# ---- Object-level ownership checks ----------------------------------------
class IsOwnerOrAdmin(BasePermission):
    """Generic owner check — used only where obj truly has `user` field."""
    # ✅ FIX #4: Add has_permission to prevent anonymous 500
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        return getattr(obj, 'user_id', None) == request.user.id


class IsSenderOrReceiverOrAdmin(BasePermission):
    """Fixes the Message bug — Message has sender/receiver, not user."""
    # ✅ FIX #4: Add has_permission to prevent anonymous 500
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        return obj.sender_id == request.user.id or obj.receiver_id == request.user.id


class IsSelfOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        return getattr(obj, 'user_id', None) == request.user.id


class IsSelfStudentOrAdminOrTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.role in ['admin', 'teacher']:
            return True
        student = getattr(obj, 'student', None)
        return student is not None and student.user_id == request.user.id


class IsOwnerParentOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.role in ['admin', 'teacher']:
            return True
        student = getattr(obj, 'student', None)
        if student is None:
            return False
        if request.user.role == 'parent':
            return student.parent.user_id == request.user.id
        if request.user.role == 'student':
            return student.user_id == request.user.id
        return False


class IsAssignedTeacherOrAdmin(BasePermission):
    """✅ FIX #1: Question model has no direct teacher field — fallback to exam.teacher."""
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        if request.user.role == 'teacher':
            teacher = getattr(obj, 'teacher', None)
            # ✅ FIX: Question model has no direct teacher — fallback to exam.teacher
            if teacher is None:
                exam = getattr(obj, 'exam', None)
                teacher = getattr(exam, 'teacher', None) if exam else None
            return teacher is not None and teacher.user_id == request.user.id
        return request.method in SAFE_METHODS


# ---- Module-specific composites -------------------------------------------
class FinancePermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role == 'admin'

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        if request.method not in SAFE_METHODS:
            return False

        # Fee has `student` directly
        student = getattr(obj, 'student', None)

        # Payment and FeeHistory have `fee` instead — fall back through it
        if student is None:
            fee = getattr(obj, 'fee', None)
            if fee is not None:
                student = getattr(fee, 'student', None)

        if student is None:
            return False
        if request.user.role == 'student':
            return student.user_id == request.user.id
        if request.user.role == 'parent':
            return student.parent.user_id == request.user.id
        return False

class HRPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.role == 'admin':
            return True
        return request.method in SAFE_METHODS and request.user.role in ['teacher', 'staff']

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        employee = getattr(obj, 'employee', None)
        return employee is not None and employee.user_id == request.user.id


# ✅ FIX #3: New LeavePermission
class LeavePermission(BasePermission):
    """Employee can create/view own leave; only admin can approve/reject."""
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        # Employee can view/edit their own leave
        if obj.employee.user_id == request.user.id:
            return True
        return False


class LibraryPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.role in ['admin', 'staff']

    def has_object_permission(self, request, view, obj):
        if request.user.role in ['admin', 'staff']:
            return True
        student = getattr(obj, 'student', None)
        if student is not None:
            if request.user.role == 'student':
                return student.user_id == request.user.id
            if request.user.role == 'parent':
                return student.parent.user_id == request.user.id
        return request.method in SAFE_METHODS


class TransportPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.role in ['admin', 'staff']

    def has_object_permission(self, request, view, obj):
        if request.user.role in ['admin', 'staff']:
            return True
        student = getattr(obj, 'student', None)
        if student is None:
            return request.method in SAFE_METHODS
        if request.user.role == 'student':
            return student.user_id == request.user.id
        if request.user.role == 'parent':
            return student.parent.user_id == request.user.id
        return False


class AuditLogPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method not in SAFE_METHODS:
            return False
        return request.user.is_authenticated and request.user.role == 'admin'


class PTMPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role in ['admin', 'teacher']

    def has_object_permission(self, request, view, obj):
        if request.user.role in ['admin', 'teacher']:
            return True

        # Direct fields (PTM, PTMMeeting objects have these)
        student = getattr(obj, 'student', None)
        parent = getattr(obj, 'parent', None)

        # PTMAttendee doesn't have `student` directly — fall back to ptm_meeting.student
        if student is None:
            ptm_meeting = getattr(obj, 'ptm_meeting', None)
            if ptm_meeting is not None:
                student = getattr(ptm_meeting, 'student', None)

        if request.user.role == 'parent':
            if parent is not None:
                return parent.user_id == request.user.id
            if student is not None:
                return student.parent.user_id == request.user.id

        if request.user.role == 'student' and student is not None:
            return student.user_id == request.user.id

        return False

class CanteenPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.role in ['admin', 'staff', 'student']

    def has_object_permission(self, request, view, obj):
        if request.user.role in ['admin', 'staff']:
            return True
        student = getattr(obj, 'student', None)
        if student is not None:
            if request.user.role == 'student':
                return student.user_id == request.user.id
            if request.user.role == 'parent':
                return student.parent.user_id == request.user.id
        return False


class EventsPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.role in ['admin', 'staff']

    def has_object_permission(self, request, view, obj):
        if request.user.role in ['admin', 'staff']:
            return True
        student = getattr(obj, 'student', None)
        if request.user.role == 'student' and student is not None:
            return student.user_id == request.user.id
        if request.user.role == 'parent' and student is not None:
            return student.parent.user_id == request.user.id
        return request.method in SAFE_METHODS


class DocumentsPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        if getattr(obj, 'user_id', None) == request.user.id:
            return True
        if request.user.role == 'parent':
            target_user = getattr(obj, 'user', None)
            student_profile = getattr(target_user, 'student_profile', None)
            if student_profile is not None:
                return student_profile.parent.user_id == request.user.id
        return False


class SecurityPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.role in ['admin', 'staff']:
            return True
        return request.method in SAFE_METHODS and request.user.role == 'parent'

    def has_object_permission(self, request, view, obj):
        if request.user.role in ['admin', 'staff']:
            return True
        if request.user.role == 'parent' and request.method in SAFE_METHODS:
            student = getattr(obj, 'student', None)
            return student is not None and student.parent.user_id == request.user.id
        return False


class AutomationPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class NotificationLogPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method not in SAFE_METHODS:
            return False
        return request.user.is_authenticated and request.user.role == 'admin'