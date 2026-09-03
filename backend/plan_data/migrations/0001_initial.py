import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Goal',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('user_id', models.UUIDField(db_index=True)),
                ('title', models.CharField(max_length=255)),
                ('raw_input', models.TextField()),
                ('description', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('active', 'Active'), ('archived', 'Archived')], default='draft', max_length=16)),
                ('target_date', models.DateField(blank=True, null=True)),
                ('hours_per_day', models.PositiveSmallIntegerField(default=2)),
                ('constraints', models.JSONField(default=list)),
                ('context', models.JSONField(default=dict)),
                ('progress_percentage', models.FloatField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('active', 'Active'), ('archived', 'Archived')], default='draft', max_length=16)),
                ('summary', models.TextField(blank=True)),
                ('source_model', models.CharField(blank=True, max_length=128)),
                ('raw_response', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('goal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='plans', to='plan_data.goal')),
            ],
        ),
        migrations.CreateModel(
            name='Stage',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('position', models.PositiveSmallIntegerField()),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stages', to='plan_data.plan')),
            ],
            options={'constraints': [models.UniqueConstraint(fields=('plan', 'position'), name='unique_stage_position')]},
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('position', models.PositiveSmallIntegerField()),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('priority', models.CharField(choices=[('high', 'High'), ('medium', 'Medium'), ('low', 'Low')], default='medium', max_length=16)),
                ('estimated_minutes', models.PositiveIntegerField()),
                ('depends_on', models.JSONField(default=list)),
                ('due_date', models.DateField(blank=True, null=True)),
                ('completed', models.BooleanField(default=False)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('stage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='plan_data.stage')),
            ],
            options={'constraints': [models.UniqueConstraint(fields=('stage', 'position'), name='unique_task_position')]},
        ),
        migrations.RunSQL(
            sql='''
                ALTER TABLE plan_data_goal ENABLE ROW LEVEL SECURITY;
                ALTER TABLE plan_data_plan ENABLE ROW LEVEL SECURITY;
                ALTER TABLE plan_data_stage ENABLE ROW LEVEL SECURITY;
                ALTER TABLE plan_data_task ENABLE ROW LEVEL SECURITY;
                CREATE POLICY goal_owner ON plan_data_goal
                    FOR ALL USING (user_id = auth.uid()) WITH CHECK (user_id = auth.uid());
                CREATE POLICY plan_owner ON plan_data_plan
                    FOR ALL USING (EXISTS (SELECT 1 FROM plan_data_goal g WHERE g.id = goal_id AND g.user_id = auth.uid()))
                    WITH CHECK (EXISTS (SELECT 1 FROM plan_data_goal g WHERE g.id = goal_id AND g.user_id = auth.uid()));
                CREATE POLICY stage_owner ON plan_data_stage
                    FOR ALL USING (EXISTS (SELECT 1 FROM plan_data_plan p JOIN plan_data_goal g ON g.id = p.goal_id WHERE p.id = plan_id AND g.user_id = auth.uid()))
                    WITH CHECK (EXISTS (SELECT 1 FROM plan_data_plan p JOIN plan_data_goal g ON g.id = p.goal_id WHERE p.id = plan_id AND g.user_id = auth.uid()));
                CREATE POLICY task_owner ON plan_data_task
                    FOR ALL USING (EXISTS (SELECT 1 FROM plan_data_stage s JOIN plan_data_plan p ON p.id = s.plan_id JOIN plan_data_goal g ON g.id = p.goal_id WHERE s.id = stage_id AND g.user_id = auth.uid()))
                    WITH CHECK (EXISTS (SELECT 1 FROM plan_data_stage s JOIN plan_data_plan p ON p.id = s.plan_id JOIN plan_data_goal g ON g.id = p.goal_id WHERE s.id = stage_id AND g.user_id = auth.uid()));
            ''',
            reverse_sql='''
                DROP POLICY IF EXISTS task_owner ON plan_data_task;
                DROP POLICY IF EXISTS stage_owner ON plan_data_stage;
                DROP POLICY IF EXISTS plan_owner ON plan_data_plan;
                DROP POLICY IF EXISTS goal_owner ON plan_data_goal;
            ''',
        ),
    ]