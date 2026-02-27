import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zonuko.settings')
django.setup()

from apps.users.models import Project, ChildProfile, ProjectProgress

print('\n=== ALL PROJECTS ===')
projects = Project.objects.all()
print(f'Total: {projects.count()}\n')
for p in projects:
    print(f'{p.id}. {p.title}')
    print(f'   Age ranges: {p.age_ranges}')
    print(f'   Min stage: {p.minimum_stage}')
    print(f'   Visibility: {p.visibility}')
    print()

print('\n=== CHILDREN ===')
children = ChildProfile.objects.all()
for child in children:
    print(f'\n{child.username} ({child.age_range})')
    print(f'Current stage: {child.progression_stage.current_stage if hasattr(child, "progression_stage") else "N/A"}')
    
    # Check their progress
    progress_items = ProjectProgress.objects.filter(child=child)
    print(f'Total progress records: {progress_items.count()}')
    
    completed = progress_items.filter(completed_at__isnull=False)
    print(f'Completed projects: {completed.count()}')
    for prog in completed:
        print(f'  - {prog.project.title} (completed: {prog.completed_at.strftime("%Y-%m-%d")})')
    
    # Show ALL progress records
    print(f'All progress records:')
    for prog in progress_items:
        status = 'COMPLETED' if prog.completed_at else prog.status
        print(f'  - {prog.project.title}: {status}')
