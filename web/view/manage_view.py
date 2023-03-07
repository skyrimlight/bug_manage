from django.shortcuts import render, redirect
from web.forms.wiki import WikiModelForm


def dashboard(request, project_id):
    return render(request, 'dashboard.html')


def statistics(request, project_id):
    return render(request, 'statistics.html')
