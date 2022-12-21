from django.forms import ModelForm, DateInput, TextInput, ChoiceField, Select
from cal.models import Event, Mem

class EventForm(ModelForm):
  name_list = Mem.objects.values_list('name', flat=True)
  choice = []
  for i in range(len(name_list)):
    choice.append((f'{i}-{name_list[i]}', name_list[i]))
  name = ChoiceField(choices=choice, required=False, widget=Select())

  def get_choice(self):
    name_list = Mem.objects.values_list('name', flat=True)
    choice = []
    for i in range(len(name_list)):
      choice.append((f'{i}-{name_list[i]}', name_list[i]))
    return choice

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
    self.fields['name'].choices = self.get_choice()
    # self.fields['name'].choices = kwargs['initial']['choice']


class MemForm(ModelForm):
  class Meta:
    model = Mem

    widgets = {
      'start_date': DateInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
      'end_date': DateInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
    }
    fields = '__all__'

  def __init__(self, *args, **kwargs):
    super(MemForm, self).__init__(*args, **kwargs)
    self.fields['start_date'].input_formats = ('%Y-%m-%dT%H:%M',)
    self.fields['end_date'].input_formats = ('%Y-%m-%dT%H:%M',)
