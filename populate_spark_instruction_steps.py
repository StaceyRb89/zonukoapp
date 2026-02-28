"""
Populate structured instruction_steps for Spark projects that don't have them.
Idempotent and safe to rerun.

Run with:
  c:/Users/zonuk/projects/zonukoapp/venv/Scripts/python.exe manage.py shell -c "exec(open('populate_spark_instruction_steps.py', encoding='utf-8').read())"
"""

import re
from apps.users.models import Project


def _clean_line(value):
    value = value.strip()
    value = re.sub(r'^[-*•\s]+', '', value)
    value = re.sub(r'^\d+[\.)]\s*', '', value)
    return value.strip()


def _split_numbered_block(text):
    # Handles: "1. Do this. 2. Do that. 3. Finish."
    matches = re.split(r'\s*(?:^|\s)\d+[\.)]\s*', text)
    parts = [_clean_line(part) for part in matches if _clean_line(part)]
    return parts


def _derive_steps(instructions):
    if not instructions:
        return []

    raw_lines = [line for line in instructions.replace('\r', '').split('\n') if line.strip()]
    steps = []

    for line in raw_lines:
        cleaned = _clean_line(line)
        if not cleaned:
            continue

        numbered_parts = _split_numbered_block(cleaned)
        if len(numbered_parts) >= 2:
            steps.extend(numbered_parts)
        else:
            steps.append(cleaned)

    if len(steps) <= 1:
        # Fallback: split by sentence boundaries
        sentence_parts = [
            _clean_line(part)
            for part in re.split(r'\.(?:\s+|$)', instructions)
            if _clean_line(part)
        ]
        if len(sentence_parts) > len(steps):
            steps = sentence_parts

    # Keep step count practical for cards
    steps = [step for step in steps if step][:8]

    return [
        {
            "title": f"Step {index}",
            "description": step,
            "image_url": "",
        }
        for index, step in enumerate(steps, start=1)
    ]


updated = 0
skipped = 0

sparks = Project.objects.filter(type=Project.TYPE_SPARK)

for project in sparks:
    existing = project.instruction_steps if isinstance(project.instruction_steps, list) else []
    if existing:
        skipped += 1
        continue

    steps = _derive_steps(project.instructions or "")
    if not steps:
        skipped += 1
        continue

    project.instruction_steps = steps
    project.save(update_fields=["instruction_steps", "updated_at"])
    updated += 1

print(f"✅ Populated Spark instruction steps. Updated: {updated}, Skipped: {skipped}")
