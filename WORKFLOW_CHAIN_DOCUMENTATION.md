# Complete Workflow Chain Documentation

## Overview
This document describes the complete multi-tier grade approval workflow that has been implemented in the ETU Student Result Management System.

## Approval Chain
```
Lecturer → HOD → DEAN → EXAM Officer → Published Result
```

### Workflow Stages

#### 1. **LECTURER SUBMITTED** (Initial Stage)
- **Who**: Lecturer submits student grades for a subject
- **What Happens**:
  - `ResultApprovalWorkflow` is created with status `lecturer_submitted`
  - The HOD of the student's department is automatically assigned as `current_hod`
  - Result stored with `is_published = False`
- **Next Step**: Awaits HOD approval

#### 2. **HOD APPROVED** (Department Level)
- **Who**: Head of Department (HOD) reviews submitted grades
- **What Happens**:
  - HOD can view all pending submissions in `/hod/pending/` or HOD dashboard
  - HOD can approve with optional notes or reject
  - If approved:
    - Workflow status changes to `hod_approved`
    - DEAN of the faculty is automatically assigned as `current_dean`
    - `hod_reviewed_at` timestamp is recorded
    - History entry created in `ApprovalHistory`
  - If rejected:
    - Workflow status changes to `hod_rejected`
    - Lecturer is notified to resubmit
- **Next Step**: Awaits DEAN approval (if approved)

#### 3. **DEAN APPROVED** (Faculty Level)
- **Who**: Dean of Faculty reviews HOD-approved grades
- **What Happens**:
  - DEAN can view all HOD-approved submissions in `/dean/pending/` or DEAN dashboard
  - DEAN can approve with optional notes or reject
  - If approved:
    - Workflow status changes to `dean_approved`
    - EXAM Officer is automatically assigned as `current_exam_officer`
    - `dean_reviewed_at` timestamp is recorded
    - History entry created in `ApprovalHistory`
  - If rejected:
    - Workflow status changes to `dean_rejected`
    - HOD is notified to review again
- **Next Step**: Awaits EXAM Officer publication (if approved)

#### 4. **EXAM PUBLISHED** (Final Stage - Publication Only)
- **Who**: EXAM Officer (Only authorized role)
- **What Happens**:
  - EXAM Officer can view all DEAN-approved submissions in `/admin/dean-approved-results/`
  - EXAM Officer can:
    - **Publish**: Mark result as `is_published = True` and available to students
      - Workflow status changes to `exam_published`
      - `exam_reviewed_at` timestamp is recorded
      - Student result becomes visible in their portal
    - **Reject**: Send back to DEAN for further review
      - Workflow status changes back to `dean_rejected`
      - DEAN is notified to review again
- **Authorization**: Only users with `exam_officer_profile` can publish results

## Database Models

### ResultApprovalWorkflow
```python
Status Choices:
- 'lecturer_submitted': Awaiting HOD approval
- 'hod_approved': Awaiting DEAN approval
- 'hod_rejected': Rejected by HOD, awaiting resubmission
- 'dean_approved': Awaiting EXAM Officer publication
- 'dean_rejected': Rejected by DEAN, awaiting HOD review
- 'exam_published': Published to students
- 'exam_rejected': Rejected by EXAM Officer

Fields:
- result: OneToOne → Result
- status: Current status in approval chain
- current_hod: FK → HeadOfDepartment (responsible at this stage)
- current_dean: FK → DeanOfFaculty (responsible at this stage)
- current_exam_officer: FK → ExamOfficer (responsible at this stage)
- hod_notes: Text notes from HOD
- dean_notes: Text notes from DEAN
- exam_notes: Text notes from EXAM Officer
- lecturer_submitted_at: Timestamp when submitted
- hod_reviewed_at: Timestamp when HOD reviewed
- dean_reviewed_at: Timestamp when DEAN reviewed
- exam_reviewed_at: Timestamp when EXAM Officer reviewed
```

### ApprovalHistory
Audit log tracking all approval actions:
```python
Actions Logged:
- hod_approved
- hod_rejected
- dean_approved
- dean_rejected
- exam_published
- exam_rejected

Fields:
- workflow: FK → ResultApprovalWorkflow
- action: Type of action performed
- admin_user: User who performed action
- notes: Notes from the action
- created_at: When action was performed
```

## URL Endpoints

### Lecturer Routes
- `POST /lecturer/upload-results/` - Submit student grades (creates workflow)

