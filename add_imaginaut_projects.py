import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zonuko.settings')
django.setup()

from apps.users.models import Project, Skill

# Get or create skills
skills_data = [
    ('🎨 Creativity', 'Expressing ideas through art and imagination'),
    ('🔧 Engineering', 'Building and constructing with materials and tools'),
    ('🧠 Problem Solving', 'Breaking down complex challenges into manageable parts'),
    ('⚙️ Physics', 'Understanding forces, motion, and energy'),
    ('🏗️ Architecture', 'Designing and planning structures'),
]

skills_map = {}
for name, description in skills_data:
    skill, created = Skill.objects.get_or_create(
        name=name,
        defaults={'description': description}
    )
    skills_map[name] = skill
    if created:
        print(f'✅ Created skill: {name}')
    else:
        print(f'ℹ️  Skill exists: {name}')

# Create 3 new Imaginauts projects (Stage 1)
new_projects = [
    {
        'title': 'Bubble Art Laboratory',
        'description': 'Discover the magic of bubbles! Mix your own bubble solution, learn about surface tension, and create beautiful bubble art by mixing colors with bubbles.',
        'category': Project.SCIENCE,
        'type': Project.TYPE_SPARK,
        'difficulty': 1,
        'age_ranges': ['IMAGINAUTS'],
        'minimum_stage': 1,
        'estimated_time': 25,
        'visibility': Project.VISIBILITY_LIVE,
        'emoji': '🫧',
        'materials_needed': 'Dish soap, water, sugar, food coloring, straws, paper, shallow trays, bubble wand',
        'instructions': '1. Mix dish soap, water, and sugar to make bubble solution. 2. Add food coloring to paper plates. 3. Blow bubbles and pop them on the colored paper. 4. Watch the patterns form! 5. Experiment with different bubble sizes.',
        'video_url': 'https://www.youtube.com/watch?v=8WR7i7UXC9M',
        'skills': ['🎨 Creativity', '⚙️ Physics'],
        'skill_dimensions': {
            'creative_thinking': 4,
            'practical_making': 2,
            'problem_solving': 1,
            'resilience': 1,
        }
    },
    {
        'title': 'DIY Marble Run Challenge',
        'description': 'Engineer and build your own marble run using household items! Design a track that guides marbles through loops, jumps, and turns.',
        'category': Project.ENGINEERING,
        'type': Project.TYPE_LAB,
        'difficulty': 2,
        'age_ranges': ['IMAGINAUTS'],
        'minimum_stage': 1,
        'estimated_time': 40,
        'visibility': Project.VISIBILITY_LIVE,
        'emoji': '🎯',
        'materials_needed': 'Cardboard tubes, plastic pipes, marbles, tape, paper, blocks for support, scissors',
        'instructions': '1. Plan your marble run on paper. 2. Cut and arrange cardboard tubes. 3. Create loops and turns with tape. 4. Test your marbles. 5. Adjust for smooth flow. 6. Decorate your creation!',
        'video_url': 'https://www.youtube.com/watch?v=K0jQNVDjqXQ',
        'skills': ['🔧 Engineering', '🧠 Problem Solving', '🏗️ Architecture'],
        'skill_dimensions': {
            'creative_thinking': 3,
            'practical_making': 5,
            'problem_solving': 4,
            'resilience': 3,
        }
    },
    {
        'title': 'Straw Buildings Studio',
        'description': 'Become an architect! Use straws to create 3D structures. Learn about how real buildings stay standing through creative straw construction.',
        'category': Project.ENGINEERING,
        'type': Project.TYPE_LAB,
        'difficulty': 1,
        'age_ranges': ['IMAGINAUTS'],
        'minimum_stage': 1,
        'estimated_time': 35,
        'visibility': Project.VISIBILITY_LIVE,
        'emoji': '🏢',
        'materials_needed': 'Plastic straws, clay or playdough, scissors, ruler, markers for decoration',
        'instructions': '1. Create a base with playdough to hold straws. 2. Push straws into the base to form a structure. 3. Add cross-supports for stability. 4. Build towers, bridges, or buildings. 5. Test stability by gently pushing. 6. Decorate your structure!',
        'video_url': 'https://www.youtube.com/watch?v=pqvlGmFfSak',
        'skills': ['🏗️ Architecture', '🔧 Engineering', '🧠 Problem Solving'],
        'skill_dimensions': {
            'creative_thinking': 3,
            'practical_making': 4,
            'problem_solving': 3,
            'resilience': 2,
        }
    },
]

print('\n' + '='*60)
print('CREATING NEW IMAGINAUT PROJECTS')
print('='*60)

for project_data in new_projects:
    skills_list = project_data.pop('skills')
    
    project, created = Project.objects.get_or_create(
        title=project_data['title'],
        defaults=project_data
    )
    
    if created:
        # Add skills
        for skill_name in skills_list:
            skill = skills_map[skill_name]
            project.skills.add(skill)
        
        print(f'\n✅ Created project: {project.emoji} {project.title}')
        print(f'   Category: {project.get_category_display()}')
        print(f'   Type: {project.get_type_display()}')
        print(f'   Time: {project.estimated_time} minutes')
        print(f'   Skills: {", ".join(skills_list)}')
        print(f'   Skill Boosts: {project.skill_dimensions}')
    else:
        print(f'\nℹ️  Project already exists: {project.emoji} {project.title}')

print('\n' + '='*60)
print('DONE! New projects created successfully.')
print('='*60)
