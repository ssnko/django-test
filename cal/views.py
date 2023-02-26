from datetime import datetime, timedelta, date
from datetime import time as date_time
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.views.generic.edit import ModelFormMixin
from django.urls import reverse, resolve
from django.utils.safestring import mark_safe
import calendar
import json
from django.contrib.auth import authenticate, login
import time

from .models import *
from .utils import Calendar, Calendar2
from .forms import EventForm, MemForm, OptionForm

def index(request):
    return HttpResponse('hello')

def list_sc(request):
    # return HttpResponse(reverse('cal:list'))

    # name_list = Mem.objects.order_by('-name')
    # print(name_list)
    # return render(request, 'cal/list.html')
    user_name = request.user.username

    name_list = Mem.objects.filter(account=user_name)
    # name_list = Mem.objects.order_by('-name')
    context = {'name_list': name_list,}
    return render(request, 'cal/list.html', context)

class CalendarView(generic.ListView):
    model = Event
    template_name = 'cal/calendar.html'

    def get_context_data(self, **kwargs):
        user_name = self.request.user.username
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get('month', None))
        cal = Calendar(d.year, d.month)
        cal.setfirstweekday(calendar.SUNDAY)
        html_cal = cal.formatmonth(user_name, withyear=True)
        context['calendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)

        op = Option.objects.filter(account=user_name).values()[0]
        if op['end_alarm'] != None:
            al = [str(op['end_alarm_cb']), op['end_alarm']]
        else:
            al = [str(op['end_alarm_cb']), '']

        user_list = list(Mem.objects.filter(account=user_name).values_list('name','health_end_date'))
        check_list = []
        for ul in user_list:
            if ul[1] != None:
                now = datetime.now()
                diff = datetime.combine(ul[1], date_time()) - now
                check_list.append([ul[0], diff.days+1])

        context['al'] = al
        context['user_list'] = check_list
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

# def event(request, event_id=None):
#     name = request.GET.get('name')
#     print(name)
#     if event_id:
#         instance = get_object_or_404(Event, pk=event_id)
#     else:
#         instance = Event()
#
#     form = EventForm(request.POST or None, instance=instance, initial={'choice': [(name, name)]})
#     if request.POST and form.is_valid():
#         form.save()
#         return HttpResponseRedirect(reverse('cal:calendar'))
#     return render(request, 'cal/event.html', {'form': form})

class CalendarView2(generic.ListView, ModelFormMixin):
    model = Event
    template_name = 'cal/event_mem.html'

    form_class = MemForm

    def get(self, request, *args, **kwargs):
        user_name = self.request.user.username
        self.object = None
        if kwargs != {}:
            instance = get_object_or_404(Mem, pk=self.id)
        else:
            instance = Mem()
        self.form = MemForm(instance=instance, initial={'account': user_name})

        return generic.ListView.get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        # self.form = self.get_form(self.form_class)
        if kwargs != {}:
            self.id = kwargs['event_id']
            instance = get_object_or_404(Mem, pk=self.id)
        else:
            instance = Mem()

        # listIWantToStore = [('2022-12-02','1'), ('2022-12-05', '2')]
        # dd = json.dumps(listIWantToStore)
        # # dd = instance.note1
        # # print(dd, type(dd))
        # jsonDec = json.decoder.JSONDecoder()
        # dd_list = jsonDec.decode(dd)

        jsonDec = json.decoder.JSONDecoder()
        user_name = self.request.user.username

        if instance.weight != None:
            weight = jsonDec.decode(instance.weight)
            self.weight = [float(i) for i in weight]
            muscle = jsonDec.decode(instance.muscle)
            self.muscle = [float(i) for i in muscle]
            fat = jsonDec.decode(instance.fat)
            self.fat = [float(i) for i in fat]
            self.date = jsonDec.decode(instance.date)
        else:
            self.weight = []
            self.muscle = []
            self.fat = []
            self.date = []

        if instance.re_data != '':
            self.re_data = jsonDec.decode(instance.re_data)
        else:
            self.re_data = []

        # 횟수당 금액 불러오는곳
        if len(Option.objects.filter(account=user_name)) != 0:
            op_id = Option.objects.filter(account=user_name).values_list('id', flat=True)[0]
            op_instance = Option.objects.get(pk=op_id)

            option = Option.objects.filter(account=user_name).values()
            if len(option) != 0:
                if option[0]['count'] == 'NaN':
                    option[0]['count'] = 0
                self.option_ = [option[0]['count'], option[0]['empty1'], option[0]['empty2'], option[0]['empty3'],
                                option[0]['empty4'], option[0]['empty5']]
            else:
                self.option_ = ['0', None, None, None, None, None]
        else:
            op_instance = Option()
            self.option_ = ['0', None, None, None, None, None]

        if op_instance.count_money != '':
            self.count = jsonDec.decode(op_instance.count_money)
        else:
            self.count = [['', '', '', '', ''], ['', '', '', '', '']]

        self.alarm_ = instance.alarm_check
        self.alarm_text = instance.alarm

        self.form = MemForm(self.request.POST or None, instance=instance, initial={'account': user_name})

        if self.form.is_valid() and request.method == 'POST':
            wei_list = []
            mus_list = []
            fat_list = []
            date_list = []
            i = 0
            while True:
                if request.POST.get(f'wei_{i}') == None:
                    break
                if request.POST.get(f'wei_{i}') != '' and request.POST.get(f'mus_{i}') != '' and request.POST.get(f'fat_{i}') != '' and request.POST.get(f'date_{i}') != '':
                    wei_list.append(request.POST.get(f'wei_{i}'))
                    mus_list.append(request.POST.get(f'mus_{i}'))
                    fat_list.append(request.POST.get(f'fat_{i}'))
                    date_list.append(request.POST.get(f'date_{i}'))
                i += 1
            self.weight = [float(i) for i in wei_list]
            self.muscle = [float(i) for i in mus_list]
            self.fat = [float(i) for i in fat_list]
            self.date = date_list

            if instance.re_data != '':
                self.re_data = jsonDec.decode(instance.re_data)
            else:
                self.re_data = []

            wei_list = json.dumps(wei_list)
            mus_list = json.dumps(mus_list)
            fat_list = json.dumps(fat_list)
            date_list = json.dumps(date_list)

            self.object = self.form.save(commit=False)
            self.object.weight = wei_list
            self.object.muscle = mus_list
            self.object.fat = fat_list
            self.object.date = date_list
            self.object.save()

            op_instance.account = user_name
            op_instance.count = request.POST.get('empty_count')
            op_instance.empty1 = request.POST.get('empty1_t')
            op_instance.empty2 = request.POST.get('empty2_t')
            op_instance.empty3 = request.POST.get('empty3_t')
            op_instance.empty4 = request.POST.get('empty4_t')
            op_instance.empty5 = request.POST.get('empty5_t')
            op_instance.save()

            if len(Option.objects.filter(account=user_name)) != 0:
                option = Option.objects.filter(account=user_name).values()
                if len(option) != 0:
                    if option[0]['count'] == 'NaN':
                        option[0]['count'] = 0
                    self.option_ = [option[0]['count'], option[0]['empty1'], option[0]['empty2'], option[0]['empty3'],
                                    option[0]['empty4'], option[0]['empty5']]
                else:
                    self.option_ = ['0', None, None, None, None, None]
            else:
                self.option_ = ['0', None, None, None, None, None]

        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        user_name = self.request.user.username
        context = super(CalendarView2, self).get_context_data(**kwargs)
        d = get_date(self.request.GET.get('month', None))
        cal = Calendar2(d.year, d.month, self.id)
        cal.setfirstweekday(calendar.SUNDAY)
        html_cal = cal.formatmonth(user_name, withyear=True)
        context['calendar'] = mark_safe(html_cal)
        context['prev_month2'] = prev_month2(d)
        context['next_month2'] = next_month2(d)
        context['form'] = self.form
        context['id'] = self.id
        context['weight_data'] = self.weight
        context['muscle_data'] = self.muscle
        context['fat_data'] = self.fat
        context['wmf_date'] = self.date
        context['empty'] = self.option_
        context['alarm_'] = self.alarm_
        context['alarm_text'] = self.alarm_text
        context['re_data'] = self.re_data
        context['count_money'] = self.count
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
    user_name = request.user.username
    if event_id:
        instance = get_object_or_404(Mem, pk=event_id)

        name = Mem.objects.filter(id=event_id, account=user_name).values()[0]['name']
        schedule = Event.objects.filter(name=name, account=user_name).values()

        form = MemForm(request.POST or None, instance=instance)
        if request.POST and form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('cal:list'))

        return render(request, 'cal/event_mem.html',{'form': form, 'name': name, 'event_id': event_id, 'schedule_list': schedule})
    else:
        instance = Mem()

        form = MemForm(request.POST or None, instance=instance, initial={'account': user_name})
        if request.POST and form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('cal:list'))

            # 이름 중복 처리
            # name_list = Mem.objects.values_list('name', flat=True)
            # if request.POST['name'] not in name_list:
            #     form.save()
            #     return HttpResponseRedirect(reverse('cal:list'))
            # return render(request, 'cal/event_mem.html', {'form': form, 'error': 'error'})

        jsonDec = json.decoder.JSONDecoder()
        weight = []
        muscle = []
        fat = []
        date = []

        # 횟수당 금액 불러오는곳
        if len(Option.objects.filter(account=user_name)) != 0:
            op_id = Option.objects.filter(account=user_name).values_list('id', flat=True)[0]
            op_instance = Option.objects.get(pk=op_id)

            option = Option.objects.filter(account=user_name).values()
            if len(option) != 0:
                if option[0]['count'] == 'NaN':
                    option[0]['count'] = 0
                option_ = [option[0]['count'], option[0]['empty1'], option[0]['empty2'], option[0]['empty3'],
                                option[0]['empty4'], option[0]['empty5']]
            else:
                option_ = ['0', None, None, None, None, None]
        else:
            op_instance = Option()
            option_ = ['0', None, None, None, None, None]

        if op_instance.count_money != '':
            count = jsonDec.decode(op_instance.count_money)
        else:
            count = [['', '', '', '', ''], ['', '', '', '', '']]

        return render(request, 'cal/event_mem.html', {'form': form, 'event_id': event_id, 'new': 1, 'count_money':count, 'empty':option_, 'weight_data':weight, 'muscle_data':muscle, 'fat_data':fat, 'wmf_date':date})

