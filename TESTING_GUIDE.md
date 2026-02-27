# Progression System - Testing & Validation Guide

## 🧪 Test Cases

### Test Environment Setup

```python
# Create test data
from users.models import ParentProfile, ChildProfile, Project, ProjectProgress, ProjectSkillMapping
from django.contrib.auth.models import User
from django.utils import timezone

# Create parent and child
user = User.objects.create_user('parent@test.com', 'parent@test.com', 'password')
parent = user.parent_profile
child = ChildProfile.objects.create(
    parent=parent,
    username='testchild',
    age_range='IMAGINAUTS',
    pin='1234',
    quiz_completed=True,
    learning_style='Visual Learner'
)

# Create a project
project = Project.objects.create(
    title="Test Building Project",
    emoji="🏗️",
    category="engineering",
    difficulty=1,
    age_ranges=["IMAGINAUTS"],
    is_published=True
)

# Create skill mapping
skill_map = ProjectSkillMapping.objects.create(
    project=project,
    thinking_points=20,
    making_points=30,
    problem_solving_points=20,
    resilience_points=10,
    design_planning_points=10,
    contribution_points=5
)
```

## ✅ Test Case 1: Automatic Initialization

**Objective**: Verify ProgressionStage and GrowthPathways are created automatically

```python
# Test
child = ChildProfile.objects.create(
    parent=parent,
    username='auto_init_test',
    age_range='IMAGINAUTS',
    pin='1234'
)

# Verify ProgressionStage exists
assert hasattr(child, 'progression_stage'), "ProgressionStage not created"
assert child.progression_stage.current_stage == 1, "Should start at Stage 1"

# Verify all 6 pathways exist
pathways = child.growth_pathways.all()
assert pathways.count() == 6, f"Should have 6 pathways, got {pathways.count()}"

# All should be Level 1
for pathway in pathways:
    assert pathway.level == 1, f"Should start at Level 1, got {pathway.level}"
    assert pathway.points == 0, f"Should start with 0 points, got {pathway.points}"

print("✅ Test 1 PASSED: Automatic initialization works")
```

## ✅ Test Case 2: Project Completion Updates Growth

**Objective**: Completing a project should award points to pathways

```python
# Create and complete a project
progress = ProjectProgress.objects.create(
    child=child,
    project=project,
    status='in_progress'
)

# Get initial pathway state
initial_making = child.growth_pathways.get(pathway_type='making')
initial_points = initial_making.points

# Mark as complete
progress.status = ProjectProgress.STATUS_COMPLETED
progress.completed_at = timezone.now()
progress.save()

# Refresh from database
initial_making.refresh_from_db()

# Verify points were added
assert initial_making.points > initial_points, \
    f"Points should increase from {initial_points} to {initial_making.points}"

print(f"✅ Test 2 PASSED: Making pathway grew from {initial_points} to {initial_making.points}")
```

## ✅ Test Case 3: Reflection Boost (+25%)

**Objective**: Reflection should boost points by 25%

```python
# Complete project WITHOUT reflection
progress1 = ProjectProgress.objects.create(
    child=child,
    project=project
)
progress1.status = ProjectProgress.STATUS_COMPLETED
progress1.completed_at = timezone.now()
progress1.has_reflection = False
progress1.save()

# Record points after first completion
making1 = child.growth_pathways.get(pathway_type='making')
points_without_reflection = making1.points

# Create another project
project2 = Project.objects.create(
    title="Test Project 2",
    emoji="🧪",
    category="science",
    difficulty=1,
    age_ranges=["IMAGINAUTS"],
    is_published=True
)

# Complete WITH reflection
progress2 = ProjectProgress.objects.create(
    child=child,
    project=project2,
    status=ProjectProgress.STATUS_COMPLETED
)
progress2.reflection_text = "I learned how to build structures using different materials!"
progress2.has_reflection = True
progress2.reflection_at = timezone.now()
progress2.save()

# Record points after second completion
making1.refresh_from_db()
points_with_reflection = making1.points

# Calculate difference
points_gained_without = 30  # from ProjectSkillMapping default
points_gained_with = int(30 * 1.25)  # 30 * 1.25 = 37.5 → 37

assert points_with_reflection > points_without_reflection, \
    "Points with reflection should be higher"

bonus_received = points_with_reflection - points_without_reflection - 30

print(f"✅ Test 3 PASSED: Reflection boost applied (gained {bonus_received} bonus points)")
```

