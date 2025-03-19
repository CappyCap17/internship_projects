from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLES = (
        ('S', 'Student'),
        ('T', 'Teacher'),
        ('P', 'Principal')
    )
    role = models.CharField(max_length=1, choices=ROLES, default='S')
    unique_id = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return f"{self.get_role_display()}: {self.username}"

class Course(models.Model):
    course_id = models.CharField(max_length=20, unique=True)
    course_name = models.CharField(max_length=100)
    
    teacher = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True,
        limit_choices_to={'role': 'T'}
    )
    
    students = models.ManyToManyField(
        CustomUser, 
        related_name='enrolled_courses', 
        limit_choices_to={'role': 'S'}
    )
    
    principal = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='managed_courses',
        limit_choices_to={'role': 'P'}
    )

    def __str__(self):
        return self.course_name

class Assignment(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    answer = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username}'s Submission for {self.assignment.title}"