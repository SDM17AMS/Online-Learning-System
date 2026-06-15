from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Student, Instructor, Employee


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'student':
            Student.objects.create(user=instance)
        elif instance.role == 'instructor':
            Instructor.objects.create(user=instance)
        elif instance.role == 'employee':
            Employee.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if instance.role == 'student' and hasattr(instance, 'student'):
        instance.student.save()
    elif instance.role == 'instructor' and hasattr(instance, 'instructor'):
        instance.instructor.save()
    elif instance.role == 'employee' and hasattr(instance, 'employee'):
        instance.employee.save()