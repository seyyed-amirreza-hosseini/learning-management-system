# Generated by Django 5.1.2 on 2024-10-28 15:48

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_quizattempt_useractivitylog_usercourseprogress_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Atendee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Meeting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic', models.CharField(max_length=255)),
                ('start_time', models.DateTimeField()),
                ('meeting_id', models.CharField(max_length=255, unique=True)),
                ('meeting_link', models.URLField()),
            ],
        ),
        migrations.AddConstraint(
            model_name='usercourseprogress',
            constraint=models.UniqueConstraint(fields=('user', 'course'), name='unique_user_course_progress'),
        ),
        migrations.AddField(
            model_name='atendee',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='meeting',
            name='host',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meetings', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='atendee',
            name='meeting',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='attendees', to='courses.meeting'),
        ),
    ]
