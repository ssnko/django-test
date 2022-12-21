from django.db import models
from django.urls import reverse

class Event(models.Model):
    name = models.CharField(max_length=200)
    time = models.DateTimeField()
    count = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    name_id = models.CharField(max_length=200, null=True, blank=True)
    # start_time = models.DateTimeField()
    # end_time = models.DateTimeField()

    @property
    def get_html_url(self):
        url = reverse('cal:event_edit', args=(self.id,))
        return f'<a href="{url}"> {self.name} </a>'

class Mem(models.Model):
    name = models.CharField(max_length=200)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    count = models.CharField(max_length=200, null=True, blank=True)
    food = models.CharField(max_length=200, null=True, blank=True)
    job = models.CharField(max_length=200, null=True, blank=True)
    residence = models.CharField(max_length=200, null=True, blank=True)
    stature = models.CharField(max_length=200, null=True, blank=True)
    age = models.CharField(max_length=200, null=True, blank=True)
    weight = models.CharField(max_length=200, null=True, blank=True)
    muscle = models.CharField(max_length=200, null=True, blank=True)
    fat = models.CharField(max_length=200, null=True, blank=True)
    hope_time = models.TextField(null=True, blank=True)
    health_career = models.TextField(null=True, blank=True)
    note1 = models.TextField(null=True, blank=True)
    note2 = models.TextField(null=True, blank=True)

    @property
    def get_html_url(self):
        url = reverse('cal:event_mem_edit', args=(self.id,))
        return f'<a href="{url}"> {self.name} </a>'

# python manage.py createsuperuser
# python manage.py makemigrations
# python manage.py migrate
# python manage.py runserver