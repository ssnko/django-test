from datetime import datetime
from calendar import HTMLCalendar
from .models import Event, Mem

class Calendar(HTMLCalendar):
	def __init__(self, year=None, month=None):
		self.year = year
		self.month = month
		super(Calendar, self).__init__()

	# formats a day as a td
	# filter events by day
	def formatday(self, day, events):
		events_per_day = events.filter(time__day=day)
		self.count += len(events_per_day)
		self.week_add[self.seven_count] += len(events_per_day)
		if len(events_per_day) > 0:
			for i in range(len(events_per_day)):
				if events_per_day[i].name_id not in self.mem_count:
					self.mem_count.append(events_per_day[i].name_id)
		d = ''
		for event in events_per_day:
			count = Mem.objects.filter(id=event.name_id).values()[0]['count']
			if count == None:
				count = 0
			# d += f'<li> {event.get_html_url} </li>'

			if event.cancel == '취소':
				d += f'<li class="event_box" style="color:#adb5bd;">{event.time.strftime("%H:%M")} {event.name} 취소</li>'
			elif event.cancel == '차감':
				d += f'<li class="event_box" style="color:#adb5bd;">{event.time.strftime("%H:%M")} {event.name} {count}/{event.count} </li>'
			else:
				d += f'<li class="event_box">{event.time.strftime("%H:%M")} {event.name} {count}/{event.count} </li>'
		if day != 0:
			b = f"location.href='/schedule/?year={self.year}&month={self.month}&day={day}'"
			now = datetime.now()
			if f'{self.year}{self.month}{day}' == f'{now.year}{now.month}{now.day}':
				return f"<td onClick=location.href={b} class='cal_line'><div class='circle'><span>{day}</span></div><ul style='padding:0;'>{d}</ul></td>"
			return f"<td onClick=location.href={b} class='cal_line'><div class='date'><span>{day}</span></div><ul style='padding:0;'>{d}</ul></td>"
		return '<td class="cal_line"></td>'

	# formats a week as a tr
	def formatweek(self, theweek, events):
		week = ''
		self.count = 0
		self.mem_count = []
		week += f'<th>{self.week_count}주</th>'
		self.seven_count = 0
		for d, weekday in theweek:
			week += self.formatday(d, events)
			self.seven_count += 1
		week += f'<th class="cal_line">{self.count}</th>'
		week += f'<th class="cal_line">{len(self.mem_count)}</th>'
		self.week_count += 1
		return f'<tr> {week} </tr>'

	# formats a month as a table
	# filter events by year and month
	def formatmonth(self, account, withyear=True):
		events = Event.objects.filter(account=account, time__year=self.year, time__month=self.month).order_by('time')
		# print(events)
		#
		# events = Event.objects.filter(time__year=self.year, time__month=self.month)

		cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'

		s = '%s년 %s월' % (self.year, self.month)
		cal += '''<tr>
		    <th style="width: 70px;"></th>
		    <th colspan="9" class="month cal_line">%s</th>
		</tr>\n
		''' % s

		# cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
		# accounts += f'{self.formatweekheader()}\n'
		cal += '''<tr><th></th><th class="sun cal_line">일</th><th class="mon cal_line">월</th><th class="tue cal_line">화</th><th class="wed cal_line">수</th><th class="thu cal_line">목</th><th class="fri cal_line">금</th><th class="sat cal_line">토</th>
			<th class="cal_line" style="width: 70px;"><a>수업</a></th>
			<th class="cal_line" style="width: 70px;"><a>회원</a></th></tr>'''
		self.week_count = 1
		self.week_add = [0,0,0,0,0,0,0]
		for week in self.monthdays2calendar(self.year, self.month):
			cal += f'{self.formatweek(week, events)}\n'

		all_add = sum(self.week_add)

		cal += f'''<tr>
					<th>총합</th>
					<th class="cal_line">{self.week_add[0]}</th>
					<th class="cal_line">{self.week_add[1]}</th>
					<th class="cal_line">{self.week_add[2]}</th>
					<th class="cal_line">{self.week_add[3]}</th>
					<th class="cal_line">{self.week_add[4]}</th>
					<th class="cal_line">{self.week_add[5]}</th>
					<th class="cal_line">{self.week_add[6]}</th>
					<th class="cal_line" rowspan="2" colspan="2">{all_add}</th>
				</tr>'''

		if all_add == 0:
			cal += f'''<tr>
						<th><a>비율</a></th>
						<th class="cal_line">0%</th>
						<th class="cal_line">0%</th>
						<th class="cal_line">0%</th>
						<th class="cal_line">0%</th>
						<th class="cal_line">0%</th>
						<th class="cal_line">0%</th>
						<th class="cal_line">0%</th>
					</tr>'''
		else:
			cal += f'''<tr>
						<th>비율</th>
						<th class="cal_line">{round(self.week_add[0]/all_add*100)}%</th>
						<th class="cal_line">{round(self.week_add[1]/all_add*100)}%</th>
						<th class="cal_line">{round(self.week_add[2]/all_add*100)}%</th>
						<th class="cal_line">{round(self.week_add[3]/all_add*100)}%</th>
						<th class="cal_line">{round(self.week_add[4]/all_add*100)}%</th>
						<th class="cal_line">{round(self.week_add[5]/all_add*100)}%</th>
						<th class="cal_line">{round(self.week_add[6]/all_add*100)}%</th>
					</tr>'''
		return cal

