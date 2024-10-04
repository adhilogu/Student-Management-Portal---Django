import csv
import json

import cv2
import numpy as np
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect

from .models import Faculty, OnDutyApplication
from .forms import OnDutyForm, OnDutySearchForm, LoginForm
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile

from datetime import timedelta, datetime
from .models import Student
from .models import PicMaster
from django.contrib.auth import logout
from .models import Faculty
from .forms import UploadCSVForm, SearchStudentForm, StudentForm
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count, Q, Sum
from django.http import HttpResponse
from .forms import StudentCardForm
import base64


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('pic_master')
            else:
                form.add_error(None, "Invalid username or password")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

@login_required
def base(request):
    return render(request, 'base.html')

def home(request):
    #students = Student.objects.all()
    return render(request, 'pic_master.html')

def logout_view(request):
    logout(request)
    return redirect('login')


def upload_files(request):
    if request.method == 'POST':
        # Check and process Student CSV file
        if 'student_csv_file' in request.FILES:
            student_csv_file = request.FILES['student_csv_file']
            if not student_csv_file.name.endswith('.csv'):
                return render(request, 'upload_records.html', {'error': 'This is not a CSV file.'})

            file_data = student_csv_file.read().decode('utf-8')
            lines = file_data.split('\n')

            for line in lines:
                fields = line.split(',')
                if len(fields) < 11:
                    continue
                Student.objects.create(
                    roll_no=fields[1],
                    student_name=fields[2],
                    mobile_number=fields[3],
                    student_email=fields[4],
                    year=fields[5],
                    department=fields[6],
                    faculty_incharge=fields[7],
                    faculty_id=fields[8],
                    lab_name=fields[9],
                    nip_status=fields[10]
                )

        # Check and process Sheet Links CSV file
        if 'sheet_links_csv_file' in request.FILES:
            sheet_links_csv_file = request.FILES['sheet_links_csv_file']
            if not sheet_links_csv_file.name.endswith('.csv'):
                return render(request, 'upload_records.html', {'error': 'This is not a CSV file.'})



        # Check and process Faculty CSV file
        if 'student_csv_file' in request.FILES:
            student_csv_file = request.FILES['student_csv_file']
            if not student_csv_file.name.endswith('.csv'):
                return render(request, 'upload_records.html', {'error': 'This is not a CSV file.'})

            file_data = student_csv_file.read().decode('utf-8')
            csv_reader = csv.DictReader(StringIO(file_data))

            missing_fields = []
            for row in csv_reader:
                try:
                    Student.objects.create(
                        roll_no=row.get('roll_no'),
                        student_name=row.get('student_name'),
                        mobile_number=row.get('mobile_number'),
                        student_email=row.get('student_email'),
                        year=row.get('year'),
                        department=row.get('department'),
                        faculty_incharge=row.get('faculty_incharge'),
                        faculty_id=row.get('faculty_id'),
                        lab_name=row.get('lab_name'),
                        nip_status=row.get('nip_status')
                    )
                except Exception as e:
                    missing_fields.append(f"Error saving row: {row}. Error: {str(e)}")

            if missing_fields:
                return render(request, 'upload_records.html',
                              {'error': 'Some rows could not be processed.', 'details': missing_fields})

            return redirect('upload_students')

        if 'sheet_links_csv_file' in request.FILES:
            # Handle sheet links CSV upload here
            pass

        if 'faculty_csv_file' in request.FILES:
            # Handle faculty CSV upload here
            pass

        return redirect('upload_students')

    return render(request, 'upload_records.html')

def upload_students(request):
    if request.method == 'POST' and request.FILES['csv_file']:
        csv_file = request.FILES['csv_file']
        if not csv_file.name.endswith('.csv'):
            return render(request, 'home.html', {'error': 'This is not a CSV file.'})

        file_data = csv_file.read().decode('utf-8')
        lines = file_data.split('\n')

        # Clear existing student data (optional)
        #Student.objects.all().delete()

        for line in lines:
            fields = line.split(',')
            if len(fields) < 11:
                continue
            Student.objects.create(
                roll_no=fields[1],
                student_name=fields[2],
                mobile_number=fields[3],
                student_email=fields[4],
                year=fields[5],
                department=fields[6],
                faculty_incharge=fields[7],
                faculty_id=fields[8],
                lab_name=fields[9],
                nip_status=fields[10]
            )

        #return redirect('home')

    students = Student.objects.all()
    return render(request, 'upload_records.html', {'students': students})
def student_list(request):
    students = Student.objects.all()
    return render(request, 'student_list.html', {'students': students})

