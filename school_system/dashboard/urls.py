from django.urls import path, include, re_path
from .views import (
    html_login_view,
    logout_view,
    principal_dashboard,
    student_dashboard,
    teacher_dashboard,
    create_course,
    edit_course,
    enroll_course,
    register_view,
    RegisterView,
    JWTLoginView,
    set_assignment,
    view_submissions,
    view_assignments,
    submit_assignment,
    AssignmentView, 
    SubmissionView
)

urlpatterns = [
    path('login/', html_login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('api/logout/', logout_view, name='api-logout'),
    path('principal/', principal_dashboard, name='principal-dash'),
    path('student/', student_dashboard, name='student-dash'),
    path('teacher/', teacher_dashboard, name='teacher-dash'),
    path('course/new/', create_course, name='create-course'),
    path('course/<int:pk>/edit/', edit_course, name='edit-course'),
    path('course/<int:pk>/enroll/', enroll_course, name='enroll-course'),
    path('register/', register_view, name='register'),
    path('api/register/', RegisterView.as_view(), name='api-register'),
    path('api/login/', JWTLoginView.as_view(), name='api-login'),
    path('course/<int:pk>/set-assignment/', set_assignment, name='set-assignment'),
    path('assignment/<int:pk>/view-submissions/', view_submissions, name='view-submissions'),
    path('student/assignments/', view_assignments, name='view-assignments'),
    path('assignment/<int:pk>/submit/', submit_assignment, name='submit-assignment'),
    path('api/assignments/', AssignmentView.as_view(), name='api-assignments'),
    path('api/assignments/<int:pk>/submissions/', SubmissionView.as_view(), name='api-submissions'),
    re_path(r'^$', html_login_view, name='home'),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)