class Calendar2(HTMLCalendar):
	def __init__(self, year=None, month=None, id=None):
		self.year = year
		self.month = month
		self.id = id
		super(Calendar2, self).__init__()

	# formats a day as a td
	# filter events by day
	def formatday(self, day, events):
		count = Mem.objects.filter(id=self.id).values()[0]['count']
		if count == None:
			count = 0
		filter_name = events.filter(name_id=self.id)
		events_per_day = filter_name.filter(time__day=day)
		self.count += len(events_per_day)
		self.week_add[self.seven_count] += len(events_per_day)
		if len(events_per_day) > 0:
			for i in range(len(events_per_day)):
				if events_per_day[i].name_id not in self.mem_count:
					self.mem_count.append(events_per_day[i].name_id)
		d = ''
		# for event in events_per_day:
		# 	# d += f'<li> {event.get_html_url} </li>'
		# 	d += f'<li> {event.name} - {event.time.strftime("%H:%M")} </li>'
		# if day != 0:
		# 	return f"<td><span class='date'>{day}</span><ul> {d} </ul></td>"
		# return '<td></td>'

		for event in events_per_day:
			if event.cancel != '취소':
				d += f'<li class="event_box">{event.time.strftime("%H:%M")} {event.name} {count}/{event.count} </li>'
			else:
				d += f'<li class="event_box">{event.time.strftime("%H:%M")} {event.name}</li>'
		if day != 0:
			b = f"location.href='/schedule/?year={self.year}&month={self.month}&day={day}&id={self.id}'"
			now = datetime.now()
			if f'{self.year}{self.month}{day}' == f'{now.year}{now.month}{now.day}':
				return f"<td onClick=location.href={b} class='cal_line'><div class='circle'><span>{day}</span></div><ul style='padding:0;'>{d}</ul></td>"
			return f"<td onClick=location.href={b} class='cal_line'><div class='date'><span>{day}</span></div><ul style='padding:0;'>{d}</ul></td>"
		return '<td class="cal_line"></td>'

	# formats a week as a tr
	def formatweek(self, theweek, events):
		week = ''
		self.count = 0
		self.mem_count = []
		week += f'<th>{self.week_count}주</th>'
		self.seven_count = 0
		for d, weekday in theweek:
			week += self.formatday(d, events)
			self.seven_count += 1
		week += f'<th class="cal_line">{self.count}</th>'
		week += f'<th class="cal_line">{len(self.mem_count)}</th>'
		self.week_count += 1
		return f'<tr> {week} </tr>'

	# formats a month as a table
	# filter events by year and month
	def formatmonth(self, account, withyear=True):
		events = Event.objects.filter(account=account, time__year=self.year, time__month=self.month).order_by('time')
		# events = Event.objects.filter(time__year=self.year, time__month=self.month)

		cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'

		s = '%s년 %s월' % (self.year, self.month)
		cal += '''<tr>
				    <th style="width: 70px;"></th>
				    <th colspan="9" class="month cal_line">%s</th>
				</tr>\n
				''' % s

		# cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
		# accounts += f'{self.formatweekheader()}\n'
		cal += '''<tr><th></th><th class="sun cal_line">일</th><th class="mon cal_line">월</th><th class="tue cal_line">화</th><th class="wed cal_line">수</th><th class="thu cal_line">목</th><th class="fri cal_line">금</th><th class="sat cal_line">토</th>
					<th class="cal_line" style="width: 70px;"><a style="font-size: 13px;">수업</a></th>
					<th class="cal_line" style="width: 70px;"><a style="font-size: 13px;">회원</a></th></tr>'''
		self.week_count = 1
		self.week_add = [0, 0, 0, 0, 0, 0, 0]
		for week in self.monthdays2calendar(self.year, self.month):
			cal += f'{self.formatweek(week, events)}\n'

		all_add = sum(self.week_add)

		cal += f'''<tr>
							<th>총합</th>
							<th class="cal_line">{self.week_add[0]}</th>
							<th class="cal_line">{self.week_add[1]}</th>
							<th class="cal_line">{self.week_add[2]}</th>
							<th class="cal_line">{self.week_add[3]}</th>
							<th class="cal_line">{self.week_add[4]}</th>
							<th class="cal_line">{self.week_add[5]}</th>
							<th class="cal_line">{self.week_add[6]}</th>
							<th class="cal_line" rowspan="2">{all_add}</th>
							<th class="cal_line" rowspan="2"></th>
						</tr>'''

		if all_add == 0:
			cal += f'''<tr>
								<th><a>비율</a></th>
								<th class="cal_line">0%</th>
								<th class="cal_line">0%</th>
								<th class="cal_line">0%</th>
								<th class="cal_line">0%</th>
								<th class="cal_line">0%</th>
								<th class="cal_line">0%</th>
								<th class="cal_line">0%</th>
							</tr>'''
		else:
			cal += f'''<tr>
								<th>비율</th>
								<th class="cal_line">{round(self.week_add[0] / all_add * 100)}%</th>
								<th class="cal_line">{round(self.week_add[1] / all_add * 100)}%</th>
								<th class="cal_line">{round(self.week_add[2] / all_add * 100)}%</th>
								<th class="cal_line">{round(self.week_add[3] / all_add * 100)}%</th>
								<th class="cal_line">{round(self.week_add[4] / all_add * 100)}%</th>
								<th class="cal_line">{round(self.week_add[5] / all_add * 100)}%</th>
								<th class="cal_line">{round(self.week_add[6] / all_add * 100)}%</th>
							</tr>'''
		return cal