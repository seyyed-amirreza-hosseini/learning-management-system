from .models import UserActivityLog


def log_user_activity(user, action, course=None, quiz=None, details=None):
    """
    Logs a user activity with optional course and additional.
    """
    UserActivityLog.objects.create(
        user=user,
        action=action,
        course=course,
        quiz=quiz,
        details=details
    )
    