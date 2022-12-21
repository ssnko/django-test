from datetime import datetime, timedelta, date
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.views.generic.edit import ModelFormMixin
from django.urls import reverse, resolve
from django.utils.safestring import mark_safe
import calendar
from django.contrib.auth import authenticate, login

from .models import *
from .utils import Calendar, Calendar2
from .forms import EventForm, MemForm

def index(request):
    return HttpResponse('hello')

def list(request):
    # return HttpResponse(reverse('cal:list'))

    # name_list = Mem.objects.order_by('-name')
    # print(name_list)
    # return render(request, 'cal/list.html')

    name_list = Mem.objects.order_by('-name')
    context = {'name_list': name_list,}
    return render(request, 'cal/list.html', context)

class CalendarView(generic.ListView):
    model = Event
    template_name = 'cal/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get('month', None))
        cal = Calendar(d.year, d.month)
        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        return context

def get_date(req_month):
    if req_month:
        year, month = (int(x) for x in req_month.split('-'))
        return date(year, month, day=1)

    return datetime.today()

def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month

def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month

def event(request, event_id=None):
    name = request.GET.get('name')
    if event_id:
        instance = get_object_or_404(Event, pk=event_id)
    else:
        instance = Event()

    form = EventForm(request.POST or None, instance=instance, initial={'choice': [(name, name)]})
    if request.POST and form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('cal:calendar'))
    return render(request, 'cal/event.html', {'form': form})

class CalendarView2(generic.ListView, ModelFormMixin):
    model = Event
    template_name = 'cal/event_mem.html'

    form_class = MemForm

    def get(self, request, *args, **kwargs):
        self.object = None
        if kwargs != {}:
            instance = get_object_or_404(Mem, pk=self.id)
        else:
            instance = Mem()
        self.form = MemForm(instance=instance)

        return generic.ListView.get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        # self.form = self.get_form(self.form_class)
        if kwargs != {}:
            self.id = kwargs['event_id']
            instance = get_object_or_404(Mem, pk=self.id)
        else:
            instance = Mem()
        self.form = MemForm(self.request.POST or None, instance=instance)

        if self.form.is_valid():
            self.object = self.form.save()

        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CalendarView2, self).get_context_data(**kwargs)
        d = get_date(self.request.GET.get('month', None))
        cal = Calendar2(d.year, d.month, self.id)
        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_cal)
        context['prev_month2'] = prev_month2(d)
        context['next_month2'] = next_month2(d)
        context['form'] = self.form
        context['id'] = self.id
        return context
    
def prev_month2(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month

def next_month2(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month

def event_mem(request, event_id=None):
    instance = Mem()
    if event_id:
        instance = get_object_or_404(Mem, pk=event_id)

        name = Mem.objects.filter(id=event_id).values()[0]['name']
        schedule = Event.objects.filter(name=name).values()

        form = MemForm(request.POST or None, instance=instance)
        if request.POST and form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('cal:list'))

        return render(request, 'cal/event_mem.html',{'form': form, 'name': name, 'event_id': event_id, 'schedule_list': schedule})
    else:
        instance = Mem()

        form = MemForm(request.POST or None, instance=instance)
        if request.POST and form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('cal:list'))

            # 이름 중복 처리
            # name_list = Mem.objects.values_list('name', flat=True)
            # if request.POST['name'] not in name_list:
            #     form.save()
            #     return HttpResponseRedirect(reverse('cal:list'))
            # return render(request, 'cal/event_mem.html', {'form': form, 'error': 'error'})

        return render(request, 'cal/event_mem.html', {'form': form, 'event_id': event_id})

def delete_post(request, pk):
    form = get_object_or_404(Mem, pk=pk)

    if request.method == 'POST':
        schedule = Event.objects.filter(name_id=pk).values_list('id', flat=True)
        for sc_id in schedule:
            sc_form = get_object_or_404(Event, pk=sc_id)
            sc_form.delete()
        form.delete()
        return redirect('/list')

    return render(request, 'cal/event_mem.html', {'form': form})

