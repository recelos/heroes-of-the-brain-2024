from django.shortcuts import render, redirect
from django import forms

class PomodoroForm(forms.Form):
    work_minutes = forms.IntegerField(label="Minutes of Work", min_value=1)
    rest_minutes = forms.IntegerField(label="Minutes of Rest", min_value=1)

def pomodoro_form(request):
    if request.method == "POST":
        form = PomodoroForm(request.POST)
        if form.is_valid():
            work_minutes = form.cleaned_data['work_minutes']
            rest_minutes = form.cleaned_data['rest_minutes']

            response = redirect('plot_view')
            response.set_cookie('work_minutes', work_minutes, max_age=3600)
            response.set_cookie('rest_minutes', rest_minutes, max_age=3600)
            return response
    else:
        form = PomodoroForm()

    return render(request, 'giga_chad_app/pomodoro_form.html', {'form': form})


def numeric_info(request):
    info = {'total_sessions': 5, 'total_time': 150}
    return render(request, 'giga_chad_app/numeric_info.html', {'info': info})

def plot_view(request):
    return render(request, 'giga_chad_app/plot_view.html', {'image_base64': 0})
