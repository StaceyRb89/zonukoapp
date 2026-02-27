from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta


class ParentProfile(models.Model):
    """Extended profile for parent/guardian users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="parent_profile")
    display_name = models.CharField(max_length=50, blank=True)
    avatar = models.ImageField(upload_to="avatars/parents/", null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.display_name or 'No name'}"

    @property
    def has_active_subscription(self):
        """Check if user has an active paid subscription"""
        try:
            return self.subscription.is_active
        except AttributeError:
            return False


class ChildProfile(models.Model):
    """Child profile linked to parent account"""
    IMAGINAUTS = "IMAGINAUTS"
    NAVIGATORS = "NAVIGATORS"
    TRAILBLAZERS = "TRAILBLAZERS"

    AGE_RANGE_CHOICES = [
        (IMAGINAUTS, "Imaginauts (6–10)"),
        (NAVIGATORS, "Navigators (11–13)"),
        (TRAILBLAZERS, "Trailblazers (14–16)"),
    ]
    
    AVATAR_CHOICES = [
        ('astronaut', '👨‍🚀 Astronaut'),
        ('scientist', '🔬 Scientist'),
        ('doctor', '👩‍⚕️ Doctor'),
        ('vet', '👨‍⚕️ Vet'),
        ('chef', '👨‍🍳 Chef'),
        ('artist', '👩‍🎨 Artist'),
        ('teacher', '👨‍🏫 Teacher'),
        ('firefighter', '👨‍🚒 Firefighter'),
        ('engineer', '👷 Engineer'),
        ('farmer', '👨‍🌾 Farmer'),
        ('mechanic', '👨‍🔧 Mechanic'),
        ('programmer', '👩‍💻 Programmer'),
    ]

    # Stage progression choices
    EXPLORER = "EXPLORER"
    EXPERIMENTER = "EXPERIMENTER"
    BUILDER = "BUILDER"
    DESIGNER = "DESIGNER"
    INDEPENDENT_MAKER = "INDEPENDENT_MAKER"
    
    STAGE_CHOICES = [
        (EXPLORER, '🌱 Explorer'),
        (EXPERIMENTER, '🔍 Experimenter'),
        (BUILDER, '🧱 Builder'),
        (DESIGNER, '🛠 Designer'),
        (INDEPENDENT_MAKER, '🔥 Independent Maker'),
    ]

    parent = models.ForeignKey(ParentProfile, on_delete=models.CASCADE, related_name="children")
    username = models.CharField(max_length=30, unique=True)
    pin = models.CharField(max_length=4, help_text="4-digit PIN for child login")
    age_range = models.CharField(max_length=50, choices=AGE_RANGE_CHOICES)
    avatar = models.CharField(max_length=20, choices=AVATAR_CHOICES, default='astronaut')
    interests = models.JSONField(default=list, blank=True, help_text="List of child's interests from quiz")
    learning_style = models.CharField(max_length=50, blank=True, help_text="Result from learning style quiz")
    quiz_completed = models.BooleanField(default=False)
    
    # Growth Map Pathways
    creative_thinking = models.IntegerField(default=0, help_text='Growth in creative thinking pathway')
    practical_making = models.IntegerField(default=0, help_text='Growth in practical making pathway')
    problem_solving = models.IntegerField(default=0, help_text='Growth in problem solving pathway')
    resilience = models.IntegerField(default=0, help_text='Growth in resilience pathway')
    
    # Stage Progression
    current_stage = models.CharField(max_length=30, choices=STAGE_CHOICES, default=EXPLORER, help_text='Current identity stage')
    total_reflections = models.IntegerField(default=0, help_text='Count of thoughtful reflections')
    badges_earned = models.JSONField(default=list, help_text='List of earned badge codes')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.age_range})"
    
    def get_avatar_emoji(self):
        """Get the emoji for the avatar"""
        for code, label in self.AVATAR_CHOICES:
            if code == self.avatar:
                return label.split()[0]  # Extract emoji from "👨‍🚀 Astronaut"
        return '👨‍🚀'
    
    def get_total_pathway_growth(self):
        """Sum of all pathway progress"""
        return self.creative_thinking + self.practical_making + self.problem_solving + self.resilience
    
    def get_projects_completed_count(self):
        """Count completed projects"""
        return self.project_progress.filter(status='completed').count()
    
    def calculate_stage(self):
        """Determine current stage based on progress"""
        completed = self.get_projects_completed_count()
        reflections = self.total_reflections
        
        # Stage thresholds
        if completed >= 25 and reflections >= 10:
            return self.INDEPENDENT_MAKER
        elif completed >= 15 and reflections >= 3:
            return self.DESIGNER
        elif completed >= 8:
            return self.BUILDER
        elif completed >= 3:
            return self.EXPERIMENTER
        else:
            return self.EXPLORER
    
    def update_stage(self):
        """Update stage and check for advancement"""
        old_stage = self.current_stage
        new_stage = self.calculate_stage()
        
        if new_stage != old_stage:
            self.current_stage = new_stage
            self.save()
            return True  # Stage advanced!
        return False
    
    def check_and_award_badges(self):
        """Check for new badge eligibility"""
        new_badges = []
        
        # Reflection badges
        if self.total_reflections >= 5 and 'deep_thinker' not in self.badges_earned:
            self.badges_earned.append('deep_thinker')
            new_badges.append({'code': 'deep_thinker', 'name': '🌟 Deep Thinker', 'desc': "You're thinking about your learning!"})
        
        if self.total_reflections >= 10 and 'thoughtful_builder' not in self.badges_earned:
            self.badges_earned.append('thoughtful_builder')
            new_badges.append({'code': 'thoughtful_builder', 'name': '💭 Thoughtful Builder', 'desc': 'Your reflections show real growth'})
        
        if self.total_reflections >= 20 and 'reflection_master' not in self.badges_earned:
            self.badges_earned.append('reflection_master')
            new_badges.append({'code': 'reflection_master', 'name': '🧠 Reflection Master', 'desc': 'You understand how you learn best'})
        
        if self.total_reflections >= 30 and 'growth_mindset' not in self.badges_earned:
            self.badges_earned.append('growth_mindset')
            new_badges.append({'code': 'growth_mindset', 'name': '🎯 Growth Mindset', 'desc': 'You know learning comes from practice'})
        
        # Resilience builder (check for reflections on challenges)
        challenge_reflections = self.project_progress.filter(
            status='completed',
            reflection_text__isnull=False
        ).exclude(reflection_text='').count()
        
        if challenge_reflections >= 10 and 'resilience_builder' not in self.badges_earned:
            self.badges_earned.append('resilience_builder')
            new_badges.append({'code': 'resilience_builder', 'name': '💪 Resilience Builder', 'desc': 'You learn from what doesn\'t work'})
        
        if new_badges:
            self.save()
        
        return new_badges
    
    def get_pathway_percentage(self, pathway_value, max_value=100):
        """Calculate percentage for progress bar display"""
        return min(100, int((pathway_value / max_value) * 100))
    
    def apply_project_completion_boost(self, project, has_thoughtful_reflection=False):
        """
        Apply skill pathway boosts when a project is completed
        Returns: dict of growth messages to show the child
        """
        skill_dims = project.skill_dimensions or {}
        growth_messages = []
        
        # Reflection multiplier: 1.5x if thoughtful reflection
        multiplier = 1.5 if has_thoughtful_reflection else 1.0
        
        # Apply boosts to each pathway
        if skill_dims.get('creative_thinking'):
            boost = int(skill_dims['creative_thinking'] * multiplier)
            self.creative_thinking += boost
            if boost > 0:
                growth_messages.append(f'🧠 Creative Thinking +{boost}')
        
        if skill_dims.get('practical_making'):
            boost = int(skill_dims['practical_making'] * multiplier)
            self.practical_making += boost
            if boost > 0:
                growth_messages.append(f'🛠 Practical Making +{boost}')
        
        if skill_dims.get('problem_solving'):
            boost = int(skill_dims['problem_solving'] * multiplier)
            self.problem_solving += boost
            if boost > 0:
                growth_messages.append(f'🔍 Problem Solving +{boost}')
        
        if skill_dims.get('resilience'):
            boost = int(skill_dims['resilience'] * multiplier)
            self.resilience += boost
            if boost > 0:
                growth_messages.append(f'💪 Resilience +{boost}')
        
        # Bonus resilience for reflecting
        if has_thoughtful_reflection:
            self.resilience += 2
            self.total_reflections += 1
            growth_messages.append('💭 Reflection bonus!')
        
        self.save()
        
        # Check for stage advancement
        stage_advanced = self.update_stage()
        
        # Check for new badges
        new_badges = self.check_and_award_badges()
        
        return {
            'growth_messages': growth_messages,
            'stage_advanced': stage_advanced,
            'new_badges': new_badges,
            'new_stage': self.get_current_stage_display() if stage_advanced else None
        }

    class Meta:
        verbose_name = "Child Profile"
        verbose_name_plural = "Child Profiles"


@receiver(post_save, sender=User)
def create_parent_profile(sender, instance, created, **kwargs):
    """Automatically create ParentProfile when a User is created"""
    if created and not instance.is_superuser:
        ParentProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_parent_profile(sender, instance, **kwargs):
    """Save the ParentProfile when User is saved"""
    if not instance.is_superuser and hasattr(instance, 'parent_profile'):
        instance.parent_profile.save()


class Subscription(models.Model):
    """Subscription model with trial and payment tracking"""
    STATUS_CHOICES = [
        ('trial', 'Trial'),
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('canceled', 'Canceled'),
        ('incomplete', 'Incomplete'),
    ]

    parent_profile = models.OneToOneField(
        ParentProfile, 
        on_delete=models.CASCADE, 
        related_name="subscription"
    )
    stripe_customer_id = models.CharField(max_length=255, blank=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='incomplete')
    founding_member = models.BooleanField(default=False, help_text="Locked at £9.99/month forever")
    trial_end = models.DateTimeField(null=True, blank=True)
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.parent_profile.user.email} - {self.status}"

    @property
    def is_active(self):
        """Check if subscription is currently active or in trial"""
        if self.status in ['trialing', 'trial', 'active']:
            # Check if trial is still valid
            if self.status in ['trialing', 'trial'] and self.trial_end:
                return timezone.now() < self.trial_end
            # Check if subscription period is still valid
            if self.current_period_end:
                return timezone.now() < self.current_period_end
            return True
        return False

    @property
    def is_in_trial(self):
        """Check if currently in trial period"""
        if self.status in ['trialing', 'trial'] and self.trial_end:
            return timezone.now() < self.trial_end
        return False

    @property
    def days_until_trial_end(self):
        """Days remaining in trial"""
        if self.is_in_trial:
            delta = self.trial_end - timezone.now()
            return max(0, delta.days)
        return 0

    def start_trial(self):
        """Start a 7-day trial"""
        self.status = 'trial'
        self.trial_end = timezone.now() + timedelta(days=7)
        self.current_period_start = timezone.now()
        self.current_period_end = self.trial_end
        self.save()

    class Meta:
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"


class Skill(models.Model):
    """Shared skill taxonomy across entire Imaginauts system"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    emoji = models.CharField(max_length=10, default='⭐')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.emoji} {self.name}"
    
    class Meta:
        ordering = ['name']


