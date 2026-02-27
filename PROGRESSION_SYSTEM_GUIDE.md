# Imaginauts Track Progression System - Implementation Guide

## 🎯 Overview

This document outlines the implementation of the complete **Imaginauts Track Progression System** which replaces traditional XP/level systems with an identity-based, growth-focused progression model designed for ages 6-16.

## 📊 System Architecture

### Core Principles

1. **Identity-Based (Not Points-Based)**: Progression reflects capability expansion, not numerical achievements
2. **Growth Over Grind**: Reflects real learning and mastery without competitive pressure
3. **Non-Competitive**: Each child has their own unique growth path
4. **Reflection-Amplified**: Deeper thinking about work directly increases growth

## 🏗️ Data Models

### 1. **ProgressionStage** 
Tracks a child's identity stage through 5 progression levels:

```
Stage 1: 🌱 Explorer - "I can follow a build"
Stage 2: 🔍 Experimenter - "I can adapt and improve"
Stage 3: 🧱 Builder - "I can strengthen designs"
Stage 4: 🛠 Designer - "I can plan before building"
Stage 5: 🔥 Independent Maker - "I build with purpose"
```

**Key Fields:**
- `current_stage` - Integer (1-5)
- `stage_description` - Optional custom text
- `reached_at` - When child reached this stage
- `updated_at` - Last update timestamp

**Automatic Initialization**: Created automatically when a ChildProfile is created.

### 2. **GrowthPathway**
Represents progress in one of six skill dimensions:

```
🧠 Creative Thinking
🛠 Practical Making
🔍 Problem Solving
💪 Resilience
📐 Design Planning
🌍 Contribution
```

**Key Fields:**
- `pathway_type` - CharField (6 pathway types)
- `level` - Integer (1-8, representing growth stages)
- `progress` - Integer (0-100%, progress to next level)
- `points` - Integer (internal tracking, not shown to child)
- `last_boosted_at` - Timestamp of last reflection boost

**Point Thresholds for Level Progression:**
```
Level 1: 0-99 points
Level 2: 100-249 points
Level 3: 250-449 points
Level 4: 450-699 points
Level 5: 700-999 points
Level 6: 1000-1349 points
Level 7: 1350-1749 points
Level 8: 1750+ points
```

### 3. **ProjectSkillMapping**
Defines how many points a completed project contributes to each pathway:

**Fields:**
- `project` - OneToOneField to Project
- `thinking_points` - Points awarded to Creative Thinking
- `making_points` - Points awarded to Practical Making
- `problem_solving_points` - Points awarded to Problem Solving
- `resilience_points` - Points awarded to Resilience
- `design_planning_points` - Points awarded to Design Planning
- `contribution_points` - Points awarded to Contribution

**Default Values (if not configured):**
```python
thinking_points = 20
making_points = 30
problem_solving_points = 20
resilience_points = 10
design_planning_points = 10
contribution_points = 5
```

### 4. **ProjectProgress** (Enhanced)
Extended to track reflections:

**New Fields:**
- `reflection_text` - TextField for child's reflection
- `has_reflection` - Boolean indicating meaningful reflection (>20 chars)
- `reflection_at` - Timestamp when reflection was added

### 5. **InspirationShare**
Tracks when children share projects and their community impact:

**Fields:**
- `child` - ForeignKey to ChildProfile
- `project_progress` - ForeignKey to ProjectProgress
- `description` - Why they're sharing
- `image_url` - Screenshot of completed project
- `saves_count` - How many others saved to their board
- `inspired_builds` - How many built something inspired by this
- `shared_at` - When it was shared
- `updated_at` - Last updated

## 🔄 Progression Logic

### How Children Advance

1. **Complete Project** → Triggers points to relevant pathways
2. **Provide Reflection** → Adds 25% bonus to all points earned
3. **Level Up Automatically** → When points reach next threshold
4. **Stage Advancement** (Future): Stages will advance based on completed projects count and mastery

### Reflection Boost System

When a ProjectProgress is marked as completed:
```python
if has_reflection and len(reflection_text) > 20:
    # Apply 25% bonus to all earned points
    points_awarded = points_awarded * 1.25
    last_boosted_at = now()
```

