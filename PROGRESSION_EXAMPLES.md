# Progression System - Implementation Examples & Best Practices

## 🎯 Quick Start Examples

### 1. Getting a Child's Current Progression

```python
from users.models import ChildProfile, ProgressionStage, GrowthPathway

# Get a child
child = ChildProfile.objects.get(username="alex")

# Get their current stage
stage = ProgressionStage.objects.get(child=child)
print(f"Current Stage: {stage.get_stage_info()['name']}")
print(f"Identity: {stage.get_stage_info()['identity']}")

# Get all pathways
pathways = GrowthPathway.objects.filter(child=child).order_by('pathway_type')
for pathway in pathways:
    emoji = pathway.get_pathway_type_display().split()[0]
    name = ' '.join(pathway.get_pathway_type_display().split()[1:])
    print(f"{emoji} {name}: Level {pathway.level} ({pathway.progress}% to next)")
```

### 2. Marking a Project as Completed

```python
from users.models import ProjectProgress
from django.utils import timezone

# Get the project progress
progress = ProjectProgress.objects.get(id=123, child=child)

# Mark as completed
progress.status = ProjectProgress.STATUS_COMPLETED
progress.completed_at = timezone.now()

# Optionally add a reflection
if user_reflection := request.POST.get('reflection'):
    progress.reflection_text = user_reflection
    progress.has_reflection = len(user_reflection.strip()) > 20
    progress.reflection_at = timezone.now()

progress.save()  # Signal automatically updates growth pathways!
```

### 3. Creating a New Project with Skill Mapping

```python
from users.models import Project, ProjectSkillMapping

# Create project
project = Project.objects.create(
    title="Build a Water Filter",
    emoji="💧",
    category="engineering",
    difficulty=2,
    age_ranges=["IMAGINAUTS", "NAVIGATORS"],
    description="Create a working water filter using household items...",
    estimated_time=45,
    is_published=True
)

# Create skill mapping
skill_map = ProjectSkillMapping.objects.create(
    project=project,
    thinking_points=25,      # More thinking for this project
    making_points=25,        # Equal making
    problem_solving_points=25, # Problem solving is key
    resilience_points=15,    # Some resilience testing
    design_planning_points=5,
    contribution_points=5
)
```

### 4. Checking Reflection-Boosted Growth

```python
from users.models import ProjectProgress

# Find projects with reflections
reflected = ProjectProgress.objects.filter(
    child=child,
    status='completed',
    has_reflection=True
).count()

print(f"{child.username} has reflected on {reflected} projects")

# See which pathways got reflection boosts
recent = ProjectProgress.objects.filter(
    child=child,
    status='completed',
    has_reflection=True,
    reflection_at__gte=timezone.now() - timezone.timedelta(days=7)
)

for progress in recent:
    print(f"✨ Reflection on {progress.project.title}")
```

### 5. Querying Pathway Progress

```python
from users.models import GrowthPathway

# Get a specific pathway
thinking = GrowthPathway.objects.get(
    child=child,
    pathway_type=GrowthPathway.THINKING
)

print(f"Creative Thinking Level {thinking.level}")
print(f"Points: {thinking.points}")
print(f"Progress: {thinking.progress}%")

# Get children at specific levels
level_5_builders = GrowthPathway.objects.filter(
    pathway_type=GrowthPathway.MAKING,
    level__gte=5
).values_list('child__username', flat=True)

# Get most advanced in a pathway
top_thinkers = GrowthPathway.objects.filter(
    pathway_type=GrowthPathway.THINKING
).order_by('-level')[:10]
```

## 🎨 Frontend Integration Examples

### 1. Display Growth Map Widget

```django
<!-- Include in any template -->
{% if child %}
    <div class="growth-widget">
        {% for pathway in child.growth_pathways.all %}
            <div class="pathway-mini">
                <span>{{ pathway.get_pathway_type_display }}</span>
                <div class="level-badge">Lvl {{ pathway.level }}</div>
                <div class="progress-bar">
                    <div class="fill" style="width: {{ pathway.progress }}%"></div>
                </div>
            </div>
        {% endfor %}
    </div>
{% endif %}
```

### 2. Show Current Stage in Header

