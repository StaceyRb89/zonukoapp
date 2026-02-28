"""
Content Query Engine

Intelligent filtering of projects based on child progression, age, and visibility.
This is the core logic that powers all world views (Imaginauts, Navigators, Trailblazers).
"""

from django.utils import timezone
from django.db.models import Q
from .models import Project


class ProjectQueryEngine:
    LAB_UNLOCK_COVERAGE_THRESHOLD = 0.75
    LAB_CORE_SKILL_WEIGHT_THRESHOLD = 4
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
        ).select_related().prefetch_related('skills', 'prerequisites', 'projectskill_set')

    def _get_effective_stage(self, base_queryset):
        """
        Determine effective unlock stage.

        Uses child's true progression stage by default, but allows a controlled
        one-stage assist when the current stage has been fully exhausted (or has
        no projects at all for that age band).
        """
        effective_stage = self.current_stage
        if self.current_stage >= 5:
            return effective_stage

        current_stage_projects = list(
            base_queryset.filter(minimum_stage__lte=self.current_stage).values_list('id', flat=True)
        )

        if not current_stage_projects:
            return min(5, self.current_stage + 1)

        progress_lookup = {
            progress.project_id: progress
            for progress in self.child.project_progress.filter(project_id__in=current_stage_projects)
        }

        for project_id in current_stage_projects:
            progress = progress_lookup.get(project_id)
            if not progress:
                return effective_stage

            if progress.status == 'in_progress':
                return effective_stage

            is_completed = bool(progress.completed_at) or progress.status == 'completed'
            if not is_completed:
                return effective_stage

        return min(5, self.current_stage + 1)
    
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
        base_queryset = self._base_query().filter(
            visibility__in=[
                Project.VISIBILITY_LIVE,
                Project.VISIBILITY_SCHEDULED
            ]
        ).exclude(
            visibility=Project.VISIBILITY_SCHEDULED,
            published_at__gt=timezone.now()
        )

        effective_stage = self._get_effective_stage(base_queryset)

        queryset = base_queryset.filter(
            minimum_stage__lte=effective_stage
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

    def get_dashboard_lists(self, new_limit=4):
        """
        Get dashboard lists with paced unlocking logic.

        - Keeps a small rolling window of new projects
        - Prioritizes Sparks first when available
        - Unlocks Labs based on skills learned from completed Sparks
        """
        available_projects = list(self.get_available())
        available_project_ids = [project.id for project in available_projects]

        progress_lookup = {
            progress.project_id: progress
            for progress in self.child.project_progress.filter(project_id__in=available_project_ids).select_related('project')
        }

        for project in available_projects:
            project.progress = progress_lookup.get(project.id)

        in_progress_projects = [
            project for project in available_projects
            if project.progress and project.progress.status == 'in_progress'
        ]

        not_started_projects = [
            project for project in available_projects
            if not project.progress or project.progress.status == 'not_started'
        ]

        new_projects = self._select_paced_new_projects(not_started_projects, limit=new_limit)

        return {
            'available_projects': available_projects,
            'in_progress_projects': in_progress_projects,
            'new_projects': new_projects,
            'progress_lookup': progress_lookup,
        }

    def _completed_progress_q(self):
        return Q(completed_at__isnull=False) | Q(status='completed')

    def _get_spark_skill_profile(self):
        """
        Build a lightweight skill profile from completed Spark projects.

        Returns:
            tuple[dict[int, int], int]
            - skill_weights_by_id: cumulative weight per skill
            - completed_sparks_count: distinct completed spark projects
        """
        completed_spark_projects = list(
            Project.objects.filter(
                id__in=self.child.project_progress.filter(self._completed_progress_q()).values_list('project_id', flat=True).distinct(),
                type=Project.TYPE_SPARK,
                age_ranges__icontains=self.age_band,
            ).prefetch_related('projectskill_set')
        )

        skill_weights_by_id = {}
        for project in completed_spark_projects:
            for project_skill in project.projectskill_set.all():
                skill_id = project_skill.skill_id
                skill_weights_by_id[skill_id] = skill_weights_by_id.get(skill_id, 0) + int(project_skill.weight or 0)

        return skill_weights_by_id, len(completed_spark_projects)

    def _select_paced_new_projects(self, not_started_projects, limit=4):
        """
        Select a staggered set of new projects.

        Rules:
        - Keep a small window (default 4) to avoid overwhelming children.
        - Prefer Sparks first where available.
        - Labs are unlocked as Spark skills are demonstrated.
        - If an age band has no Sparks, gracefully seed Labs so children aren't blocked.
        """
        if not not_started_projects:
            return []

        total_slots = max(2, min(limit, 4))
        spark_candidates = [project for project in not_started_projects if project.type == Project.TYPE_SPARK]
        lab_candidates = [project for project in not_started_projects if project.type == Project.TYPE_LAB]

        skill_weights_by_id, completed_sparks_count = self._get_spark_skill_profile()
        mastered_skill_ids = {skill_id for skill_id, weight in skill_weights_by_id.items() if weight >= 3}

        spark_slots = total_slots
        lab_slots = 0

        if spark_candidates:
            base_spark_slots = 2 if completed_sparks_count == 0 else 1
            skill_growth_bonus = min(2, len(mastered_skill_ids) // 2)
            spark_slots = min(total_slots, base_spark_slots + skill_growth_bonus)

            if completed_sparks_count >= 2:
                lab_slots = min(total_slots - spark_slots, 1 + (completed_sparks_count // 4))
        else:
            spark_slots = 0
            lab_slots = total_slots

        selected = []

        if spark_slots > 0:
            selected.extend(spark_candidates[:spark_slots])

        aligned_lab_projects = []
        fallback_labs = []

        if lab_slots > 0 and lab_candidates:
            for project in lab_candidates:
                project_skill_rows = list(project.projectskill_set.all())
                project_skill_ids = {project_skill.skill_id for project_skill in project_skill_rows}

                if not project_skill_ids:
                    fallback_labs.append(project)
                    continue

                core_skill_ids = {
                    project_skill.skill_id
                    for project_skill in project_skill_rows
                    if int(project_skill.weight or 0) >= self.LAB_CORE_SKILL_WEIGHT_THRESHOLD
                }

                if not core_skill_ids and project_skill_rows:
                    max_weight = max(int(project_skill.weight or 0) for project_skill in project_skill_rows)
                    core_skill_ids = {
                        project_skill.skill_id
                        for project_skill in project_skill_rows
                        if int(project_skill.weight or 0) == max_weight
                    }

                matched_skill_ids = project_skill_ids.intersection(mastered_skill_ids)
                matched_count = len(matched_skill_ids)
                total_skill_count = len(project_skill_ids)
                coverage = (matched_count / total_skill_count) if total_skill_count else 0
                has_all_core = core_skill_ids.issubset(mastered_skill_ids) if core_skill_ids else True

                if has_all_core and coverage >= self.LAB_UNLOCK_COVERAGE_THRESHOLD:
                    overlap_score = sum(skill_weights_by_id.get(skill_id, 0) for skill_id in matched_skill_ids)
                    aligned_lab_projects.append((coverage, overlap_score, project))
                else:
                    fallback_labs.append(project)

            aligned_lab_projects.sort(key=lambda item: (item[0], item[1]), reverse=True)
            selected.extend([project for _, _, project in aligned_lab_projects[:lab_slots]])

            remaining_lab_slots = lab_slots - min(lab_slots, len(aligned_lab_projects))
            if remaining_lab_slots > 0 and not spark_candidates:
                selected.extend(fallback_labs[:remaining_lab_slots])

        if len(selected) < total_slots:
            used_ids = {project.id for project in selected}

            allowed_fill_pool = list(spark_candidates)
            allowed_fill_pool.extend([project for _, _, project in aligned_lab_projects])

            if not spark_candidates:
                allowed_fill_pool.extend(fallback_labs)

            for project in allowed_fill_pool:
                if project.id in used_ids:
                    continue
                selected.append(project)
                if len(selected) >= total_slots:
                    break

        return selected[:total_slots]