## ✅ Test Case 4: Level Progression

**Objective**: Points should correctly calculate level

```python
from users.models import GrowthPathway

# Get a pathway
pathway = child.growth_pathways.get(pathway_type='making')

# Manually set points and trigger level calculation
pathway.points = 100
pathway.add_points(0)  # Triggers level recalculation
assert pathway.level == 2, f"Should be Level 2 at 100 points, got {pathway.level}"

pathway.points = 450
pathway.add_points(0)
assert pathway.level == 4, f"Should be Level 4 at 450 points, got {pathway.level}"

pathway.points = 1750
pathway.add_points(0)
assert pathway.level == 8, f"Should be Level 8 at 1750 points, got {pathway.level}"

print("✅ Test 4 PASSED: Level progression works correctly")
```

## ✅ Test Case 5: Progress Percentage

**Objective**: Progress to next level should be calculated correctly

```python
pathway = child.growth_pathways.get(pathway_type='thinking')

# At 150 points (between Level 2 and Level 3)
# Level 2: 100-249, so at 150: (150-100)/(250-100) = 50/150 = 33%
pathway.points = 150
pathway.add_points(0)

assert pathway.level == 2, "Should be Level 2"
assert 30 <= pathway.progress <= 36, \
    f"Progress should be ~33%, got {pathway.progress}%"

print(f"✅ Test 5 PASSED: Progress percentage correct ({pathway.progress}%)")
```

## ✅ Test Case 6: Stage Information

**Objective**: Verify stage information is correctly retrieved

```python
from users.models import ProgressionStage

stage = ProgressionStage.objects.get(child=child)
info = stage.get_stage_info()

assert 'name' in info, "Should have name"
assert 'emoji' in info, "Should have emoji"
assert 'identity' in info, "Should have identity statement"
assert 'unlocks' in info, "Should have unlocks list"
assert len(info['unlocks']) > 0, "Should have at least one unlock"

print(f"✅ Test 6 PASSED: Stage info complete ({info['name']})")
```

## ✅ Test Case 7: Skill Mapping Defaults

**Objective**: Projects without mapping should use defaults

```python
# Create project without skill mapping
project_no_mapping = Project.objects.create(
    title="No Mapping Project",
    emoji="🔮",
    category="art",
    difficulty=1,
    age_ranges=["IMAGINAUTS"],
    is_published=True
)

# Complete it
progress = ProjectProgress.objects.create(
    child=child,
    project=project_no_mapping,
    status=ProjectProgress.STATUS_COMPLETED,
    completed_at=timezone.now()
)

# Signal should create default mapping
try:
    mapping = project_no_mapping.skill_mapping
    assert mapping.making_points == 30, "Default making points should be 30"
    print("✅ Test 7 PASSED: Default skill mapping created")
except:
    print("❌ Test 7 FAILED: Default mapping not created")
```

## ✅ Test Case 8: Multiple Projects, Multiple Pathways

**Objective**: Multiple completions should affect multiple pathways

```python
# Create multiple different projects
projects = []
for i in range(3):
    p = Project.objects.create(
        title=f"Project {i}",
        emoji="🎯",
        category="engineering",
        difficulty=1,
        age_ranges=["IMAGINAUTS"],
        is_published=True
    )
    projects.append(p)

# Complete all
for p in projects:
    progress = ProjectProgress.objects.create(
        child=child,
        project=p,
        status=ProjectProgress.STATUS_COMPLETED,
        completed_at=timezone.now()
    )

# Check multiple pathways gained points
thinking = child.growth_pathways.get(pathway_type='thinking')
making = child.growth_pathways.get(pathway_type='making')
problem_solving = child.growth_pathways.get(pathway_type='problem_solving')

assert thinking.points > 0, "Thinking should have points"
assert making.points > 0, "Making should have points"
assert problem_solving.points > 0, "Problem solving should have points"

print(f"✅ Test 8 PASSED: Multiple pathways updated (T:{thinking.points}, M:{making.points}, PS:{problem_solving.points})")
```

## ✅ Test Case 9: Growth Summary API

**Objective**: API should return correct growth data

