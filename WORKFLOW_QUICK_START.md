# Workflow Chain Quick Reference

## What is the Workflow Chain?

The workflow chain is a multi-tier approval system that ensures student grades go through proper review before being published. It works like this:

```
Lecturer Submits Grades
        ↓ (Automatic assignment)
    HOD Reviews
        ↓ (If approved)
    DEAN Reviews
        ↓ (If approved)
  EXAM Officer Publishes
        ↓
  Students See Results
```

## Key Point: Only EXAM Officer Can Publish

**IMPORTANT**: Only the EXAM Officer has permission to publish results to students. This ensures quality control at every step.

## Testing the Workflow

### Quick Test (Automated)
```bash
python test_workflow_chain.py
```
This runs the entire workflow automatically and shows you each step.

### Manual Test (Step-by-Step)

#### Step 1: Login as Lecturer
1. Go to `http://localhost:8000/lecturer/login/`
2. Login with:
   - Username: `ishmail`
   - Password: `TestPass123!`

#### Step 2: Upload Grades
1. Click "Upload Results"
2. Select students, subject, scores
3. Submit
4. **Result**: Workflow created with HOD marked as pending

#### Step 3: Login as HOD
1. Go to `http://localhost:8000/hod/login/`
2. Login with:
   - Username: `hod_cs`
   - Password: `HodPass123!`
3. Click "Pending Reviews" or go to `/hod/pending/`
4. Click "Review & Approve" for the result
5. Add notes (optional)
6. Click "Approve"
7. **Result**: Workflow forwarded to DEAN

#### Step 4: Login as DEAN
1. Go to `http://localhost:8000/dean/login/`
2. Login with:
   - Username: `dean_science`
   - Password: `DeanPass123!`
3. Click "Pending Reviews" or go to `/dean/pending/`
4. Click "Review & Approve" for the result
5. Add notes (optional)
6. Click "Approve"
7. **Result**: Workflow forwarded to EXAM Officer

#### Step 5: Login as EXAM Officer
1. Go to `http://localhost:8000/admin/login/`
2. Login with:
   - Username: `exam_officer`
   - Password: `ExamOff123!`
3. Go to "Dean Approved Results" or `/admin/dean-approved-results/`
4. Click "Review & Publish"
5. Add notes (optional)
6. Click "Publish Result"
7. **Result**: Result is now published to student

## URLs by Role

### Lecturer
- Login: `/lecturer/login/`
- Dashboard: `/lecturer/dashboard/`
- Upload Results: `/lecturer/upload-results/`

### HOD
- Login: `/hod/login/`
- Dashboard: `/hod/dashboard/`
- Pending Reviews: `/hod/pending/`
- Approved Results: `/hod/approved/`
- Review Result: `/hod/review-result/<id>/`

### DEAN
- Login: `/dean/login/`
- Dashboard: `/dean/dashboard/`
- Pending Reviews: `/dean/pending/`
- Finalized Results: `/dean/finalized/`
- Review Result: `/dean/review-result/<id>/`

### EXAM Officer
- Login: `/admin/login/`
- Dashboard: `/admin/dashboard/`
- Dean Approved Results: `/admin/dean-approved-results/`
- Publish Result: `/admin/publish-result/<id>/`

## Workflow Status Values

| Status | Meaning | Current Owner | Next Step |
|--------|---------|---------------|-----------|
| `lecturer_submitted` | Awaiting HOD review | HOD | Approve/Reject |
| `hod_approved` | Awaiting DEAN review | DEAN | Approve/Reject |
| `dean_approved` | Awaiting EXAM publication | EXAM Officer | Publish/Reject |
| `exam_published` | Published to students | - | Complete ✓ |
| `hod_rejected` | HOD rejected, needs resubmit | Lecturer | Resubmit |
| `dean_rejected` | DEAN rejected, needs HOD review | HOD | Review again |

## Search and Filter

Each role can search by:
- **Student ID**: Type exact or partial student ID
- **Subject**: Type subject name to filter

Examples:
- Search for student: `TESTSTD1763114749`
- Search for subject: `Math`

## Rejection Flow

### If HOD Rejects
- Status: `hod_rejected`
- Lecturer must resubmit

### If DEAN Rejects
- Status: `dean_rejected`
- HOD reviews again
- Can approve on review or request lecturer resubmit

### If EXAM Rejects
- Status: `dean_rejected` (goes back to DEAN)
- DEAN reviews again
- Can approve again or request HOD review

## Audit Trail

Every action is logged with:
- Who performed the action
- When it was performed
- What notes they added

View in: Database → `ApprovalHistory` table

## Important Rules

1. ✓ **Automatic Routing**: Each stage automatically finds next approver
2. ✓ **Must Follow Chain**: Cannot skip stages (HOD → DEAN → EXAM)
3. ✓ **Only EXAM Can Publish**: No other role can make results public
4. ✓ **Notes Optional**: Each role can add optional notes
5. ✓ **Search Available**: Search by Student ID or Subject
6. ✓ **Full Audit Trail**: All actions logged for accountability

## Troubleshooting

**Q: My result doesn't appear in the next stage after I approved**
- A: Refresh the page. Check if status changed correctly.
  
**Q: Can I publish as HOD or DEAN?**
- A: No. Only EXAM Officer can publish. This ensures quality control.

**Q: What if EXAM Officer rejects?**
- A: Status goes back to `dean_rejected`. DEAN reviews again.

**Q: Can I see rejected results?**
- A: Yes, they appear in your dashboard as rejected with the original notes.

**Q: Who can see all results?**
- A: Each role sees only results assigned to them at their stage.

## Technical Details

**Workflow Model**: `admin_hierarchy.models.ResultApprovalWorkflow`
**Audit Log Model**: `admin_hierarchy.models.ApprovalHistory`
**Result Model**: `student.models.Result`

To check workflow status in Django shell:
```python
from admin_hierarchy.models import ResultApprovalWorkflow
w = ResultApprovalWorkflow.objects.get(id=1)
print(w.status)  # Current status
print(w.current_hod)  # Current HOD if awaiting HOD
print(w.current_dean)  # Current DEAN if awaiting DEAN
print(w.current_exam_officer)  # Current EXAM if awaiting EXAM
```

## Contact & Support

For issues or questions about the workflow, check:
- `WORKFLOW_CHAIN_DOCUMENTATION.md` - Full technical details
- `test_workflow_chain.py` - Working example of complete flow
- Database logs - Check `ApprovalHistory` for audit trail
