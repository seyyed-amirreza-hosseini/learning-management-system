from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Avg
from celery import shared_task
from courses.models import UserCourseProgress


@shared_task
def send_assignment_reminder_email(subject, message, recipient_list):
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=False,
    )

@shared_task
def send_weekly_course_report():
    average_progress = UserCourseProgress.objects.aggregate(avg_progress=Avg('progress_percentage'))
    report = f"Average course completion rate: {average_progress['avg_progress']:.2f}%"

    send_mail('Weekly Course Report', report, 'admin@lms.com', ['students@lms.com'])