def delete_post(request, pk):
    form = get_object_or_404(Mem, pk=pk)
    user_name = request.user.username

    if request.method == 'POST':
        schedule = Event.objects.filter(name_id=pk, account=user_name).values_list('id', flat=True)
        for sc_id in schedule:
            sc_form = get_object_or_404(Event, pk=sc_id)
            sc_form.delete()
        form.delete()
        return redirect('/list')

    return render(request, 'cal/event_mem.html', {'form': form})

def delete_schedule(request):
    schedule_id = request.GET.get('event_id')
    form = get_object_or_404(Event, pk=schedule_id)

    if request.method == 'GET':
        form.delete()

        data = Event.objects.filter(name_id=schedule_id).order_by('time').values()
        for i in range(len(data)):
            count = Event.objects.get(pk=data[i]['id'])
            count.count = i + 1
            count.save()

        year = request.GET.get('year')
        month = request.GET.get('month')
        day = request.GET.get('day')
        id = request.GET.get('id')

        if id != 'null':
            if  id != '':
                return redirect(f'/schedule/?year={year}&month={month}&day={day}&id={id}')
            else:
                return HttpResponseRedirect(reverse('cal:calendar'))
        else:
            return HttpResponseRedirect(reverse('cal:calendar'))

    return render(request, 'cal/event_mem.html', {'form': form})

