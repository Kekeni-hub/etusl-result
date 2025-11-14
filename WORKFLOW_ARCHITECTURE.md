# Workflow Chain Architecture Diagram

## System Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     ETU STUDENT RESULT WORKFLOW CHAIN                   │
└─────────────────────────────────────────────────────────────────────────┘

STAGE 1: LECTURER SUBMISSION
═════════════════════════════════════════════════════════════════════════

    ┌──────────────────────────────────┐
    │   Lecturer Portal                │
    │  (lecturer/upload-results/)      │
    └───────────┬──────────────────────┘
                │
                │ 1. Select Students
                │ 2. Enter Scores
                │ 3. Submit
                ↓
    ┌──────────────────────────────────────────┐
    │ Create ResultApprovalWorkflow             │
    │ ✓ Status: lecturer_submitted             │
    │ ✓ current_hod = auto-assigned from dept  │
    │ ✓ Result.is_published = False            │
    └──────────────────────────────────────────┘
                │
                ↓

STAGE 2: HOD DEPARTMENT REVIEW
═════════════════════════════════════════════════════════════════════════

    ┌──────────────────────────────────────────┐
    │   HOD Portal                             │
    │  (/hod/pending/)                         │
    │  View assigned workflows                 │
    └───────────┬──────────────────────────────┘
                │
        ┌───────┴──────────┐
        │                  │
        ↓ APPROVE         ↓ REJECT
        │                  │
    ┌───────────┐     ┌──────────┐
    │ Verify    │     │ Send back│
    │ Scores    │     │ to       │
    │ Add notes │     │ Lecturer │
    │ Approve   │     │ hod_rejected
    └───┬───────┘     └──────────┘
        │
        ↓
    ┌──────────────────────────────────────────┐
    │ Update ResultApprovalWorkflow             │
    │ ✓ Status: hod_approved                   │
    │ ✓ current_dean = auto-assigned from fac  │
    │ ✓ hod_notes = stored                     │
    │ ✓ hod_reviewed_at = timestamp            │
    │ ✓ ApprovalHistory entry created          │
    └──────────────────────────────────────────┘
                │
                ↓

STAGE 3: DEAN FACULTY REVIEW
═════════════════════════════════════════════════════════════════════════

    ┌──────────────────────────────────────────┐
    │   DEAN Portal                            │
    │  (/dean/pending/)                        │
    │  View HOD-approved workflows             │
    └───────────┬──────────────────────────────┘
                │
        ┌───────┴──────────┐
        │                  │
        ↓ APPROVE         ↓ REJECT
        │                  │
    ┌────────────┐    ┌──────────────┐
    │ Verify HOD │    │ Send back to │
    │ approval   │    │ HOD for      │
    │ Add notes  │    │ review       │
    │ Approve    │    │ dean_rejected │
    └────┬───────┘    └──────────────┘
        │
        ↓
    ┌──────────────────────────────────────────┐
    │ Update ResultApprovalWorkflow             │
    │ ✓ Status: dean_approved                  │
    │ ✓ current_exam_officer = auto-assigned   │
    │ ✓ dean_notes = stored                    │
    │ ✓ dean_reviewed_at = timestamp           │
    │ ✓ ApprovalHistory entry created          │
    └──────────────────────────────────────────┘
                │
                ↓

STAGE 4: EXAM OFFICER PUBLICATION (FINAL)
═════════════════════════════════════════════════════════════════════════

    ┌──────────────────────────────────────────┐
    │   EXAM Officer Portal                    │
    │  (/admin/dean-approved-results/)         │
    │  View DEAN-approved ready for publish    │
    └───────────┬──────────────────────────────┘
                │
        ┌───────┴──────────┐
        │                  │
        ↓ PUBLISH         ↓ REJECT
        │                  │
    ┌────────────┐    ┌──────────────┐
    │ Final QC   │    │ Send back to │
    │ Add notes  │    │ DEAN for     │
    │ Publish    │    │ review       │
    └────┬───────┘    │ dean_rejected │
        │             └──────────────┘
        ↓
    ┌──────────────────────────────────────────┐
    │ Update Result & ResultApprovalWorkflow    │
    │ ✓ Result.is_published = True             │
    │ ✓ Result.published_date = now()          │
    │ ✓ Status: exam_published                 │
    │ ✓ exam_notes = stored                    │
    │ ✓ exam_reviewed_at = timestamp           │
    │ ✓ ApprovalHistory entry created          │
    │ ✓ Notification sent to student           │
    └──────────────────────────────────────────┘
                │
                ↓
    ┌──────────────────────────────────────────┐
    │   WORKFLOW COMPLETE ✓                    │
    │   Result visible in Student Portal       │
    └──────────────────────────────────────────┘