def delete_schedule(request):
    # print(resolve(request.path_info).url_name)
    schedule_id = request.GET.get('schedule')
    form = get_object_or_404(Event, pk=schedule_id)

    if request.method == 'GET':
        form.delete()

        data = Event.objects.filter(name_id=schedule_id).order_by('time').values()
        for i in range(len(data)):
            count = Event.objects.get(pk=data[i]['id'])
            count.count = i + 1
            count.save()

        event_id = request.GET.get("event_id")
        if event_id != '1000000':
            return redirect(f'/event_mem/edit/{request.GET.get("event_id")}/')
        else:
            year = request.GET.get('year')
            month = request.GET.get('month')
            day = request.GET.get('day')
            return redirect(f'/schedule/?year={year}&month={month}&day={day}&id=')

    return render(request, 'cal/event_mem.html', {'form': form})

def schedule(request):
    year = request.GET.get('year')
    month = request.GET.get('month')
    day = request.GET.get('day')
    id = request.GET.get('id')

    if len(month) == 1:
        month = f'0{month}'
    if len(day) == 1:
        day = f'0{day}'

    instance = Event()
    if id != '':
        name = Mem.objects.filter(id=id).values()[0]['name']
        events = Event.objects.filter(time__year=year, time__month=month, time__day=day, name_id=id).values()
    else:
        name = ''
        events = Event.objects.filter(time__year=year, time__month=month, time__day = day).values()

    form = EventForm(request.POST or None, instance=instance, initial={'time': f'{year}-{month}-{day}T00:00'})
    if request.POST and form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('cal:calendar'))

    return render(request, 'cal/schedule.html', {'form': form, 'schedule_list': events, 'year': year, 'month': month, 'day': day, 'id': id})

def schedule_add(request):
    year = request.GET.get('year')
    month = request.GET.get('month')
    day = request.GET.get('day')
    id = request.GET.get('id')

    instance = Event()
    if id == '':
        name = ''
        form = EventForm(request.POST or None, instance=instance, initial={'time': f'{year}-{month}-{day}T00:00', 'name_id': id})
    else:
        # name = Mem.objects.filter(id=id).values()[0]['name'].
        mem_list = Mem.objects.all().values()
        number = 0
        for i in range(len(mem_list)):
            if mem_list[i]['id'] == int(id):
                number = i
                name = mem_list[i]['name']
                break

        form = EventForm(request.POST or None, instance=instance, initial={'time': f'{year}-{month}-{day}T00:00', 'name': f'{number}-{name}', 'name_id': id})

    if request.POST and form.is_valid():
        v1, v2 = form.data['name'].split('-')
        if id == '':
            # name_id = Mem.objects.filter(name=form.data['name']).values()[0]['id']
            name_id = Mem.objects.all().values()[int(v1)]['id']
            com = form.save(commit=False)
            com.name = v2
            com.name_id = name_id
            com.save()
            data = Event.objects.filter(name_id=name_id).order_by('time').values()
            for i in range(len(data)):
                count = Event.objects.get(pk=data[i]['id'])
                count.count = i + 1
                count.save()
        else:
            com = form.save(commit=False)
            com.name = v2
            com.save()
            data = Event.objects.filter(name_id=form.data['name_id']).order_by('time').values()
            for i in range(len(data)):
                count = Event.objects.get(pk=data[i]['id'])
                count.count = i + 1
                count.save()

        return HttpResponseRedirect(reverse('cal:calendar'))

    return render(request, 'cal/schedule_add.html', {'form': form, 'year': year, 'month': month, 'day': day})

def schedule_edit(request, event_id=None):
    instance = get_object_or_404(Event, pk=event_id)

    form = EventForm(request.POST or None, instance=instance)
    if request.POST and form.is_valid():
        v1, v2 = form.data['name'].split('-')

        com = form.save(commit=False)
        com.name = v2
        com.save()
        data = Event.objects.filter(name_id=form.data['name_id']).order_by('time').values()
        for i in range(len(data)):
            count = Event.objects.get(pk=data[i]['id'])
            count.count = i + 1
            count.save()

        return HttpResponseRedirect(reverse('cal:list'))

    return render(request, 'cal/schedule_add.html',{'form': form, 'event_id': event_id})

def main(request):
    if request.method == "GET":
        return render(request, 'cal/main.html')

    elif request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
                login(request, user)
                # Redirect to a success page.
                return HttpResponseRedirect(reverse('cal:calendar'))
        else:
            # Return an 'invalid login' error message.
            return render(request, 'cal/main.html')