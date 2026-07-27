from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from datetime import datetime, timedelta, date
from decimal import Decimal

from apps.users.models import User, Student, Teacher, Staff, Parent
from apps.academics.models import Class, Section, Subject, Room, ClassSubject, Timetable
from apps.hr.models import Department, Employee
from apps.finance.models import FeeStructure, Fee
from apps.library.models import Book
from apps.transport.models import Bus, Route, BusStop, BusStudent
from apps.canteen.models import Category, MenuItem
from apps.exams.models import Exam, Question, Result
from apps.attendance.models import Attendance
from apps.analytics.models import SkillMapping, StudentSkill


class Command(BaseCommand):
    help = 'Seed database with sample data for testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🌱 Starting seed data insertion...'))
        
        # ========================================
        # 1. CREATE DEPARTMENTS
        # ========================================
        self.stdout.write('📚 Creating departments...')
        dept_academics, _ = Department.objects.get_or_create(
            name="Academics",
            defaults={"description": "Academic Department"}
        )
        dept_hr, _ = Department.objects.get_or_create(
            name="Human Resources",
            defaults={"description": "HR Department"}
        )
        
        # ========================================
        # 2. CREATE USERS
        # ========================================
        self.stdout.write('👤 Creating users...')
        
        # Admin
        admin_user, _ = User.objects.get_or_create(
            email="admin@school.com",
            defaults={
                "name": "Admin User",
                "role": "admin",
                "password": make_password("admin123"),
                "is_staff": True,
                "is_superuser": True,
                "status": "active"
            }
        )
        
        # Teachers
        teacher1, _ = User.objects.get_or_create(
            email="teacher.ali@school.com",
            defaults={
                "name": "Mr. Ali Ahmed",
                "role": "teacher",
                "password": make_password("teacher123"),
                "status": "active"
            }
        )
        teacher2, _ = User.objects.get_or_create(
            email="teacher.fatima@school.com",
            defaults={
                "name": "Ms. Fatima Khan",
                "role": "teacher",
                "password": make_password("teacher123"),
                "status": "active"
            }
        )
        
        # Students
        students = []
        for i in range(1, 4):
            student, _ = User.objects.get_or_create(
                email=f"student{i}@school.com",
                defaults={
                    "name": f"Student {i}",
                    "role": "student",
                    "password": make_password("student123"),
                    "status": "active"
                }
            )
            students.append(student)
        
        # Parents
        parent1, _ = User.objects.get_or_create(
            email="parent.ali@school.com",
            defaults={
                "name": "Parent of Student 1",
                "role": "parent",
                "password": make_password("parent123"),
                "status": "active"
            }
        )
        
        # Staff
        staff_user, _ = User.objects.get_or_create(
            email="staff.hr@school.com",
            defaults={
                "name": "HR Staff",
                "role": "staff",
                "password": make_password("staff123"),
                "status": "active"
            }
        )
        
        # ========================================
        # 3. CREATE CLASSES & SUBJECTS
        # ========================================
        self.stdout.write('📖 Creating classes and subjects...')
        
        class_10, _ = Class.objects.get_or_create(
            name="Class 10",
            defaults={"description": "Class 10 - Matriculation", "academic_year": "2024-2025"}
        )
        class_9, _ = Class.objects.get_or_create(
            name="Class 9",
            defaults={"description": "Class 9 - Matriculation", "academic_year": "2024-2025"}
        )
        
        # Sections
        section_a, _ = Section.objects.get_or_create(
            class_obj=class_10,
            defaults={"name": "A", "capacity": 30}
        )
        section_9a, _ = Section.objects.get_or_create(
            class_obj=class_9,
            defaults={"name": "A", "capacity": 30}
        )
        
        # Subjects
        math, _ = Subject.objects.get_or_create(
            code="MATH101",
            defaults={"name": "Mathematics", "description": "Mathematics subject"}
        )
        physics, _ = Subject.objects.get_or_create(
            code="PHY101",
            defaults={"name": "Physics", "description": "Physics subject"}
        )
        
        # Rooms
        room_101, _ = Room.objects.get_or_create(
            name="Room 101",
            defaults={"location": "Building A, Floor 1", "capacity": 30}
        )
        
        # ========================================
        # 4. CREATE TEACHER PROFILES
        # ========================================
        self.stdout.write('👨‍🏫 Creating teacher profiles...')
        
        teacher1_obj, _ = Teacher.objects.get_or_create(
            user=teacher1,
            defaults={
                "qualification": "MSc Mathematics",
                "experience": 10,
                "join_date": date(2015, 1, 1),
                "subject_specialization": "Mathematics",
                "phone": "0300-1111111",
                "status": "active"
            }
        )
        teacher2_obj, _ = Teacher.objects.get_or_create(
            user=teacher2,
            defaults={
                "qualification": "MSc Physics",
                "experience": 8,
                "join_date": date(2016, 6, 1),
                "subject_specialization": "Physics",
                "phone": "0300-2222222",
                "status": "active"
            }
        )
        
        # ========================================
        # 5. CREATE EMPLOYEES
        # ========================================
        self.stdout.write('👔 Creating employees...')
        
        Employee.objects.get_or_create(
            user=teacher1,
            defaults={
                "designation": "Senior Teacher",
                "department": dept_academics,
                "salary": Decimal('80000.00'),
                "join_date": date(2015, 1, 1),
                "status": "active",
                "leave_balance": 20
            }
        )
        Employee.objects.get_or_create(
            user=staff_user,
            defaults={
                "designation": "HR Manager",
                "department": dept_hr,
                "salary": Decimal('70000.00'),
                "join_date": date(2018, 3, 1),
                "status": "active",
                "leave_balance": 15
            }
        )
        
        # ========================================
        # 6. CREATE PARENT & STUDENT PROFILES
        # ========================================
        self.stdout.write('👨‍👩‍👧 Creating parent and student profiles...')
        
        parent1_obj, _ = Parent.objects.get_or_create(
            user=parent1,
            defaults={
                "occupation": "Engineer",
                "phone": "0300-4444444",
                "address": "House 1, Street 1, Lahore"
            }
        )
        
        student_objs = []
        for i, student_user in enumerate(students):
            student_obj, _ = Student.objects.get_or_create(
                user=student_user,
                defaults={
                    "class_obj": class_10 if i < 2 else class_9,
                    "parent": parent1_obj,
                    "admission_no": f"STU-2024-{i+1:04d}",
                    "dob": date(2008, 1, 1 + i),
                    "gender": "male" if i % 2 == 0 else "female",
                    "address": f"Student {i+1} Address",
                    "phone": f"0300-{i+1:04d}",
                    "admission_date": date(2024, 1, 1)
                }
            )
            student_objs.append(student_obj)
        
        # ========================================
        # 7. CREATE CLASS-SUBJECT ASSIGNMENTS
        # ========================================
        self.stdout.write('📚 Creating class-subject assignments...')
        
        ClassSubject.objects.get_or_create(
            class_obj=class_10,
            subject=math,
            defaults={"teacher": teacher1_obj}
        )
        ClassSubject.objects.get_or_create(
            class_obj=class_10,
            subject=physics,
            defaults={"teacher": teacher2_obj}
        )
        ClassSubject.objects.get_or_create(
            class_obj=class_9,
            subject=math,
            defaults={"teacher": teacher1_obj}
        )
        
        # ========================================
        # 8. CREATE TIMETABLE
        # ========================================
        self.stdout.write('🕐 Creating timetable...')
        
        Timetable.objects.get_or_create(
            class_obj=class_10,
            section=section_a,
            subject=math,
            teacher=teacher1_obj,
            room=room_101,
            day='mon',
            start_time='08:00',
            end_time='08:45'
        )
        Timetable.objects.get_or_create(
            class_obj=class_10,
            section=section_a,
            subject=physics,
            teacher=teacher2_obj,
            room=room_101,
            day='mon',
            start_time='08:45',
            end_time='09:30'
        )
        
        # ========================================
        # 9. CREATE FEE STRUCTURES
        # ========================================
        self.stdout.write('💰 Creating fee structures...')
        
        fee_10, _ = FeeStructure.objects.get_or_create(
            class_obj=class_10,
            title="Tuition Fee - Class 10",
            defaults={
                "amount": Decimal('15000.00'),
                "frequency": "monthly",
                "description": "Monthly tuition fee for Class 10"
            }
        )
        
        # ========================================
        # 10. CREATE FEES FOR STUDENTS
        # ========================================
        self.stdout.write('📝 Creating student fees...')
        
        for student_obj in student_objs[:2]:
            Fee.objects.get_or_create(
                student=student_obj,
                fee_structure=fee_10,
                defaults={
                    "amount": Decimal('15000.00'),
                    "due_date": date(2024, 12, 31),
                    "status": "pending"
                }
            )
        
        # ========================================
        # 11. CREATE BOOKS
        # ========================================
        self.stdout.write('📚 Creating books...')
        
        Book.objects.get_or_create(
            isbn="978-969-1234-01-5",
            defaults={
                "title": "Mathematics Grade 10",
                "author": "Dr. Ahmed",
                "total_copies": 10,
                "available_copies": 10
            }
        )
        Book.objects.get_or_create(
            isbn="978-969-1234-02-2",
            defaults={
                "title": "Physics Grade 10",
                "author": "Prof. Khan",
                "total_copies": 8,
                "available_copies": 8
            }
        )
        
        # ========================================
        # 12. CREATE BUSES AND ROUTES
        # ========================================
        self.stdout.write('🚌 Creating transport data...')
        
        bus_1, _ = Bus.objects.get_or_create(
            bus_no="BUS-001",
            defaults={"capacity": 30, "status": "active"}
        )
        
        route_1, _ = Route.objects.get_or_create(
            name="Route 1 - Lahore",
            defaults={
                "description": "Lahore to School",
                "start_point": "Lahore",
                "end_point": "School"
            }
        )
        
        stop_1, _ = BusStop.objects.get_or_create(
            route=route_1,
            name="Stop 1 - Main Market",
            defaults={"stop_order": 1}
        )
        stop_3, _ = BusStop.objects.get_or_create(
            route=route_1,
            name="Stop 3 - School",
            defaults={"stop_order": 3}
        )
        
        for student_obj in student_objs[:2]:
            BusStudent.objects.get_or_create(
                bus=bus_1,
                student=student_obj,
                defaults={
                    "pickup_stop": stop_1,
                    "drop_stop": stop_3
                }
            )
        
        # ========================================
        # 13. CREATE CANTEEN DATA
        # ========================================
        self.stdout.write('🍽️ Creating canteen data...')
        
        cat_burger, _ = Category.objects.get_or_create(
            name="Burgers",
            defaults={"description": "Burger Category"}
        )
        
        MenuItem.objects.get_or_create(
            name="Chicken Burger",
            defaults={
                "price": Decimal('250.00'),
                "category": cat_burger,
                "is_available": True
            }
        )
        MenuItem.objects.get_or_create(
            name="Cold Drink",
            defaults={
                "price": Decimal('100.00'),
                "category": cat_burger,
                "is_available": True
            }
        )
        
        # ========================================
        # 14. CREATE EXAM DATA
        # ========================================
        self.stdout.write('📝 Creating exam data...')
        
        exam_1, _ = Exam.objects.get_or_create(
            name="Term Exam 1 - Math Class 10",
            defaults={
                "class_obj": class_10,
                "subject": math,
                "teacher": teacher1_obj,
                "exam_type": "term",
                "date": date(2024, 12, 15),
                "total_marks": 100,
                "description": "First term exam for Class 10 Mathematics"
            }
        )
        
        Question.objects.get_or_create(
            exam=exam_1,
            question_text="What is 2+2?",
            defaults={
                "question_type": "mcq",
                "answer_text": "4",
                "marks": 5
            }
        )
        
        for student_obj in student_objs[:2]:
            Result.objects.get_or_create(
                exam=exam_1,
                student=student_obj,
                defaults={
                    "marks_obtained": 75 + student_obj.id % 20,
                    "percentage": Decimal('75.00'),
                    "grade": None,
                    "gpa": Decimal('3.00')
                }
            )
        
        # ========================================
        # 15. CREATE ATTENDANCE DATA
        # ========================================
        self.stdout.write('📋 Creating attendance data...')
        
        today = date.today()
        for student_obj in student_objs:
            for i in range(3):
                att_date = today - timedelta(days=i)
                if att_date.weekday() < 5:
                    status = 'present' if i % 2 == 0 else 'absent'
                    Attendance.objects.get_or_create(
                        student=student_obj,
                        date=att_date,
                        defaults={
                            "status": status,
                            "teacher": teacher1_obj,
                            "marked_by": teacher1_obj
                        }
                    )
        
        # ========================================
        # 16. CREATE SKILL MAPPINGS
        # ========================================
        self.stdout.write('🎯 Creating skill mappings...')
        
        skill_math, _ = SkillMapping.objects.get_or_create(
            name="Mathematics",
            defaults={
                "category": "Academic",
                "description": "Mathematical skills"
            }
        )
        
        for student_obj in student_objs[:2]:
            StudentSkill.objects.get_or_create(
                student=student_obj,
                skill=skill_math,
                defaults={
                    "proficiency_level": "intermediate",
                    "acquired_on": date(2024, 1, 1)
                }
            )
        
        # ========================================
        # 17. SUMMARY
        # ========================================
        self.stdout.write(self.style.SUCCESS('\n✅ Seed data inserted successfully!'))
        self.stdout.write('\n📊 Summary:')
        self.stdout.write(f'   👤 Users: {User.objects.count()}')
        self.stdout.write(f'   🎓 Students: {Student.objects.count()}')
        self.stdout.write(f'   👨‍🏫 Teachers: {Teacher.objects.count()}')
        self.stdout.write(f'   👨‍👩‍👧 Parents: {Parent.objects.count()}')
        self.stdout.write(f'   📚 Classes: {Class.objects.count()}')
        self.stdout.write(f'   📖 Subjects: {Subject.objects.count()}')
        self.stdout.write(f'   📝 Exams: {Exam.objects.count()}')
        self.stdout.write(f'   💰 Fees: {Fee.objects.count()}')
        self.stdout.write(f'   📚 Books: {Book.objects.count()}')
        self.stdout.write(f'   🚌 Buses: {Bus.objects.count()}')
        
        self.stdout.write('\n🔑 Login Credentials:')
        self.stdout.write('   Admin:     admin@school.com / admin123')
        self.stdout.write('   Teacher 1: teacher.ali@school.com / teacher123')
        self.stdout.write('   Teacher 2: teacher.fatima@school.com / teacher123')
        self.stdout.write('   Student 1: student1@school.com / student123')
        self.stdout.write('   Student 2: student2@school.com / student123')
        self.stdout.write('   Student 3: student3@school.com / student123')
        self.stdout.write('   Parent:    parent.ali@school.com / parent123')
        self.stdout.write('   Staff:     staff.hr@school.com / staff123')
        
        self.stdout.write(self.style.SUCCESS('\n🌱 Seed data completed!'))