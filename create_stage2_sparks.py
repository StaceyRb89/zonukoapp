"""
Create stage-2 Spark projects for Navigators and Trailblazers.
Idempotent: safe to run multiple times.

Run with:
  c:/Users/zonuk/projects/zonukoapp/venv/Scripts/python.exe manage.py shell -c "exec(open('create_stage2_sparks.py', encoding='utf-8').read())"
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


STAGE2_SPARKS = [
    # NAVIGATORS stage 2
    {
        "title": "Hydro Test Sprint",
        "description": "Run rapid filtration mini-tests and compare clarity results with a simple scoring method.",
        "category": Project.SCIENCE,
        "type": Project.TYPE_SPARK,
        "difficulty": 2,
        "age_ranges": ["NAVIGATORS"],
        "minimum_stage": 2,
        "estimated_time": 18,
        "visibility": Project.VISIBILITY_LIVE,
        "emoji": "🧪",
        "materials_needed": "2 cups, coffee filters, sand, gravel, dirty water sample, score sheet",
        "instructions": "1. Build two filter variants. 2. Run each test. 3. Score clarity. 4. Explain best design choice.",
        "tags": ["water", "testing", "analysis"],
        "skill_dimensions": {
            "creative_thinking": 1,
            "practical_making": 3,
            "problem_solving": 3,
            "resilience": 2,
        },
        "skills": ["🔬 Scientific Method", "💧 Environmental Science", "🧠 Problem Solving"],
    },
    {
        "title": "Circuit Debug Dash",
        "description": "Diagnose and repair a pre-broken simple circuit under timed constraints.",
        "category": Project.TECH,
        "type": Project.TYPE_SPARK,
        "difficulty": 2,
        "age_ranges": ["NAVIGATORS"],
        "minimum_stage": 2,
        "estimated_time": 16,
        "visibility": Project.VISIBILITY_LIVE,
        "emoji": "🔌",
        "materials_needed": "Battery, LED, resistor, jumper wires, bug checklist",
        "instructions": "1. Inspect the circuit. 2. Find faults. 3. Repair and test. 4. Document the fix path.",
        "tags": ["electronics", "debug", "logic"],
        "skill_dimensions": {
            "creative_thinking": 1,
            "practical_making": 2,
            "problem_solving": 4,
            "resilience": 2,
        },
        "skills": ["💻 Technology", "⚙️ Physics", "🧠 Problem Solving"],
    },
    {
        "title": "Flow Force Microbuild",
        "description": "Build a mini fluid-flow rig and predict pressure changes across different heights.",
        "category": Project.ENGINEERING,
        "type": Project.TYPE_SPARK,
        "difficulty": 2,
        "age_ranges": ["NAVIGATORS"],
        "minimum_stage": 2,
        "estimated_time": 20,
        "visibility": Project.VISIBILITY_LIVE,
        "emoji": "🌊",
        "materials_needed": "Clear tubing, two bottles, clips, ruler",
        "instructions": "1. Assemble the rig. 2. Change height difference. 3. Observe flow behavior. 4. Record explanation.",
        "tags": ["flow", "pressure", "physics"],
        "skill_dimensions": {
            "creative_thinking": 1,
            "practical_making": 4,
            "problem_solving": 3,
            "resilience": 1,
        },
        "skills": ["⚙️ Physics", "🔧 Engineering", "🔬 Scientific Method"],
    },

    # TRAILBLAZERS stage 2
    {
        "title": "Rapid Prototype Loop",
        "description": "Run a two-iteration design sprint and justify what changed between versions.",
        "category": Project.ENGINEERING,
        "type": Project.TYPE_SPARK,
        "difficulty": 2,
        "age_ranges": ["TRAILBLAZERS"],
        "minimum_stage": 2,
        "estimated_time": 20,
        "visibility": Project.VISIBILITY_LIVE,
        "emoji": "🛠️",
        "materials_needed": "Cardboard, tape, marker, timer",
        "instructions": "1. Build v1 in 8 mins. 2. Test and critique. 3. Build v2. 4. Compare decisions and outcomes.",
        "tags": ["prototype", "iterate", "design"],
        "skill_dimensions": {
            "creative_thinking": 3,
            "practical_making": 4,
            "problem_solving": 2,
            "resilience": 2,
        },
        "skills": ["🔧 Engineering", "🎨 Creativity", "🧠 Problem Solving"],
    },
    {
        "title": "Energy Transfer Sprint",
        "description": "Test multiple launch systems and quantify how design changes alter output distance.",
        "category": Project.SCIENCE,
        "type": Project.TYPE_SPARK,
        "difficulty": 2,
        "age_ranges": ["TRAILBLAZERS"],
        "minimum_stage": 2,
        "estimated_time": 18,
        "visibility": Project.VISIBILITY_LIVE,
        "emoji": "🚀",
        "materials_needed": "Rubber bands, spoon, paper balls, tape measure",
        "instructions": "1. Build 2 launch variants. 2. Run 3 trials each. 3. Measure distance. 4. Explain energy transfer.",
        "tags": ["energy", "measurement", "physics"],
        "skill_dimensions": {
            "creative_thinking": 1,
            "practical_making": 3,
            "problem_solving": 4,
            "resilience": 2,
        },
        "skills": ["⚙️ Physics", "🔧 Engineering", "🧠 Problem Solving"],
    },
    {
        "title": "Data Ethics Micro Case",
        "description": "Solve a short tech ethics scenario and defend your decision framework.",
        "category": Project.TECH,
        "type": Project.TYPE_SPARK,
        "difficulty": 2,
        "age_ranges": ["TRAILBLAZERS"],
        "minimum_stage": 2,
        "estimated_time": 15,
        "visibility": Project.VISIBILITY_LIVE,
        "emoji": "⚖️",
        "materials_needed": "Scenario card set, decision matrix worksheet",
        "instructions": "1. Read case. 2. Identify trade-offs. 3. Choose decision criteria. 4. Present final recommendation.",
        "tags": ["ethics", "technology", "decision"],
        "skill_dimensions": {
            "creative_thinking": 2,
            "practical_making": 1,
            "problem_solving": 4,
            "resilience": 1,
        },
        "skills": ["💻 Technology", "🤝 Collaboration", "🧠 Problem Solving"],
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

for row in STAGE2_SPARKS:
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

    for index, skill_name in enumerate(skill_names):
        weight = 5 if index == 0 else 3
        ProjectSkill.objects.update_or_create(
            project=project,
            skill=skills_map[skill_name],
            defaults={"weight": weight},
        )

print(f"✅ Stage-2 sparks seeded. Created: {created_count}, Updated: {updated_count}")
print("   Navigators stage-2 sparks:", Project.objects.filter(type=Project.TYPE_SPARK, minimum_stage=2, age_ranges__icontains='NAVIGATORS').count())
print("   Trailblazers stage-2 sparks:", Project.objects.filter(type=Project.TYPE_SPARK, minimum_stage=2, age_ranges__icontains='TRAILBLAZERS').count())