```django
{% with stage=child.progression_stage %}
    <div class="stage-badge">
        <span class="emoji">{{ stage.get_stage_info.emoji }}</span>
        <span class="name">{{ stage.get_stage_info.name }}</span>
    </div>
{% endwith %}
```

### 3. Reflection Form

```django
<form method="post" action="{% url 'users:update_reflection' progress.id %}">
    {% csrf_token %}
    <div class="reflection-form">
        <label>What did you learn?</label>
        <textarea name="reflection_text" placeholder="Tell us what you discovered..."></textarea>
        <p class="hint">✨ Detailed reflections help you grow faster!</p>
        <button type="submit">Save Reflection</button>
    </div>
</form>

<script>
fetch("{% url 'users:update_reflection' progress.id %}", {
    method: "POST",
    headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie('csrftoken')
    },
    body: JSON.stringify({
        reflection_text: document.querySelector('textarea').value
    })
})
.then(r => r.json())
.then(data => {
    if (data.success) {
        alert(data.message);  // "✨ Your reflection strengthened your growth!"
    }
});
</script>
```

### 4. API Integration

```javascript
// Get child's growth summary
fetch('/members/api/growth-summary/')
    .then(r => r.json())
    .then(growth => {
        // Use growth.stage and growth.pathways
        console.log(`Child is at Stage ${growth.stage.level}: ${growth.stage.name}`);
        
        growth.pathways.forEach(pathway => {
            console.log(`${pathway.name}: Level ${pathway.level}`);
        });
    });
```

## 📊 Admin Usage Examples

### 1. Bulk Create Skill Mappings

```python
from users.models import Project, ProjectSkillMapping

# Create default skill mappings for all projects without one
for project in Project.objects.filter(skill_mapping__isnull=True):
    ProjectSkillMapping.objects.create(
        project=project,
        thinking_points=20,
        making_points=30,
        problem_solving_points=20,
        resilience_points=10,
        design_planning_points=10,
        contribution_points=5
    )
```

### 2. Analyze Child Progression

```python
from users.models import ProgressionStage, GrowthPathway
from django.db.models import Avg

# Get average level across all children
avg_levels = GrowthPathway.objects.values(
    'pathway_type'
).annotate(
    avg_level=Avg('level')
)

for item in avg_levels:
    print(f"{item['pathway_type']}: Avg Level {item['avg_level']:.1f}")

# Get children who haven't started (all Level 1)
inactive = ChildProfile.objects.filter(
    growth_pathways__level=1
).annotate(
    unique_levels=Count('growth_pathways__level', distinct=True)
).filter(
    unique_levels=1
)
```

### 3. Identify Reflection Leaders

```python
from users.models import ProjectProgress
from django.db.models import Count

# Get children with most reflections
reflection_leaders = ProjectProgress.objects.filter(
    status='completed',
    has_reflection=True
).values(
    'child__username'
).annotate(
    reflection_count=Count('id')
).order_by('-reflection_count')[:10]

for leader in reflection_leaders:
    print(f"{leader['child__username']}: {leader['reflection_count']} reflections")
```

## 🔧 Customization Guide

### 1. Adjust Point Thresholds

If you want different level progression speeds, modify `GrowthPathway.add_points()`:

```python
# Current thresholds (in models.py)
level_thresholds = [0, 100, 250, 450, 700, 1000, 1350, 1750, 2200]

# Make progression faster (easier)
# level_thresholds = [0, 50, 125, 225, 350, 500, 675, 875, 1100]

# Make progression slower (harder)
# level_thresholds = [0, 200, 500, 900, 1400, 2000, 2700, 3500, 4400]
```

### 2. Customize Reflection Bonus

Change the bonus percentage in `GrowthPathway.add_points()`:

```python
# Current: 25% bonus
if reflection_boost:
    self.points += int(points * 0.25)  # 25% bonus

# Option: 50% bonus (more incentive)
# self.points += int(points * 0.50)

# Option: 10% bonus (subtle)
# self.points += int(points * 0.10)
```

### 3. Add Custom Pathways

To add a 7th pathway (e.g., "Collaboration"):

```python
# 1. Update GrowthPathway model
class GrowthPathway(models.Model):
    COLLABORATION = 'collaboration'
    
    PATHWAY_CHOICES = [
        # ... existing choices
        (COLLABORATION, "👥 Collaboration"),
    ]

# 2. Create migration

# 3. Create pathway for existing children
from users.models import ChildProfile, GrowthPathway
for child in ChildProfile.objects.all():
    GrowthPathway.objects.create(
        child=child,
        pathway_type=GrowthPathway.COLLABORATION,
        progress=0,
        level=1
    )
```

