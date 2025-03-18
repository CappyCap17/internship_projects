from django.urls import path, include, re_path
from .views import (
    APILoginView,
    html_login_view,
    logout_view,
    principal_dashboard,
    student_dashboard,
    teacher_dashboard,
    create_course,
    edit_course,
    enroll_course,
    register_view,
    RegisterView
)

urlpatterns = [
    path('login/', html_login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('api/login/', APILoginView.as_view(), name='api-login'),
    path('api/logout/', logout_view, name='api-logout'),
    path('principal/', principal_dashboard, name='principal-dash'),
    path('student/', student_dashboard, name='student-dash'),
    path('teacher/', teacher_dashboard, name='teacher-dash'),
    path('course/new/', create_course, name='create-course'),
    path('course/<int:pk>/edit/', edit_course, name='edit-course'),
    path('course/<int:pk>/enroll/', enroll_course, name='enroll-course'),
    path('register/', register_view, name='register'),
    path('api/register/', RegisterView.as_view(), name='api-register'),
    re_path(r'^$', html_login_view, name='home'),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
