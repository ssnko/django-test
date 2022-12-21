from django.urls import re_path
from . import views

app_name = 'cal'
urlpatterns = [
    re_path(r'^index/$', views.index, name='index'),
    re_path(r'^calendar/$', views.CalendarView.as_view(), name='calendar'),
    re_path(r'^list/$', views.list, name='list'),
    re_path(r'^event/new/$', views.event, name='event_new'),
	re_path(r'^event/edit/(?P<event_id>\d+)/$', views.event, name='event_edit'),
    re_path(r'^event_mem/new/$', views.event_mem, name='event_mem_new'),
    re_path(r'^event_mem/edit/(?P<event_id>\d+)/$', views.CalendarView2.as_view(), name='event_mem_edit'),
    re_path(r'^delete/(?P<pk>[0-9]+)/$', views.delete_post, name='delete_post'),
    re_path(r'^delete_sc/$', views.delete_schedule, name='delete_schedule'),
    re_path(r'^schedule/$', views.schedule, name='schedule'),
    re_path(r'^schedule_add/$', views.schedule_add, name='schedule_add'),
    re_path(r'^schedule/edit/(?P<event_id>\d+)/$', views.schedule_edit, name='schedule_edit'),
]