class ProjectSkill(models.Model):
    """Link projects to skills with weighted importance"""
    WEIGHT_CHOICES = [
        (1, '⭐ Minimal focus'),
        (2, '⭐⭐ Light focus'),
        (3, '⭐⭐⭐ Moderate focus'),
        (4, '⭐⭐⭐⭐ Heavy focus'),
        (5, '⭐⭐⭐⭐⭐ Primary focus'),
    ]
    
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    weight = models.IntegerField(choices=WEIGHT_CHOICES, default=3, help_text="How central is this skill to the project?")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.project.title} → {self.skill.name} ({self.weight}★)"
    
    class Meta:
        unique_together = ('project', 'skill')
        verbose_name = "Project Skill"
        verbose_name_plural = "Project Skills"


class Project(models.Model):
    """STEAM projects for children to explore - Content Engine"""
    SCIENCE = 'science'
    TECH = 'tech'
    ENGINEERING = 'engineering'
    ART = 'art'
    MATH = 'math'
    
    CATEGORY_CHOICES = [
        (SCIENCE, 'Science'),
        (TECH, 'Technology'),
        (ENGINEERING, 'Engineering'),
        (ART, 'Art'),
        (MATH, 'Math'),
    ]
    
    TYPE_SPARK = 'spark'
    TYPE_LAB = 'lab'
    
    TYPE_CHOICES = [
        (TYPE_SPARK, 'Spark (Quick 5-10 min touch)'),
        (TYPE_LAB, 'Lab (Full project 30-60+ min)'),
    ]
    
    VISIBILITY_HIDDEN = 'hidden'
    VISIBILITY_SCHEDULED = 'scheduled'
    VISIBILITY_LIVE = 'live'
    VISIBILITY_COMING_SOON = 'coming_soon'
    
    VISIBILITY_CHOICES = [
        (VISIBILITY_HIDDEN, 'Hidden'),
        (VISIBILITY_SCHEDULED, 'Scheduled (publish at date)'),
        (VISIBILITY_LIVE, 'Live'),
        (VISIBILITY_COMING_SOON, 'Coming Soon (teaser)'),
    ]
    
    # Basic info
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_LAB)
    difficulty = models.IntegerField(default=1, help_text="1=Easy, 2=Medium, 3=Hard")
    age_ranges = models.JSONField(default=list, help_text="List of age ranges: IMAGINAUTS, NAVIGATORS, TRAILBLAZERS")
    tags = models.JSONField(default=list, help_text="Tags for recommendation matching")
    emoji = models.CharField(max_length=10, default='🔬')
    estimated_time = models.IntegerField(default=30, help_text="Estimated time in minutes")
    
    # Progression gating
    minimum_stage = models.IntegerField(default=1, help_text="Child must be at this stage (1-5) to access")
    prerequisites = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='unlocked_by', help_text="Projects that must be completed first")
    
    # Skills (M2M with weight through ProjectSkill)
    skills = models.ManyToManyField('Skill', through='ProjectSkill', blank=True, related_name='projects')
    
    # Growth Map Skill Dimensions (for pathway boosts)
    skill_dimensions = models.JSONField(
        default=dict,
        help_text='Skill pathway boosts: {"creative_thinking": 3, "practical_making": 5, "problem_solving": 2, "resilience": 1}'
    )
    
    # Media files
    video_file = models.FileField(upload_to='videos/', blank=True, null=True, help_text="Upload video file (will be stored on Digital Ocean Spaces)")
    video_url = models.URLField(blank=True, help_text="Or paste YouTube/Vimeo URL")
    pdf_guide = models.FileField(upload_to='guides/', blank=True, null=True, help_text="Printable PDF guide")
    
    # Content
    materials_needed = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    
    # Publishing & visibility
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default=VISIBILITY_HIDDEN)
    published_at = models.DateTimeField(null=True, blank=True, help_text="Auto-publish at this date/time (leave blank for manual)")
    is_featured = models.BooleanField(default=False, help_text="Pin this to top of world")
    order_priority = models.IntegerField(default=0, help_text="Higher numbers appear first within visibility category")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.emoji} {self.title}"
    
    def is_live(self):
        """Check if project is currently live (handles scheduled publishing)"""
        if self.visibility == self.VISIBILITY_LIVE:
            return True
        if self.visibility == self.VISIBILITY_SCHEDULED and self.published_at:
            return timezone.now() >= self.published_at
        return False
    
    class Meta:
        ordering = ['-is_featured', '-order_priority', '-created_at']
        verbose_name = "Project"
        verbose_name_plural = "Projects"


