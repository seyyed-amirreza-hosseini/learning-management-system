from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator, MaxLengthValidator, FileExtensionValidator


class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student')
    major = models.CharField(max_length=100, blank=True)
    
    @property
    def enrollment_date(self):
        return self.user.date_joined
    
    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'


class Teacher(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    department = models.CharField(max_length=255, blank=True)

    @property
    def hire_date(self):
        return self.user.date_joined

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'


class Course(models.Model):
    class Level(models.TextChoices):
        BEGINNER = 'BE', _('Beginner')
        INTERMEDIATE = 'IN', _('Intermediate')
        ADVANCED = 'AD', _('Advanced')

    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=255)
    level = models.CharField(max_length=2, choices=Level, default=Level.BEGINNER)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    instructors = models.ManyToManyField(Teacher, through='InstructorCourse')

    def __str__(self):
        return self.name
    

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    comment = models.TextField()
    rating = models.PositiveSmallIntegerField(
        default=1, 
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review: {self.pk} by {self.user.email} for {self.course.name} course"
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'course'], name='unique_user_course')
        ]


# Intermediate Table
class InstructorCourse(models.Model):
    class Role(models.TextChoices):
        TEACHER = 'TE', _('Teacher')
        ASSISTANT = "AS", _('Assistant')
        COORDINATOR = 'CO', _('Coordinator')

    course = models.ForeignKey(Course, on_delete=models.CASCADE) 
    instructor = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    assigned_date = models.DateField()
    role = models.CharField(max_length=15, choices=Role)


class Module(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    order = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Lesson(models.Model):
    class ContentType(models.TextChoices):
        VIDEO = 'video', _('Video')
        ARTICLE = 'article', _('Article/Text')
        QUIZ = 'quiz', _('Quiz')
        ASSIGNMENT = 'assignment', _('Assignment')
        PRESENTATION = 'presentation', _('Presentation')
        IMAGE = 'image', _('Image')
        AUDIO = 'audio', _('Audio')
        LIVE_SESSION = 'live_session', _('Live Session')
        PDF = 'pdf', _('PDF')

    name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=20, choices=ContentType)
    content = models.TextField()
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    order = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    duration = models.DurationField(null=True, blank=True)
    is_published = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resources = models.FileField(upload_to='lesson_resources', null=True, blank=True)

    def __str__(self):
        return self.name


class VideoLecture(models.Model):
    lesson = models.ForeignKey(Lesson, related_name='video_lectures', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    video_url = models.URLField()  # URL for the video (YouTube, Vimeo, etc.)
    description = models.TextField(blank=True, null=True)
    duration = models.DurationField(blank=True, null=True)  # Duration of the video

    def __str__(self):
        return self.title


class Quiz(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    passing_score = models.IntegerField(default=50)

    def __str__(self):
        return self.title
    
    def get_correct_answers(self):
        """
        Returns a dictionary of correct answers for each question in the quiz.
        Example format: {question_id: correct_option_id}
        """
        correct_answers = {}
        for question in self.questions.all():
            correct_choice = question.choices.filter(is_correct=True).first()
            if correct_choice:
                correct_answers[question.id] = correct_choice.id

        return correct_answers
    

class UserActivityLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.action} at {self.timestamp}"


class UserCourseProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    progress_percentage = models.FloatField(default=0)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'course'], name='unique_user_course_progress')
        ]


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()

    def __str__(self):
        return self.text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class QuizAttempt(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    attempt_time = models.DateTimeField(auto_now=True)
    

class Assignment(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateTimeField()
    max_score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxLengthValidator(20)],
        default=0
    )
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='assignments')

    def __str__(self):
        return f'{self.name}: {self.lesson.module.course.name} - {self.lesson.module.name} - {self.lesson.name}'


class Enrollment(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', _('Active')
        COMPLETED = 'completed', _('Completed')
        DROPPED = 'dropped', _('Dropped')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateField(auto_now_add=True)
    progress = models.FloatField(default=0.0)
    status = models.CharField(max_length=10, choices=Status, default=Status.ACTIVE)
    grade = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)
    completion_date = models.DateField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['course', 'student'], name='unique_course_student')
        ]


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    feedback = models.TextField(blank=True)
    file = models.FileField(
        upload_to='submissions/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'rar'])]            
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['assignment', 'student'], name='unique_assignment_student')
        ]


class Forum(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='forums')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='forums')

    def __str__(self):
        return self.title


class Post(models.Model):
    title = models.CharField(max_length=255)
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE, related_name='posts')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}'s post in {self.forum.title}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}'s comment in {self.post.title}"
    

class Meeting(models.Model):
    host = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='meetings')
    topic = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    meeting_link = models.URLField()


class Atendee(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.PROTECT, related_name='attendees')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True) 
