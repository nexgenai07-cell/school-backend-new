"""
Labeled multi-tenant seed data.

Runs once per school tenant so every record carries the school's label in its
human-readable fields (names/titles) — making cross-tenant isolation visually
obvious when inspecting data.

Globally-unique columns (User.email, Student.admission_no, Subject.code,
Book.isbn, Bus.bus_no) are slug-prefixed so repeated runs across schools never
collide on database constraints.

Usage:
    python manage.py seed --school=school-a --label-prefix="School A" --enable-feature student-blood-group
    python manage.py seed --school=school-b --label-prefix="School B"
    python manage.py seed --school=school-c --label-prefix="School C"
"""
from datetime import date
from decimal import Decimal

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand

from apps.academics.models import Class, ClassSubject, Room, Section, Subject, Timetable
from apps.analytics.models import SkillMapping, StudentSkill
from apps.attendance.models import Attendance
from apps.canteen.models import Category, MenuItem
from apps.exams.models import Exam, Question, Result
from apps.finance.models import Fee, FeeStructure
from apps.hr.models import Department, Employee
from apps.library.models import Book
from apps.tenants.context import current_tenant
from apps.tenants.models import Feature, School, SchoolFeature
from apps.transport.models import Bus, BusStop, BusStudent, Route
from apps.users.models import Parent, Staff, Student, Teacher, User