class ProjectProgress(models.Model):
    """Track child's progress and interaction with projects"""
    STATUS_NOT_STARTED = 'not_started'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'
    
    STATUS_CHOICES = [
        (STATUS_NOT_STARTED, 'Not Started'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_COMPLETED, 'Completed'),
    ]
    
    child = models.ForeignKey(ChildProfile, on_delete=models.CASCADE, related_name='project_progress')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='child_progress')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NOT_STARTED)
    rating = models.IntegerField(null=True, blank=True, help_text="1-5 stars")
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, help_text="Child's notes or reflections")
    
    # Reflection tracking
    reflection_text = models.TextField(blank=True, help_text="Deeper reflection on learning")
    has_reflection = models.BooleanField(default=False, help_text="Whether child provided meaningful reflection")
    reflection_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.child.username} - {self.project.title} ({self.status})"
    
    class Meta:
        unique_together = ['child', 'project']
        ordering = ['-started_at']
        verbose_name = "Project Progress"
        verbose_name_plural = "Project Progress"


# ============================================================================
# IMAGINAUTS PROGRESSION SYSTEM - Stages & Growth Map
# ============================================================================

class ProgressionStage(models.Model):
    """
    Track progression stage for Imaginauts.
    Stages replace traditional levels and are identity-based.
    """
    EXPLORER = 1
    EXPERIMENTER = 2
    BUILDER = 3
    DESIGNER = 4
    INDEPENDENT_MAKER = 5
    
    STAGE_CHOICES = [
        (EXPLORER, "🌱 Explorer - I can follow a build"),
        (EXPERIMENTER, "🔍 Experimenter - I can adapt and improve"),
        (BUILDER, "🧱 Builder - I can strengthen designs"),
        (DESIGNER, "🛠 Designer - I can plan before building"),
        (INDEPENDENT_MAKER, "🔥 Independent Maker - I build with purpose"),
    ]
    
    child = models.OneToOneField(ChildProfile, on_delete=models.CASCADE, related_name="progression_stage")
    current_stage = models.IntegerField(choices=STAGE_CHOICES, default=EXPLORER)
    stage_description = models.CharField(max_length=255, blank=True)
    reached_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.child.username} - Stage {self.current_stage}: {self.get_current_stage_display()}"
    
    def get_stage_info(self):
        """Get detailed info about current stage"""
        stage_info = {
            self.EXPLORER: {
                "name": "Explorer",
                "emoji": "🌱",
                "identity": "I can follow a build.",
                "unlocks": [
                    "Beginner challenges",
                    "Inspiration board browsing",
                    "Basic reflection prompts"
                ]
            },
            self.EXPERIMENTER: {
                "name": "Experimenter",
                "emoji": "🔍",
                "identity": "I can adapt and improve.",
                "unlocks": [
                    '"Try it differently" prompts',
                    "Material swap challenges",
                    "Compare builds on inspiration board"
                ]
            },
            self.BUILDER: {
                "name": "Builder",
                "emoji": "🧱",
                "identity": "I can strengthen and improve designs.",
                "unlocks": [
                    "Constraint challenges",
                    "Limited-material builds",
                    "Skill pathway visibility"
                ]
            },
            self.DESIGNER: {
                "name": "Designer",
                "emoji": "🛠",
                "identity": "I can plan before building.",
                "unlocks": [
                    "Design-your-own variation",
                    "Project remix mode",
                    '"Improve someone else\'s idea" challenge'
                ]
            },
            self.INDEPENDENT_MAKER: {
                "name": "Independent Maker",
                "emoji": "🔥",
                "identity": "I build with purpose.",
                "unlocks": [
                    "Open-ended builds",
                    "Community inspiration contribution badge",
                    "Advanced track pathways"
                ]
            }
        }
        return stage_info.get(self.current_stage, {})
    
    class Meta:
        verbose_name = "Progression Stage"
        verbose_name_plural = "Progression Stages"


