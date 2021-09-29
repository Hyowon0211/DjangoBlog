from django.urls import path
from . import views

urlpatterns = [ # 서버ip/
    path('', views.langing), # 서버IP/
    path('about_me/', views.about_me)  # 서브 IP/about_me/
]