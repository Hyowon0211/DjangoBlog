from django.db import models
from django.contrib.auth.models import User
import os
# Create your models here.

class Post(models.Model):
    title = models.CharField(max_length=30)
    hook_text = models.CharField(max_length=100, blank=True)
    content = models.TextField()

    head_image = models.ImageField(upload_to='blog/images/%Y/%m/%d', blank=True)
    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    #author = models.ForeignKey(User, on_delete=models.CASCADE) # 모델에서 사용자 사라지면 ㄱ 사용자가 작성한 포스트도 다 삭제되라
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL) # user삭제돼도 포스트는 남겨.
    def __str__(self):
        return f'[{self.pk}] {self.title} ::: {self.author}'


    def get_absolute_url(self):
        return f'/blog/{self.pk}'


    def get_file_name(self):
        return os.path.basename(self.file_upload.name)

    def get_file_ext(self):
        return self.get_file_name().split('.')[-1]   # -1 은 마지막 요소






