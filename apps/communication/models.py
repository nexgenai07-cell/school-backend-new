from apps.common.models import BaseModel
from django.db import models


class Message(BaseModel):
    sender = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        db_table = 'messages'

    def __str__(self):
        return f"{self.sender} -> {self.receiver}"


class Notification(BaseModel):
    TYPE_CHOICES = [('sms', 'SMS'), ('email', 'Email'), ('push', 'Push')]

    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='notifications', help_text="Target user")
    title = models.CharField(max_length=200)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    is_read = models.BooleanField(default=False)

    class Meta:
        db_table = 'notifications'

    def __str__(self):
        return self.title


class NotificationLog(BaseModel):
    STATUS_CHOICES = [('sent', 'Sent'), ('delivered', 'Delivered'), ('read', 'Read'), ('failed', 'Failed')]

    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='logs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'notification_log'

    def __str__(self):
        return f"{self.notification} - {self.status}"