```

## Database Model Relationships

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           DATABASE SCHEMA                               │
└─────────────────────────────────────────────────────────────────────────┘

Result (student.Result)
├── id (PK)
├── student (FK → Student)
├── subject
├── score
├── grade
├── is_published ← Key field for status
├── uploaded_by (FK → Lecturer)
└── published_date (Timestamp when published)
    │
    ├────→ OneToOne Relationship
    │
    ↓
ResultApprovalWorkflow (admin_hierarchy.ResultApprovalWorkflow)
├── id (PK)
├── result (OneToOne → Result)
├── status (Enum: lecturer_submitted | hod_approved | ... | exam_published)
│
├── ROUTING FIELDS (Auto-assigned at each stage)
│   ├── current_hod (FK → HeadOfDepartment) ← Stage 2
│   ├── current_dean (FK → DeanOfFaculty) ← Stage 3
│   └── current_exam_officer (FK → ExamOfficer) ← Stage 4
│
├── NOTES (Optional comments from each role)
│   ├── hod_notes
│   ├── dean_notes
│   └── exam_notes
│
├── TIMESTAMPS (Track review progress)
│   ├── lecturer_submitted_at
│   ├── hod_reviewed_at
│   ├── dean_reviewed_at
│   └── exam_reviewed_at
    │
    ├────→ Reverse Relationship (One-to-Many)
    │
    ↓
ApprovalHistory (admin_hierarchy.ApprovalHistory)
├── id (PK)
├── workflow (FK → ResultApprovalWorkflow)
├── action (hod_approved | hod_rejected | dean_approved | ...)
├── admin_user (FK → User)
├── notes
└── created_at (Timestamp of action)

Additional Linked Models:
├── HeadOfDepartment (admin_hierarchy.HeadOfDepartment)
│   ├── user (OneToOne → User)
│   ├── department (OneToOne → Department)
│   └── hod_id (Unique identifier)
│
├── DeanOfFaculty (admin_hierarchy.DeanOfFaculty)
│   ├── user (OneToOne → User)
│   ├── faculty (OneToOne → Faculty)
│   └── dean_id (Unique identifier)
│
└── ExamOfficer (exam_officer.ExamOfficer)
    ├── user (OneToOne → User)
    └── officer_id (Unique identifier)
```

## Workflow Status Transitions

```
┌──────────────────────────────────────────────────────────────────────┐
│                    STATUS TRANSITION DIAGRAM                         │
└──────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────┐
                    │  lecturer_submitted │
                    │  (Awaiting HOD)     │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
            ┌───────▼────────┐    ┌──────▼──────────┐
            │  hod_approved  │    │  hod_rejected   │
            │  (Awaiting     │    │  [END - Retry]  │
            │   DEAN)        │    └─────────────────┘
            └───────┬────────┘
                    │
            ┌───────┴──────────┐
            │                  │
    ┌───────▼─────────┐  ┌────▼──────────────┐
    │  dean_approved  │  │  dean_rejected    │
    │  (Awaiting      │  │  [Back to HOD]    │
    │   EXAM)         │  └───────────────────┘
    └────────┬────────┘
             │
     ┌───────┴──────────┐
     │                  │
 ┌───▼──────────┐  ┌───▼──────────────┐
 │exam_published│  │ exam_rejected    │
 │ ✓ FINAL      │  │ [Back to DEAN]   │
 │ ✓ Visible to │  │                  │
 │   students   │  └──────────────────┘
 └──────────────┘

Legend:
─────> Status transition
[...]  Outcome or next action
✓      Completion indicator
```

## Role-Based Access Control

```
┌─────────────────────────────────────────────────────────────────────┐
│                     WHO CAN DO WHAT                                 │
└─────────────────────────────────────────────────────────────────────┘

╔═══════════════╤══════════════════════════════════════════════════╗
║ Role          │ Permissions                                      ║
╠═══════════════╪══════════════════════════════════════════════════╣
║ Lecturer      │ ✓ Upload results (creates workflow)              ║
║               │ ✓ View own uploaded results                      ║
║               │ ✗ Approve/Reject (not allowed)                  ║
║               │ ✗ Publish (not allowed)                         ║
╠═══════════════╪══════════════════════════════════════════════════╣
║ HOD           │ ✓ View pending (status: lecturer_submitted)      ║
║               │ ✓ View approved (status: hod_approved)           ║
║               │ ✓ Approve/Reject pending results                 ║
║               │ ✓ Add notes to approval                          ║
║               │ ✗ Publish (not allowed)                         ║
║               │ ✗ Approve DEAN-level results (not allowed)      ║
╠═══════════════╪══════════════════════════════════════════════════╣
║ DEAN          │ ✓ View pending (status: hod_approved)            ║
║               │ ✓ View finalized (status: dean_approved)         ║
║               │ ✓ Approve/Reject pending results                 ║
║               │ ✓ Add notes to approval                          ║
║               │ ✗ Publish (not allowed)                         ║
║               │ ✗ Approve HOD-level results (not allowed)       ║
╠═══════════════╪══════════════════════════════════════════════════╣
║ EXAM Officer  │ ✓ View DEAN-approved (status: dean_approved)     ║
║               │ ✓ Publish results to students                    ║
║               │ ✓ Reject and send back to DEAN                   ║
║               │ ✓ Add notes to publication                       ║
║               │ ✓ Search all faculties' results                  ║
║               │ ✗ Approve HOD/DEAN workflows (not allowed)      ║
║               │ ✓ ONLY role that can publish                     ║
╚═══════════════╧══════════════════════════════════════════════════╝
```