### HOD Routes
- `GET /hod/pending/` - View pending submissions (status: 'lecturer_submitted')
- `GET /hod/approved/` - View approved submissions (status: 'hod_approved')
- `POST /hod/review-result/<id>/` - Approve or reject (forwarding logic to DEAN)

### DEAN Routes
- `GET /dean/pending/` - View pending submissions (status: 'hod_approved')
- `GET /dean/finalized/` - View finalized submissions (status: 'dean_approved')
- `POST /dean/review-result/<id>/` - Approve or reject (forwarding logic to EXAM)

### EXAM Officer Routes
- `GET /admin/dean-approved-results/` - View results ready for publication
- `POST /admin/publish-result/<id>/` - Publish or reject (final action)

## Test Accounts

Use these credentials to test the workflow:

### Lecturer
- Username: `ishmail`
- Email: `ishmail@example.local`
- Password: `TestPass123!`
- Department: Computer Science (must have HOD)

### HOD (Computer Science)
- Username: `hod_cs`
- Email: `hod.cs@example.local`
- Password: `HodPass123!`
- Department: Computer Science
- Faculty: Science

### DEAN (Science Faculty)
- Username: `dean_science`
- Email: `dean.science@example.local`
- Password: `DeanPass123!`
- Faculty: Science

### EXAM Officer
- Username: `exam_officer`
- Email: `exam.officer@example.local`
- Password: `ExamOff123!`
- Can publish results from any faculty

## Testing the Workflow

Run the included test script to verify the entire workflow chain:

```bash
python test_workflow_chain.py
```

This script will:
1. Create a test student (if needed)
2. Simulate lecturer submitting a grade
3. Simulate HOD approving and forwarding to DEAN
4. Simulate DEAN approving and forwarding to EXAM Officer
5. Simulate EXAM Officer publishing the result
6. Display complete approval history

Expected output: `TEST PASSED!`

## Key Features

### 1. Automatic Routing
- Each stage automatically identifies and assigns the next responsible person
- HOD lookup: By student's department
- DEAN lookup: By student's faculty
- EXAM Officer lookup: First active exam officer (can be extended for multiple officers)

### 2. Status Tracking
- Each workflow maintains a clear status showing current stage
- Timestamps record when each stage was completed
- Full audit trail in `ApprovalHistory`

### 3. Search and Pagination
- HOD, DEAN, and EXAM Officer can search by:
  - Student ID
  - Subject name
- All lists paginated (10-20 per page)

### 4. Notes and Comments
- Each role can add optional notes when approving/rejecting
- Notes are stored in workflow and history for reference

### 5. Authorization
- HOD can only approve HOD-assigned workflows
- DEAN can only approve DEAN-assigned workflows
- EXAM Officer can only publish EXAM-assigned workflows
- Only EXAM Officer can publish results

### 6. Rejection Flow
- If HOD rejects: Stays with HOD for resubmission
- If DEAN rejects: Returns to HOD for review
- If EXAM rejects: Returns to DEAN for review
- Each rejection is logged with reason

## Important Notes

1. **Only EXAM Officer Can Publish**
   - Even if a result is DEAN-approved, only EXAM Officers can make it available to students
   - This ensures final quality control before publication

2. **Automatic Assignment**
   - System automatically routes to next stage based on organizational structure
   - No manual intervention needed for routing

3. **Cannot Bypass Stages**
   - Lecturer → HOD (mandatory)
   - HOD → DEAN (mandatory)
   - DEAN → EXAM (mandatory)
   - EXAM → Published (mandatory)

4. **Audit Trail**
   - Every action is logged with timestamp and admin user
   - Used for accountability and troubleshooting

## Troubleshooting

### Issue: "No DEAN assigned when HOD approves"
- **Solution**: Ensure HOD's department is linked to a Faculty, and a DEAN exists for that Faculty

### Issue: "No EXAM Officer available"
- **Solution**: Create at least one active EXAM Officer account in admin

### Issue: Result not appearing in next stage
- **Solution**: Refresh page, check workflow status in database
  ```bash
  python manage.py shell
  >>> from admin_hierarchy.models import ResultApprovalWorkflow
  >>> w = ResultApprovalWorkflow.objects.get(id=<id>)
  >>> print(w.status, w.current_dean)
  ```

## Future Enhancements

- Multiple EXAM Officers with role-based assignment
- Email notifications at each stage
- Batch approval for multiple results
- Appeal/override workflow
- Report generation showing approval statistics
