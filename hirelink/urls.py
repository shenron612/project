from django.contrib import admin
from django.urls import path
from skillsync import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('search-workers/', views.search_workers, name='search_workers'),
    path('make-payment/', views.make_payment, name='make_payment'),
    path('stk-push/', views.stk_push, name='stk_push'),
    path('mpesa-callback/', views.mpesa_callback, name='mpesa_callback'),
    path('about/', views.about, name='about'),
]
