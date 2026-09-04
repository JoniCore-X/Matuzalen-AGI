from django.db import models


class ChatMessage(models.Model):
    user_id = models.CharField(max_length=128, db_index=True)
    role = models.CharField(max_length=20)  # 'user' o 'agent'
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.role}:{self.user_id}:{self.created_at}"