This mechanic teaches intrinsic motivation: **Thinking about your work makes you better.**

### Event Handling (Signals)

**Signal: `post_save` on `ChildProfile`**
- Automatically creates ProgressionStage (Stage 1)
- Initializes all 6 GrowthPathways at Level 1

**Signal: `post_save` on `ProjectProgress`**
- When status changes to COMPLETED:
  - Retrieves or creates ProjectSkillMapping
  - Calculates reflection bonus
  - Updates all relevant GrowthPathways with points
  - Saves updated pathway levels and progress

## 🎨 User Interface

### Views

1. **`growth_map(request)`** - Display child's growth map
   - URL: `/members/kids/growth-map/`
   - Shows all pathways with levels, progress, and points
   - Displays current stage and unlocks
   - Renders: `growth_map.html`

2. **`progression_detail(request)`** - Detailed stage information
   - URL: `/members/kids/progression/`
   - Timeline view of all 5 stages
   - Current stage highlighted
   - Unlocks and description for each stage
   - Renders: `progression_detail.html`

3. **`growth_summary_api(request)`** - JSON API for summaries
   - URL: `/members/api/growth-summary/`
   - Returns JSON with current stage and all pathway data
   - Used for dashboard widgets and other embeds

4. **`update_reflection(request, progress_id)`** - Save reflection
   - URL: `/members/api/projects/<id>/reflection/` (POST)
   - Accepts JSON: `{"reflection_text": "..."}`
   - Triggers growth updates
   - Returns JSON confirmation

### Templates

1. **`growth_map.html`** - Main growth visualization
   - Stage header with emoji and identity statement
   - Unlocks section
   - Overall growth summary with quick stats
   - Individual pathway cards with:
     - Progress bars
     - Level display
     - Organic vine visualization
     - Points and level stats

2. **`progression_detail.html`** - Stage timeline
   - Visual timeline of 5 stages
   - Current stage highlighted
   - Stage descriptions and unlocks for each
   - Responsive design for mobile

3. **Updated `child_dashboard.html`**
   - Added "🗺️ Growth Map" button in header
   - Link to progression system

## 📈 Admin Interface

All new models are registered with comprehensive admin interfaces:

- **ProgressionStageAdmin** - View/edit stage with stage info
- **GrowthPathwayAdmin** - View/edit pathways with current levels
- **ProjectSkillMappingAdmin** - Configure point distribution per project
- **InspirationShareAdmin** - View community shares and engagement
- **ProjectProgressAdmin** - Enhanced with reflection fields

### Admin Features

- List displays with relevant info
- Filter by pathway type, level, reflection status
- Readonly fields for timestamps
- Custom display methods for computed values

## 🔗 URL Routes

```python
# Growth & Progression
path("kids/growth-map/", growth_map, name="growth_map")
path("kids/progression/", progression_detail, name="progression_detail")

# API Endpoints
path("api/growth-summary/", growth_summary_api, name="growth_summary_api")
path("api/projects/<int:progress_id>/reflection/", update_reflection, name="update_reflection")
```

## 🗄️ Database Migration

Migration `0009_progression_system.py` includes:

1. Updates to ProjectProgress model (reflection fields)
2. New ProgressionStage model creation
3. New GrowthPathway model creation
4. New ProjectSkillMapping model creation
5. New InspirationShare model creation

**Run migrations:**
```bash
python manage.py migrate
```

## 🎓 Onboarding Flow

When a child account is created:

1. ✅ ProgressionStage created (Stage 1: Explorer)
2. ✅ 6 GrowthPathways initialized (all Level 1)
3. 🔄 Child sees growth map with all pathways at Level 1
4. 🚀 First project completion starts growth

## 📊 Default Project Skill Mappings

When a project doesn't have a custom skill mapping, defaults are applied:

- **Making** (30pts) - Always highest for building projects
- **Thinking** (20pts) - Creative problem solving
- **Problem Solving** (20pts) - Analytical thinking
- **Resilience** (10pts) - Testing and failing
- **Design Planning** (10pts) - Planning before building
- **Contribution** (5pts) - Sharing and inspiring others

