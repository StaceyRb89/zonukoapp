"""
Create age-appropriate Spark projects for Navigators and Trailblazers.
Idempotent: safe to run multiple times.

Run with:
  c:/Users/zonuk/projects/zonukoapp/venv/Scripts/python.exe manage.py shell -c "exec(open('create_age_band_sparks.py', encoding='utf-8').read())"
"""

from apps.users.models import Project, Skill, ProjectSkill


SKILLS_REQUIRED = {
    "🧠 Problem Solving": "Breaking down complex challenges into manageable parts",
    "🔧 Engineering": "Building and constructing with materials and tools",
    "🔬 Scientific Method": "Observing, hypothesizing, testing, and learning",
    "🎨 Creativity": "Expressing ideas through art and imagination",
    "💻 Technology": "Using digital tools and coding",
    "🤝 Collaboration": "Working together and learning from others",
    "💧 Environmental Science": "Understanding water, ecosystems, and sustainability",
    "⚙️ Physics": "Understanding forces, motion, and energy",
}


SPARK_PROJECTS = [
    # NAVIGATORS (11–13) - Stage 1 sparks
    {
        "title": "Data Pattern Sprint",
        "description": "Find patterns in real-world mini datasets and turn them into quick visual insights.",
        "category": Project.TECH,
        "type": Project.TYPE_SPARK,
        "difficulty": 1,
        "age_ranges": ["NAVIGATORS"],
        "minimum_stage": 1,
        "estimated_time": 15,
        "visibility": Project.VISIBILITY_LIVE,
        "emoji": "📊",
        "materials_needed": "Printed mini data cards, graph paper, colored pens",
        "instructions": "1. Pick a data card set. 2. Group values into patterns. 3. Sketch a visual chart. 4. Explain one insight.",
        "tags": ["patterns", "data", "insight"],
        "skill_dimensions": {
            "creative_thinking": 2,
            "practical_making": 1,
            "problem_solving": 4,
            "resilience": 2,
        },
        "skills": ["🧠 Problem Solving", "💻 Technology", "🤝 Collaboration"],
    },
    {
        "title": "Bridge Remix Spark",
        "description": "Remix a simple paper bridge design to hold more weight with fewer materials.",
        "category": Project.ENGINEERING,
        "type": Project.TYPE_SPARK,
        "difficulty": 1,
        "age_ranges": ["NAVIGATORS"],
        "minimum_stage": 1,
        "estimated_time": 18,
        "visibility": Project.VISIBILITY_LIVE,
        "emoji": "🌉",
        "materials_needed": "Paper strips, tape, coins or washers",
        "instructions": "1. Build a base bridge. 2. Test load. 3. Change one variable. 4. Retest and compare.",
        "tags": ["engineering", "load", "iterate"],
        "skill_dimensions": {
            "creative_thinking": 2,
            "practical_making": 4,
            "problem_solving": 3,
            "resilience": 2,
        },
        "skills": ["🔧 Engineering", "⚙️ Physics", "🧠 Problem Solving"],
    },
    {
        "title": "Eco Sensor Sketch",
        "description": "Design a low-fi environmental sensor idea and test what data it should capture.",
        "category": Project.SCIENCE,
        "type": Project.TYPE_SPARK,
        "difficulty": 1,
        "age_ranges": ["NAVIGATORS"],
        "minimum_stage": 1,
        "estimated_time": 16,
        "visibility": Project.VISIBILITY_LIVE,
        "emoji": "🌿",
        "materials_needed": "Paper, marker pens, optional recycled materials",
        "instructions": "1. Pick an environment problem. 2. Sketch a sensor concept. 3. Define measurable signals. 4. Share test plan.",
        "tags": ["environment", "sensor", "prototype"],
        "skill_dimensions": {
            "creative_thinking": 3,
            "practical_making": 2,
            "problem_solving": 3,
            "resilience": 1,
        },
        "skills": ["💧 Environmental Science", "🔬 Scientific Method", "🔧 Engineering"],
    },
    {
        "title": "Algorithm Maze Cards",
        "description": "Use instruction cards to navigate a maze and debug logic when it breaks.",
        "category": Project.TECH,
        "type": Project.TYPE_SPARK,
        "difficulty": 1,
        "age_ranges": ["NAVIGATORS"],
        "minimum_stage": 1,
        "estimated_time": 14,
        "visibility": Project.VISIBILITY_LIVE,
        "emoji": "🧩",
        "materials_needed": "Maze sheet, direction cards, timer",
        "instructions": "1. Build an instruction sequence. 2. Run the maze. 3. Debug failed steps. 4. Optimize path.",
        "tags": ["algorithm", "debug", "logic"],
        "skill_dimensions": {
            "creative_thinking": 1,
            "practical_making": 1,
            "problem_solving": 4,
            "resilience": 3,
        },
        "skills": ["💻 Technology", "🧠 Problem Solving", "🤝 Collaboration"],
    },

    # TRAILBLAZERS (14–16) - Stage 1 sparks
    {
        "title": "Startup Pitch Spark",
        "description": "Create a 90-second micro-pitch for a problem-solving product idea.",
        "category": Project.ART,
        "type": Project.TYPE_SPARK,
        "difficulty": 1,
        "age_ranges": ["TRAILBLAZERS"],
        "minimum_stage": 1,
        "estimated_time": 20,
        "visibility": Project.VISIBILITY_LIVE,
        "emoji": "🎤",
        "materials_needed": "Pitch canvas sheet, timer, optional slides",
        "instructions": "1. Choose a real problem. 2. Define your solution. 3. Craft 3 key points. 4. Deliver and refine.",
        "tags": ["pitch", "communication", "design"],
        "skill_dimensions": {
            "creative_thinking": 4,
            "practical_making": 1,
            "problem_solving": 3,
            "resilience": 2,
        },
        "skills": ["🎨 Creativity", "🤝 Collaboration", "🧠 Problem Solving"],
    },
    {
        "title": "Solar Tracker Mini Build",
        "description": "Prototype a simple adjustable solar angle rig and test light-capture changes.",
        "category": Project.ENGINEERING,
        "type": Project.TYPE_SPARK,
        "difficulty": 1,
        "age_ranges": ["TRAILBLAZERS"],
        "minimum_stage": 1,
        "estimated_time": 18,
        "visibility": Project.VISIBILITY_LIVE,
        "emoji": "☀️",
        "materials_needed": "Cardboard, skewer, protractor, tape, torch/light source",
        "instructions": "1. Build angle frame. 2. Test three angles. 3. Record light response. 4. Pick best orientation.",
        "tags": ["solar", "angles", "prototype"],
        "skill_dimensions": {
            "creative_thinking": 2,
            "practical_making": 4,
            "problem_solving": 3,
            "resilience": 1,
        },
        "skills": ["⚙️ Physics", "🔧 Engineering", "🔬 Scientific Method"],
    },
    {
        "title": "Debug Sprint: Broken Bot",
        "description": "Fix a deliberately broken pseudo-code flow and ship a clean version fast.",
        "category": Project.TECH,
        "type": Project.TYPE_SPARK,
        "difficulty": 1,
        "age_ranges": ["TRAILBLAZERS"],
        "minimum_stage": 1,
        "estimated_time": 15,
        "visibility": Project.VISIBILITY_LIVE,
        "emoji": "🤖",
        "materials_needed": "Pseudo-code worksheet, bug checklist",
        "instructions": "1. Read broken flow. 2. Identify failures. 3. Patch logic. 4. Validate with test cases.",
        "tags": ["debug", "logic", "tests"],
        "skill_dimensions": {
            "creative_thinking": 1,
            "practical_making": 1,
            "problem_solving": 5,
            "resilience": 3,
        },
        "skills": ["💻 Technology", "🧠 Problem Solving", "🤝 Collaboration"],
    },
    {
        "title": "Systems Mapping Spark",
        "description": "Map a local sustainability system and identify one leverage point for improvement.",
        "category": Project.SCIENCE,
        "type": Project.TYPE_SPARK,
        "difficulty": 1,
        "age_ranges": ["TRAILBLAZERS"],
        "minimum_stage": 1,
        "estimated_time": 17,
        "visibility": Project.VISIBILITY_LIVE,
        "emoji": "🗺️",
        "materials_needed": "Paper, sticky notes, pens",
        "instructions": "1. Pick a system (water, food, waste). 2. Map inputs/outputs. 3. Identify bottleneck. 4. Propose intervention.",
        "tags": ["systems", "sustainability", "analysis"],
        "skill_dimensions": {
            "creative_thinking": 3,
            "practical_making": 1,
            "problem_solving": 4,
            "resilience": 1,
        },
        "skills": ["💧 Environmental Science", "🔬 Scientific Method", "🤝 Collaboration"],
    },
]


def ensure_skills():
    skills = {}
    for name, description in SKILLS_REQUIRED.items():
        skill, _ = Skill.objects.get_or_create(name=name, defaults={"description": description})
        skills[name] = skill
    return skills


skills_map = ensure_skills()
created_count = 0
updated_count = 0

for row in SPARK_PROJECTS:
    skill_names = row.pop("skills")

    project, created = Project.objects.get_or_create(
        title=row["title"],
        defaults=row,
    )

    if not created:
        for field, value in row.items():
            setattr(project, field, value)
        project.save()
        updated_count += 1
    else:
        created_count += 1

    for skill_name in skill_names:
        weight = 5 if skill_name == skill_names[0] else 3
        ProjectSkill.objects.update_or_create(
            project=project,
            skill=skills_map[skill_name],
            defaults={"weight": weight},
        )

print(f"✅ Sparks seeded. Created: {created_count}, Updated: {updated_count}")
print("   Navigators sparks:", Project.objects.filter(type=Project.TYPE_SPARK, age_ranges__icontains='NAVIGATORS').count())
print("   Trailblazers sparks:", Project.objects.filter(type=Project.TYPE_SPARK, age_ranges__icontains='TRAILBLAZERS').count())
