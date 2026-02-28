"""
Dry-run migration helper for instruction steps.

Purpose:
- Read legacy Project.instruction_steps JSON
- Compare against new ProjectInstructionStep rows
- Report what would be created/updated
- Do NOT write changes unless APPLY_CHANGES = True

Run:
  c:/Users/zonuk/projects/zonukoapp/venv/Scripts/python.exe manage.py shell -c "exec(open('dry_run_instruction_step_migration.py', encoding='utf-8').read())"
"""

from apps.users.models import Project, ProjectInstructionStep

APPLY_CHANGES = True


def normalize_step(step, index):
    if isinstance(step, dict):
        title = step.get("title") or f"Step {index}"
        description = (step.get("description") or step.get("text") or "").strip()
    else:
        title = f"Step {index}"
        description = str(step).strip()

    return {
        "order": index,
        "title": title.strip()[:120] if title else f"Step {index}",
        "description": description,
    }


total_projects = 0
projects_with_legacy_json = 0
projects_with_new_rows = 0
projects_needing_migration = 0
steps_to_create = 0
steps_to_update = 0
sample_changes = []

for project in Project.objects.all().order_by("id"):
    total_projects += 1

    legacy_steps = project.instruction_steps if isinstance(project.instruction_steps, list) else []
    if not legacy_steps:
        continue

    projects_with_legacy_json += 1

    normalized_legacy = [normalize_step(step, idx) for idx, step in enumerate(legacy_steps, start=1)]
    existing_rows = list(project.instruction_step_items.all().order_by("order", "id"))

    if existing_rows:
        projects_with_new_rows += 1

    existing_by_order = {row.order: row for row in existing_rows}

    project_creates = 0
    project_updates = 0

    for legacy in normalized_legacy:
        row = existing_by_order.get(legacy["order"])
        if row is None:
            project_creates += 1
            if APPLY_CHANGES:
                ProjectInstructionStep.objects.create(
                    project=project,
                    order=legacy["order"],
                    title=legacy["title"],
                    description=legacy["description"],
                )
        else:
            needs_update = (row.title != legacy["title"]) or (row.description != legacy["description"])
            if needs_update:
                project_updates += 1
                if APPLY_CHANGES:
                    row.title = legacy["title"]
                    row.description = legacy["description"]
                    row.save(update_fields=["title", "description", "updated_at"])

    if project_creates or project_updates:
        projects_needing_migration += 1
        steps_to_create += project_creates
        steps_to_update += project_updates
        if len(sample_changes) < 10:
            sample_changes.append(
                f"- {project.title}: create {project_creates}, update {project_updates}"
            )

print("=== Instruction Step Migration (Dry Run) ===")
print("APPLY_CHANGES:", APPLY_CHANGES)
print("Total projects:", total_projects)
print("Projects with legacy JSON:", projects_with_legacy_json)
print("Projects already using new step rows:", projects_with_new_rows)
print("Projects needing migration:", projects_needing_migration)
print("Step rows to create:", steps_to_create)
print("Step rows to update:", steps_to_update)

if sample_changes:
    print("\nSample affected projects:")
    for line in sample_changes:
        print(line)
else:
    print("\nNo changes needed.")
