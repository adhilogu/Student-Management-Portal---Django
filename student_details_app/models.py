from datetime import datetime, timedelta

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
import numpy as np
from django.contrib.auth.models import AbstractUser, Group, Permission



class Student(models.Model):
    DoesNotExist = None
    objects = None
    roll_no = models.CharField(max_length=20)
    student_name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15)
    student_email = models.EmailField()
    year = models.CharField(max_length=10)
    department = models.CharField(max_length=100)
    faculty_incharge = models.CharField(max_length=100)
    faculty_id = models.CharField(max_length=20)
    lab_name = models.CharField(max_length=100)
    nip_status = models.CharField(max_length=100)

    def __str__(self):
        return self.student_name



class Faculty(models.Model):
    objects = None
    lab_name = models.CharField(max_length=100)
    lab_code = models.CharField(max_length=50)
    faculty_incharges = models.CharField(max_length=100)
    fi = models.CharField(max_length=100)  # Assuming 'fi' is a field you want to include
    faculty_id = models.CharField(max_length=50)
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    email = models.EmailField()
    contact_no = models.CharField(max_length=15)

    def __str__(self):
        return self.faculty_incharges

class PicMaster(models.Model):
    objects = None
    lab_name = models.CharField(max_length=100)
    lab_count = models.IntegerField()
    year_1 = models.IntegerField(default=0)
    year_2 = models.IntegerField(default=0)
    year_3 = models.IntegerField(default=0)
    year_4 = models.IntegerField(default=0)

    def __str__(self):
        return self.lab_name



class OnDutyApplication(models.Model):
    objects = None
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    lab_name = models.CharField(max_length=100)
    from_date = models.DateField()
    to_date = models.DateField()
    applied_date = models.DateField(default=datetime.now)
    purpose = models.TextField(blank=True)  # New field for purpose

    def __str__(self):
        return f"{self.student.student_name} - {self.lab_name} - {self.applied_date}"
