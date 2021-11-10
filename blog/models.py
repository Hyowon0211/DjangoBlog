from django.db import models
from django.contrib.auth.models import User
from markdownx.utils import markdown
from markdownx.models import MarkdownxField
import os
# Create your models here.
#from single_pages.models import Hello
import single_pages


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/blog/tag/{self.slug}'



class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/blog/category/{self.slug}'

    class Meta:
        verbose_name_plural = 'Categories'  #복수형이걸로 쓰겠다


class Post(models.Model):
    title = models.CharField(max_length=30)
    hook_text = models.CharField(max_length=100, blank=True)
    #content = models.TextField()
    content = MarkdownxField()

    head_image = models.ImageField(upload_to='blog/images/%Y/%m/%d', blank=True)
    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    #author = models.ForeignKey(User, on_delete=models.CASCADE) # 모델에서 사용자 사라지면 ㄱ 사용자가 작성한 포스트도 다 삭제되라
    author = models.ForeignKey(User, null=True,  on_delete=models.SET_NULL) # user삭제돼도 포스트는 남겨.

    category = models.ForeignKey(Category, null=True, blank=True,on_delete=models.SET_NULL)
# null=True는 없어졌을 때 null로 한다는거지 첨부터 등록할 때부터 값을 안넣어도 된다 아님
    # 첨부터 안넣어도 되는거 허용하려면 blank=True해야함
    tags = models.ManyToManyField(Tag, blank=True)
                            # blank=True admin자체에서 빈값으로 저장하는것을 허용
    h = models.ManyToManyField('single_pages.Hello', blank=True)
    def __str__(self):
        return f'[{self.pk}] {self.title} ::: {self.author}'


    def get_absolute_url(self):
        return f'/blog/{self.pk}'


    def get_file_name(self):
        return os.path.basename(self.file_upload.name)

    def get_file_ext(self):
        return self.get_file_name().split('.')[-1]   # -1 은 마지막 요소

    def get_content_markdown(self):
        return markdown(self.content)






