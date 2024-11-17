from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.pomodoro_form, name='pomodoro_form'),
    path('plot/', views.plot_view, name='plot_view'),
    path('info/', views.numeric_info, name='numeric_info'),
]