from django.contrib import admin
from django.urls import path, include
from giga_chad_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('giga_chad_app.urls'))
]