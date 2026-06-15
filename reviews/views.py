from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import Review
from .forms import ReviewForm


@login_required
def add_review(request, course_slug):
    from courses.models import Course
    from enrollments.models import Enrollment
    
    course = get_object_or_404(Course, slug=course_slug)
    
    # Only enrolled students can review
    if not request.user.is_student:
        messages.error(request, "Only students can leave reviews.")
        return redirect('courses:course_detail', slug=course_slug)
    
    enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
    if not enrollment:
        messages.error(request, "You must be enrolled in this course to review it.")
        return redirect('courses:course_detail', slug=course_slug)
    
    # Check if already reviewed
    existing = Review.objects.filter(student=request.user, course=course).first()
    if existing:
        messages.info(request, "You have already reviewed this course. You can edit your existing review.")
        return redirect('reviews:edit_review', review_id=existing.pk)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.student = request.user
            review.course = course
            review.save()
            messages.success(request, "Review submitted successfully!")
            return redirect('courses:course_detail', slug=course_slug)
    else:
        form = ReviewForm()
    
    return render(request, 'reviews/review_form.html', {
        'form': form,
        'course': course,
    })


@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    
    # Only the student who wrote it can edit
    if review.student != request.user and not request.user.is_employee:
        raise PermissionDenied
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Review updated!")
            return redirect('courses:course_detail', slug=review.course.slug)
    else:
        form = ReviewForm(instance=review)
    
    return render(request, 'reviews/review_form.html', {
        'form': form,
        'course': review.course,
        'review': review,
    })


@login_required
def course_reviews(request, course_slug):
    from courses.models import Course
    
    course = get_object_or_404(Course, slug=course_slug)
    
    # Employees see all reviews including pending
    if request.user.is_employee:
        reviews = course.reviews.all().order_by('-created_at')
    else:
        reviews = course.reviews.filter(is_approved=True).order_by('-created_at')
    
    return render(request, 'reviews/course_reviews.html', {
        'course': course,
        'reviews': reviews,
    })


@login_required
def moderate_reviews(request):
    if not request.user.is_employee:
        raise PermissionDenied
    
    pending = Review.objects.filter(is_approved=False).select_related('student', 'course').order_by('-created_at')
    all_reviews = Review.objects.filter(is_approved=True).select_related('student', 'course').order_by('-created_at')[:50]
    
    return render(request, 'reviews/moderate.html', {
        'pending_reviews': pending,
        'recent_reviews': all_reviews,
    })


@login_required
def approve_review(request, review_id):
    if not request.user.is_employee:
        raise PermissionDenied
    
    review = get_object_or_404(Review, pk=review_id)
    review.is_approved = True
    review.save()
    messages.success(request, "Review approved!")
    return redirect('reviews:moderate')


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    
    # Only employee or the student who wrote it
    if review.student != request.user and not request.user.is_employee:
        raise PermissionDenied
    
    course_slug = review.course.slug
    review.delete()
    messages.success(request, "Review deleted.")
    return redirect('courses:course_detail', slug=course_slug)