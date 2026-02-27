# Imaginauts Progression System - Quick Reference

## 🚀 Quick Start (5 minutes)

### 1. Run Migration
```bash
python manage.py migrate users 0009_progression_system
```

### 2. Access Growth Map
- Child logs in → Click "🗺️ Growth Map" button
- URL: `/members/kids/growth-map/`

### 3. Configure Project Skills
- Django Admin → Project Skill Mappings
- Edit each project's point distribution
- Or leave defaults (30 making, 20 thinking, 20 problem-solving, etc.)

### 4. Complete a Test Project
1. Log in as child
2. Complete a project
3. Check growth_map for updated levels

### 5. Test Reflection Boost
1. Complete project
2. Add reflection (>20 characters)
3. Verify 25% bonus to points

Done! System is live. ✅

---

## 📋 File Structure

```
zonukoapp/
├── apps/users/
│   ├── models.py                    ← New progression models
│   ├── views.py                     ← New growth views + signals
│   ├── admin.py                     ← New admin interfaces
│   ├── urls.py                      ← New routes
│   ├── migrations/
│   │   └── 0009_progression_system.py  ← Migration file
│   └── templates/users/
│       ├── growth_map.html          ← Visual growth map
│       ├── progression_detail.html  ← Stage timeline
│       └── child_dashboard.html     ← Updated with link
├── PROGRESSION_SYSTEM_GUIDE.md       ← Full documentation
├── PROGRESSION_EXAMPLES.md           ← Code examples
├── IMPLEMENTATION_SUMMARY.md         ← Changes overview
├── TESTING_GUIDE.md                  ← Test cases
└── QUICK_REFERENCE.md              ← This file
```

---

## 🎯 Core Concepts (30 seconds)

| Concept | What It Is | Why It Matters |
|---------|-----------|----------------|
| **Stage** | 5 identity levels (Explorer → Maker) | Shows growth mindset |
| **Pathway** | 6 skill dimensions | Tracks diverse growth |
| **Level** | 1-8 per pathway | Progression representation |
| **Points** | Internal score (hidden) | Drives level calculations |
| **Reflection** | Child's written thought | Boosts points by 25% |

---

## 🔧 Common Tasks

### Task: Add Skill Mapping for New Project
```python
# In Django shell
from users.models import Project, ProjectSkillMapping

project = Project.objects.get(id=123)
ProjectSkillMapping.objects.create(
    project=project,
    thinking_points=25,
    making_points=30,
    problem_solving_points=20,
    resilience_points=10,
    design_planning_points=10,
    contribution_points=5
)
```

### Task: Check Child's Progression
```python
child = ChildProfile.objects.get(username='alex')
stage = child.progression_stage
print(f"Stage: {stage.get_stage_info()['name']}")

for pathway in child.growth_pathways.all():
    print(f"{pathway.get_pathway_type_display()}: Level {pathway.level}")
```

### Task: Bulk Update All Project Mappings
```python
from users.models import Project, ProjectSkillMapping

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

### Task: Export Growth Report
```python
from django.db.models import Avg
from users.models import GrowthPathway

for pathway_choice in GrowthPathway.PATHWAY_CHOICES:
    pathway_type = pathway_choice[0]
    avg_level = GrowthPathway.objects.filter(
        pathway_type=pathway_type
    ).aggregate(Avg('level'))['level__avg'] or 0
    print(f"{pathway_choice[1]}: {avg_level:.1f}")
```

---

## 📱 URLs Map

```
/members/kids/growth-map/              → Display growth visualization
/members/kids/progression/             → Show stage timeline
/members/api/growth-summary/           → JSON growth data
/members/api/projects/<id>/reflection/ → POST reflection update
```

---

## 🎨 UI Components

### Growth Map Page
- Stage header with emoji and identity
- Unlocks section
- 6 pathway cards with:
  - Progress bar (0-100%)
  - Level badge (1-8)
  - Points counter
  - Vine visualization

### Progression Timeline
- 5 stage items in vertical timeline
- Each shows description and unlocks
- Current stage highlighted
- Completed stages show checkmark

---

## 🧬 Data Model Relationships

```
ChildProfile
├── progression_stage (OneToOne) → ProgressionStage
└── growth_pathways (ForeignKey) → GrowthPathway (6 instances)

Project
├── skill_mapping (OneToOne) → ProjectSkillMapping
└── child_progress (ForeignKey) → ProjectProgress

