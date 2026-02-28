"""
Safely clear legacy Project.instruction_steps JSON only when row-based
ProjectInstructionStep data already exists.

Run:
  c:/Users/zonuk/projects/zonukoapp/venv/Scripts/python.exe manage.py shell -c "exec(open('cleanup_legacy_instruction_steps.py', encoding='utf-8').read())"
"""

from apps.users.models import Project

APPLY_CHANGES = True

projects_scanned = 0
projects_with_legacy = 0
projects_cleared = 0
projects_skipped_no_rows = 0

for project in Project.objects.all().order_by("id"):
    projects_scanned += 1
    legacy_steps = project.instruction_steps if isinstance(project.instruction_steps, list) else []

    if not legacy_steps:
        continue

    projects_with_legacy += 1
    has_row_steps = project.instruction_step_items.exists()

    if not has_row_steps:
        projects_skipped_no_rows += 1
        continue

    if APPLY_CHANGES:
        project.instruction_steps = []
        project.save(update_fields=["instruction_steps", "updated_at"])

    projects_cleared += 1

print("=== Legacy Instruction Steps Cleanup ===")
print("APPLY_CHANGES:", APPLY_CHANGES)
print("Projects scanned:", projects_scanned)
print("Projects with legacy JSON:", projects_with_legacy)
print("Projects cleared:", projects_cleared)
print("Projects skipped (no row steps):", projects_skipped_no_rows)
