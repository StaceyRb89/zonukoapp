# Generated migration for progression system

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_alter_childprofile_avatar'),
    ]

    operations = [
        # Update ProjectProgress to add reflection fields
        migrations.AddField(
            model_name='projectprogress',
            name='reflection_text',
            field=models.TextField(blank=True, help_text="Deeper reflection on learning"),
        ),
        migrations.AddField(
            model_name='projectprogress',
            name='has_reflection',
            field=models.BooleanField(default=False, help_text="Whether child provided meaningful reflection"),
        ),
        migrations.AddField(
            model_name='projectprogress',
            name='reflection_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
        
        # Create ProgressionStage model
        migrations.CreateModel(
            name='ProgressionStage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_stage', models.IntegerField(choices=[(1, '🌱 Explorer - I can follow a build'), (2, '🔍 Experimenter - I can adapt and improve'), (3, '🧱 Builder - I can strengthen designs'), (4, '🛠 Designer - I can plan before building'), (5, '🔥 Independent Maker - I build with purpose')], default=1)),
                ('stage_description', models.CharField(blank=True, max_length=255)),
                ('reached_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('child', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='progression_stage', to='users.childprofile')),
            ],
            options={
                'verbose_name': 'Progression Stage',
                'verbose_name_plural': 'Progression Stages',
            },
        ),
        
        # Create GrowthPathway model
        migrations.CreateModel(
            name='GrowthPathway',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pathway_type', models.CharField(choices=[('thinking', '🧠 Creative Thinking'), ('making', '🛠 Practical Making'), ('problem_solving', '🔍 Problem Solving'), ('resilience', '💪 Resilience'), ('design_planning', '📐 Design Planning'), ('contribution', '🌍 Contribution')], max_length=20)),
                ('progress', models.IntegerField(default=0, help_text='Progress 0-100 as a percentage')),
                ('level', models.IntegerField(default=1, help_text='Level 1-8 representing growth stages')),
                ('points', models.IntegerField(default=0, help_text='Internal points tracking (not shown to child)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('last_boosted_at', models.DateTimeField(null=True, blank=True, help_text='Last reflection boost')),
                ('child', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='growth_pathways', to='users.childprofile')),
            ],
            options={
                'verbose_name': 'Growth Pathway',
                'verbose_name_plural': 'Growth Pathways',
                'ordering': ['pathway_type'],
                'unique_together': {('child', 'pathway_type')},
            },
        ),
        
        # Create ProjectSkillMapping model
        migrations.CreateModel(
            name='ProjectSkillMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('thinking_points', models.IntegerField(default=0)),
                ('making_points', models.IntegerField(default=0)),
                ('problem_solving_points', models.IntegerField(default=0)),
                ('resilience_points', models.IntegerField(default=0)),
                ('design_planning_points', models.IntegerField(default=0)),
                ('contribution_points', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('project', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='skill_mapping', to='users.project')),
            ],
            options={
                'verbose_name': 'Project Skill Mapping',
                'verbose_name_plural': 'Project Skill Mappings',
            },
        ),
        
        # Create InspirationShare model
        migrations.CreateModel(
            name='InspirationShare',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, help_text="Why they're sharing this")),
                ('image_url', models.URLField(blank=True, help_text='Image of completed project')),
                ('saves_count', models.IntegerField(default=0, help_text='How many saved this to their board')),
                ('inspired_builds', models.IntegerField(default=0, help_text='How many built something inspired by this')),
                ('shared_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('child', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inspiration_shares', to='users.childprofile')),
                ('project_progress', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inspiration_shares', to='users.projectprogress')),
            ],
            options={
                'verbose_name': 'Inspiration Share',
                'verbose_name_plural': 'Inspiration Shares',
                'ordering': ['-shared_at'],
            },
        ),
    ]
