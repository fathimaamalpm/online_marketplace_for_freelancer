from django.urls import path
from .import views

urlpatterns = [
    path('index/',views.index,name='index'),
    path('root/', views.root_redirect, name='main_login_page'),
    path('login/',views.login_view,name='login'),
    path('register/',views.register_employee,name='register'),
    path('logout',views.logout_user,name='logout_user')
]