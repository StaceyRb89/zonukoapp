#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zonuko.settings')
django.setup()

from apps.users.models import Project

# Add video URLs to projects
video_map = {
    'Tie-Dye T-Shirt Design': 'https://www.youtube.com/watch?v=Z8R-RA7qdYE',
    'Paper Tower Challenge': 'https://www.youtube.com/watch?v=7FU6N_i6gOQ',
    'Crystal Garden': 'https://www.youtube.com/watch?v=jPJfQLDHnQQ',
    'Build a Water Filter': 'https://www.youtube.com/watch?v=7iHXQGr8F2E',
    'Make a Siphon': 'https://www.youtube.com/watch?v=KsKRZaL9yWM',
    'Simple Circuit Challenge': 'https://www.youtube.com/watch?v=ZMLqhqZXFYE',
    'Build a Wattle and Daub Structure': 'https://www.youtube.com/watch?v=RmgHK6rJVjc',
    'Marble Run Machine': 'https://www.youtube.com/watch?v=lZipFrBCIkA',
    'Build a Miniature Catapult': 'https://www.youtube.com/watch?v=h5LdAYjMqnI',
    'Design Your Own Ecosystem': 'https://www.youtube.com/watch?v=FzfHwvMlWCY',
    'Code a Simple Game': 'https://www.youtube.com/watch?v=PfRH8FQWZOU',
    'Advanced Robotics Challenge': 'https://www.youtube.com/watch?v=Mqs8PJJ5eIk',
    'Build a Wind Turbine': 'https://www.youtube.com/watch?v=Xj9yxkHGN7s',
}

for title, url in video_map.items():
    project = Project.objects.filter(title=title).first()
    if project:
        project.video_url = url
        project.save()
        print(f'✅ Updated: {title}')
    else:
        print(f'❌ Not found: {title}')

print('\nAll projects updated with video URLs!')
