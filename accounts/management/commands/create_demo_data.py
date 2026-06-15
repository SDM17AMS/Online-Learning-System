from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from courses.models import Category, Tag, Course
from lessons.models import Lesson
from enrollments.models import Enrollment

User = get_user_model()


class Command(BaseCommand):
    help = 'Create demo users and sample data'

    def handle(self, *args, **kwargs):
        # Categories
        cat_prog, _ = Category.objects.get_or_create(name='Programming', slug='programming')
        cat_design, _ = Category.objects.get_or_create(name='Design', slug='design')
        
        # Tags
        tag_python, _ = Tag.objects.get_or_create(name='Python', slug='python')
        tag_web, _ = Tag.objects.get_or_create(name='Web Development', slug='web-development')
        tag_beginner, _ = Tag.objects.get_or_create(name='Beginner', slug='beginner')
        
        # Student
        if not User.objects.filter(username='student').exists():
            student = User.objects.create_user(
                username='student',
                email='student@example.com',
                password='demo12345',
                role='student'
            )
            self.stdout.write(self.style.SUCCESS(f'Created student: {student.username}'))
        
        # Instructor
        if not User.objects.filter(username='instructor').exists():
            instructor = User.objects.create_user(
                username='instructor',
                email='instructor@example.com',
                password='demo12345',
                role='instructor'
            )
            self.stdout.write(self.style.SUCCESS(f'Created instructor: {instructor.username}'))
        
        # Employee
        if not User.objects.filter(username='employee').exists():
            employee = User.objects.create_superuser(
                username='employee',
                email='employee@example.com',
                password='demo12345',
                role='employee'
            )
            self.stdout.write(self.style.SUCCESS(f'Created employee: {employee.username}'))
        
        # Sample course
        instructor_user = User.objects.get(username='instructor')
        if not Course.objects.filter(slug='python-for-beginners').exists():
            course = Course.objects.create(
                instructor=instructor_user,
                category=cat_prog,
                title='Python for Beginners',
                slug='python-for-beginners',
                description='Learn Python from scratch.',
                price=29.99,
                is_published=True
            )
            course.tags.add(tag_python, tag_beginner)
            
            Lesson.objects.create(course=course, title='Introduction to Python', order=1, duration=15, description='What is Python?')
            Lesson.objects.create(course=course, title='Variables and Data Types', order=2, duration=20, description='Understanding variables.')
            Lesson.objects.create(course=course, title='Control Flow', order=3, duration=25, description='If statements and loops.')
            
            self.stdout.write(self.style.SUCCESS(f'Created course: {course.title}'))
        
        # Enroll student
        student_user = User.objects.get(username='student')
        course = Course.objects.get(slug='python-for-beginners')
        Enrollment.objects.get_or_create(student=student_user, course=course, defaults={'status': 'active'})
        
        self.stdout.write(self.style.SUCCESS('Demo data ready!'))
