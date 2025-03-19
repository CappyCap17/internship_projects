from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .serializers import UserSerializer
from django.contrib.auth import authenticate, login, logout
from .models import Assignment, Submission, CustomUser, Course
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CourseForm, AssignmentForm, SubmissionForm
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken

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
    assignments = Assignment.objects.filter(teacher=request.user)
    return render(request, 'teacher_dash.html', {'courses': courses, 'assignments': assignments})


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

class JWTLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        
        if not user:
            return Response({'error': 'Invalid credentials'}, status=401)

        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user_id': user.id,
            'role': user.role,
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        })

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(serializer.validated_data['password'])
            user.save()
            
            # Generate tokens for new user
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'status': 'registered',
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }, status=201)
        return Response(serializer.errors, status=400)

def logout_view(request):
    logout(request)
    return redirect('login')

def html_login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        
        if user:
            login(request, user)  # Log user in for session-based views
            if user.role == 'S':
                return redirect('student-dash')
            elif user.role == 'T':
                return redirect('teacher-dash')
            elif user.role == 'P':
                return redirect('principal-dash')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration.html', {'form': form})


@login_required
@user_passes_test(teacher_check)
def set_assignment(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.course = course
            assignment.teacher = request.user
            assignment.save()
            return redirect('teacher-dash')
    else:
        form = AssignmentForm()
    return render(request, 'set_assignment.html', {'form': form, 'course': course})

@login_required
@user_passes_test(teacher_check)
def view_submissions(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    submissions = Submission.objects.filter(assignment=assignment)
    return render(request, 'view_submissions.html', {'submissions': submissions})

@login_required
@user_passes_test(student_check)
def view_assignments(request):
    courses = request.user.enrolled_courses.all()
    print("Enrolled Courses:", courses)
    
    assignments = Assignment.objects.filter(course__in=courses)
    print("Assignments:", assignments)
    
    return render(request, 'view_assignments.html', {'assignments': assignments})


@login_required
@user_passes_test(student_check)
def submit_assignment(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    if request.method == 'POST':
        form = SubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = request.user
            submission.save()
            return redirect('student-dash')
    else:
        form = SubmissionForm()
    return render(request, 'submit_assignment.html', {'form': form, 'assignment': assignment})

# API Views

from .serializers import AssignmentSerializer, SubmissionSerializer

class AssignmentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        assignments = Assignment.objects.filter(teacher=request.user)
        serializer = AssignmentSerializer(assignments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AssignmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(teacher=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class SubmissionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        assignment = get_object_or_404(Assignment, pk=pk)
        submissions = Submission.objects.filter(assignment=assignment)
        serializer = SubmissionSerializer(submissions, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        assignment = get_object_or_404(Assignment, pk=pk)
        serializer = SubmissionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(assignment=assignment, student=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)