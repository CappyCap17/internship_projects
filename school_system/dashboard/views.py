from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CustomUser, Course
from .serializers import UserSerializer
from .forms import UserRegistrationForm, CourseForm
from django.contrib.auth.views import LoginView

# ======================
# Authentication Views
# ======================

class CustomLoginView(LoginView):
    template_name = 'login.html'

    def get_success_url(self):
        user = self.request.user
        if user.role == 'S':
            return reverse('student-dash')
        elif user.role == 'T':
            return reverse('teacher-dash')
        elif user.role == 'P':
            return reverse('principal-dash')
        return super().get_success_url()

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(serializer.validated_data['password'])
            user.save()
            return Response({'status': 'registered'}, status=201)
        return Response(serializer.errors, status=400)

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('login')  # Redirect to login after registration
    else:
        form = UserRegistrationForm()
    return render(request, 'registration.html', {'form': form})

class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return redirect('login')

# ======================
# Role Checks
# ======================

def principal_check(user):
    return user.role == 'P'

def student_check(user):
    return user.role == 'S'

def teacher_check(user):
    return user.role == 'T'

# ======================
# Dashboard Views
# ======================

@login_required
@user_passes_test(principal_check)
def principal_dashboard(request):
    courses = Course.objects.filter(principal=request.user)
    return render(request, 'principal_dash.html', {'courses': courses})

@login_required
@user_passes_test(student_check)
def student_dashboard(request):
    courses = request.user.enrolled_courses.all()
    return render(request, 'student_dash.html', {'courses': courses})

@login_required
@user_passes_test(teacher_check)
def teacher_dashboard(request):
    courses = Course.objects.filter(teacher=request.user)
    return render(request, 'teacher_dash.html', {'courses': courses})

# ======================
# Course Management
# ======================

@login_required
@user_passes_test(principal_check)
def create_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.principal = request.user
            course.save()
            form.save_m2m()
            return redirect('principal-dash')
    else:
        form = CourseForm()
    return render(request, 'create_course.html', {'form': form})

@login_required
@user_passes_test(principal_check)
def edit_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            updated_course = form.save(commit=False)
            updated_course.principal = request.user
            updated_course.save()
            form.save_m2m()
            return redirect('principal-dash')
    else:
        form = CourseForm(instance=course)
    return render(request, 'edit_course.html', {'form': form})