class Command(BaseCommand):
    help = 'Seed labeled sample data for a single school tenant.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--school', required=True,
            help='Tenant slug, e.g. school-a',
        )
        parser.add_argument(
            '--label-prefix', required=True,
            help='Human-readable prefix baked into every record, e.g. "School A"',
        )
        parser.add_argument(
            '--domain', default=None,
            help='Custom domain for the tenant (default: <slug-no-dashes>.nxgenai.pro)',
        )
        parser.add_argument(
            '--enable-feature', action='append', dest='enable_features',
            metavar='FEATURE_KEY',
            help='Feature key to enable for this school (repeatable)',
        )

    def handle(self, *args, **options):
        slug = options['school'].strip().lower()
        pfx = options['label_prefix'].strip()
        domain = options.get('domain') or f"{slug.replace('-', '')}.nxgenai.pro"
        enable_features = [k.strip() for k in (options.get('enable_features') or []) if k.strip()]

        school, created = School.objects.get_or_create(
            slug=slug,
            defaults={'name': pfx, 'domain': domain},
        )
        if created:
            self.stdout.write(self.style.SUCCESS(
                f"🏫 Created school '{school.name}' (slug={school.slug}, domain={school.domain})"))
        else:
            self.stdout.write(f"🏫 School '{school.name}' already exists — topping up data")

        self._ensure_features(school, enable_features)

        token = current_tenant.set(school)
        try:
            self._seed(school=school, pfx=pfx, code=self._short_code(slug))
        finally:
            current_tenant.reset(token)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _short_code(slug):
        """'school-a' -> 'A'; falls back to full uppercased slug."""
        if '-' in slug:
            return slug.split('-', 1)[1].replace('-', '').upper() or slug.upper()
        return slug.upper()

    def _ensure_features(self, school, feature_keys):
        for key in feature_keys:
            feature, f_created = Feature.objects.get_or_create(
                key=key,
                defaults={
                    'name': key.replace('-', ' ').title(),
                    'description': f'Auto-registered while seeding {school.slug}',
                    'default_enabled': False,
                },
            )
            SchoolFeature.objects.update_or_create(
                school=school, feature=feature,
                defaults={'is_enabled': True},
            )
            state = 'registered + enabled' if f_created else 'enabled'
            self.stdout.write(self.style.SUCCESS(f"   ⭐ Feature '{key}' {state} for {school.slug}"))

    # ------------------------------------------------------------------
    # Seeding
    # ------------------------------------------------------------------
    def _seed(self, school, pfx, code):
        ed = f"{school.slug.replace('-', '')}.nxgenai.pro"  # email domain

        # ========================================
        # 1. DEPARTMENTS
        # ========================================
        self.stdout.write('📚 Creating departments...')
        dept_names = ['Academics', 'Human Resources', 'Finance',
                      'Administration', 'Canteen', 'Transport', 'Library']
        depts = {}
        for name in dept_names:
            depts[name], _ = Department.objects.get_or_create(
                name=f"[{pfx}] {name}",
                defaults={'description': f'{name} Department ({pfx})'},
            )
        dept_academics = depts['Academics']
        dept_hr = depts['Human Resources']

        # ========================================
        # 2. USERS + PROFILES
        # ========================================
        self.stdout.write('👤 Creating users...')

        admin_user, _ = User.objects.get_or_create(
            email=f"admin@{ed}",
            defaults={
                'name': f'{pfx} - Admin User',
                'role': 'admin',
                'password': make_password('admin123'),
                'is_staff': True,       # Django-admin access only (no superuser!)
                'status': 'active',
            },
        )

        teacher_specs = [
            ('teacher.ali@', 'Mr. Ali Ahmed', 'Mathematics'),
            ('teacher.fatima@', 'Ms. Fatima Zahra', 'English'),
            ('teacher.ahmed@', 'Mr. Ahmed Hassan', 'Science'),
        ]
        teacher_users, teachers = [], []
        for local, human, specialization in teacher_specs:
            t_user, _ = User.objects.get_or_create(
                email=f"{local}{ed}",
                defaults={
                    'name': f'{pfx} - {human}',
                    'role': 'teacher',
                    'password': make_password('teacher123'),
                    'status': 'active',
                },
            )
            employee, _ = Employee.objects.get_or_create(
                user=t_user,
                defaults={
                    'designation': 'Teacher',
                    'department': dept_academics,
                    'salary': Decimal('45000.00'),
                    'join_date': date(2023, 8, 1),
                },
            )
            profile, _ = Teacher.objects.get_or_create(
                user=t_user,
                defaults={
                    'employee': employee,
                    'qualification': 'MSc',
                    'join_date': date(2023, 8, 1),
                    'subject_specialization': specialization,
                },
            )
            teacher_users.append(t_user)
            teachers.append(profile)

        staff_user, _ = User.objects.get_or_create(
            email=f"staff.hr@{ed}",
            defaults={
                'name': f'{pfx} - Ms. Sara (HR Staff)',
                'role': 'staff',
                'password': make_password('staff123'),
                'status': 'active',
            },
        )
        staff_employee, _ = Employee.objects.get_or_create(
            user=staff_user,
            defaults={
                'designation': 'HR Officer',
                'department': dept_hr,
                'salary': Decimal('35000.00'),
                'join_date': date(2023, 9, 15),
            },
        )
        Staff.objects.get_or_create(
            user=staff_user,
            defaults={
                'employee': staff_employee,
                'designation': 'HR Officer',
                'department': f'[HR] {pfx}',
                'join_date': date(2023, 9, 15),
            },
        )

        parent_specs = [
            ('parent.ali@', 'Ali Raza (Parent)', 'Engineer'),
            ('parent.fatima@', 'Fatima Bibi (Parent)', 'Doctor'),
        ]
        parents = []
        for local, human, occupation in parent_specs:
            p_user, _ = User.objects.get_or_create(
                email=f"{local}{ed}",
                defaults={
                    'name': f'{pfx} - {human}',
                    'role': 'parent',
                    'password': make_password('parent123'),
                    'status': 'active',
                },
            )
            profile, _ = Parent.objects.get_or_create(
                user=p_user,
                defaults={'occupation': occupation},
            )
            parents.append(profile)

        student_names = [
            ('Ahmed Khan', 'male'), ('Fatima Noor', 'female'), ('Bilal Raza', 'male'),
            ('Ayesha Siddiqui', 'female'), ('Usman Tariq', 'male'),
        ]
        blood_groups = ['B+', 'O+', 'A-', 'AB+', 'O-']
        student_users, students = [], []
        for i, (human, gender) in enumerate(student_names, start=1):
            s_user, _ = User.objects.get_or_create(
                email=f"student{i}@{ed}",
                defaults={
                    'name': f'{pfx} - {human}',
                    'role': 'student',
                    'password': make_password('student123'),
                    'status': 'active',
                },
            )
            student_users.append(s_user)
            students.append({'user': s_user, 'gender': gender, 'idx': i})
            if i % 5 == 0:
                self.stdout.flush()

        # ========================================
        # 3. ACADEMICS
        # ========================================
        self.stdout.write(f'[seed:step=academics]', ending='\n')
        self.stdout.flush()
        self.stdout.write('🎓 Creating academics...')
        klass, _ = Class.objects.get_or_create(
            name=f'{pfx} - Grade 5',
            defaults={'description': f'Grade 5 ({pfx})', 'academic_year': '2024-2025'},
        )
        section, _ = Section.objects.get_or_create(
            class_obj=klass, name='A',
            defaults={'capacity': 40},
        )
        room, _ = Room.objects.get_or_create(
            name=f'{pfx} - Room 101',
            defaults={'location': 'Main Block', 'capacity': 40},
        )

        subject_specs = [
            ('Mathematics', 'MATH', teacher_users[0]),
            ('English', 'ENG', teacher_users[1]),
            ('Science', 'SCI', teacher_users[2]),
        ]
        subjects = []
        for subj_name, subj_code, t_user in subject_specs:
            subject, _ = Subject.objects.get_or_create(
                code=f"{subj_code}-{code}",
                defaults={'name': f'{pfx} - {subj_name}'},
            )
            teacher_profile = Teacher.objects.get(user=t_user)
            ClassSubject.objects.get_or_create(
                class_obj=klass, subject=subject, teacher=teacher_profile,
            )
            subjects.append((subject, teacher_profile))

        # ========================================
        # 4. STUDENT PROFILES
        # ========================================
        self.stdout.write('🧑‍🎓 Creating student profiles...')
        for entry in students:
            i = entry['idx']
            profile, _ = Student.objects.get_or_create(
                user=entry['user'],
                defaults={
                    'class_obj': klass,
                    'parent': parents[(i - 1) % len(parents)],
                    'admission_no': f'SCH-{code}-{i:03d}',
                    'dob': date(2013, 3, i),
                    'gender': entry['gender'],
                    'address': f'{pfx} Campus Address, Lahore',
                    'phone': f'+92-300-{code}-00{i}',
                    'admission_date': date(2024, 4, 1),
                    'blood_group': blood_groups[(i - 1) % len(blood_groups)],
                },
            )
            entry['profile'] = profile

        # ========================================
        # 5. TIMETABLE (one slot)
        # ========================================
        math_subject, math_teacher = subjects[0]
        Timetable.objects.get_or_create(
            class_obj=klass, section=section, subject=math_subject, day='mon',
            defaults={
                'teacher': math_teacher,
                'room': room,
                'start_time': '08:00',
                'end_time': '08:45',
            },
        )

        # ========================================
        # 6. FINANCE
        # ========================================
        self.stdout.write('💰 Creating fees...')
        self.stdout.flush()
        fee_structure, _ = FeeStructure.objects.get_or_create(
            class_obj=klass, title=f'{pfx} - Monthly Tuition',
            defaults={
                'amount': Decimal('5000.00'),
                'frequency': 'monthly',
                'description': f'Tuition fee ({pfx})',
            },
        )
        for entry in students:
            Fee.objects.get_or_create(
                student=entry['profile'], fee_structure=fee_structure,
                defaults={
                    'amount': Decimal('5000.00'),
                    'due_date': date(2024, 6, 10),
                    'status': 'pending',
                },
            )

        # ========================================
        # 7. LIBRARY
        # ========================================
        lib_category, _ = Category.objects.get_or_create(
            name=f'{pfx} - General',
            defaults={'description': f'General books ({pfx})'},
        )
        Book.objects.get_or_create(
            isbn=f'ISBN-{code}-001',
            defaults={
                'title': f'{pfx} - Introduction to Algebra',
                'author': f'{pfx} Press',
                'category': lib_category,
                'total_copies': 5,
                'available_copies': 5,
            },
        )

        # ========================================
        # 8. CANTEEN
        # ========================================
        food_category, _ = Category.objects.get_or_create(
            name=f'{pfx} - Food',
            defaults={'description': f'Canteen food ({pfx})'},
        )
        MenuItem.objects.get_or_create(
            name=f'{pfx} - Chicken Sandwich',
            defaults={
                'price': Decimal('150.00'),
                'category': food_category,
            },
        )

        # ========================================
        # 9. TRANSPORT
        # ========================================
        self.stdout.write('[seed:step=transport]')
        self.stdout.flush()
        bus, _ = Bus.objects.get_or_create(
            bus_no=f'BUS-{code}-01',
            defaults={'capacity': 30},
        )
        route, _ = Route.objects.get_or_create(
            name=f'{pfx} - Route 1',
            defaults={'start_point': f'{pfx} Gate', 'end_point': 'City Center'},
        )
        stop1, _ = BusStop.objects.get_or_create(
            route=route, stop_order=1,
            defaults={'name': f'{pfx} - Stop 1 (Main Gate)'},
        )
        stop2, _ = BusStop.objects.get_or_create(
            route=route, stop_order=2,
            defaults={'name': f'{pfx} - Stop 2 (Bazaar)'},
        )
        BusStudent.objects.get_or_create(
            student=students[0]['profile'], bus=bus,
            defaults={'pickup_stop': stop1, 'drop_stop': stop2},
        )

        # ========================================
        # 10. EXAMS
        # ========================================
        self.stdout.write('📝 Creating exams...')
        exam, _ = Exam.objects.get_or_create(
            class_obj=klass, subject=math_subject, exam_type='term',
            defaults={
                'name': f'{pfx} - Mathematics Midterm',
                'date': date(2024, 5, 20),
                'total_marks': 100,
                'teacher': math_teacher,
                'description': f'Midterm exam ({pfx})',
            },
        )
        Question.objects.get_or_create(
            exam=exam, question_text=f'What is 12 x 8? ({pfx})',
            defaults={
                'question_type': 'mcq',
                'marks': 10,
                'options': {'a': '88', 'b': '96', 'c': '104', 'd': '108'},
                'correct_answer': 'b',
                'answer_text': '12 x 8 = 96',
            },
        )
        Result.objects.get_or_create(
            exam=exam, student=students[0]['profile'],
            defaults={'marks_obtained': 85},
        )

        # ========================================
        # 11. ATTENDANCE
        # ========================================
        Attendance.objects.get_or_create(
            student=students[0]['profile'], date=date(2024, 6, 3),
            defaults={'status': 'present', 'teacher': math_teacher, 'marked_by': math_teacher},
        )

        # ========================================
        # 12. ANALYTICS
        # ========================================
        skill, _ = SkillMapping.objects.get_or_create(
            name=f'{pfx} - Mathematics',
            defaults={'category': 'Academic', 'description': f'Mathematical skills ({pfx})'},
        )
        StudentSkill.objects.get_or_create(
            student=students[0]['profile'], skill=skill,
            defaults={'proficiency_level': 'intermediate', 'acquired_on': date(2024, 1, 15)},
        )

        # ========================================
        # 13. SUMMARY
        # ========================================
        self.stdout.write(self.style.SUCCESS(f'\n✅ Seed data for {pfx} completed!'))
        self.stdout.write('\n📊 Summary (tenant-scoped counts):')
        self.stdout.write(f'   👤 Users: {User.objects.count()}')
        self.stdout.write(f'   🎓 Students: {Student.objects.count()}')
        self.stdout.write(f'   👨‍🏫 Teachers: {Teacher.objects.count()}')
        self.stdout.write(f'   👨‍👩‍👧 Parents: {Parent.objects.count()}')
        self.stdout.write(f'   🏛️ Departments: {Department.objects.count()}')
        self.stdout.write(f'   📚 Classes: {Class.objects.count()}')
        self.stdout.write(f'   📖 Subjects: {Subject.objects.count()}')
        self.stdout.write(f'   📝 Exams: {Exam.objects.count()}')
        self.stdout.write(f'   💰 Fees: {Fee.objects.count()}')
        self.stdout.write(f'   📚 Books: {Book.objects.count()}')
        self.stdout.write(f'   🚌 Buses: {Bus.objects.count()}')
        self.stdout.write('\n🔑 Login credentials:')
        self.stdout.write(f'   Admin:    admin@{ed} / admin123')
        self.stdout.write(f'   Teacher:  teacher.ali@{ed} / teacher123')
        self.stdout.write(f'   Student:  student1@{ed} / student123')
        self.stdout.write(f'   Parent:   parent.ali@{ed} / parent123')
        self.stdout.write(f'   Staff:    staff.hr@{ed} / staff123')
