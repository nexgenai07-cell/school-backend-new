from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone

from .models import ActivityLog, LoginLog


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    LoginLog.objects.create(
        user=user,
        login_time=timezone.now(),
        ip_address=request.META.get('REMOTE_ADDR'),
        device=request.META.get('HTTP_USER_AGENT', '')[:150],
        status='success',
    )


def log_model_activity(model_class, entity_name):
    @receiver(post_save, sender=model_class, weak=False)
    def _log(sender, instance, created, **kwargs):
        user = getattr(instance, 'created_by', None) or getattr(instance, 'user', None)
        if user is None:
            return
        ActivityLog.objects.create(
            user=user if hasattr(user, 'id') else None,
            action='create' if created else 'update',
            entity_type=entity_name,
            entity_id=instance.id,
        )
    return _log