from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Avg
from django.contrib import messages
from .models import Course, Category, Tag
from .forms import CourseForm


class CourseListView(ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 9
    
    def get_queryset(self):
        queryset = Course.objects.filter(is_published=True)
        if category := self.request.GET.get('category'):
            queryset = queryset.filter(category__slug=category)
        if tag := self.request.GET.get('tag'):
            queryset = queryset.filter(tags__slug=tag)
        if instructor := self.request.GET.get('instructor'):
            queryset = queryset.filter(instructor__username=instructor)
        if q := self.request.GET.get('q'):
            queryset = queryset.filter(Q(title__icontains=q) | Q(description__icontains=q))
        return queryset.select_related('instructor', 'category').prefetch_related('tags')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['tags'] = Tag.objects.all()
        context['instructors'] = Course.objects.filter(is_published=True).values_list('instructor__username', flat=True).distinct()
        context['search_query'] = self.request.GET.get('q', '')
        return context


class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    slug_url_kwarg = 'slug'
    context_object_name = 'course'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        context['lessons'] = course.lessons.all()
        context['is_enrolled'] = False
        context['avg_rating'] = course.reviews.filter(is_approved=True).aggregate(avg=Avg('rating'))['avg']
        context['review_count'] = course.reviews.filter(is_approved=True).count()
        if self.request.user.is_authenticated and self.request.user.is_student:
            context['is_enrolled'] = course.enrollments.filter(student=self.request.user).exists()
        return context


class InstructorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_instructor


class CourseCreateView(LoginRequiredMixin, InstructorRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    success_url = '/dashboard/instructor/'
    
    def form_valid(self, form):
        form.instance.instructor = self.request.user
        messages.success(self.request, 'Course created successfully!')
        return super().form_valid(form)


class CourseUpdateView(LoginRequiredMixin, InstructorRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    slug_url_kwarg = 'slug'
    success_url = '/dashboard/instructor/'
    
    def get_queryset(self):
        return Course.objects.filter(instructor=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Course updated successfully!')
        return super().form_valid(form)


class CourseDeleteView(LoginRequiredMixin, InstructorRequiredMixin, DeleteView):
    model = Course
    template_name = 'courses/course_confirm_delete.html'
    slug_url_kwarg = 'slug'
    success_url = '/dashboard/instructor/'
    
    def get_queryset(self):
        return Course.objects.filter(instructor=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Course deleted successfully.')
        return super().delete(request, *args, **kwargs)


@login_required
def enroll_course(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    if not request.user.is_student:
        messages.error(request, "Only students can enroll in courses.")
        return redirect('courses:course_detail', slug=slug)
    from enrollments.models import Enrollment
    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user, course=course, defaults={'status': 'active'}
    )
    if created:
        messages.success(request, f'You have enrolled in {course.title}!')
    else:
        messages.info(request, f'You are already enrolled in {course.title}.')
    return redirect('dashboard:student')