from django.db import migrations


APP_MODELS = {
    "academics": ["class", "section", "subject", "room", "classsubject", "timetable"],
    "analytics": ["skillmapping", "automationrule", "automationlog", "analyticssnapshot", "prediction", "recommendation", "studentgoal", "studentskill", "parentengagement"],
    "assignments": ["assignment", "submission"],
    "attendance": ["attendance", "behaviorlog"],
    "canteen": ["category", "menuitem", "orderitem"],
    "communication": ["message", "notification", "notificationlog"],
    "documents": ["documenttype", "document"],
    "events": ["event", "eventparticipation"],
    "exams": ["gradescale", "exam", "question", "studentanswer", "result", "aiautochecking"],
    "finance": ["feestructure", "expense", "fee", "payment", "feehistory"],
    "hr": ["department", "employee", "payroll", "leave", "salaryhistory", "leavehistory"],
    "library": ["book", "bookissue", "bookissuehistory"],
    "logs": ["activitylog", "loginlog", "errorlog"],
    "ptm": ["ptm", "ptmmeeting", "ptmattendee"],
    "security": ["visitor", "accesslog", "entryexitlog"],
    "transport": ["bus", "route", "busstop", "busstudent", "transportattendance"],
    "users": ["user", "student", "teacher", "staff", "parent"],
}


def backfill_default_school(apps, schema_editor):
    School = apps.get_model("tenants", "School")
    school, _ = School.objects.get_or_create(
        slug="default-school", defaults={"name": "Default School"}
    )
    for app_label, model_names in APP_MODELS.items():
        for model_name in model_names:
            apps.get_model(app_label, model_name).objects.filter(school__isnull=True).update(school=school)


class Migration(migrations.Migration):
    dependencies = [
        ("tenants", "0001_initial"),
        ("academics", "0004_class_school_classsubject_school_room_school_and_more"),
        ("analytics", "0003_analyticssnapshot_school_automationlog_school_and_more"),
        ("assignments", "0004_assignment_school_submission_school"),
        ("attendance", "0004_attendance_school_behaviorlog_school"),
        ("canteen", "0003_category_school_menuitem_school_orderitem_school"),
        ("communication", "0003_message_school_notification_school_and_more"),
        ("documents", "0004_document_school_documenttype_school"),
        ("events", "0004_event_school_eventparticipation_school"),
        ("exams", "0005_aiautochecking_school_exam_school_gradescale_school_and_more"),
        ("finance", "0003_expense_school_fee_school_feehistory_school_and_more"),
        ("hr", "0004_department_school_employee_school_leave_school_and_more"),
        ("library", "0004_book_school_bookissue_school_bookissuehistory_school"),
        ("logs", "0003_activitylog_school_errorlog_school_loginlog_school"),
        ("ptm", "0004_ptm_school_ptmattendee_school_ptmmeeting_school"),
        ("security", "0003_accesslog_school_entryexitlog_school_visitor_school"),
        ("transport", "0003_bus_school_busstop_school_busstudent_school_and_more"),
        ("users", "0002_parent_school_staff_school_student_school_and_more"),
    ]
    operations = [migrations.RunPython(backfill_default_school, migrations.RunPython.noop)]
