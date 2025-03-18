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
