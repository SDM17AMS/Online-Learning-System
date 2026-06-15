from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
from .models import Assignment, Submission
from .forms import AssignmentForm, SubmissionForm, GradeForm


class InstructorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (user.is_instructor or user.is_employee)


class AssignmentCreateView(LoginRequiredMixin, InstructorRequiredMixin, CreateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'assignments/assignment_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        from lessons.models import Lesson
        self.lesson = get_object_or_404(Lesson, pk=self.kwargs['lesson_id'])
        if self.lesson.course.instructor != request.user and not request.user.is_employee:
            return redirect('courses:course_detail', slug=self.lesson.course.slug)
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.lesson = self.lesson
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('courses:course_detail', kwargs={'slug': self.lesson.course.slug})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lesson'] = self.lesson
        return context


class AssignmentUpdateView(LoginRequiredMixin, InstructorRequiredMixin, UpdateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'assignments/assignment_form.html'
    pk_url_kwarg = 'pk'
    
    def get_queryset(self):
        if self.request.user.is_employee:
            return Assignment.objects.all()
        return Assignment.objects.filter(lesson__course__instructor=self.request.user)
    
    def get_success_url(self):
        return reverse('courses:course_detail', kwargs={'slug': self.object.lesson.course.slug})


@login_required
def submit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    
    if not request.user.is_student:
        messages.error(request, "Only students can submit assignments.")
        return redirect('lessons:lesson_detail', pk=assignment.lesson.pk)
    
    existing = Submission.objects.filter(assignment=assignment, student=request.user).first()
    if existing:
        messages.info(request, "You have already submitted this assignment.")
        return redirect('assignments:my_submissions')
    
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = request.user
            submission.save()
            messages.success(request, "Assignment submitted successfully!")
            return redirect('dashboard:student')
    else:
        form = SubmissionForm()
    
    return render(request, 'assignments/submission_form.html', {
        'form': form,
        'assignment': assignment,
    })


@login_required
def my_submissions(request):
    submissions = Submission.objects.filter(student=request.user).select_related(
        'assignment', 'assignment__lesson__course'
    ).order_by('-submitted_at')
    
    return render(request, 'assignments/my_submissions.html', {
        'submissions': submissions,
    })


@login_required
def grade_submissions(request):
    if not (request.user.is_instructor or request.user.is_employee):
        return redirect('dashboard:redirect')
    
    if request.user.is_employee:
        submissions = Submission.objects.filter(score__isnull=True)
    else:
        submissions = Submission.objects.filter(
            assignment__lesson__course__instructor=request.user,
            score__isnull=True
        )
    
    submissions = submissions.select_related('student', 'assignment', 'assignment__lesson__course')
    
    return render(request, 'assignments/grade_list.html', {
        'submissions': submissions,
    })


@login_required
def grade_submission(request, submission_id):
    if not (request.user.is_instructor or request.user.is_employee):
        return redirect('dashboard:redirect')
    
    submission = get_object_or_404(
        Submission.objects.select_related('assignment'),
        pk=submission_id
    )
    
    if request.user.is_instructor and submission.assignment.lesson.course.instructor != request.user:
        return redirect('dashboard:instructor')
    
    if request.method == 'POST':
        form = GradeForm(request.POST, instance=submission, max_score=submission.assignment.max_score)
        if form.is_valid():
            from django.utils import timezone
            submission = form.save(commit=False)
            submission.graded_at = timezone.now()
            submission.save()
            messages.success(request, f"Graded {submission.student.username}'s submission!")
            return redirect('assignments:grade_list')
    else:
        form = GradeForm(instance=submission, max_score=submission.assignment.max_score)
    
    return render(request, 'assignments/grade_form.html', {
        'form': form,
        'submission': submission,
    })