def schedule(request):
    year = request.GET.get('year')
    month = request.GET.get('month')
    day = request.GET.get('day')
    id = request.GET.get('id')
    user_name = request.user.username

    if len(month) == 1:
        month = f'0{month}'
    if len(day) == 1:
        day = f'0{day}'

    instance = Event()
    if id != None:
        name = Mem.objects.filter(id=id).values()[0]['name']
        # events = Event.objects.filter(time__year=year, time__month=month, time__day=day, name_id=id, account=user_name).values()
        events = Event.objects.filter(account=user_name, time__contains=f'{year}-{month}-{day}', name_id=id).values()
    else:
        name = ''
        # events = Event.objects.filter(time__year=year, time__month=month, time__day = day, account=user_name).values()
        events = Event.objects.filter(account=user_name, time__contains=f'{year}-{month}-{day}').values()

    name_list = Mem.objects.filter(account=user_name).values_list('name', flat=True)
    choice = []
    for i in range(len(name_list)):
        choice.append({'num': i, 'name': name_list[i]})

    time_30 = ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30',
               '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00',
               '21:30', '22:00', '22:30', '23:00', '23:30', '24:00']

    form = EventForm(request.POST or None, instance=instance, initial={'name': '데이터', 'account': user_name})
    if request.POST and form.is_valid():
        try:  # 기타일정 추가부분
            form_name = request.POST['a_value']
            form_time = request.POST["sc_time"]
            name_id = ''

            create_date = f'{year}-{month}-{day} {form_time}'
            create_date = datetime.strptime(create_date, '%Y-%m-%d %H:%M')
            overlap = Event.objects.filter(time=create_date, account=user_name).values_list('id', flat=True)
            if len(overlap) != 0:
                Event.objects.get(pk=overlap[0]).delete()

            com = form.save(commit=False)
            com.name = form_name
            com.time = f'{year}-{month}-{day}T{form_time}'
            com.name_id = name_id
            com.save()
            # if id != None:
            #     events = Event.objects.filter(time__year=year, time__month=month, time__day=day, name_id=id, account=user_name).values()
            # else:
            #     events = Event.objects.filter(time__year=year, time__month=month, time__day=day, account=user_name).values()

            if id != None:
                events = Event.objects.filter(account=user_name, time__contains=f'{year}-{month}-{day}', name_id=id).values()
            else:
                events = Event.objects.filter(account=user_name, time__contains=f'{year}-{month}-{day}').values()

            for i in range(len(events)):
                if events[i]['name_id'] == '':
                    events[i]['full_count'] = ''
                else:
                    full_count = Mem.objects.filter(id=events[i]['name_id']).values()[0]['count']

                    if full_count == None:
                        full_count = 0
                    events[i]['full_count'] = f'{full_count}/'

            event_list = []
            for i in range(len(time_30)):
                event_list.append('')

            for i in range(len(events)):
                if events[i]['time'].strftime('%H:%M') in time_30:
                    event_list[time_30.index(events[i]['time'].strftime('%H:%M'))] = events[i]

            if id != None:
                return render(request, 'cal/schedule.html',
                              {'form': form, 'event_list': event_list, 'year': year, 'month': month, 'day': day,
                               'id': id, 'time_list': time_30, 'name_list': choice, 'name_hidden': 'none', 'name_hidden2': 'block',
                               'checked2': 'checked', 'name_line_width': '45%'})
            else:
                return render(request, 'cal/schedule.html',
                              {'form': form, 'event_list': event_list, 'year': year, 'month': month, 'day': day,
                               'time_list': time_30, 'name_list': choice, 'name_hidden': 'none', 'name_hidden2': 'block', 'checked2': 'checked',
                               'name_line_width': '45%'})
        except:
            form_name = name_list[int(request.POST['number'])]
            form_time = request.POST["sc_time"]
            name_id = Mem.objects.filter(account=user_name).values()[int(request.POST['number'])]['id']

            create_date = f'{year}-{month}-{day} {form_time}'
            create_date = datetime.strptime(create_date, '%Y-%m-%d %H:%M')
            overlap = Event.objects.filter(time=create_date, account=user_name).values_list('id', flat=True)
            if len(overlap) != 0:
                Event.objects.get(pk=overlap[0]).delete()

            com = form.save(commit=False)

            com.name = form_name
            com.time = f'{year}-{month}-{day}T{form_time}'
            com.name_id = name_id
            com.save()
            data = Event.objects.filter(name_id=name_id, account=user_name).order_by('time').values()
            start_count = Mem.objects.filter(account=user_name, name=form_name).values_list('start_count', flat=True)
            if start_count[0] != None:
                start_count = start_count[0]-1
            else:
                start_count = 0
            for i in range(len(data)):
                count = Event.objects.get(pk=data[i]['id'])
                count.count = i + 1 + start_count
                count.save()

            if id != None:
                events = Event.objects.filter(account=user_name, time__contains=f'{year}-{month}-{day}', name_id=id).values()
            else:
                events = Event.objects.filter(account=user_name, time__contains=f'{year}-{month}-{day}').values()

            for i in range(len(events)):
                if events[i]['name_id'] == '':
                    events[i]['full_count'] = ''
                else:
                    full_count = Mem.objects.filter(id=events[i]['name_id']).values()[0]['count']

                    if full_count == None:
                        full_count = 0
                    events[i]['full_count'] = f'{full_count}/'

            event_list = []
            for i in range(len(time_30)):
                event_list.append('')

            for i in range(len(events)):
                if events[i]['time'].strftime('%H:%M') in time_30:
                    event_list[time_30.index(events[i]['time'].strftime('%H:%M'))] = events[i]

            if id != None:
                return render(request, 'cal/schedule.html', {'form': form, 'event_list': event_list, 'year': year, 'month': month, 'day': day, 'id': id, 'time_list': time_30, 'name_list': choice, 'name_hidden': 'none', 'name_hidden2': 'none', 'checked': 'checked', 'name_line_width': '75%'})
            else:
                return render(request, 'cal/schedule.html', {'form': form, 'event_list': event_list, 'year': year, 'month': month, 'day': day, 'time_list': time_30, 'name_list': choice, 'name_hidden': 'block', 'name_hidden2': 'none', 'checked': 'checked', 'name_line_width': '45%'})

    for i in range(len(events)):
        if events[i]['name_id'] == '' or events[i]['name_id'] == None:
            events[i]['full_count'] = ''
            events[i]['count'] = ''
        else:
            full_count = Mem.objects.filter(id=events[i]['name_id']).values()[0]['count']

            if full_count == None:
                full_count = 0
            events[i]['full_count'] = f'{full_count}/'

    event_list = []
    for i in range(len(time_30)):
        event_list.append('')

    for i in range(len(events)):
        if events[i]['time'].strftime('%H:%M') in time_30:
            event_list[time_30.index(events[i]['time'].strftime('%H:%M'))] = events[i]

    if id != None:
        return render(request, 'cal/schedule.html', {'form': form, 'event_list': event_list, 'year': year, 'month': month, 'day': day, 'id': id, 'time_list': time_30, 'name_list': choice, 'name_hidden': 'none', 'name_hidden2': 'none', 'name_line_width': '75%'})
    else:
        return render(request, 'cal/schedule.html', {'form': form, 'event_list': event_list, 'year': year, 'month': month, 'day': day, 'time_list': time_30, 'name_list': choice, 'name_hidden': 'none', 'name_hidden2': 'none', 'name_line_width': '75%'})

