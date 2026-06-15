from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

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


@method_decorator(login_required, name='dispatch')
class InstructorDashboardView(TemplateView):
    template_name = 'dashboard/instructor_dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_instructor:
            return redirect('dashboard:redirect')
        return super().dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class EmployeeDashboardView(TemplateView):
    template_name = 'dashboard/employee_dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_employee:
            return redirect('dashboard:redirect')
        return super().dispatch(request, *args, **kwargs)