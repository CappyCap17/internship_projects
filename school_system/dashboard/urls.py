from django.urls import path
from . import views

urlpatterns = [
     path('register/', views.register_view, name='register'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('principal/', views.principal_dashboard, name='principal-dash'),
    path('course/new/', views.create_course, name='create-course'),
    path('course/<int:pk>/edit/', views.edit_course, name='edit-course'),
    path('', views.principal_dashboard, name='dashboard-home'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('register/', views.register_view, name='register'),
    path('student/', views.student_dashboard, name='student-dash'),
    path('teacher/', views.teacher_dashboard, name='teacher-dash'),
    
]


