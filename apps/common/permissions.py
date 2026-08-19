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
        if not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        # FIX: write access sirf admin/teacher tak — Student/Parent read-only rahenge
        return request.user.role in ['admin', 'teacher']

    def has_object_permission(self, request, view, obj):
        if request.user.role in ['admin', 'teacher']:
            return True

        student = getattr(obj, 'student', None)

        if request.user.role == 'parent':
            if student is not None:
                return student.parent.user_id == request.user.id
            # FIX: ParentEngagement has `parent` directly, not `student` — fallback
            parent = getattr(obj, 'parent', None)
            if parent is not None:
                return parent.user_id == request.user.id
            return False

        if request.user.role == 'student':
            if student is None:
                return False
            return student.user_id == request.user.id

        return False

class IsAssignedTeacherOrAdmin(BasePermission):
    """
    FIX #1: Restricts write access (POST/PUT/PATCH/DELETE) to admin/teacher only —
            prevents students/parents from creating records.
    FIX #2: Question model has no direct `teacher` field — falls back to exam.teacher
            for object-level ownership check.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role in ['admin', 'teacher']

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        if request.user.role == 'teacher':
            teacher = getattr(obj, 'teacher', None)
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
        user = request.user
        
        # Admin/Teacher -> full access
        if user.role in ['admin', 'teacher']:
            return True
        
        # Parent -> check if object belongs to their children
        if user.role == 'parent':
            # ✅ PTM object -> check class_obj students
            if hasattr(obj, 'class_obj') and obj.class_obj:
                return obj.class_obj.students.filter(parent__user=user).exists()
            
            # PTMMeeting object -> check student's parent
            if hasattr(obj, 'student') and obj.student:
                return obj.student.parent.user_id == user.id
            
            # PTMAttendee object -> check parent directly
            if hasattr(obj, 'parent') and obj.parent:
                return obj.parent.user_id == user.id
            
            # PTMAttendee with ptm_meeting fallback
            if hasattr(obj, 'ptm_meeting') and obj.ptm_meeting:
                return obj.ptm_meeting.student.parent.user_id == user.id
        
        # Student -> check if object belongs to them
        if user.role == 'student':
            if hasattr(obj, 'student') and obj.student:
                return obj.student.user_id == user.id
            if hasattr(obj, 'ptm_meeting') and obj.ptm_meeting:
                return obj.ptm_meeting.student.user_id == user.id
        
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

        target_user = getattr(obj, 'user', None)
        student_profile = getattr(target_user, 'student_profile', None) if target_user else None

        if request.user.role == 'parent' and student_profile is not None:
            return student_profile.parent.user_id == request.user.id

        if request.user.role == 'teacher' and student_profile is not None:
            return student_profile.class_obj.class_subjects.filter(teacher__user=request.user).exists()

        if request.user.role == 'staff':
            # Staff (e.g. front office/librarian) can view any student's documents
            return student_profile is not None

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