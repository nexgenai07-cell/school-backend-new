#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import django
from datetime import datetime, timedelta, date
from decimal import Decimal


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    # Initialize Django
    django.setup()
    
    # Now import models after Django is setup (ONLY ONCE)
    from django.contrib.auth.hashers import make_password
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
    
    seed_data()


def seed_data():
    print("🌱 Starting seed data insertion...")
    
    # ========================================
    # 1. CREATE DEPARTMENTS
    # ========================================
    print("📚 Creating departments...")
    dept_hr, _ = Department.objects.get_or_create(
        name="Human Resources",
        defaults={"description": "HR Department"}
    )
    dept_academics, _ = Department.objects.get_or_create(
        name="Academics",
        defaults={"description": "Academic Department"}
    )
    dept_finance, _ = Department.objects.get_or_create(
        name="Finance",
        defaults={"description": "Finance Department"}
    )
    dept_admin, _ = Department.objects.get_or_create(
        name="Administration",
        defaults={"description": "Administration Department"}
    )
    dept_canteen, _ = Department.objects.get_or_create(
        name="Canteen",
        defaults={"description": "Canteen Department"}
    )
    dept_transport, _ = Department.objects.get_or_create(
        name="Transport",
        defaults={"description": "Transport Department"}
    )
    dept_library, _ = Department.objects.get_or_create(
        name="Library",
        defaults={"description": "Library Department"}
    )
    
    # ========================================
    # 2. CREATE USERS
    # ========================================
    print("👤 Creating users...")
    
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
    teacher3, _ = User.objects.get_or_create(
        email="teacher.ahmed@school.com",
        defaults={
            "name": "Mr. Ahmed Hassan",
            "role": "teacher",
            "password": make_password("teacher123"),
            "status": "active"
        }
    )
    
    # Students
    students = []
    for i in range(1, 6):
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
    parent2, _ = User.objects.get_or_create(
        email="parent.fatima@school.com",
        defaults={
            "name": "Parent of Student 2",
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
    print("📖 Creating classes and subjects...")
    
    class_10, _ = Class.objects.get_or_create(
        name="Class 10",
        defaults={
            "description": "Class 10 - Matriculation",
            "academic_year": "2024-2025"
        }
    )
    class_9, _ = Class.objects.get_or_create(
        name="Class 9",
        defaults={
            "description": "Class 9 - Matriculation",
            "academic_year": "2024-2025"
        }
    )
    
    # Sections
    section_a, _ = Section.objects.get_or_create(
        class_obj=class_10,
        defaults={"name": "A", "capacity": 30}
    )
    section_b, _ = Section.objects.get_or_create(
        class_obj=class_10,
        defaults={"name": "B", "capacity": 30}
    )
    section_9a, _ = Section.objects.get_or_create(
        class_obj=class_9,
        defaults={"name": "A", "capacity": 30}
    )
    
    # Subjects
    math, _ = Subject.objects.get_or_create(
        code="MATH101",
        defaults={
            "name": "Mathematics",
            "description": "Mathematics subject"
        }
    )
    physics, _ = Subject.objects.get_or_create(
        code="PHY101",
        defaults={
            "name": "Physics",
            "description": "Physics subject"
        }
    )
    chemistry, _ = Subject.objects.get_or_create(
        code="CHEM101",
        defaults={
            "name": "Chemistry",
            "description": "Chemistry subject"
        }
    )
    english, _ = Subject.objects.get_or_create(
        code="ENG101",
        defaults={
            "name": "English",
            "description": "English subject"
        }
    )
    urdu, _ = Subject.objects.get_or_create(
        code="URD101",
        defaults={
            "name": "Urdu",
            "description": "Urdu subject"
        }
    )
    
    # Rooms
    room_101, _ = Room.objects.get_or_create(
        name="Room 101",
        defaults={"location": "Building A, Floor 1", "capacity": 30}
    )
    room_102, _ = Room.objects.get_or_create(
        name="Room 102",
        defaults={"location": "Building A, Floor 1", "capacity": 30}
    )
    room_201, _ = Room.objects.get_or_create(
        name="Room 201",
        defaults={"location": "Building A, Floor 2", "capacity": 30}
    )
    
    # ========================================
    # 4. CREATE TEACHER PROFILES
    # ========================================
    print("👨‍🏫 Creating teacher profiles...")
    
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
    teacher3_obj, _ = Teacher.objects.get_or_create(
        user=teacher3,
        defaults={
            "qualification": "MSc Chemistry",
            "experience": 6,
            "join_date": date(2018, 3, 1),
            "subject_specialization": "Chemistry",
            "phone": "0300-3333333",
            "status": "active"
        }
    )
    
    # Create Employee records for teachers
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
        user=teacher2,
        defaults={
            "designation": "Teacher",
            "department": dept_academics,
            "salary": Decimal('60000.00'),
            "join_date": date(2016, 6, 1),
            "status": "active",
            "leave_balance": 18
        }
    )
    Employee.objects.get_or_create(
        user=teacher3,
        defaults={
            "designation": "Teacher",
            "department": dept_academics,
            "salary": Decimal('60000.00'),
            "join_date": date(2018, 3, 1),
            "status": "active",
            "leave_balance": 18
        }
    )
    
    # ========================================
    # 5. CREATE PARENT PROFILES
    # ========================================
    print("👨‍👩‍👧 Creating parent profiles...")
    
    parent1_obj, _ = Parent.objects.get_or_create(
        user=parent1,
        defaults={
            "occupation": "Engineer",
            "phone": "0300-4444444",
            "address": "House 1, Street 1, Lahore"
        }
    )
    parent2_obj, _ = Parent.objects.get_or_create(
        user=parent2,
        defaults={
            "occupation": "Doctor",
            "phone": "0300-5555555",
            "address": "House 2, Street 2, Lahore"
        }
    )
    
    # ========================================
    # 6. CREATE STUDENT PROFILES
    # ========================================
    print("🎓 Creating student profiles...")
    
    student_objs = []
    for i, student_user in enumerate(students[:3]):
        student_obj, _ = Student.objects.get_or_create(
            user=student_user,
            defaults={
                "class_obj": class_10,
                "parent": parent1_obj if i == 0 else parent2_obj,
                "admission_no": f"STU-2024-{i+1:04d}",
                "dob": date(2008, 1, 1 + i),
                "gender": "male" if i % 2 == 0 else "female",
                "address": f"Student {i+1} Address",
                "phone": f"0300-{i+1:04d}",
                "admission_date": date(2024, 1, 1)
            }
        )
        student_objs.append(student_obj)
    
    for i, student_user in enumerate(students[3:5]):
        student_obj, _ = Student.objects.get_or_create(
            user=student_user,
            defaults={
                "class_obj": class_9,
                "parent": parent2_obj if i == 0 else parent1_obj,
                "admission_no": f"STU-2024-{i+4:04d}",
                "dob": date(2009, 1, 1 + i),
                "gender": "male" if i % 2 == 0 else "female",
                "address": f"Student {i+4} Address",
                "phone": f"0300-{i+4:04d}",
                "admission_date": date(2024, 1, 1)
            }
        )
        student_objs.append(student_obj)
    
    # ========================================
    # 7. CREATE CLASS-SUBJECT ASSIGNMENTS
    # ========================================
    print("📚 Creating class-subject assignments...")
    
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
        class_obj=class_10,
        subject=english,
        defaults={"teacher": teacher1_obj}
    )
    ClassSubject.objects.get_or_create(
        class_obj=class_9,
        subject=math,
        defaults={"teacher": teacher1_obj}
    )
    ClassSubject.objects.get_or_create(
        class_obj=class_9,
        subject=chemistry,
        defaults={"teacher": teacher3_obj}
    )
    ClassSubject.objects.get_or_create(
        class_obj=class_9,
        subject=urdu,
        defaults={"teacher": teacher2_obj}
    )
    
    # ========================================
    # 8. CREATE TIMETABLE
    # ========================================
    print("🕐 Creating timetable...")
    
    timetable_entries = [
        (class_10, section_a, math, teacher1_obj, room_101, 'mon', '08:00', '08:45'),
        (class_10, section_a, physics, teacher2_obj, room_102, 'mon', '08:45', '09:30'),
        (class_10, section_a, english, teacher1_obj, room_101, 'mon', '09:30', '10:15'),
        (class_10, section_a, math, teacher1_obj, room_101, 'tue', '08:00', '08:45'),
        (class_10, section_a, physics, teacher2_obj, room_102, 'tue', '08:45', '09:30'),
        (class_9, section_9a, math, teacher1_obj, room_201, 'mon', '10:30', '11:15'),
        (class_9, section_9a, chemistry, teacher3_obj, room_201, 'mon', '11:15', '12:00'),
        (class_9, section_9a, urdu, teacher2_obj, room_201, 'mon', '12:00', '12:45'),
    ]
    
    for entry in timetable_entries:
        Timetable.objects.get_or_create(
            class_obj=entry[0],
            section=entry[1],
            subject=entry[2],
            teacher=entry[3],
            room=entry[4],
            day=entry[5],
            start_time=entry[6],
            end_time=entry[7]
        )
    
    # ========================================
    # 9. CREATE EMPLOYEE FOR STAFF
    # ========================================
    print("👔 Creating staff employee...")
    
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
    # 10. CREATE FEE STRUCTURES
    # ========================================
    print("💰 Creating fee structures...")
    
    fee_10, _ = FeeStructure.objects.get_or_create(
        class_obj=class_10,
        title="Tuition Fee - Class 10",
        defaults={
            "amount": Decimal('15000.00'),
            "frequency": "monthly",
            "description": "Monthly tuition fee for Class 10"
        }
    )
    fee_9, _ = FeeStructure.objects.get_or_create(
        class_obj=class_9,
        title="Tuition Fee - Class 9",
        defaults={
            "amount": Decimal('12000.00'),
            "frequency": "monthly",
            "description": "Monthly tuition fee for Class 9"
        }
    )
    
    # ========================================
    # 11. CREATE FEES FOR STUDENTS
    # ========================================
    print("📝 Creating student fees...")
    
    for student_obj in student_objs[:3]:
        Fee.objects.get_or_create(
            student=student_obj,
            fee_structure=fee_10,
            defaults={
                "amount": Decimal('15000.00'),
                "due_date": date(2024, 12, 31),
                "status": "pending"
            }
        )
    
    for student_obj in student_objs[3:5]:
        Fee.objects.get_or_create(
            student=student_obj,
            fee_structure=fee_9,
            defaults={
                "amount": Decimal('12000.00'),
                "due_date": date(2024, 12, 31),
                "status": "pending"
            }
        )
    
    # ========================================
    # 12. CREATE BOOKS
    # ========================================
    print("📚 Creating books...")
    
    books_data = [
        {"title": "Mathematics Grade 10", "author": "Dr. Ahmed", "isbn": "978-969-1234-01-5", "total_copies": 10},
        {"title": "Physics Grade 10", "author": "Prof. Khan", "isbn": "978-969-1234-02-2", "total_copies": 8},
        {"title": "Chemistry Grade 9", "author": "Dr. Hassan", "isbn": "978-969-1234-03-9", "total_copies": 6},
        {"title": "English Grammar", "author": "Ms. Fatima", "isbn": "978-969-1234-04-6", "total_copies": 12},
    ]
    
    for book_data in books_data:
        Book.objects.get_or_create(
            isbn=book_data["isbn"],
            defaults={
                "title": book_data["title"],
                "author": book_data["author"],
                "total_copies": book_data["total_copies"],
                "available_copies": book_data["total_copies"]
            }
        )
    
    # ========================================
    # 13. CREATE BUSES AND ROUTES
    # ========================================
    print("🚌 Creating transport data...")
    
    bus_1, _ = Bus.objects.get_or_create(
        bus_no="BUS-001",
        defaults={"capacity": 30, "status": "active"}
    )
    bus_2, _ = Bus.objects.get_or_create(
        bus_no="BUS-002",
        defaults={"capacity": 25, "status": "active"}
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
    stop_2, _ = BusStop.objects.get_or_create(
        route=route_1,
        name="Stop 2 - Model Town",
        defaults={"stop_order": 2}
    )
    stop_3, _ = BusStop.objects.get_or_create(
        route=route_1,
        name="Stop 3 - School",
        defaults={"stop_order": 3}
    )
    
    for student_obj in student_objs[:3]:
        BusStudent.objects.get_or_create(
            bus=bus_1,
            student=student_obj,
            defaults={
                "pickup_stop": stop_1,
                "drop_stop": stop_3
            }
        )
    
    # ========================================
    # 14. CREATE CANTEEN DATA
    # ========================================
    print("🍽️ Creating canteen data...")
    
    cat_burger, _ = Category.objects.get_or_create(
        name="Burgers",
        defaults={"description": "Burger Category"}
    )
    cat_pizza, _ = Category.objects.get_or_create(
        name="Pizzas",
        defaults={"description": "Pizza Category"}
    )
    cat_drinks, _ = Category.objects.get_or_create(
        name="Drinks",
        defaults={"description": "Drinks Category"}
    )
    
    menu_items = [
        {"name": "Chicken Burger", "price": Decimal('250.00'), "category": cat_burger},
        {"name": "Beef Burger", "price": Decimal('300.00'), "category": cat_burger},
        {"name": "Small Pizza", "price": Decimal('400.00'), "category": cat_pizza},
        {"name": "Large Pizza", "price": Decimal('600.00'), "category": cat_pizza},
        {"name": "Cold Drink", "price": Decimal('100.00'), "category": cat_drinks},
        {"name": "Fresh Juice", "price": Decimal('150.00'), "category": cat_drinks},
    ]
    
    for item in menu_items:
        MenuItem.objects.get_or_create(
            name=item["name"],
            defaults={
                "price": item["price"],
                "category": item["category"],
                "is_available": True
            }
        )
    
    # ========================================
    # 15. CREATE EXAM DATA
    # ========================================
    print("📝 Creating exam data...")
    
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
    
    questions = [
        {"text": "What is 2+2?", "type": "mcq", "answer": "4", "marks": 5},
        {"text": "What is the square root of 16?", "type": "short", "answer": "4", "marks": 10},
        {"text": "Solve: 3x + 5 = 20", "type": "long", "answer": "x = 5", "marks": 15},
    ]
    
    for q in questions:
        Question.objects.get_or_create(
            exam=exam_1,
            question_text=q["text"],
            defaults={
                "question_type": q["type"],
                "answer_text": q["answer"],
                "marks": q["marks"]
            }
        )
    
    for student_obj in student_objs[:3]:
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
    # 16. CREATE ATTENDANCE DATA
    # ========================================
    print("📋 Creating attendance data...")
    
    today = date.today()
    for student_obj in student_objs:
        for i in range(5):
            att_date = today - timedelta(days=i)
            if att_date.weekday() < 5:
                status = 'present' if i % 3 != 0 else 'absent'
                Attendance.objects.get_or_create(
                    student=student_obj,
                    date=att_date,
                    defaults={
                        "status": status,
                        "teacher": teacher1_obj if student_obj.class_obj == class_10 else teacher3_obj,
                        "marked_by": teacher1_obj if student_obj.class_obj == class_10 else teacher3_obj
                    }
                )
    
    # ========================================
    # 17. CREATE SKILL MAPPINGS
    # ========================================
    print("🎯 Creating skill mappings...")
    
    skill_math, _ = SkillMapping.objects.get_or_create(
        name="Mathematics",
        defaults={
            "category": "Academic",
            "description": "Mathematical skills"
        }
    )
    skill_science, _ = SkillMapping.objects.get_or_create(
        name="Science",
        defaults={
            "category": "Academic",
            "description": "Scientific skills"
        }
    )
    skill_english, _ = SkillMapping.objects.get_or_create(
        name="English",
        defaults={
            "category": "Language",
            "description": "English language skills"
        }
    )
    
    for student_obj in student_objs[:3]:
        StudentSkill.objects.get_or_create(
            student=student_obj,
            skill=skill_math,
            defaults={
                "proficiency_level": "intermediate",
                "acquired_on": date(2024, 1, 1)
            }
        )
    
    # ========================================
    # 18. SUMMARY
    # ========================================
    print("\n✅ Seed data inserted successfully!")
    print("\n📊 Summary:")
    print(f"   👤 Users: {User.objects.count()}")
    print(f"   🎓 Students: {Student.objects.count()}")
    print(f"   👨‍🏫 Teachers: {Teacher.objects.count()}")
    print(f"   👨‍👩‍👧 Parents: {Parent.objects.count()}")
    print(f"   📚 Classes: {Class.objects.count()}")
    print(f"   📖 Subjects: {Subject.objects.count()}")
    print(f"   📝 Exams: {Exam.objects.count()}")
    print(f"   📋 Attendance Records: {Attendance.objects.count()}")
    print(f"   💰 Fees: {Fee.objects.count()}")
    print(f"   📚 Books: {Book.objects.count()}")
    print(f"   🚌 Buses: {Bus.objects.count()}")
    
    print("\n🔑 Login Credentials:")
    print("   Admin:     admin@school.com / admin123")
    print("   Teacher 1: teacher.ali@school.com / teacher123")
    print("   Teacher 2: teacher.fatima@school.com / teacher123")
    print("   Teacher 3: teacher.ahmed@school.com / teacher123")
    print("   Student 1: student1@school.com / student123")
    print("   Student 2: student2@school.com / student123")
    print("   Student 3: student3@school.com / student123")
    print("   Student 4: student4@school.com / student123")
    print("   Student 5: student5@school.com / student123")
    print("   Parent 1:  parent.ali@school.com / parent123")
    print("   Parent 2:  parent.fatima@school.com / parent123")
    print("   Staff:     staff.hr@school.com / staff123")
    
    print("\n🧪 Test Endpoints:")
    print("   GET  /api/users/students/")
    print("   GET  /api/academics/classes/")
    print("   GET  /api/academics/subjects/")
    print("   GET  /api/academics/timetable/")
    print("   GET  /api/exams/exams/")
    print("   GET  /api/exams/results/")
    print("   GET  /api/finance/fees/")
    print("   GET  /api/library/books/")
    print("   GET  /api/transport/buses/")
    print("   GET  /api/canteen/menu-items/")
    print("   GET  /api/attendance/attendance/")
    print("   GET  /api/hr/employees/")
    print("   GET  /api/communication/messages/")
    print("   GET  /api/ptm/ptm/")
    print("   GET  /api/events/events/")
    print("   GET  /api/documents/documents/")
    print("   GET  /api/analytics/predictions/")
    
    print("\n🌱 Seed data completed!")


if __name__ == "__main__":
    main()