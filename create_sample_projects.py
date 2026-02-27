"""
Script to create sample projects for testing the content engine.
Run with: python manage.py shell < create_sample_projects.py
"""

from apps.users.models import Project, Skill, ProjectSkill
from django.utils import timezone

# First, create skills if they don't exist
skills_data = [
    ('🧠 Problem Solving', 'Breaking down complex challenges into manageable parts'),
    ('🔧 Engineering', 'Building and constructing with materials and tools'),
    ('🔬 Scientific Method', 'Observing, hypothesizing, testing, and learning'),
    ('🎨 Creativity', 'Expressing ideas through art and imagination'),
    ('💻 Technology', 'Using digital tools and coding'),
    ('🤝 Collaboration', 'Working together and learning from others'),
    ('💧 Environmental Science', 'Understanding water, ecosystems, and sustainability'),
    ('⚙️ Physics', 'Understanding forces, motion, and energy'),
]

print("Creating skills...")
skills_map = {}
for name, description in skills_data:
    skill, created = Skill.objects.get_or_create(
        name=name,
        defaults={'description': description}
    )
    skills_map[name] = skill
    if created:
        print(f"  ✅ Created: {name}")
    else:
        print(f"  ℹ️  Exists: {name}")

# Sample projects
projects_data = [
    # Stage 1 - Explorer (Easy, introductory)
    {
        'title': 'Tie-Dye T-Shirt Design',
        'description': 'Learn the art of tie-dye! Discover how color patterns form when you fold and dye fabric. A fun, tactile introduction to color mixing.',
        'category': Project.ART,
        'type': Project.TYPE_SPARK,
        'difficulty': 1,
        'age_ranges': ['IMAGINAUTS'],
        'minimum_stage': 1,
        'estimated_time': 20,
        'visibility': Project.VISIBILITY_LIVE,
        'is_featured': True,
        'emoji': '🎨',
        'materials_needed': 'White cotton t-shirt, rubber bands, tie-dye kit or food coloring, water, plastic bags',
        'instructions': '1. Fold your t-shirt in interesting ways. 2. Secure with rubber bands. 3. Mix your dye. 4. Apply colors. 5. Let sit overnight. 6. Rinse and dry.',
        'skills': ['🎨 Creativity', '⚙️ Physics'],
    },
    {
        'title': 'Paper Tower Challenge',
        'description': 'How tall can you build a tower using only paper and tape? Learn about structural stability while having fun.',
        'category': Project.ENGINEERING,
        'type': Project.TYPE_SPARK,
        'difficulty': 1,
        'age_ranges': ['IMAGINAUTS'],
        'minimum_stage': 1,
        'estimated_time': 15,
        'visibility': Project.VISIBILITY_LIVE,
        'emoji': '📄',
        'materials_needed': 'Paper (newspaper, printer paper), tape, ruler',
        'instructions': '1. Roll paper into tubes. 2. Connect tubes with tape. 3. Build upward. 4. Measure your height. 5. Try to beat your record!',
        'skills': ['🔧 Engineering', '🧠 Problem Solving'],
    },
    {
        'title': 'Crystal Garden',
        'description': 'Grow beautiful crystals at home! A classic STEM experiment that shows how salt or sugar forms patterns over time.',
        'category': Project.SCIENCE,
        'type': Project.TYPE_LAB,
        'difficulty': 1,
        'age_ranges': ['IMAGINAUTS', 'NAVIGATORS'],
        'minimum_stage': 1,
        'estimated_time': 30,
        'visibility': Project.VISIBILITY_LIVE,
        'emoji': '💎',
        'materials_needed': 'Salt or borax, hot water, jar, spoon, food coloring (optional), pipe cleaners (optional)',
        'instructions': '1. Dissolve salt in hot water. 2. Pour into jar. 3. Let cool slowly. 4. Crystals will form over 24-48 hours. 5. Observe and measure.',
        'skills': ['🔬 Scientific Method', '💧 Environmental Science'],
    },
    
    # Stage 2 - Experimenter (Medium difficulty)
    {
        'title': 'Build a Water Filter',
        'description': 'Create your own water filtration system using sand, gravel, and charcoal. Learn how water treatment works in the real world.',
        'category': Project.SCIENCE,
        'type': Project.TYPE_LAB,
        'difficulty': 2,
        'age_ranges': ['IMAGINAUTS', 'NAVIGATORS', 'TRAILBLAZERS'],
        'minimum_stage': 2,
        'estimated_time': 45,
        'visibility': Project.VISIBILITY_LIVE,
        'emoji': '💧',
        'materials_needed': 'Two clear bottles, sand, gravel, activated charcoal, cotton balls, dirty water, measuring cup',
        'instructions': '1. Cut bottle in half. 2. Layer materials: cotton, charcoal, sand, gravel. 3. Pour dirty water through. 4. Observe filtered water. 5. Test clarity.',
        'skills': ['🔬 Scientific Method', '💧 Environmental Science', '🧠 Problem Solving'],
    },
    {
        'title': 'Make a Siphon',
        'description': 'Master the physics of siphoning! Learn how to move water uphill without a pump using gravity and air pressure.',
        'category': Project.ENGINEERING,
        'type': Project.TYPE_LAB,
        'difficulty': 2,
        'age_ranges': ['NAVIGATORS', 'TRAILBLAZERS'],
        'minimum_stage': 2,
        'estimated_time': 30,
        'visibility': Project.VISIBILITY_LIVE,
        'is_featured': True,
        'emoji': '🌊',
        'materials_needed': 'Flexible tubing, two containers at different heights, water',
        'instructions': '1. Fill tube with water. 2. Block both ends. 3. Position in containers. 4. Release to start siphon. 5. Observe continuous flow.',
        'skills': ['⚙️ Physics', '🔧 Engineering', '🔬 Scientific Method'],
    },
    {
        'title': 'Simple Circuit Challenge',
        'description': 'Build a working electrical circuit with a battery, LED, and resistor. Your first step into electronics!',
        'category': Project.TECH,
        'type': Project.TYPE_LAB,
        'difficulty': 2,
        'age_ranges': ['NAVIGATORS', 'TRAILBLAZERS'],
        'minimum_stage': 2,
        'estimated_time': 20,
        'visibility': Project.VISIBILITY_LIVE,
        'emoji': '💡',
        'materials_needed': 'Battery (AA or AAA), LED, resistor, jumper wires or copper wire, breadboard or tape',
        'instructions': '1. Connect positive battery terminal. 2. Add resistor. 3. Add LED (note polarity). 4. Complete circuit to negative. 5. Light up!',
        'skills': ['💻 Technology', '⚙️ Physics', '🧠 Problem Solving'],
    },
    
    # Stage 3 - Builder (Challenging)
    {
        'title': 'Build a Wattle and Daub Structure',
        'description': 'Construct a historical building technique used for centuries. Learn architecture and material science by building your own miniature structure.',
        'category': Project.ENGINEERING,
        'type': Project.TYPE_LAB,
        'difficulty': 3,
        'age_ranges': ['NAVIGATORS', 'TRAILBLAZERS'],
        'minimum_stage': 3,
        'estimated_time': 120,
        'visibility': Project.VISIBILITY_LIVE,
        'is_featured': True,
        'emoji': '🏗️',
        'materials_needed': 'Wooden dowels or thin branches, clay or mud, straw or hay, water, wooden frame (or build from larger dowels)',
        'instructions': '1. Create wooden frame. 2. Weave thin branches (wattle). 3. Mix clay and straw (daub). 4. Cover frame with daub. 5. Let dry. 6. Observe structural integrity.',
        'skills': ['🔧 Engineering', '🧠 Problem Solving', '⚙️ Physics'],
    },
    {
        'title': 'Marble Run Machine',
        'description': 'Design and build an elaborate marble run with ramps, loops, and obstacles. A project combining engineering, physics, and creativity.',
        'category': Project.ENGINEERING,
        'type': Project.TYPE_LAB,
        'difficulty': 3,
        'age_ranges': ['IMAGINAUTS', 'NAVIGATORS', 'TRAILBLAZERS'],
        'minimum_stage': 2,
        'estimated_time': 90,
        'visibility': Project.VISIBILITY_LIVE,
        'emoji': '🔴',
        'materials_needed': 'Cardboard tubes, marble or ball, wooden dowels, tape, scissors, ramps, containers',
        'instructions': '1. Plan your run on paper. 2. Build ramps at angles. 3. Create obstacles. 4. Test with marble. 5. Adjust and refine.',
        'skills': ['🔧 Engineering', '⚙️ Physics', '🎨 Creativity', '🧠 Problem Solving'],
    },
    {
        'title': 'Build a Miniature Catapult',
        'description': 'Engineer a working catapult using simple materials. Learn about levers, energy, and force while launching projectiles!',
        'category': Project.ENGINEERING,
        'type': Project.TYPE_LAB,
        'difficulty': 2,
        'age_ranges': ['IMAGINAUTS', 'NAVIGATORS', 'TRAILBLAZERS'],
        'minimum_stage': 2,
        'estimated_time': 45,
        'visibility': Project.VISIBILITY_LIVE,
        'emoji': '🎯',
        'materials_needed': 'Wooden spoon or popsicle sticks, rubber band, container, projectiles (small stones or foam), tape',
        'instructions': '1. Bundle sticks for base. 2. Attach spoon with rubber band. 3. Create launch cup. 4. Test launches. 5. Measure distance.',
        'skills': ['🔧 Engineering', '⚙️ Physics', '🧠 Problem Solving'],
    },
    
    # Stage 4 - Designer (Advanced, cross-disciplinary)
    {
        'title': 'Design Your Own Ecosystem',
        'description': 'Create a living terrarium ecosystem. Research, design, and build a closed system that sustains plant life.',
        'category': Project.SCIENCE,
        'type': Project.TYPE_LAB,
        'difficulty': 3,
        'age_ranges': ['NAVIGATORS', 'TRAILBLAZERS'],
        'minimum_stage': 4,
        'estimated_time': 60,
        'visibility': Project.VISIBILITY_LIVE,
        'emoji': '🌿',
        'materials_needed': 'Clear container with lid, soil, rocks, plants, water, charcoal, moss',
        'instructions': '1. Research terrarium design. 2. Layer materials. 3. Select appropriate plants. 4. Add water. 5. Seal and observe over weeks.',
        'skills': ['🔬 Scientific Method', '💧 Environmental Science', '🎨 Creativity'],
    },
    {
        'title': 'Code a Simple Game',
        'description': 'Create your first game! Use Python or JavaScript to build an interactive game. Learn programming logic and creative problem-solving.',
        'category': Project.TECH,
        'type': Project.TYPE_LAB,
        'difficulty': 3,
        'age_ranges': ['NAVIGATORS', 'TRAILBLAZERS'],
        'minimum_stage': 3,
        'estimated_time': 120,
        'visibility': Project.VISIBILITY_LIVE,
        'emoji': '🎮',
        'materials_needed': 'Computer, Python or JavaScript, text editor',
        'instructions': '1. Plan your game (tic-tac-toe, number guessing, etc). 2. Write code. 3. Test gameplay. 4. Debug issues. 5. Share with friends!',
        'skills': ['💻 Technology', '🧠 Problem Solving', '🤝 Collaboration'],
    },
    
    # Stage 5 - Independent Maker (Expert)
    {
        'title': 'Advanced Robotics Challenge',
        'description': 'Build and program a robot to complete a complex task. Integrate engineering, coding, and problem-solving at an advanced level.',
        'category': Project.TECH,
        'type': Project.TYPE_LAB,
        'difficulty': 3,
        'age_ranges': ['TRAILBLAZERS'],
        'minimum_stage': 5,
        'estimated_time': 240,
        'visibility': Project.VISIBILITY_LIVE,
        'emoji': '🤖',
        'materials_needed': 'Robot kit (LEGO, Arduino, etc), sensors, motors, programming environment',
        'instructions': '1. Design robot. 2. Build structure. 3. Add sensors. 4. Program behavior. 5. Test and iterate.',
        'skills': ['💻 Technology', '🔧 Engineering', '⚙️ Physics', '🧠 Problem Solving'],
    },
    
    # Coming Soon Projects
    {
        'title': 'Build a Wind Turbine',
        'description': 'Harness renewable energy! Create a model wind turbine and measure how it converts wind into electricity.',
        'category': Project.ENGINEERING,
        'type': Project.TYPE_LAB,
        'difficulty': 3,
        'age_ranges': ['NAVIGATORS', 'TRAILBLAZERS'],
        'minimum_stage': 4,
        'estimated_time': 90,
        'visibility': Project.VISIBILITY_COMING_SOON,
        'emoji': '💨',
        'materials_needed': 'Plastic cups or cardboard, dowel, motor, LED, tape',
        'instructions': 'Coming soon! Stay tuned.',
        'skills': ['⚙️ Physics', '💡 Engineering'],
    },
]

# Create projects
print("\nCreating projects...")
for proj_data in projects_data:
    skill_names = proj_data.pop('skills')
    
    project, created = Project.objects.get_or_create(
        title=proj_data['title'],
        defaults=proj_data
    )
    
    if created:
        # Add skills with weights
        for i, skill_name in enumerate(skill_names):
            if skill_name in skills_map:
                weight = 5 if i == 0 else 3  # Primary skill gets weight 5
                ProjectSkill.objects.get_or_create(
                    project=project,
                    skill=skills_map[skill_name],
                    defaults={'weight': weight}
                )
        print(f"  ✅ Created: {project.emoji} {project.title}")
    else:
        print(f"  ℹ️  Exists: {project.emoji} {project.title}")

print("\n✨ Sample projects created! Visit http://127.0.0.1:8000/creator/users/project/ to view them.")