def edit_student(request, pk):
    student = Student.objects.get(pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student_list')
    else:
        form = StudentForm(instance=student)
    return render(request, 'edit_student.html', {'form': form})

def delete_student(request, pk):
    student = Student.objects.get(pk=pk)
    if request.method == 'POST':
        student.delete()
        return redirect('student_list')
    return render(request, 'delete_student.html', {'student': student})



def search_student(request):
    form = SearchStudentForm(request.GET or None)
    results = []
    missing_entries = []
    filter_value = request.GET.get('filter', '')
    search_term = request.GET.get('search', '')

    if form.is_valid():
        if filter_value and search_term:
            search_terms = [term.strip() for term in search_term.split(' ')]
            queries = Q()
            for term in search_terms:
                queries |= Q(**{f"{filter_value}__icontains": term})
            results = Student.objects.filter(queries).distinct()

            # Check for missing entries
            for term in search_terms:
                if not results.filter(**{f"{filter_value}__icontains": term}).exists():
                    missing_entries.append(term)

    context = {
        'form': form,
        'results': results,
        'filter': filter_value,
        'search': search_term,
        'missing_entries': missing_entries,
    }
    return render(request, 'search_student.html', context)

def search_faculty(request):
    form = SearchStudentForm(request.GET or None)
    results = []
    filter_value = request.GET.get('filter', '')
    search_term = request.GET.get('search', '')

    if form.is_valid():
        if filter_value and search_term:
            search_terms = [term.strip() for term in search_term.split(' ')]
            queries = Q()
            for term in search_terms:
                queries |= Q(**{f"{filter_value}__icontains": term})
            results = Faculty.objects.filter(queries).distinct()

    context = {
        'form': form,
        'results': results,
        'filter': filter_value,
        'search': search_term,
    }
    return render(request, 'search_faculty.html', context)

def update_pic_master():
    # Fetch all distinct lab names
    labs = Student.objects.values('lab_name').distinct()

    # Initialize or clear PicMaster table
    PicMaster.objects.all().delete()

    for lab in labs:
        lab_name = lab['lab_name']

        # Aggregate counts by year
        year_counts = Student.objects.filter(lab_name=lab_name).values('year').annotate(count=Count('id'))

        # Initialize or get the PicMaster entry
        pic_master_entry, created = PicMaster.objects.get_or_create(
            lab_name=lab_name,
            defaults={'lab_count': 0, 'year_1': 0, 'year_2': 0, 'year_3': 0, 'year_4': 0}
        )

        # Update lab count
        pic_master_entry.lab_count = Student.objects.filter(lab_name=lab_name).count()

        # Reset year counts
        pic_master_entry.year_1 = 0
        pic_master_entry.year_2 = 0
        pic_master_entry.year_3 = 0
        pic_master_entry.year_4 = 0

        # Update year counts based on the aggregated data
        for year_count in year_counts:
            year = year_count['year']
            count = year_count['count']

            if year == 'I':
                pic_master_entry.year_1 = count
            elif year == 'II':
                pic_master_entry.year_2 = count
            elif year == 'III':
                pic_master_entry.year_3 = count
            elif year == 'IV':
                pic_master_entry.year_4 = count

        # Save the updated PicMaster entry
        pic_master_entry.save()

    # Compute totals
    total_lab_count = PicMaster.objects.aggregate(Sum('lab_count'))['lab_count__sum'] or 0
    total_year_1 = PicMaster.objects.aggregate(Sum('year_1'))['year_1__sum'] or 0
    total_year_2 = PicMaster.objects.aggregate(Sum('year_2'))['year_2__sum'] or 0
    total_year_3 = PicMaster.objects.aggregate(Sum('year_3'))['year_3__sum'] or 0
    total_year_4 = PicMaster.objects.aggregate(Sum('year_4'))['year_4__sum'] or 0


def pic_master_view(request):
    update_pic_master()
    query = request.GET.get('q', '')

    if query:
        pic_masters = PicMaster.objects.filter(lab_name__icontains=query)
    else:
        pic_masters = PicMaster.objects.all()

    total_lab_count = PicMaster.objects.aggregate(total=Sum('lab_count'))['total']
    total_year_1 = PicMaster.objects.aggregate(total=Sum('year_1'))['total']
    total_year_2 = PicMaster.objects.aggregate(total=Sum('year_2'))['total']
    total_year_3 = PicMaster.objects.aggregate(total=Sum('year_3'))['total']
    total_year_4 = PicMaster.objects.aggregate(total=Sum('year_4'))['total']

    context = {
        'pic_masters': pic_masters,
        'query': query,
        'total_lab_count': total_lab_count or 0,
        'total_year_1': total_year_1 or 0,
        'total_year_2': total_year_2 or 0,
        'total_year_3': total_year_3 or 0,
        'total_year_4': total_year_4 or 0,
    }

    return render(request, 'pic_master.html', context)

def download_csv(request):
    filter_value = request.GET.get('filter', '')
    search_term = request.GET.get('search', '')
    results = []

    if filter_value and search_term:
        search_terms = [term.strip() for term in search_term.split(' ')]
        queries = Q()
        for term in search_terms:
            queries |= Q(**{f"{filter_value}__icontains": term})
        results = Student.objects.filter(queries).distinct()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students.csv"'

    writer = csv.writer(response)
    writer.writerow(['Roll No', 'Student Name', 'Mobile Number', 'Student Email', 'Year', 'Department', 'Faculty Incharge', 'Faculty ID', 'Lab Name', 'NIP Status'])

    for student in results:
        writer.writerow([student.roll_no, student.student_name, student.mobile_number, student.student_email, student.year, student.department, student.faculty_incharge, student.faculty_id, student.lab_name, student.nip_status])

    return response


"""def generate_date_range(start_date, end_date):
    start = datetime.strptime(start_date, "%d-%m-%Y")
    end = datetime.strptime(end_date, "%d-%m-%Y")
    date_generated = [(start + timedelta(days=x)).strftime("%d-%m-%Y") for x in range((end - start).days + 1)]
    return date_generated"""


def generate_date_range(from_date, to_date):
    start_date = datetime.strptime(from_date, "%d-%m-%Y")
    end_date = datetime.strptime(to_date, "%d-%m-%Y")
    date_range = []
    current_date = start_date
    while current_date <= end_date:
        date_range.append(current_date.strftime("%d-%m-%Y"))
        current_date += timedelta(days=1)
    return date_range

def robotics_lab(request):
    return render(request, 'robotics_lab.html')


"""def apply_on_duty(request):
    if request.method == "POST" and "apply_on_duty" in request.POST:
        lab_name = request.POST.get('lab_name')
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        selected_students = request.POST.getlist('selected_students')

        if selected_students:
            date_range = generate_date_range(from_date, to_date)
            for student_id in selected_students:
                student = Student.objects.get(id=student_id)
                OnDutyApplication.objects.create(
                    student=student,
                    lab_name=lab_name,
                    from_date=datetime.strptime(from_date, "%d-%m-%Y").date(),
                    to_date=datetime.strptime(to_date, "%d-%m-%Y").date(),
                    applied_dates=date_range
                )

            return HttpResponse("On Duty Applications Submitted")

    return render(request, 'on_duty.html')"""

def on_duty(request):
    lab_names = Student.objects.values_list('lab_name', flat=True).distinct()
    form = OnDutyForm()
    students = []
    date_range = []
    purpose = request.POST.get('purpose', '')  # Retrieve the purpose from POST

    success_message = None
    error_message = None
    successful_students = []
    unsuccessful_students = []

    if request.method == "GET" and 'lab_name' in request.GET:
        lab_name = request.GET.get('lab_name')
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        purpose = request.GET.get('purpose', '')  # Retrieve the purpose from GET

        if lab_name and from_date and to_date:
            from_date_db_format = datetime.strptime(from_date, "%d-%m-%Y").strftime("%Y-%m-%d")
            to_date_db_format = datetime.strptime(to_date, "%d-%m-%Y").strftime("%Y-%m-%d")
            students = Student.objects.filter(lab_name=lab_name)
            date_range = generate_date_range(from_date, to_date)

    if request.method == "POST":
        lab_name = request.POST.get('lab_name')
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        selected_students = request.POST.getlist('selected_students')
        purpose = request.POST.get('purpose', '')

        if "generate_csv" in request.POST:
            if selected_students:
                students = Student.objects.filter(id__in=selected_students)
                date_range = generate_date_range(from_date, to_date)

                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="on_duty_{lab_name}.csv"'

                writer = csv.writer(response)
                header = ['S.No', 'Name', 'Roll No', 'Department', 'Lab', 'Mail ID', 'Faculty Incharge', 'Year'] + date_range
                writer.writerow(header)

                for idx, student in enumerate(students, start=1):
                    row = [
                        idx, student.student_name, student.roll_no, student.department,
                        student.lab_name, student.student_email, student.faculty_incharge, student.year
                    ] + ['✓' if f"{student.id}_{date}" in request.POST else '' for date in date_range]
                    writer.writerow(row)

                return response

        if "apply_on_duty" in request.POST:
            if selected_students and from_date and to_date:
                try:
                    applied_dates = []
                    for student_id in selected_students:
                        for date in generate_date_range(from_date, to_date):
                            if f"{student_id}_{date}" in request.POST:
                                OnDutyApplication.objects.create(
                                    student_id=student_id,
                                    lab_name=lab_name,
                                    from_date=datetime.strptime(from_date, "%d-%m-%Y").date(),
                                    to_date=datetime.strptime(to_date, "%d-%m-%Y").date(),
                                    applied_date=datetime.strptime(date, "%d-%m-%Y").date(),
                                    purpose=purpose  # Save the purpose of the on-duty application
                                )
                                applied_dates.append(date)

                    successful_students = Student.objects.filter(id__in=selected_students)
                    success_message = (
                        f"Successfully applied on-duty STUDENTS ->\n"
                        f"{', '.join(student.student_name for student in successful_students)}\n\n"
                        f" :DATES APPLIED ->\n"
                        f"{', '.join(applied_dates)}\n\n"
                        f" :PURPOSE ->  {purpose}"
                    )
                except Exception as e:
                    unsuccessful_students = Student.objects.filter(id__in=selected_students)
                    error_message = (
                        f"Error applying for on-duty: {str(e)}.\n"
                        f"Failed students: {', '.join(student.student_name for student in unsuccessful_students)}"
                    )
                    print(f'Error applying for on-duty: {str(e)}')
            else:
                error_message = 'No students selected for on-duty application.'

    context = {
        'form': form,
        'lab_names': lab_names,
        'students': students,
        'date_range': date_range,
        'lab_name': request.GET.get('lab_name', ''),
        'from_date': request.GET.get('from_date', ''),
        'to_date': request.GET.get('to_date', ''),
        'purpose': purpose,  # Include purpose in the context
        'success_message': success_message,
        'error_message': error_message,
    }
    return render(request, 'on_duty.html', context)


def search_on_duty(request):
    lab_names = Student.objects.values_list('lab_name', flat=True).distinct()
    applications = []
    date_range = []
    lab_name = request.GET.get('lab_name', 'all')
    from_date = request.GET.get('from_date', '')
    to_date = request.GET.get('to_date', '')
    purpose = request.GET.get('purpose', '')

    if request.method == "GET":
        filter_kwargs = {}

        if from_date and to_date:
            from_date_db_format = datetime.strptime(from_date, "%d-%m-%Y").strftime("%Y-%m-%d")
            to_date_db_format = datetime.strptime(to_date, "%d-%m-%Y").strftime("%Y-%m-%d")
            date_range = generate_date_range(from_date, to_date)
            filter_kwargs['applied_date__range'] = [from_date_db_format, to_date_db_format]

        if lab_name != "all":
            filter_kwargs['student__lab_name'] = lab_name

        if purpose:
            filter_kwargs['purpose__icontains'] = purpose

        if filter_kwargs:
            applications = OnDutyApplication.objects.filter(**filter_kwargs).select_related('student')

        if request.GET.get('generate_csv') == 'true':
            return generate_od_csv(applications, date_range)

    return render(request, 'search_on_duty.html', {
        'lab_names': lab_names,
        'applications': applications,
        'date_range': date_range,
        'lab_name': lab_name,
        'from_date': from_date,
        'to_date': to_date,
        'purpose': purpose,
    })

def generate_od_csv(applications, date_range):
    # Create a CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="on_duty_applications.csv"'

    writer = csv.writer(response)
    header = ['S.No', 'Name', 'Roll No', 'Department', 'Lab', 'Mail ID', 'Faculty Incharge', 'Year', 'Purpose'] + date_range
    writer.writerow(header)

    for index, application in enumerate(applications):
        row = [
            index + 1,
            application.student.student_name,
            application.student.roll_no,
            application.student.department,
            application.student.lab_name,
            application.student.student_email,
            application.student.faculty_incharge,
            application.student.year,
            application.purpose,
        ]
        # Add tick marks for applied dates
        applied_dates = ['✓' if date == application.applied_date.strftime("%d-%m-%Y") else '' for date in date_range]
        row.extend(applied_dates)
        writer.writerow(row)

    return response


def student_card(request):
    form = StudentCardForm(request.GET or None)
    student = None
    error_message = None
    roll_no = request.GET.get('roll_no', '').strip()
    missing_entries = []

    if roll_no:
        search_terms = [term.strip() for term in roll_no.split(' ')]
        queries = Q()
        for term in search_terms:
            queries |= Q(roll_no__icontains=term)

        student = Student.objects.filter(queries).distinct()

        # Check for missing entries
        for term in search_terms:
            if not student.filter(roll_no__icontains=term).exists():
                missing_entries.append(term)

        if not student.exists():
            error_message = f"No student matches the given roll number: {roll_no}"
        else:
            student = student.first()  # Assuming you want to show the first match

    context = {
        'form': form,
        'student': student,
        'error_message': error_message,
        'searched_roll_no': roll_no,
        'missing_entries': missing_entries,
    }
    return render(request, 'student_card.html', context)



def admin_base(request):
    return render(request, 'admin_base.html')

def student_base(request):
    return render(request, 'student_base.html')

def faculty_base(request):
    return render(request, 'faculty_base.html')