class GrowthPathway(models.Model):
    """
    Core growth pathways for visual growth map.
    Instead of XP, children see their growth in specific skills.
    """
    THINKING = 'thinking'
    MAKING = 'making'
    PROBLEM_SOLVING = 'problem_solving'
    RESILIENCE = 'resilience'
    DESIGN_PLANNING = 'design_planning'
    CONTRIBUTION = 'contribution'
    
    PATHWAY_CHOICES = [
        (THINKING, "🧠 Creative Thinking"),
        (MAKING, "🛠 Practical Making"),
        (PROBLEM_SOLVING, "🔍 Problem Solving"),
        (RESILIENCE, "💪 Resilience"),
        (DESIGN_PLANNING, "📐 Design Planning"),
        (CONTRIBUTION, "🌍 Contribution"),
    ]
    
    child = models.ForeignKey(ChildProfile, on_delete=models.CASCADE, related_name="growth_pathways")
    pathway_type = models.CharField(max_length=20, choices=PATHWAY_CHOICES)
    progress = models.IntegerField(default=0, help_text="Progress 0-100 as a percentage")
    level = models.IntegerField(default=1, help_text="Level 1-8 representing growth stages")
    points = models.IntegerField(default=0, help_text="Internal points tracking (not shown to child)")
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_boosted_at = models.DateTimeField(null=True, blank=True, help_text="Last reflection boost")
    
    class Meta:
        unique_together = ['child', 'pathway_type']
        ordering = ['pathway_type']
        verbose_name = "Growth Pathway"
        verbose_name_plural = "Growth Pathways"
    
    def __str__(self):
        return f"{self.child.username} - {self.get_pathway_type_display()} (Lvl {self.level})"
    
    def add_points(self, points, reflection_boost=False):
        """Add points and update progress level"""
        self.points += points
        
        # Reflection boost: grants extra growth
        if reflection_boost:
            self.points += int(points * 0.25)  # 25% bonus
            self.last_boosted_at = timezone.now()
        
        # Calculate level based on points
        # Each level requires progressively more points
        level_thresholds = [0, 100, 250, 450, 700, 1000, 1350, 1750, 2200]
        
        for lvl, threshold in enumerate(level_thresholds, 1):
            if self.points < threshold:
                self.level = max(1, lvl - 1)
                break
        else:
            self.level = 8
        
        # Calculate progress to next level
        current_threshold = level_thresholds[self.level - 1]
        next_threshold = level_thresholds[min(self.level, 8)]
        self.progress = int(((self.points - current_threshold) / (next_threshold - current_threshold)) * 100) if next_threshold > current_threshold else 100
        
        self.save()