### 4. Create Custom Reports

```python
from users.models import GrowthPathway, ProgressionStage
from django.db.models import Avg, Q

# Monthly growth report
print("=== GROWTH REPORT ===")
print(f"Average Thinking Level: {GrowthPathway.objects.filter(pathway_type='thinking').aggregate(Avg('level'))['level__avg']:.1f}")
print(f"Average Making Level: {GrowthPathway.objects.filter(pathway_type='making').aggregate(Avg('level'))['level__avg']:.1f}")

# Stage distribution
stages = ProgressionStage.objects.values('current_stage').annotate(count=Count('id')).order_by('current_stage')
for stage in stages:
    print(f"Stage {stage['current_stage']}: {stage['count']} children")
```

## 🎓 Teaching Guides

### 1. Explaining Stages to Children

```python
# Use these in your teaching materials:
stage_messages = {
    1: "You're just starting your creative journey! 🌱",
    2: "You're experimenting and discovering what works! 🔍",
    3: "You understand how things work and can improve them! 🧱",
    4: "You can plan and design before you build! 🛠",
    5: "You're creating with purpose and inspiring others! 🔥"
}
```

### 2. Encouraging Reflection

```python
# Use these prompts in your interface:
reflection_prompts = [
    "What surprised you most about this project?",
    "What would you do differently next time?",
    "Who could you teach this skill to?",
    "How does this connect to something you already know?",
    "What was the hardest part and how did you solve it?"
]
```

### 3. Celebrating Growth

```python
# Messages when levels increase:
level_up_messages = {
    2: "You're getting better at this skill! 📈",
    4: "Wow! You're making real progress! 🚀",
    6: "You're becoming a master of this! 💪",
    8: "You've reached the highest level! 🌟"
}
```

## 🐛 Debugging Tips

### 1. Check Signal Connections

```python
from django.db.models.signals import post_save
from users.models import ChildProfile, ProjectProgress

# Verify signals are connected
print(post_save.receivers_gone())  # Should be empty
print(len(post_save._live_receivers(ChildProfile)))  # Should be > 0
```

### 2. Trace Growth Calculation

```python
from users.models import ProjectProgress, GrowthPathway
import logging

logger = logging.getLogger(__name__)

progress = ProjectProgress.objects.get(id=123)
logger.info(f"Project: {progress.project.title}")
logger.info(f"Child: {progress.child.username}")
logger.info(f"Has reflection: {progress.has_reflection}")

# Check skill mapping
try:
    mapping = progress.project.skill_mapping
    logger.info(f"Skill mapping found: {mapping.get_contributions()}")
except:
    logger.error("No skill mapping found")

# Check pathway updates
for pathway in GrowthPathway.objects.filter(child=progress.child):
    logger.info(f"{pathway.get_pathway_type_display()}: Level {pathway.level}, Points {pathway.points}")
```

### 3. Manual Growth Trigger

```python
# If signals aren't firing, manually trigger updates:
from users.models import ProjectProgress

progress = ProjectProgress.objects.get(id=123)

# Import the signal handler directly
from users.models import update_growth_on_project_completion

# Call it manually
update_growth_on_project_completion(
    sender=ProjectProgress,
    instance=progress,
    created=False
)
```

## 📈 Analytics Queries

### Top Reflectors

```python
from django.db.models import Count

top_reflectors = ProjectProgress.objects.filter(
    has_reflection=True,
    status='completed'
).values('child__username').annotate(
    reflection_count=Count('id')
).order_by('-reflection_count')[:10]
```

### Growth Momentum (Last 7 Days)

```python
from django.utils import timezone
from datetime import timedelta

last_week = timezone.now() - timedelta(days=7)

recent_growth = ProjectProgress.objects.filter(
    completed_at__gte=last_week,
    status='completed'
).count()

recent_reflections = ProjectProgress.objects.filter(
    reflection_at__gte=last_week,
    has_reflection=True
).count()

print(f"Projects completed: {recent_growth}")
print(f"With reflection: {recent_reflections}")
```

---

**Last Updated**: February 2026
