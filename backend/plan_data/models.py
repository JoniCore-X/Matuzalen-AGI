import uuid

from django.db import models


class Goal(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        ACTIVE = 'active', 'Active'
        ARCHIVED = 'archived', 'Archived'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(db_index=True)
    title = models.CharField(max_length=255)
    raw_input = models.TextField()
    description = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=Status, default=Status.DRAFT)
    target_date = models.DateField(null=True, blank=True)
    hours_per_day = models.PositiveSmallIntegerField(default=2)
    constraints = models.JSONField(default=list)
    context = models.JSONField(default=dict)
    progress_percentage = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Plan(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        ACTIVE = 'active', 'Active'
        ARCHIVED = 'archived', 'Archived'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='plans')
    status = models.CharField(max_length=16, choices=Status, default=Status.DRAFT)
    summary = models.TextField(blank=True)
    source_model = models.CharField(max_length=128, blank=True)
    raw_response = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Stage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='stages')
    position = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['plan', 'position'], name='unique_stage_position'),
        ]


class Task(models.Model):
    class Priority(models.TextChoices):
        HIGH = 'high', 'High'
        MEDIUM = 'medium', 'Medium'
        LOW = 'low', 'Low'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name='tasks')
    position = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=16, choices=Priority, default=Priority.MEDIUM)
    estimated_minutes = models.PositiveIntegerField()
    depends_on = models.JSONField(default=list)
    due_date = models.DateField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['stage', 'position'], name='unique_task_position'),
        ]