from django.urls import path
from . import views

urlpatterns = [
   # path('<int:pk>/', views.single_post_page),
   # path('',views.index), # 서버IP/blog


    # 뷰를 부르는 부분을 함수가 아니라 클래스로 부름
    path('<int:pk>/', views.PostDetail.as_view()),
    path('', views.PostList.as_view()),

]