class ProjectSkillMapping(models.Model):
    """
    Maps projects to the skill dimensions they develop.
    When a child completes a project, it contributes to specific pathways.
    """
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name="skill_mapping")
    
    # Pathway contributions (0-100 points)
    thinking_points = models.IntegerField(default=0)
    making_points = models.IntegerField(default=0)
    problem_solving_points = models.IntegerField(default=0)
    resilience_points = models.IntegerField(default=0)
    design_planning_points = models.IntegerField(default=0)
    contribution_points = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.project.title} - Skill Mapping"
    
    def get_contributions(self):
        """Return dict of pathway contributions"""
        return {
            GrowthPathway.THINKING: self.thinking_points,
            GrowthPathway.MAKING: self.making_points,
            GrowthPathway.PROBLEM_SOLVING: self.problem_solving_points,
            GrowthPathway.RESILIENCE: self.resilience_points,
            GrowthPathway.DESIGN_PLANNING: self.design_planning_points,
            GrowthPathway.CONTRIBUTION: self.contribution_points,
        }
    
    class Meta:
        verbose_name = "Project Skill Mapping"
        verbose_name_plural = "Project Skill Mappings"


class InspirationShare(models.Model):
    """
    Track when a child shares a project to inspiration board.
    This contributes to their contribution pathway.
    """
    child = models.ForeignKey(ChildProfile, on_delete=models.CASCADE, related_name="inspiration_shares")
    project_progress = models.ForeignKey(ProjectProgress, on_delete=models.CASCADE, related_name="inspiration_shares")
    
    description = models.TextField(blank=True, help_text="Why they're sharing this")
    image_url = models.URLField(blank=True, help_text="Image of completed project")
    
    # Engagement metrics (internal, not shown directly)
    saves_count = models.IntegerField(default=0, help_text="How many saved this to their board")
    inspired_builds = models.IntegerField(default=0, help_text="How many built something inspired by this")
    
    shared_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.child.username} shared {self.project_progress.project.title}"
    
    class Meta:
        ordering = ['-shared_at']
        verbose_name = "Inspiration Share"
        verbose_name_plural = "Inspiration Shares"


