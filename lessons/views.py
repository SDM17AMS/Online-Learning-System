from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from .models import Lesson
from .forms import LessonForm
from courses.models import Course
from enrollments.models import Enrollment, LessonProgress


class InstructorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (user.is_instructor or user.is_employee)


class LessonDetailView(LoginRequiredMixin, DetailView):
    model = Lesson
    template_name = 'lessons/lesson_detail.html'
    context_object_name = 'lesson'
    pk_url_kwarg = 'pk'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = self.get_object()
        context['course'] = lesson.course
        
        if self.request.user.is_student:
            try:
                enrollment = Enrollment.objects.get(student=self.request.user, course=lesson.course)
                context['is_enrolled'] = True
                context['enrollment'] = enrollment
                context['progress'], created = LessonProgress.objects.get_or_create(
                    enrollment=enrollment,
                    lesson=lesson
                )
            except Enrollment.DoesNotExist:
                context['is_enrolled'] = False
        return context


class LessonCreateView(LoginRequiredMixin, InstructorRequiredMixin, CreateView):
    model = Lesson
    form_class = LessonForm
    template_name = 'lessons/lesson_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, pk=self.kwargs['course_id'])
        if self.course.instructor != request.user and not request.user.is_employee:
            return redirect('courses:course_detail', slug=self.course.slug)
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.course = self.course
        if form.instance.order == 0:
            last_lesson = Lesson.objects.filter(course=self.course).order_by('order').last()
            form.instance.order = (last_lesson.order + 1) if last_lesson else 1
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('courses:course_detail', kwargs={'slug': self.course.slug})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.course
        return context


class LessonUpdateView(LoginRequiredMixin, InstructorRequiredMixin, UpdateView):
    model = Lesson
    form_class = LessonForm
    template_name = 'lessons/lesson_form.html'
    pk_url_kwarg = 'pk'
    
    def get_queryset(self):
        if self.request.user.is_employee:
            return Lesson.objects.all()
        return Lesson.objects.filter(course__instructor=self.request.user)
    
    def get_success_url(self):
        return reverse('courses:course_detail', kwargs={'slug': self.object.course.slug})


class LessonDeleteView(LoginRequiredMixin, InstructorRequiredMixin, DeleteView):
    model = Lesson
    template_name = 'lessons/lesson_confirm_delete.html'
    pk_url_kwarg = 'pk'
    
    def get_queryset(self):
        if self.request.user.is_employee:
            return Lesson.objects.all()
        return Lesson.objects.filter(course__instructor=self.request.user)
    
    def get_success_url(self):
        return reverse('courses:course_detail', kwargs={'slug': self.object.course.slug})


@login_required
def mark_lesson_complete(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    
    if not request.user.is_student:
        return redirect('lessons:lesson_detail', pk=pk)
    
    enrollment = get_object_or_404(Enrollment, student=request.user, course=lesson.course)
    progress, created = LessonProgress.objects.get_or_create(enrollment=enrollment, lesson=lesson)
    progress.is_completed = True
    progress.completed_at = timezone.now()
    progress.save()
    
    total_lessons = lesson.course.lessons.count()
    completed = LessonProgress.objects.filter(enrollment=enrollment, is_completed=True).count()
    enrollment.progress = int((completed / total_lessons) * 100) if total_lessons > 0 else 0
    if enrollment.progress >= 100:
        enrollment.status = 'completed'
    enrollment.save()
    
    messages.success(request, f'Lesson "{lesson.title}" marked as complete!')
    return redirect('lessons:lesson_detail', pk=pk)
