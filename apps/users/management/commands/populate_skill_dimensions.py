"""
Management command to populate skill_dimensions for existing projects
Based on category and difficulty
"""
from django.core.management.base import BaseCommand
from apps.users.models import Project


class Command(BaseCommand):
    help = 'Populate skill_dimensions for projects based on category and difficulty'

    def handle(self, *args, **options):
        """Assign skill dimensions to projects based on their category"""
        
        # Skill dimension templates by category
        CATEGORY_DIMENSIONS = {
            'science': {
                'creative_thinking': 3,
                'practical_making': 4,
                'problem_solving': 5,  # Science is heavy on problem solving
                'resilience': 2,
            },
            'tech': {
                'creative_thinking': 4,
                'practical_making': 3,
                'problem_solving': 5,  # Tech requires logical thinking
                'resilience': 3,
            },
            'engineering': {
                'creative_thinking': 3,
                'practical_making': 5,  # Engineering is very hands-on
                'problem_solving': 4,
                'resilience': 3,
            },
            'art': {
                'creative_thinking': 5,  # Art is highly creative
                'practical_making': 4,
                'problem_solving': 2,
                'resilience': 2,
            },
            'math': {
                'creative_thinking': 3,
                'practical_making': 2,
                'problem_solving': 5,  # Math is problem-solving heavy
                'resilience': 3,
            },
        }
        
        projects = Project.objects.all()
        updated_count = 0
        
        for project in projects:
            # Get base dimensions for this category
            base_dims = CATEGORY_DIMENSIONS.get(project.category, {
                'creative_thinking': 3,
                'practical_making': 3,
                'problem_solving': 3,
                'resilience': 2,
            })
            
            # Adjust based on difficulty (1=Easy, 2=Medium, 3=Hard)
            difficulty_multiplier = 0.8 + (project.difficulty * 0.2)  # 1.0, 1.2, 1.4
            
            skill_dimensions = {}
            for pathway, value in base_dims.items():
                adjusted = int(value * difficulty_multiplier)
                skill_dimensions[pathway] = min(5, max(1, adjusted))  # Keep between 1-5
            
            # Harder projects build more resilience
            if project.difficulty >= 2:
                skill_dimensions['resilience'] = min(5, skill_dimensions['resilience'] + 1)
            
            project.skill_dimensions = skill_dimensions
            project.save()
            updated_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ {project.emoji} {project.title}: {skill_dimensions}'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Updated {updated_count} projects with skill dimensions')
        )
