from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .serializers import UserSerializer
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser, Course
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CourseForm
from django.shortcuts import get_object_or_404


def principal_check(user):
    return user.role == 'P'

def student_check(user):
    return user.role == 'S'

def teacher_check(user):
    return user.role == 'T'

@login_required
@user_passes_test(principal_check)
def principal_dashboard(request):
    courses = Course.objects.filter(principal=request.user)
    return render(request, 'principal_dash.html', {'courses': courses})

@login_required
@user_passes_test(student_check)
def student_dashboard(request):
    courses = request.user.enrolled_courses.all()
    all_courses = Course.objects.exclude(students=request.user)
    return render(request, 'student_dash.html', {
        'courses': courses,
        'all_courses': all_courses,
    })

@login_required
@user_passes_test(teacher_check)
def teacher_dashboard(request):
    courses = Course.objects.filter(teacher=request.user)
    return render(request, 'teacher_dash.html', {'courses': courses})

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
            form.save()
            return redirect('principal-dash')
    else:
        form = CourseForm(instance=course)
    return render(request, 'edit_course.html', {'form': form})

@login_required
@user_passes_test(student_check)
def enroll_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    
    if request.method == 'POST':
        course.students.add(request.user)
        courses = request.user.enrolled_courses.all()
        all_courses = Course.objects.exclude(students=request.user)
        return render(request, 'student_dash.html', {
            'courses': courses,
            'all_courses': all_courses,
        })
    
    return render(request, 'enroll_course.html', {'course': course})

class APILoginView(APIView):
    permission_classes = [permissions.AllowAny]  # Allow unauthenticated access
    
    def post(self, request):
        user = authenticate(
            username=request.data.get('username'),
            password=request.data.get('password')
        )
        
        if not user:
            return Response({'error': 'Invalid credentials'}, status=401)
            
        login(request, user)  # Creates session cookie
        return Response({
            'user_id': user.id,
            'role': user.role,
            'sessionid': request.session.session_key
        })

def logout_view(request):
    logout(request)
    return redirect('login')

def html_login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        
        if user:
            login(request, user)
            if user.role == 'S':
                return redirect('student-dash')
            elif user.role == 'T':
                return redirect('teacher-dash')
            elif user.role == 'P':
                return redirect('principal-dash')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(serializer.validated_data['password'])
            user.save()
            return Response({'status': 'registered'}, status=201)
        return Response(serializer.errors, status=400)

from django.shortcuts import redirect
from .forms import UserRegistrationForm

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
