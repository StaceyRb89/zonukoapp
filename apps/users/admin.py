from django.contrib import admin
from django import forms
from tinymce.widgets import TinyMCE
import json
from .models import (
    ParentProfile, ChildProfile, Subscription, Project, ProjectProgress,
    ProgressionStage, GrowthPathway, ProjectSkillMapping, InspirationShare,
    Skill, ProjectSkill, ProjectInstructionStep
)


class ProjectAdminForm(forms.ModelForm):
    """Custom form for Project admin with rich text editors and better widgets"""
    
    # Multiple choice field for age ranges
    age_ranges = forms.MultipleChoiceField(
        choices=[
            ('IMAGINAUTS', '🎨 Imaginauts (6-10)'),
            ('NAVIGATORS', '🧭 Navigators (11-13)'),
            ('TRAILBLAZERS', '🚀 Trailblazers (14-16)'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=True,
        help_text="Select all age groups this project is suitable for"
    )
    
    # Text input for tags (comma-separated)
    tags_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g., science, experiments, chemistry, reactions',
            'style': 'width: 100%;'
        }),
        help_text="Enter tags separated by commas. Common tags: science, art, coding, robots, experiments, nature, space, chemistry, physics, building, crafts, music, engineering"
    )

    instruction_steps_input = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 10,
            'style': 'width: 100%; font-family: monospace;'
        }),
        help_text='Optional JSON list for visual step cards. Example: [{"title":"Step 1","description":"Do this","image_url":"https://..."}]'
    )
    
    class Meta:
        model = Project
        fields = '__all__'
        widgets = {
            'description': TinyMCE(attrs={'cols': 80, 'rows': 10}),
            'instructions': TinyMCE(attrs={'cols': 80, 'rows': 15}),
            'materials_needed': forms.Textarea(attrs={'rows': 8, 'cols': 80}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-populate fields from JSON if editing existing project
        if self.instance.pk:
            if self.instance.age_ranges:
                self.initial['age_ranges'] = self.instance.age_ranges
            if self.instance.tags:
                self.initial['tags_input'] = ', '.join(self.instance.tags)
            if self.instance.instruction_steps:
                self.initial['instruction_steps_input'] = json.dumps(self.instance.instruction_steps, indent=2)
    
    def clean_age_ranges(self):
        """Convert selected checkboxes to list"""
        return list(self.cleaned_data.get('age_ranges', []))
    
    def clean(self):
        cleaned_data = super().clean()
        # Convert comma-separated tags to list
        tags_input = cleaned_data.get('tags_input', '')
        if tags_input:
            tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
            cleaned_data['tags'] = tags
        else:
            cleaned_data['tags'] = []

        instruction_steps_input = cleaned_data.get('instruction_steps_input', '').strip()
        if instruction_steps_input:
            try:
                parsed = json.loads(instruction_steps_input)
            except json.JSONDecodeError:
                self.add_error('instruction_steps_input', 'Enter valid JSON (a list of step objects).')
                parsed = []

            if parsed and not isinstance(parsed, list):
                self.add_error('instruction_steps_input', 'Instruction steps JSON must be a list.')
                parsed = []

            cleaned_data['instruction_steps'] = parsed
        else:
            cleaned_data['instruction_steps'] = []
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Ensure age_ranges and tags are saved as lists
        instance.age_ranges = self.cleaned_data.get('age_ranges', [])
        instance.tags = self.cleaned_data.get('tags', [])
        instance.instruction_steps = self.cleaned_data.get('instruction_steps', [])
        if commit:
            instance.save()
        return instance


@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "display_name", "created_at", "has_active_subscription")
    search_fields = ("user__email", "display_name")
    list_filter = ("created_at",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(ChildProfile)
class ChildProfileAdmin(admin.ModelAdmin):
    list_display = ("username", "parent", "age_range", "created_at")
    search_fields = ("username", "parent__user__email")
    list_filter = ("age_range", "created_at")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("parent_profile", "status", "is_in_trial", "trial_end", "current_period_end", "created_at")
    search_fields = ("parent_profile__user__email", "stripe_customer_id", "stripe_subscription_id")
    list_filter = ("status", "created_at")
    readonly_fields = ("created_at", "updated_at", "is_in_trial", "days_until_trial_end")
    
    fieldsets = (
        ("User", {
            "fields": ("parent_profile",)
        }),
        ("Stripe Info", {
            "fields": ("stripe_customer_id", "stripe_subscription_id")
        }),
        ("Subscription Details", {
            "fields": ("status", "trial_end", "current_period_start", "current_period_end", "cancel_at_period_end")
        }),
        ("Trial Info", {
            "fields": ("is_in_trial", "days_until_trial_end")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )


class ProjectSkillInline(admin.TabularInline):
    """Inline editor for ProjectSkill through model"""
    model = ProjectSkill
    extra = 1
    fields = ("skill", "weight")
    verbose_name = "Skill"
    verbose_name_plural = "Skills"


class ProjectInstructionStepInline(admin.StackedInline):
    model = ProjectInstructionStep
    extra = 1
    fields = ("order", "title", "description", "image", "image_alt_text")
    ordering = ("order", "id")
    verbose_name = "Instruction Step"
    verbose_name_plural = "Instruction Steps (with optional uploaded images)"


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm
    list_display = ("emoji", "title", "get_type", "category", "difficulty", "get_age_ranges", "get_visibility", "is_featured", "minimum_stage", "created_at")
    search_fields = ("title", "description")
    list_filter = ("type", "category", "difficulty", "visibility", "is_featured", "minimum_stage", "created_at")
    list_editable = ("is_featured",)
    readonly_fields = ("created_at", "updated_at")
    filter_horizontal = ("prerequisites",)
    inlines = (ProjectSkillInline, ProjectInstructionStepInline)
    
    fieldsets = (
        ("📝 Basic Information", {
            "fields": ("title", "emoji", "description", "category", "type")
        }),
        ("🎯 Target Audience & Difficulty", {
            "fields": ("age_ranges", "difficulty", "minimum_stage", "estimated_time", "tags_input")
        }),
        ("🔗 Learning Paths", {
            "fields": ("prerequisites",),
            "description": "Projects that should be completed before this one"
        }),
        ("📹 Media & Resources", {
            "fields": ("video_file", "video_url", "pdf_guide"),
            "description": "Upload video file OR paste YouTube/Vimeo URL (not both)"
        }),
        ("📚 Content", {
            "fields": ("materials_needed", "instructions", "instruction_steps_input"),
            "classes": ("collapse",)
        }),
        ("⚙️ Publishing & Visibility", {
            "fields": ("visibility", "published_at", "is_featured", "order_priority", "created_at", "updated_at")
        }),
    )
    
    def get_age_ranges(self, obj):
        """Display age ranges as badges"""
        if not obj.age_ranges:
            return "-"
        badges = {
            "IMAGINAUTS": "🎨 Imag",
            "NAVIGATORS": "🧭 Navi",
            "TRAILBLAZERS": "🚀 Trail"
        }
        return " ".join([badges.get(ar, ar) for ar in obj.age_ranges])
    get_age_ranges.short_description = "Age Groups"
    
    def get_type(self, obj):
        """Display project type"""
        types = {
            'spark': '✨ Spark',
            'lab': '🔬 Lab'
        }
        return types.get(obj.type, obj.type)
    get_type.short_description = "Type"
    
    def get_visibility(self, obj):
        """Display visibility status"""
        status = {
            'hidden': '👻 Hidden',
            'scheduled': '📅 Scheduled',
            'live': '🟢 Live',
            'coming_soon': '🔮 Coming Soon'
        }
        return status.get(obj.visibility, obj.visibility)
    get_visibility.short_description = "Status"



@admin.register(ProjectProgress)
class ProjectProgressAdmin(admin.ModelAdmin):
    list_display = ("child", "project", "status", "rating", "has_reflection", "started_at", "completed_at")
    search_fields = ("child__username", "project__title")
    list_filter = ("status", "rating", "has_reflection")
    readonly_fields = ("started_at", "completed_at", "reflection_at")
    fieldsets = (
        ("Child & Project", {
            "fields": ("child", "project", "status", "rating")
        }),
        ("Progress Tracking", {
            "fields": ("started_at", "completed_at")
        }),
        ("Reflection & Notes", {
            "fields": ("notes", "reflection_text", "has_reflection", "reflection_at")
        }),
    )


@admin.register(ProgressionStage)
class ProgressionStageAdmin(admin.ModelAdmin):
    list_display = ("child", "current_stage", "get_stage_name", "updated_at")
    search_fields = ("child__username",)
    list_filter = ("current_stage",)
    readonly_fields = ("reached_at", "updated_at")
    
    fieldsets = (
        ("Child", {
            "fields": ("child",)
        }),
        ("Stage Information", {
            "fields": ("current_stage", "stage_description")
        }),
        ("Timestamps", {
            "fields": ("reached_at", "updated_at")
        }),
    )
    
    def get_stage_name(self, obj):
        return obj.get_stage_info().get('name', 'Unknown')
    get_stage_name.short_description = "Stage Name"


@admin.register(GrowthPathway)
class GrowthPathwayAdmin(admin.ModelAdmin):
    list_display = ("child", "pathway_type", "level", "progress", "points", "updated_at")
    search_fields = ("child__username",)
    list_filter = ("pathway_type", "level")
    readonly_fields = ("created_at", "updated_at", "last_boosted_at")
    
    fieldsets = (
        ("Child & Pathway", {
            "fields": ("child", "pathway_type")
        }),
        ("Progress Metrics", {
            "fields": ("level", "progress", "points")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at", "last_boosted_at")
        }),
    )


@admin.register(ProjectSkillMapping)
class ProjectSkillMappingAdmin(admin.ModelAdmin):
    list_display = ("project", "get_total_points", "created_at")
    search_fields = ("project__title",)
    readonly_fields = ("created_at", "updated_at")
    
    fieldsets = (
        ("Project", {
            "fields": ("project",)
        }),
        ("Skill Contributions", {
            "fields": ("thinking_points", "making_points", "problem_solving_points", 
                      "resilience_points", "design_planning_points", "contribution_points")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )
    
    def get_total_points(self, obj):
        total = (obj.thinking_points + obj.making_points + obj.problem_solving_points +
                obj.resilience_points + obj.design_planning_points + obj.contribution_points)
        return f"{total} pts"
    get_total_points.short_description = "Total Points"


@admin.register(InspirationShare)
class InspirationShareAdmin(admin.ModelAdmin):
    list_display = ("child", "project_progress", "saves_count", "inspired_builds", "shared_at")
    search_fields = ("child__username", "project_progress__project__title")
    list_filter = ("shared_at",)
    readonly_fields = ("shared_at", "updated_at")
    
    fieldsets = (
        ("Share Information", {
            "fields": ("child", "project_progress")
        }),
        ("Content", {
            "fields": ("description", "image_url")
        }),
        ("Engagement", {
            "fields": ("saves_count", "inspired_builds")
        }),
        ("Timestamps", {
            "fields": ("shared_at", "updated_at")
        }),
    )



@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    """Admin for skill taxonomy"""
    list_display = ("emoji", "name", "get_project_count", "created_at")
    search_fields = ("name", "description")
    readonly_fields = ("created_at",)
    
    fieldsets = (
        ("📌 Skill Definition", {
            "fields": ("emoji", "name", "description")
        }),
        ("Timestamps", {
            "fields": ("created_at",)
        }),
    )
    
    def get_project_count(self, obj):
        """Show how many projects use this skill"""
        return obj.projects.count()
    get_project_count.short_description = "Used in Projects"


@admin.register(ProjectSkill)
class ProjectSkillAdmin(admin.ModelAdmin):
    """Admin for project-skill relationships with weights"""
    list_display = ("get_project_title", "get_skill_name", "get_weight_stars", "created_at")
    search_fields = ("project__title", "skill__name")
    list_filter = ("weight", "project__category", "skill")
    readonly_fields = ("created_at",)
    
    fieldsets = (
        ("Link", {
            "fields": ("project", "skill")
        }),
        ("Weight", {
            "fields": ("weight",),
            "description": "How central is this skill to the project?"
        }),
    )
    
    def get_project_title(self, obj):
        return f"{obj.project.emoji} {obj.project.title}"
    get_project_title.short_description = "Project"
    
    def get_skill_name(self, obj):
        return f"{obj.skill.emoji} {obj.skill.name}"
    get_skill_name.short_description = "Skill"
    
    def get_weight_stars(self, obj):
        """Display weight as stars"""
        stars = {1: '⭐', 2: '⭐⭐', 3: '⭐⭐⭐', 4: '⭐⭐⭐⭐', 5: '⭐⭐⭐⭐⭐'}
        return stars.get(obj.weight, '?')
    get_weight_stars.short_description = "Weight"