# ============================================================================
# SIGNAL HANDLERS FOR PROGRESSION SYSTEM
# ============================================================================

@receiver(post_save, sender=ChildProfile)
def initialize_progression_for_child(sender, instance, created, **kwargs):
    """
    When a new child is created, initialize their progression stage and growth pathways.
    """
    if created:
        # Create progression stage
        ProgressionStage.objects.get_or_create(
            child=instance,
            defaults={'current_stage': ProgressionStage.EXPLORER}
        )
        
        # Create all growth pathways at level 1
        pathway_types = [
            GrowthPathway.THINKING,
            GrowthPathway.MAKING,
            GrowthPathway.PROBLEM_SOLVING,
            GrowthPathway.RESILIENCE,
            GrowthPathway.DESIGN_PLANNING,
            GrowthPathway.CONTRIBUTION,
        ]
        
        for pathway_type in pathway_types:
            GrowthPathway.objects.get_or_create(
                child=instance,
                pathway_type=pathway_type,
                defaults={
                    'progress': 0,
                    'level': 1,
                    'points': 0
                }
            )


@receiver(post_save, sender=ProjectProgress)
def update_growth_on_project_completion(sender, instance, created=False, **kwargs):
    """
    When a project is completed, update the child's growth pathways.
    If they provided reflection, grant reflection bonus.
    """
    # Only process when status changes to completed
    if instance.status == ProjectProgress.STATUS_COMPLETED:
        try:
            skill_mapping = ProjectSkillMapping.objects.get(project=instance.project)
        except ProjectSkillMapping.DoesNotExist:
            # If no skill mapping exists, create a default one
            skill_mapping, created = ProjectSkillMapping.objects.get_or_create(
                project=instance.project,
                defaults={
                    'thinking_points': 20,
                    'making_points': 30,
                    'problem_solving_points': 20,
                    'resilience_points': 10,
                    'design_planning_points': 10,
                    'contribution_points': 5,
                }
            )
        
        # Check if child has reflection
        has_reflection = instance.has_reflection and len(instance.reflection_text.strip()) > 20
        
        # Update each growth pathway
        contributions = skill_mapping.get_contributions()
        for pathway_type, points in contributions.items():
            if points > 0:
                try:
                    pathway = GrowthPathway.objects.get(
                        child=instance.child,
                        pathway_type=pathway_type
                    )
                    pathway.add_points(points, reflection_boost=has_reflection)
                except GrowthPathway.DoesNotExist:
                    # This shouldn't happen if initialize_progression is called
                    pathway = GrowthPathway.objects.create(
                        child=instance.child,
                        pathway_type=pathway_type
                    )
                    pathway.add_points(points, reflection_boost=has_reflection)
