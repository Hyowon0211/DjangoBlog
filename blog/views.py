from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.core.exceptions import PermissionDenied
from .models import Post, Category, Tag
from .forms import CommentForm
from django.db.models  import Q


# 템플릿 연결해주는게 뷰 역할

def new_comment(request, pk):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, pk=pk)
        if request.method == 'POST':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                return redirect(comment.get_absolute_url())
        else:
            return redirect(post.get_absolute_url())
    else:
        raise PermissionDenied

class PostCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category'] # tag는 사용자가 추가 하게 하려고 뺌

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):
        current_user = self.request.user
                        # 로그인 되어있고
        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser) :
            form.instance.author = current_user
            response = super(PostCreate, self).form_valid(form)
            tags_str = self.request.POST.get('tags_str') # post_form에서 name ='tags_str'이거랑 일치해야함
            if tags_str:
                tags_str = tags_str.strip() # 불필요한 공백 지우기
                tags_str = tags_str.replace(',', ';') # ,를 ;로 대체 (모든 태그는 다 ;로 구분되게)
                tags_list = tags_str.split(';')
                for t in tags_list:
                    t = t.strip()
                    tag, is_tag_created = Tag.objects.get_or_create(name=t)
                            #get_or_create 메소드 !! 있으면 get없으면 create
                    if is_tag_created:
                        tag.slug = slugify(t, allow_unicode=True)
                        tag.save()
                    self.object.tags.add(tag)
            return response
        else:
            return redirect('/blog/')


def tag_page(request, slug):
        tag = Tag.objects.get(slug=slug)
        post_list = tag.post_set.all() # 해당 tag와 연결되어있는모든 post데이터 가져와 # Post.objects.filter(tags=tag)다대다라 이렇겐 안됨

        return render(request, 'blog/post_list.html',
                      {
                          'post_list' : post_list,
                           'categories' : Category.objects.all(),
                            'no_category_post_count' : Post.objects.filter(category=None).count(),
                            'tag' : tag,
                      }

                      )

def category_page(request, slug):
    if slug == 'no_category':
        category = '미분류'
        post_list = Post.objects.filter(category=None)
    else:
        category = Category.objects.get(slug=slug)
        post_list = Post.objects.filter(category=category)
    return render(request, 'blog/post_list.html',
                  { # 기존의 post_list 템플릿 그대로 쓰는데!!
                      # category 를 받아와서 그 카테고리 포스트만 보여주게(filter() 사용)
                      'post_list' :post_list,
                      'categories' : Category.objects.all(),
                      'no_category_post_count' : Post.objects.filter(category=None).count(), # 카테고리가 없는 글 개수
                      'category' : category
                  }
    )


class PostUpdate(LoginRequiredMixin, UpdateView): # 모델명_form (자동) -> 근데 post create랑 똑같아서 헷갈리니까 별ㅗ로 만들어줘야함
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']

    template_name = 'blog/post_update_form.html'
    # 장고에서 get으로 접근했는지 post로 접근 해는지 확인해주는 함수 dispatch
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostUpdate, self).get_context_data()
        if self.object.tags.exists():
            tags_str_list = list()
            for t in self.object.tags.all() :
                tags_str_list.append(t.name)
            context['tag_str_default'] = '; '.join(tags_str_list)
        return context

    def form_valid(self, form):  # update인 경우에는 dispatch에서 유저 권한체크 해주기때문에 안해도됨
        response = super(PostUpdate, self).form_valid(form)
        self.object.tags.clear()
        tags_str = self.request.POST.get('tags_str')
        if tags_str:
            tags_str = tags_str.strip()
            tags_str = tags_str.replace(',', ';')
            tags_list = tags_str.split(';')
            for t in tags_list:
                t = t.strip()
                tag, is_tag_created = Tag.objects.get_or_create(name=t)
                if is_tag_created:
                    tag.slug = slugify(t, allow_unicode=True)
                    tag.save()
                self.object.tags.add(tag)
        return response


class PostList(ListView):
    model = Post
    ordering = '-pk'  # 최신순으로
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostList, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        #context['user'] = self.request.user
        return context
 #   template_name = 'blog/index.html'    # 직접부르기
 # post_list.html



class PostSearch(PostList):
    paginate_by = None

    def get_queryset(self):
        q = self.kwargs['q']
        post_list = Post.objects.filter(
            Q(title__contains=q) | Q(tags__name__contains=q)
        ).distinct()
        return post_list

    def get_context_data(self, **kwargs):
        context = super(PostSearch, self).get_context_data()
        q = self.kwargs['q']
        context['search_info'] = f'Search : {q}({self.get_queryset().count()})'

        return context

class PostDetail(DetailView) :
    model = Post

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostDetail, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
       # context['user'] = self.request.user # 이거 안해도 post_detail.html에서 user쓸 수 있는거야..?
        context['comment_form'] = CommentForm
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