def schedule_add(request):
    year = request.GET.get('year')
    month = request.GET.get('month')
    day = request.GET.get('day')
    id = request.GET.get('id')
    user_name = request.user.username

    instance = Event()
    if id == '':
        name = ''
        form = EventForm(request.POST or None, instance=instance, initial={'time': f'{year}-{month}-{day}T00:00', 'name_id': id, 'account': user_name})
    else:
        # name = Mem.objects.filter(id=id).values()[0]['name'].
        mem_list = Mem.objects.filter(account=user_name).values()
        number = 0
        for i in range(len(mem_list)):
            if mem_list[i]['id'] == int(id):
                number = i
                name = mem_list[i]['name']
                break

        form = EventForm(request.POST or None, instance=instance, initial={'time': f'{year}-{month}-{day}T00:00', 'name': f'{number}-{name}', 'name_id': id, 'account': user_name})

    if request.POST and form.is_valid():
        v1, v2 = form.data['name'].split('-')
        if id == '':
            # name_id = Mem.objects.filter(name=form.data['name']).values()[0]['id']
            name_id = Mem.objects.filter(account=user_name).values()[int(v1)]['id']
            com = form.save(commit=False)
            com.name = v2
            com.name_id = name_id
            com.save()
            data = Event.objects.filter(name_id=name_id, account=user_name).order_by('time').values()
            for i in range(len(data)):
                count = Event.objects.get(pk=data[i]['id'])
                count.count = i + 1
                count.save()
        else:
            com = form.save(commit=False)
            com.name = v2
            com.save()
            data = Event.objects.filter(name_id=form.data['name_id'], account=user_name).order_by('time').values()
            for i in range(len(data)):
                count = Event.objects.get(pk=data[i]['id'])
                count.count = i + 1
                count.save()

        return HttpResponseRedirect(reverse('cal:calendar'))

    return render(request, 'cal/schedule_add.html', {'form': form, 'year': year, 'month': month, 'day': day})

