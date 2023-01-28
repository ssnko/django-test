from django.db import models
from django.urls import reverse

class Event(models.Model):
    name = models.CharField(max_length=200)
    time = models.DateTimeField(null=True, blank=True)
    count = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    name_id = models.CharField(max_length=200, null=True, blank=True)
    account = models.CharField(max_length=200)
    cancel = models.CharField(max_length=2, null=True, blank=True)  # 스케쥴 취소
    cancel_comment = models.TextField(null=True, blank=True)  # 희망 운동시간
    # start_time = models.DateTimeField()
    # end_time = models.DateTimeField()

    @property
    def get_html_url(self):
        url = reverse('accounts:event_edit', args=(self.id,))
        return f'<a href="{url}"> {self.name} </a>'

class Mem(models.Model):
    name = models.CharField(max_length=200, null=True)  # 회원 이름
    phone = models.CharField(max_length=200, null=True, blank=True)  # 폰 번호
    start_date = models.DateField(null=True, blank=True)  # 시작일
    end_date = models.DateField(null=True, blank=True)  # 종료일


    count = models.CharField(max_length=200, blank=True, null=True)  # pt횟수
    food = models.CharField(max_length=200, null=True, blank=True)  # 식단진행
    job = models.CharField(max_length=200, null=True, blank=True)  # 직업
    residence = models.CharField(max_length=200, null=True, blank=True)  # 거주
    stature = models.CharField(max_length=200, null=True, blank=True)  # 키
    age = models.CharField(max_length=200, null=True, blank=True)  # 나이
    weight = models.CharField(max_length=200, null=True, blank=True)  # 체중
    muscle = models.CharField(max_length=200, null=True, blank=True)  # 골격근량
    fat = models.CharField(max_length=200, null=True, blank=True)  # 체지방률
    date = models.CharField(max_length=200, null=True, blank=True)  # 체중/골격근량/체지방률 날짜
    hope_time = models.TextField(null=True, blank=True)  # 희망 운동시간
    health_career = models.TextField(null=True, blank=True)  # 운동경력
    note1 = models.TextField(null=True, blank=True)  # 특이사항 및 병력
    note2 = models.TextField(null=True, blank=True)  # 운동목적 및 방향
    account = models.CharField(max_length=200, null=True)  # 로그인 계정 구분
    membership_start_date = models.DateField(null=True, blank=True)  # 회원권 시작일
    membership_end_date = models.DateField(null=True, blank=True)  # 회원권 종료일
    health_start_date = models.DateField(null=True, blank=True)  # 헬스 시작일
    health_end_date = models.DateField(null=True, blank=True)  # 헬스 종료일
    class_start_date = models.DateField(null=True, blank=True)  # 수업 시작일
    class_end_date = models.DateField(null=True, blank=True)  # 수업 종료(예상)일

    resist_CHOICES = (
        ('', ''),
        ('워크인', '워크인'),
        ('재등록', '재등록'),
        ('SNS', 'SNS'),
        ('OT', 'OT'),
    )
    resist_category = models.CharField(max_length=3, choices=resist_CHOICES, blank=True, default='')  # 등록 구분(초이스필드) -워크인,재등록,SNS,OT

    payment_CHOICES = (
        ('', ''),
        ('카드', '카드'),
        ('현금', '현금'),
        ('이체', '이체'),
    )
    payment = models.CharField(max_length=2, choices=payment_CHOICES, blank=True, default='')  # 결제 방식(초이스필드)
    empty1 = models.BooleanField(default=False)  # 비고칸
    empty2 = models.BooleanField(default=False)  # 비고칸
    empty3 = models.BooleanField(default=False)  # 비고칸
    empty4 = models.BooleanField(default=False)  # 비고칸
    empty5 = models.BooleanField(default=False)  # 비고칸
    alarm = models.TextField(null=True, blank=True)  # 알림칸
    alarm_check = models.BooleanField(default=False)  # 비고칸
    # photo = models.FileField(upload_to = 'uploads/', null=True)
    money = models.CharField(max_length=200, blank=True)  # 금액
    re_data = models.TextField(blank=True)  # 재 등록시 과거 데이터 저장

    @property
    def get_html_url(self):
        url = reverse('accounts:event_mem_edit', args=(self.id,))
        return f'<a href="{url}"> {self.name} </a>'

class Option(models.Model):
    account = models.CharField(max_length=200, null=True, blank=True)  # 로그인 계정 구분
    count = models.CharField(max_length=200, null=True, blank=True)  # 비고칸
    empty1 = models.CharField(max_length=200, null=True, blank=True)  # 비고칸
    empty2 = models.CharField(max_length=200, null=True, blank=True)  # 비고칸
    empty3 = models.CharField(max_length=200, null=True, blank=True)  # 비고칸
    empty4 = models.CharField(max_length=200, null=True, blank=True)  # 비고칸
    empty5 = models.CharField(max_length=200, null=True, blank=True)  # 비고칸
    count_money = models.TextField(blank=True)  # 횟수에 따른 금액 변화 설정

    @property
    def get_html_url(self):
        url = reverse('accounts:event_edit', args=(self.id,))
        return f'<a href="{url}"> {self.name} </a>'


# python manage.py createsuperuser
# python manage.py makemigrations
# python manage.py migrate
# python manage.py runserver
# python manage.py runserver 0.0.0.0:8080

# git add .
# git commit -m "message"
# git push -u origin master