**To customize:** Edit the `ProjectSkillMapping` in admin for specific projects.

## 🌟 Key Design Decisions

### Why No XP Numbers Shown?

- Removes extrinsic motivation (points, leaderboards)
- Reduces social comparison and anxiety
- Focuses on capability, not achievement
- More inclusive of different learning paces

### Why 8 Levels Per Pathway?

- Enough progression to feel substantial
- Not overwhelming (no "Level 98")
- Matches age-appropriate cognitive load
- Allows for mastery without endless grinding

### Why Reflection is Boosted?

- Teaches metacognition (thinking about thinking)
- Builds intrinsic motivation
- Creates space for deeper learning
- Makes introspection valuable

### Why No Public Leaderboards?

- Aligned with Zonuko ethos: non-competitive growth
- Protects mental health and confidence
- Encourages collaboration over comparison
- Parents can see progression privately in accounts

## 🚀 Future Enhancements

1. **Stage Advancement**: Auto-advance stages based on milestones
2. **Confidence Compass**: Circular visual showing 4 core competencies
3. **Skill Clusters**: Group pathways into themes (e.g., "Building", "Thinking")
4. **Achievement Badges**: Identity-based badges (e.g., "First Builder", "Reflection Master")
5. **Parent Dashboard**: High-level view of child's growth
6. **Pathway Recommendations**: Suggest projects based on pathway interests
7. **Multi-track Progression**: Different pathways for Navigators & Trailblazers

## 📝 Code Examples

### Completing a Project and Earning Growth

```python
# In views.py when project is marked complete
progress = ProjectProgress.objects.get(id=project_id, child=child)
progress.status = ProjectProgress.STATUS_COMPLETED
progress.completed_at = timezone.now()

# Optional: Add reflection
progress.reflection_text = "I learned that..."
progress.has_reflection = True
progress.reflection_at = timezone.now()

progress.save()
# Signal automatically triggers growth updates
```

### Checking a Child's Growth

```python
from users.models import GrowthPathway, ProgressionStage

# Get child's current stage
stage = ProgressionStage.objects.get(child=child)
print(f"{child.username} is at {stage.get_stage_info()['name']}")

# Get all pathway progress
pathways = GrowthPathway.objects.filter(child=child)
for pathway in pathways:
    print(f"{pathway.get_pathway_type_display()}: Level {pathway.level}")
```

### API Response Format

```json
{
  "stage": {
    "level": 1,
    "name": "Explorer",
    "emoji": "🌱"
  },
  "pathways": [
    {
      "type": "thinking",
      "name": "🧠 Creative Thinking",
      "level": 2,
      "progress": 45
    },
    {
      "type": "making",
      "name": "🛠 Practical Making",
      "level": 3,
      "progress": 22
    }
    // ... more pathways
  ]
}
```

## 🐛 Troubleshooting

### Pathways Not Updating After Project Completion

1. Check `ProjectSkillMapping` exists for the project
2. Verify `ProjectProgress.status == COMPLETED`
3. Check `ProjectProgress.child` is set correctly
4. Verify signals are connected (check logs)

### Child Created but No Progression Data

1. Run migration: `python manage.py migrate users 0009_progression_system`
2. Check ProgressionStage and GrowthPathway are created via signal
3. If missing, manually create via admin or shell

### Reflection Boost Not Applied

1. Ensure `has_reflection = True` before saving
2. Verify `reflection_text` length > 20 characters
3. Check signal is being called (view logs)

## 📞 Support & Maintenance

- Monitor growth data quality in admin
- Regularly review and adjust skill mapping points
- Gather child feedback on progression experience
- Track engagement metrics (project completions, reflections, stage advancement)
- Update pathways based on child feedback

## 🎉 Success Metrics

- Increased project completion rates
- More meaningful reflections provided
- Steady progression through stages
- Positive engagement with growth map
- Reduced anxiety about "performance"
- Increased intrinsic motivation indicators

---

**Version**: 1.0  
**Last Updated**: February 2026  
**Author**: Zonuko Development Team