def schedule_edit(request, event_id=None):
    user_name = request.user.username
    instance = get_object_or_404(Event, pk=event_id)

    year = request.GET.get('year')
    month = request.GET.get('month')
    day = request.GET.get('day')
    id = request.GET.get('id')

    # form = EventForm(request.POST, instance=instance, initial={'account': user_name, 'name': instance.name})
    form = EventForm(request.POST or None, instance=instance)
    if request.POST and form.is_valid():
        form.save()
        num = 1
        if request.POST['name_id'] != '':
            data = Event.objects.filter(name_id=request.POST['name_id'], account=user_name).order_by('time').values()
            for i in range(len(data)):
                event = Event.objects.get(pk=data[i]['id'])
                if event.cancel != '취소':
                    event.count = num
                    num += 1
                else:
                    event.count = ''
                event.save()

        return HttpResponseRedirect(reverse('cal:calendar'))

    return render(request, 'cal/schedule_add.html',{'form': form, 'event_id': event_id, 'year': year, 'month': month, 'day': day, 'id': id, 'name_id': instance.name_id})

def main(request):
    if request.method == "GET":
        user_name = request.user.username
        if user_name == '':
            return render(request, 'cal/main.html')
        else:
            return HttpResponseRedirect(reverse('cal:calendar'))

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

