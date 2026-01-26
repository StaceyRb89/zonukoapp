from django.contrib import admin
from django import forms
from tinymce.widgets import TinyMCE
from .models import ParentProfile, ChildProfile, Subscription, Project, ProjectProgress


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
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Ensure age_ranges and tags are saved as lists
        instance.age_ranges = self.cleaned_data.get('age_ranges', [])
        instance.tags = self.cleaned_data.get('tags', [])
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


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm
    list_display = ("emoji", "title", "category", "difficulty", "get_age_ranges", "estimated_time", "is_published", "created_at")
    search_fields = ("title", "description")
    list_filter = ("category", "difficulty", "is_published", "created_at")
    list_editable = ("is_published",)
    readonly_fields = ("created_at",)
    
    fieldsets = (
        ("📝 Basic Information", {
            "fields": ("title", "emoji", "description", "category")
        }),
        ("🎯 Target Audience", {
            "fields": ("age_ranges", "difficulty", "estimated_time", "tags_input")
        }),
        ("📹 Media & Resources", {
            "fields": ("video_file", "video_url", "pdf_guide"),
            "description": "Upload video file OR paste YouTube/Vimeo URL (not both)"
        }),
        ("📚 Content", {
            "fields": ("materials_needed", "instructions"),
            "classes": ("collapse",)
        }),
        ("⚙️ Publishing", {
            "fields": ("is_published", "created_at")
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


@admin.register(ProjectProgress)
class ProjectProgressAdmin(admin.ModelAdmin):
    list_display = ("child", "project", "status", "rating", "started_at", "completed_at")
    search_fields = ("child__username", "project__title")
    list_filter = ("status", "rating")
    readonly_fields = ("started_at", "completed_at")