## Data Flow Timeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXAMPLE TIMELINE                             │
└─────────────────────────────────────────────────────────────────┘

Time    Event                          Database Changes
────────────────────────────────────────────────────────────────

00:00   Lecturer submits grade      ResultApprovalWorkflow created
        for Student A, Math          ├─ status = lecturer_submitted
                                     ├─ current_hod = HOD_CS
                                     └─ lecturer_submitted_at = 00:00
                                     Result.is_published = False

        → Workflow assigned to HOD

01:30   HOD reviews                  ResultApprovalWorkflow updated
        Approves with note           ├─ status = hod_approved
        "Verified by department"     ├─ current_dean = DEAN_Science
                                     ├─ hod_notes = "..."
                                     ├─ hod_reviewed_at = 01:30
                                     
                                     ApprovalHistory created
                                     ├─ action = hod_approved
                                     ├─ admin_user = HOD_CS
                                     └─ notes = "..."

        → Workflow assigned to DEAN

03:15   DEAN reviews                 ResultApprovalWorkflow updated
        Approves with note           ├─ status = dean_approved
        "Approved by faculty"        ├─ current_exam_officer = EXAM_EO
                                     ├─ dean_notes = "..."
                                     ├─ dean_reviewed_at = 03:15
                                     
                                     ApprovalHistory created
                                     ├─ action = dean_approved
                                     ├─ admin_user = DEAN_Science
                                     └─ notes = "..."

        → Workflow assigned to EXAM Officer

04:45   EXAM Officer reviews        Result updated
        Publishes                    ├─ is_published = True
                                     └─ published_date = 04:45
                                     
                                     ResultApprovalWorkflow updated
                                     ├─ status = exam_published
                                     ├─ exam_notes = "Published OK"
                                     └─ exam_reviewed_at = 04:45
                                     
                                     ApprovalHistory created
                                     ├─ action = exam_published
                                     ├─ admin_user = EXAM_Officer
                                     └─ notes = "..."
                                     
                                     Notification sent to Student A

        → WORKFLOW COMPLETE ✓
        → Student A can now see grade in portal
```

## Authorization Flow

```
┌─────────────────────────────────────────────────────────────────┐
│           HOW THE SYSTEM ROUTES AUTOMATICALLY                   │
└─────────────────────────────────────────────────────────────────┘

When Lecturer Submits Result for Student:
─────────────────────────────────────────

1. Get Student's Department
   └─→ Student.department = "Computer Science"

2. Find HOD for that Department
   └─→ HeadOfDepartment.objects.get(department=CS)
   └─→ Found: Hoda CS

3. Create Workflow with HOD assigned
   └─→ ResultApprovalWorkflow.current_hod = Hoda CS


When HOD Approves:
──────────────────

1. Get Student's Faculty (via department)
   └─→ Student.department.faculty = "Science"

2. Find DEAN for that Faculty
   └─→ DeanOfFaculty.objects.get(faculty=Science)
   └─→ Found: Deana Science

3. Update Workflow with DEAN assigned
   └─→ ResultApprovalWorkflow.current_dean = Deana Science


When DEAN Approves:
───────────────────

1. Find first active EXAM Officer
   └─→ ExamOfficer.objects.filter(is_active=True).first()
   └─→ Found: Exam Officer (EO001)

2. Update Workflow with EXAM Officer assigned
   └─→ ResultApprovalWorkflow.current_exam_officer = Exam Officer


When EXAM Officer Publishes:
────────────────────────────

1. Mark Result as published
   └─→ Result.is_published = True
   └─→ Result.published_date = now()

2. Update Workflow status
   └─→ ResultApprovalWorkflow.status = exam_published

3. Notify Student
   └─→ Student receives notification in portal
```
