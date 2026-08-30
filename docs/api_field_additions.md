# 📋 FRONTEND API FIELD REFERENCE — Added Name Fields

**What changed:** Every serializer now returns the related object's **name** as an extra field (previously only the ID was returned). All new fields are **read-only** — they appear in responses only, you do NOT send them in POST/PATCH bodies. Naming pattern: `{field}_name` or `{field}_title`.

---

## 🟦 1. USERS (`/api/users/`)

### `GET/PATCH .../students/` & `.../students/me/`
| Field | Meaning |
|---|---|
| `user_name` | Student's name |
| `class_name` | Class name |
| `parent_name` | Parent name *(nullable)* |

### `GET/PATCH .../teachers/` & `.../teachers/me/`
| Field | Meaning |
|---|---|
| `user_name` | Teacher's name |
| `employee_name` | Employee profile name *(nullable)* |

### `GET/PATCH .../staff/` & `.../staff/me/`
| Field | Meaning |
|---|---|
| `user_name` | Staff name |
| `employee_name` | Employee profile name *(nullable)* |

### `GET/PATCH .../parents/` & `.../parents/me/`
| Field | Meaning |
|---|---|
| `user_name` | Parent's name |

---

## 🟦 2. ACADEMICS (`/api/academics/`)

### `.../sections/`
| Field | Meaning |
|---|---|
| `class_name` | Class name |

### `.../class-subjects/`
| Field | Meaning |
|---|---|
| `class_name` | Class name |
| `subject_name` | Subject name |
| `teacher_name` | Teacher name *(nullable)* |

### `.../timetable/`
| Field | Meaning |
|---|---|
| `class_name` | Class name |
| `section_name` | Section name |
| `subject_name` | Subject name |
| `teacher_name` | Teacher name |
| `room_name` | Room name *(nullable)* |

---

## 🟦 3. ASSIGNMENTS (`/api/assignments/`)

### `.../assignments/`
| Field | Meaning |
|---|---|
| `class_name` | Class name |
| `subject_name` | Subject name |
| `teacher_name` | Teacher name *(nullable)* |

### `.../submissions/`
| Field | Meaning |
|---|---|
| `student_name` | Student name |
| `assignment_title` | Assignment title |

---

## 🟦 4. ATTENDANCE (`/api/attendance/`)

### `.../attendance/`
| Field | Meaning |
|---|---|
| `student_name` | Student name |
| `teacher_name` | Teacher name *(nullable)* |
| `marked_by_name` | Who marked it *(nullable)* |

### `.../behavior-logs/`
| Field | Meaning |
|---|---|
| `student_name` | Student name |
| `teacher_name` | Teacher name *(nullable)* |

---

## 🟦 5. FINANCE (`/api/finance/`)

### `.../fee-structures/` → `class_name`
### `.../expenses/` → `paid_by_name` *(nullable)*
### `.../fees/` → `student_name`, `fee_structure_title`
### `.../payments/` → `student_name`, `fee_title`
### `.../fee-history/` → `student_name`, `changed_by_name` *(nullable)*

---

## 🟦 6. EXAMS (`/api/exams/`)

### `.../exams/` → `class_name`, `subject_name`, `teacher_name` *(nullable)*
### `.../questions/` → `exam_name` *(class_name, subject_name already existed)*
### `.../student-answers/` → `student_name`, `exam_name`
### `.../results/` → `student_name`, `exam_name`
### `.../ai-auto-checking/` → `student_name`, `exam_name`, `reviewed_by_teacher_name` *(nullable)*

---

## 🟦 7. LIBRARY (`/api/library/`)

### `.../books/` → `category_name` *(nullable)*
### `.../book-issues/` → `book_title`, `student_name`
### `.../book-issue-history/` → `book_title`, `student_name`, `changed_by_name` *(nullable)*

---

## 🟦 8. TRANSPORT (`/api/transport/`)

### `.../bus-stops/` → `route_name`
### `.../bus-students/` → `bus_number`, `student_name`, `pickup_stop_name` *(nullable)*, `drop_stop_name` *(nullable)*
### `.../transport-attendance/` → `student_name`, `bus_number`

---

## 🟦 9. CANTEEN (`/api/canteen/`)

### `.../menu-items/` → `category_name` *(nullable)*
### `.../order-items/` → `student_name`, `item_name`

---

## 🟦 10. PTM (`/api/ptm/`)

### `.../ptms/` → `class_name`
### `.../ptm-meetings/` → `ptm_name`, `student_name`, `teacher_name`
### `.../ptm-attendees/` → `parent_name`, `meeting_label` *(e.g. "PTM Name - Student Name")*

---

## 🟦 11. COMMUNICATION (`/api/communication/`)

### `.../messages/` → `sender_name`, `receiver_name`
### `.../notifications/` → `user_name`
### `.../notification-logs/` → `notification_title`

---

## 🟦 12. HR (`/api/hr/`)

### `.../employees/` → `user_name`, `department_name` *(nullable)*
### `.../leaves/` → `employee_name`
### `.../payroll/` → `employee_name`
### `.../salary-history/` → `employee_name`, `changed_by_name` *(nullable)*
### `.../leave-history/` → `employee_name`, `changed_by_name` *(nullable)*

---

## 🟦 13. ANALYTICS (`/api/analytics/`)

### `.../automation-logs/` → `rule_name`
### `.../predictions/` → `student_name`
### `.../recommendations/` → `student_name`
### `.../student-goals/` → `student_name`
### `.../student-skills/` → `student_name`, `skill_name`
### `.../parent-engagement/` → `parent_name`

---

## 🟦 14. SECURITY (`/api/security/`)

### `.../visitors/` → `approved_by_name` *(nullable)*
### `.../access-logs/` → `user_name`
### `.../entry-exit-logs/` → `student_name`

---

## 🟦 15. LOGS (`/api/logs/`)

### `.../activity-logs/` → `user_name`
### `.../login-logs/` → `user_name`
### `.../error-logs/` → `user_name` *(nullable)*

---

## 🟦 16. DOCUMENTS

### `.../documents/` → `user_name`, `doc_type_name` *(nullable)*, `uploaded_by_name` *(nullable)*

---

## 🟦 17. EVENTS (`/api/events/`)

### `.../events/` → `organizer_name` *(nullable)*
### `.../event-participation/` → `event_name`, `student_name`

---

## 📌 3 Key Notes for the Frontend Team

1. **All new fields are read-only** — they only appear in JSON responses; you do NOT send them in POST/PATCH request bodies.
2. **Fields marked (nullable)** — e.g., `parent_name`, `teacher_name`, `room_name`, `department_name` — can be `null`. Handle them with optional chaining (`?.`) or `?? ''` / `|| ''`.
3. **Endpoints themselves did NOT change** — only extra fields were added to each response. Everything is backward-compatible.
