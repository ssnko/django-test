from django.contrib import admin
from cal.models import Event, Mem, Option

# Register your models here.
admin.site.register(Event)
admin.site.register(Mem)
admin.site.register(Option)