ProjectProgress
├── child (ForeignKey) → ChildProfile
├── project (ForeignKey) → Project
└── inspiration_shares (ForeignKey) → InspirationShare
```

---

## 📊 Point Thresholds

```
Level 1: 0-99      | ██░░░░░░░
Level 2: 100-249   | ███░░░░░░
Level 3: 250-449   | ████░░░░░
Level 4: 450-699   | █████░░░░
Level 5: 700-999   | ██████░░░
Level 6: 1000-1349 | ███████░░
Level 7: 1350-1749 | ████████░
Level 8: 1750+     | █████████
```

---

## 🔐 Security Checklist

- [x] Views require @login_required
- [x] Child ownership verified
- [x] Session-based authentication
- [x] CSRF protection on POST
- [x] No direct access to other children's data
- [x] Admin views restricted

---

## 🚨 Troubleshooting (2 minutes)

| Problem | Solution |
|---------|----------|
| Pathways not updating | Verify ProjectSkillMapping exists |
| Child not initialized | Run `python manage.py migrate` |
| Wrong level displayed | Check point thresholds in model |
| Reflection not boosting | Verify `has_reflection=True` before save |
| API returns 401 | Check session has `child_id` |

---

## 📚 Documentation Structure

1. **QUICK_REFERENCE.md** (You are here)
   - 2-minute overview
   - Common tasks
   - Troubleshooting

2. **IMPLEMENTATION_SUMMARY.md**
   - Changes made
   - Features added
   - Integration steps

3. **PROGRESSION_SYSTEM_GUIDE.md**
   - Complete technical docs
   - API details
   - Admin guide

4. **PROGRESSION_EXAMPLES.md**
   - Code examples
   - Best practices
   - Customization

5. **TESTING_GUIDE.md**
   - Test cases
   - Validation
   - Performance testing

---

## 🎯 Success Indicators

Track these metrics:
- ✅ Project completion rate increases
- ✅ Reflection submission rate > 20%
- ✅ Average level progression speed
- ✅ Stage advancement milestones
- ✅ Child satisfaction surveys
- ✅ Parent feedback on growth visibility

---

## 📞 Support Questions

**Q: How long until a child levels up?**
A: Depends on project frequency. ~5-8 projects to reach Level 2.

**Q: Can I change the 25% reflection bonus?**
A: Yes, edit `add_points()` method in GrowthPathway model.

**Q: Do stages auto-advance?**
A: Currently manual. Future: will auto-advance at milestones.

**Q: Can children share growth on social media?**
A: Not by default. Share links can be added in future versions.

**Q: How do parents see progression?**
A: Parent dashboard planned for future release.

**Q: What happens if a project has no skill mapping?**
A: Default values are used (30 making, 20 thinking, etc.).

---

## 🚀 Deployment Checklist

- [ ] Backup database
- [ ] Run migration: `python manage.py migrate`
- [ ] Test growth_map view loads
- [ ] Complete test project
- [ ] Verify growth updates
- [ ] Check admin interface
- [ ] Test on mobile
- [ ] Monitor for errors
- [ ] Gather user feedback
- [ ] Deploy to production

---

## 📊 Key Stats

| Metric | Value |
|--------|-------|
| Pathways | 6 |
| Levels per Pathway | 8 |
| Stages | 5 |
| Reflection Bonus | 25% |
| Level Progression | ~5-10 projects |
| Default Project Points | 85 total |

---

## 🎓 Teaching the System

**To Children:**
"Your growth map shows how you're getting better at different skills. No points, no pressure—just real growth. The more you reflect, the faster you grow."

**To Parents:**
"We track 6 dimensions of creative growth. This shows us which skills your child is developing through projects."

**To Educators:**
"Use the growth map to identify which pathways each child excels at, and recommend projects accordingly."

---

## 🔄 Release Notes

**v1.0 - Initial Release**
- ✅ 5-stage progression system
- ✅ 6 growth pathways
- ✅ Reflection boost system
- ✅ Visual growth map
- ✅ Stage timeline
- ✅ Admin interface
- ✅ API endpoints

**Future (v1.1+)**
- Auto-stage advancement
- Confidence compass visualization
- Parent dashboard
- Achievement badges
- Skill clusters
- Pathway recommendations

---

## 💡 Tips & Tricks

1. **Customize points per project** → Different project types can emphasize different skills
2. **Monitor reflection rate** → High reflection rate = engaged learners
3. **Use stages as milestones** → Celebrate stage achievements
4. **Track pathway trends** → Identify which skills are developing fastest
5. **Celebrate Level 8** → Those reaching max level are mastering skills

---

**Last Updated**: February 26, 2026  
**Version**: 1.0  
**Status**: Production Ready ✅
