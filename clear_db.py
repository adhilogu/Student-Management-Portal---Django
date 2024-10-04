# myapp/management/commands/clear_students.py

from django.core.management.base import BaseCommand
from student_details_app.models import Student

class Command(BaseCommand):
    help = 'Delete all records from the Student table'

    def handle(self, *args, **kwargs):
        Student.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully deleted all records from the Student table'))
