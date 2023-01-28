from django.forms import ModelForm, DateInput, TextInput, ChoiceField, Select, widgets
from cal.models import Event, Mem, Option
import json

class EventForm(ModelForm):
  # def get_choice(self, account):
  #   name_list = Mem.objects.filter(account=account).values_list('name', flat=True)
  #   choice = []
  #   for i in range(len(name_list)):
  #     choice.append((f'{i}-{name_list[i]}', name_list[i]))
  #   return choice

  class Meta:
    model = Event
    # datetime-local is a HTML5 input type, format to make date time show on fields

    widgets = {
      # 'start_time': DateInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
      # 'end_time': DateInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
      'time': DateInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
    }
    fields = '__all__'

  def __init__(self, *args, **kwargs):
    super(EventForm, self).__init__(*args, **kwargs)
    # input_formats parses HTML5 datetime-local input to datetime field
    # self.fields['start_time'].input_formats = ('%Y-%m-%dT%H:%M',)
    # self.fields['end_time'].input_formats = ('%Y-%m-%dT%H:%M',)
    self.fields['time'].input_formats = ('%Y-%m-%dT%H:%M',)
    # if 'initial' in kwargs:
    #   self.fields['name'].choices = self.get_choice(kwargs['initial']['account'])


class MemForm(ModelForm):
  def get_choice(self, account):
    id = Option.objects.filter(account=account).values_list('id', flat=True)[0]
    instance = Option.objects.get(pk=id)

    jsonDec = json.decoder.JSONDecoder()

    if instance.count_money != '':
      weight = jsonDec.decode(instance.count_money)
    else:
      weight = [['', '', '', '', ''], ['', '', '', '', '']]

    choice = [['', '']]
    for i in range(len(weight[0])):
      if weight[0][i] != '':
        choice.append((weight[0][i], weight[0][i]))

    return choice

  class Meta:
    model = Mem

    widgets = {
      'start_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
      'end_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
      'membership_start_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
      'membership_end_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
      'health_start_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
      'health_end_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
      'class_start_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
      'class_end_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
    }
    fields = '__all__'

  def __init__(self, *args, **kwargs):
    super(MemForm, self).__init__(*args, **kwargs)
    self.fields['start_date'].input_formats = ('%Y-%m-%d',)
    self.fields['end_date'].input_formats = ('%Y-%m-%d',)
    self.fields['membership_start_date'].input_formats = ('%Y-%m-%d',)
    self.fields['membership_end_date'].input_formats = ('%Y-%m-%d',)
    self.fields['health_start_date'].input_formats = ('%Y-%m-%d',)
    self.fields['health_end_date'].input_formats = ('%Y-%m-%d',)
    self.fields['class_start_date'].input_formats = ('%Y-%m-%d',)
    self.fields['class_end_date'].input_formats = ('%Y-%m-%d',)
    if 'initial' in kwargs:
      if 'account' in kwargs['initial']:
        # self.fields['count'].choices = self.get_choice(kwargs['initial']['account'])
        self.fields["count"].widget = widgets.Select(choices=self.get_choice(kwargs['initial']['account']))


class OptionForm(ModelForm):
  class Meta:
    model = Option

    widgets = {
    }
    fields = '__all__'

  def __init__(self, *args, **kwargs):
    super(OptionForm, self).__init__(*args, **kwargs)
