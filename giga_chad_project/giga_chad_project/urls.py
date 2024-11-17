from django.contrib import admin
from django.urls import path
from giga_chad_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pomodoro/', views.pomodoro_form, name='pomodoro_form'),
    path('plot/', views.plot_view, name='plot_view'),
    path('info/', views.numeric_info, name='numeric_info'),
]