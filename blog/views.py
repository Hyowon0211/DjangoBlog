from django.shortcuts import render
from django.views.generic import ListView, DetailView

from .models import Post, Category

# Create your views here.


# 템플릿 연결해주는게 뷰 역할

class PostList(ListView) :
    model = Post
    ordering = '-pk'  # 최신순으로

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostList, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        return context
 #   template_name = 'blog/index.html'    # 직접부르기
 # post_list.html


class PostDetail(DetailView) :
    model = Post

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostDetail, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        return context
# post_detail.html       # model이름_detail.html 이라는 템플릿이 불리어지게 됨. 자동으로?? .  html또 만들필요없다했는데 난 걍 만들어봄




# 함수로 템플릿 불러오기? 위에껀 클래스로 불러오기?

# def index(request) :
#     posts = Post.objects.all().order_by('-pk')
#
#     # template/blog/index.html
#     return render(request, 'blog/index.html',
#                   {
#                       'posts' : posts ,
#                   }
#                   )
#
#
# def single_post_page(request, pk) :
#     post = Post.objects.get(pk=pk)
#
#     return render(request, 'blog/single_post_page.html',
#                   {
#                       'post' : post
#                   }
#                   )



