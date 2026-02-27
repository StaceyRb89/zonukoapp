"""
Content Query Engine

Intelligent filtering of projects based on child progression, age, and visibility.
This is the core logic that powers all world views (Imaginauts, Navigators, Trailblazers).
"""

from django.utils import timezone
from .models import Project


class ProjectQueryEngine:
    """
    Smart query engine for fetching projects based on child context.
    
    Usage:
        engine = ProjectQueryEngine(child)
        available = engine.get_available()
        teasers = engine.get_teasers()
        coming_soon = engine.get_coming_soon()
    """
    
    def __init__(self, child):
        """
        Initialize engine with a child profile.
        
        Args:
            child: ChildProfile instance
        """
        self.child = child
        self.age_band = child.age_range  # IMAGINAUTS, NAVIGATORS, TRAILBLAZERS
        
        # Get child's current progression stage (defaults to 1 if not initialized)
        try:
            self.current_stage = child.progression_stage.current_stage
        except AttributeError:
            self.current_stage = 1
    
    def _base_query(self):
        """Base queryset with age band filtering"""
        # Use icontains for SQLite compatibility (searching JSON array as string)
        return Project.objects.filter(
            age_ranges__icontains=self.age_band
        ).select_related().prefetch_related('skills', 'prerequisites')
    
    def get_available(self, limit=None):
        """
        Get projects child can access now.
        
        Filters by:
        - Age band match
        - Child's current stage >= project's minimum_stage
        - Visibility is LIVE or SCHEDULED+published
        
        Args:
            limit: Optional limit to number of results
            
        Returns:
            QuerySet of available projects
        """
        queryset = self._base_query().filter(
            minimum_stage__lte=self.current_stage
        ).filter(
            visibility__in=[
                Project.VISIBILITY_LIVE,
                Project.VISIBILITY_SCHEDULED
            ]
        ).exclude(
            # Exclude scheduled projects that aren't published yet
            visibility=Project.VISIBILITY_SCHEDULED,
            published_at__gt=timezone.now()
        ).distinct()
        
        if limit:
            queryset = queryset[:limit]
        
        return queryset
    
    def get_teasers(self, limit=None):
        """
        Get locked projects from the next stage.
        
        Shows what's coming when child progresses.
        
        Args:
            limit: Optional limit to number of results
            
        Returns:
            QuerySet of teaser projects
        """
        # Only show teasers for next stage if not at max stage (5)
        if self.current_stage >= 5:
            return Project.objects.none()
        
        queryset = self._base_query().filter(
            minimum_stage=self.current_stage + 1,
            visibility__in=[
                Project.VISIBILITY_LIVE,
                Project.VISIBILITY_SCHEDULED
            ]
        ).exclude(
            visibility=Project.VISIBILITY_SCHEDULED,
            published_at__gt=timezone.now()
        ).distinct()
        
        if limit:
            queryset = queryset[:limit]
        
        return queryset
    
    def get_coming_soon(self, limit=None):
        """
        Get projects marked as coming soon.
        
        Args:
            limit: Optional limit to number of results
            
        Returns:
            QuerySet of coming soon projects
        """
        queryset = self._base_query().filter(
            visibility=Project.VISIBILITY_COMING_SOON
        ).distinct()
        
        if limit:
            queryset = queryset[:limit]
        
        return queryset
    
    def get_featured(self, limit=None):
        """
        Get featured projects child can access.
        
        Args:
            limit: Optional limit to number of results (default 3)
            
        Returns:
            QuerySet of featured projects
        """
        if limit is None:
            limit = 3
        
        queryset = self.get_available().filter(
            is_featured=True
        ).distinct()
        
        if limit:
            queryset = queryset[:limit]
        
        return queryset
    
    def get_by_skill(self, skill, limit=None):
        """
        Get available projects focused on a specific skill.
        
        Args:
            skill: Skill instance or skill name string
            limit: Optional limit to number of results
            
        Returns:
            QuerySet of projects with this skill
        """
        if isinstance(skill, str):
            from .models import Skill
            try:
                skill = Skill.objects.get(name=skill)
            except Skill.DoesNotExist:
                return Project.objects.none()
        
        queryset = self.get_available().filter(
            skills=skill
        ).distinct()
        
        if limit:
            queryset = queryset[:limit]
        
        return queryset
    
    def get_by_category(self, category, limit=None):
        """
        Get available projects in a category.
        
        Args:
            category: Category string (SCIENCE, TECH, ENGINEERING, ART, MATH)
            limit: Optional limit to number of results
            
        Returns:
            QuerySet of projects in this category
        """
        queryset = self.get_available().filter(
            category=category
        ).distinct()
        
        if limit:
            queryset = queryset[:limit]
        
        return queryset
    
    def get_by_difficulty(self, difficulty, limit=None):
        """
        Get available projects at a difficulty level.
        
        Args:
            difficulty: 1, 2, or 3
            limit: Optional limit to number of results
            
        Returns:
            QuerySet of projects at this difficulty
        """
        if difficulty not in [1, 2, 3]:
            return Project.objects.none()
        
        queryset = self.get_available().filter(
            difficulty=difficulty
        ).distinct()
        
        if limit:
            queryset = queryset[:limit]
        
        return queryset
    
    def get_sparks(self, limit=None):
        """Get available Spark projects (quick 5-10 min)"""
        queryset = self.get_available().filter(
            type=Project.TYPE_SPARK
        ).distinct()
        
        if limit:
            queryset = queryset[:limit]
        
        return queryset
    
    def get_labs(self, limit=None):
        """Get available Lab projects (full 30-60+ min)"""
        queryset = self.get_available().filter(
            type=Project.TYPE_LAB
        ).distinct()
        
        if limit:
            queryset = queryset[:limit]
        
        return queryset
    
    def get_dashboard_content(self):
        """
        Get all dashboard content sections in one call.
        
        Returns:
            dict with featured, available, teasers, coming_soon
        """
        return {
            'featured': self.get_featured(3),
            'available': self.get_available(6),
            'teasers': self.get_teasers(2),
            'coming_soon': self.get_coming_soon(1),
        }
