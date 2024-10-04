from django.contrib import admin
from django.urls import path
from . import views
from django.contrib import admin
from django.urls import path, include



urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('base',views.base,name="base"),

    path('admin_base/', views.admin_base, name='admin_base'),
    path('student_base/', views.student_base, name='student_base'),
    path('faculty_base/', views.faculty_base, name='faculty_base'),

    path('upload/', views.upload_files, name='upload_students'),
    path('students/', views.student_list, name='student_list'),
    path('students/edit/<int:pk>/', views.edit_student, name='edit_student'),
    path('students/delete/<int:pk>/', views.delete_student, name='delete_student'),
    path('search/', views.search_student, name='search_student'),
    path('pic-master/', views.pic_master_view, name='pic_master'),
    path('download_csv/', views.download_csv, name='download_csv'),
    path('student_card/', views.student_card, name='student_card'),
    path('search_faculty/', views.search_faculty, name='search_faculty'),
    path('on_duty/', views.on_duty, name='on_duty'),
    path('search_on_duty/', views.search_on_duty, name='search_on_duty'),
    path('robotics-lab/', views.robotics_lab, name='robotics_lab'),
]