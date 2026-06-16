## Setup Commands

```bash

# 1. virtual environment for window
python -m venv venv
python -m venv env

#Linux or Mac
python3 -m venv venv
python3 -m venv env

# 2.Virutual Environment Activation
## Window
venv/scripts/activate
env/scripts/activate

##linux or max
soruce venv/bin/activate
source env/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run database migrations
python manage.py migrate

# 5. Create demo users and sample data
python manage.py create_demo_data

# 6. Start development server
python manage.py runserver

Demo Credentials
Student
Username: student
Password: demo12345
Instructor
Username: instructor
Password: demo12345
Employee
Username: employee
Password: demo12345

| Feature        | Description                                                           |
| -------------- | --------------------------------------------------------------------- |
| Authentication | Custom User model with role field (student/instructor/employee)       |
| Courses        | Browse, filter by category/tag/instructor, create, edit, delete       |
| Lessons        | Video (YouTube embed with auto-URL cleaning), PDF uploads, sequencing |
| Enrollments    | Students enroll, track lesson completion progress                     |
| Assignments    | Instructors create, students submit file/code/text, instructors grade |
| Reviews        | Students rate/review enrolled courses, employees moderate             |
| Dashboards     | Role-specific dashboards with stats and management links              |
| Admin          | All models registered in Django admin for employee management         |


| URL                   | Page                             |
| --------------------- | -------------------------------- |
| `/`                   | Browse courses                   |
| `/accounts/login/`    | Login                            |
| `/accounts/register/` | Register                         |
| `/dashboard/`         | Role-specific dashboard redirect |
| `/admin/`             | Django admin panel               |

OLS/
├── accounts/       # Custom User, Student, Instructor, Employee
├── courses/        # Category, Tag, Course
├── lessons/        # Lesson, video/PDF content
├── enrollments/    # Enrollment, LessonProgress
├── assignments/    # Assignment, Submission
├── reviews/        # Review
└── dashboard/      # Role-based dashboards

##Link embeed Still need to ask teacher