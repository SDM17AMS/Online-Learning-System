from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Count
from django.contrib.auth import get_user_model

from courses.models import Course
from enrollments.models import Enrollment, LessonProgress
from assignments.models import Assignment, Submission
from reviews.models import Review

User = get_user_model()


@login_required
def dashboard_redirect(request):
    if request.user.is_student:
        return redirect('dashboard:student')
    elif request.user.is_instructor:
        return redirect('dashboard:instructor')
    elif request.user.is_employee:
        return redirect('dashboard:employee')
    return redirect('accounts:login')


@method_decorator(login_required, name='dispatch')
class StudentDashboardView(TemplateView):
    template_name = 'dashboard/student_dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_student:
            return redirect('dashboard:redirect')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user
        
        context['enrollments'] = Enrollment.objects.filter(
            student=student
        ).select_related('course').order_by('-enrolled_at')
        
        context['total_lessons_completed'] = LessonProgress.objects.filter(
            enrollment__student=student, is_completed=True
        ).count()
        
        enrolled_course_ids = Enrollment.objects.filter(
            student=student
        ).values_list('course_id', flat=True)
        
        context['upcoming_assignments'] = Assignment.objects.filter(
            lesson__course_id__in=enrolled_course_ids
        ).select_related('lesson', 'lesson__course').order_by('due_date')[:5]
        
        context['graded_submissions'] = Submission.objects.filter(
            student=student, score__isnull=False
        ).select_related('assignment').order_by('-graded_at')[:5]
        
        context['my_reviews'] = Review.objects.filter(
            student=student
        ).select_related('course').order_by('-created_at')
        
        return context


@method_decorator(login_required, name='dispatch')
class InstructorDashboardView(TemplateView):
    template_name = 'dashboard/instructor_dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_instructor:
            return redirect('dashboard:redirect')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instructor = self.request.user
        
        context['my_courses'] = Course.objects.filter(
            instructor=instructor
        ).annotate(
            student_count=Count('enrollments')
        ).order_by('-created_at')
        
        context['total_students'] = Enrollment.objects.filter(
            course__instructor=instructor
        ).count()
        
        context['pending_submissions'] = Submission.objects.filter(
            assignment__lesson__course__instructor=instructor,
            score__isnull=True
        ).select_related('student', 'assignment').order_by('submitted_at')[:10]
        
        context['published_courses'] = Course.objects.filter(
            instructor=instructor, is_published=True
        ).count()
        
        context['draft_courses'] = Course.objects.filter(
            instructor=instructor, is_published=False
        ).count()
        
        return context


@method_decorator(login_required, name='dispatch')
class EmployeeDashboardView(TemplateView):
    template_name = 'dashboard/employee_dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_employee:
            return redirect('dashboard:redirect')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['total_users'] = User.objects.count()
        context['total_students'] = User.objects.filter(role='student').count()
        context['total_instructors'] = User.objects.filter(role='instructor').count()
        context['total_courses'] = Course.objects.count()
        context['published_courses'] = Course.objects.filter(is_published=True).count()
        context['total_enrollments'] = Enrollment.objects.count()
        context['total_reviews'] = Review.objects.count()
        context['pending_reviews'] = Review.objects.filter(is_approved=False).count()
        
        context['recent_enrollments'] = Enrollment.objects.select_related(
            'student', 'course'
        ).order_by('-enrolled_at')[:10]
        
        context['recent_reviews'] = Review.objects.select_related(
            'student', 'course'
        ).order_by('-created_at')[:5]
        
        context['admin_models'] = [
            {'name': 'Users', 'url': '/admin/accounts/user/'},
            {'name': 'Courses', 'url': '/admin/courses/course/'},
            {'name': 'Lessons', 'url': '/admin/lessons/lesson/'},
            {'name': 'Enrollments', 'url': '/admin/enrollments/enrollment/'},
            {'name': 'Assignments', 'url': '/admin/assignments/assignment/'},
            {'name': 'Submissions', 'url': '/admin/assignments/submission/'},
            {'name': 'Reviews', 'url': '/admin/reviews/review/'},
        ]
        
        return context