def option(request):
    user_name = request.user.username
    if len(Option.objects.filter(account=user_name)) != 0:
        id = Option.objects.filter(account=user_name).values_list('id', flat=True)[0]
        instance = Option.objects.get(pk=id)
    else:
        instance = Option()

    form = OptionForm(request.POST or None, instance=instance)

    jsonDec = json.decoder.JSONDecoder()

    if instance.count_money != '':
        weight = jsonDec.decode(instance.count_money)
    else:
        weight = [['', '', '', '', ''],['', '', '', '', '']]

    if request.POST and form.is_valid():
        count1 = request.POST.get('count_0')
        count2 = request.POST.get('count_1')
        count3 = request.POST.get('count_2')
        count4 = request.POST.get('count_3')
        count5 = request.POST.get('count_4')

        money1 = request.POST.get('money_0')
        money2 = request.POST.get('money_1')
        money3 = request.POST.get('money_2')
        money4 = request.POST.get('money_3')
        money5 = request.POST.get('money_4')

        cm = [[count1, count2, count3, count4, count5], [money1, money2, money3, money4, money5]]

        cm = json.dumps(cm)

        com = form.save(commit=False)
        com.account = user_name
        com.count_money = cm
        com.save()

        return HttpResponseRedirect(reverse('cal:calendar'))

    return render(request, 'cal/option.html', {'form': form, 'weight': weight})