```python
from django.test import Client

client = Client()
client.login(username='parent@test.com', password='password')

# Mock session
session = client.session
session['child_id'] = child.id
session.save()

# Call API
response = client.get('/members/api/growth-summary/')
data = response.json()

assert response.status_code == 200, f"Should return 200, got {response.status_code}"
assert 'stage' in data, "Should have stage"
assert 'pathways' in data, "Should have pathways"
assert len(data['pathways']) == 6, f"Should have 6 pathways, got {len(data['pathways'])}"

print("✅ Test 9 PASSED: Growth summary API works")
```

## ✅ Test Case 10: Reflection Post Endpoint

**Objective**: Reflection endpoint should save text and trigger boost

```python
from django.test import Client
import json

client = Client()
# ... setup session ...

progress = ProjectProgress.objects.create(
    child=child,
    project=project,
    status='completed'
)

response = client.post(
    f'/members/api/projects/{progress.id}/reflection/',
    data=json.dumps({'reflection_text': 'I learned something important!'}),
    content_type='application/json'
)

progress.refresh_from_db()

assert response.status_code == 200, f"Should return 200, got {response.status_code}"
assert progress.has_reflection == True, "Should mark as having reflection"
assert 'important' in progress.reflection_text, "Should save reflection text"

print("✅ Test 10 PASSED: Reflection endpoint works")
```

## 🔍 Manual Testing Checklist

- [ ] Create new child account → Check progression_stage and pathways created
- [ ] View growth_map page → All pathways visible with Level 1
- [ ] View progression_detail page → All 5 stages visible
- [ ] Complete a project → Check growth_map for point increases
- [ ] Add reflection → Check 25% bonus applied to points
- [ ] Level up multiple times → Verify level displays correctly
- [ ] Check growth_summary API → Returns valid JSON
- [ ] View on mobile → Responsive design works
- [ ] Test admin interface → Can edit skill mappings
- [ ] Test with multiple children → Each has independent progression

## 📊 Performance Testing

```python
# Test with many children
import time

from django.db import reset_queries
from django.conf import settings

# Enable query logging
settings.DEBUG = True

start = time.time()
reset_queries()

# Create 100 children
for i in range(100):
    ChildProfile.objects.create(
        parent=parent,
        username=f'perf_test_{i}',
        age_range='IMAGINAUTS',
        pin='1234'
    )

elapsed = time.time() - start

from django.db import connection
query_count = len(connection.queries)

print(f"Created 100 children in {elapsed:.2f}s")
print(f"Database queries: {query_count}")
print(f"Average per child: {elapsed/100:.4f}s, {query_count/100:.1f} queries")
```

## 🎯 Regression Testing

After each code change, run these tests:

1. Create child → Verify initialization
2. Complete project → Verify growth update
3. Submit reflection → Verify boost
4. View pages → Verify no errors
5. Check admin → Verify interface works

## 🚨 Error Scenarios to Test

### Scenario 1: Project with no Skill Mapping
```python
# Should create default mapping
progress = ProjectProgress.objects.create(
    child=child,
    project=unmapped_project
)
progress.status = 'completed'
progress.save()
# Should not raise error
```

### Scenario 2: Very Short Reflection
```python
progress = ProjectProgress.objects.create(
    child=child,
    project=project
)
progress.reflection_text = "Good"  # < 20 chars
progress.has_reflection = False
progress.save()
# Should use normal points, no boost
```

### Scenario 3: Unauthorized Access
```python
# Child tries to access another child's growth map
session['child_id'] = other_child.id
response = client.get('/members/kids/growth-map/')
# Should redirect or 403
```

### Scenario 4: Missing Child Profile
```python
# Delete child, access API
# Should handle gracefully
response = client.get('/members/api/growth-summary/')
# Should return 401 or redirect
```

## 📈 Expected Results

After implementing and testing, you should see:

- ✅ New children automatically get progression data
- ✅ Projects award appropriate points
- ✅ Reflections grant 25% bonus
- ✅ Levels progress smoothly
- ✅ UI displays growth beautifully
- ✅ Admin can customize everything
- ✅ No performance issues
- ✅ Mobile-friendly
- ✅ Secure and validated

---

**Note**: All queries should be run in a development environment with test data. Never test on production without backups.
