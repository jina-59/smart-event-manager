from django.db import models
from django.conf import settings

class Event(models.Model):
    title = models.CharField(max_length=200)       # 이벤트 제목
    description = models.TextField()               # 설명
    date = models.DateTimeField()                  # 일시
    location = models.CharField(max_length=255)    # 장소
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title