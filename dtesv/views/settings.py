from django.shortcuts import render, redirect
from dtesv.forms import SettingsForm
from dtesv.models import Settings

def settings_list(request):
    settings = Settings.objects.all()
    return render(request, 'settings.html', {'settings': settings})

def settings_create(request):
    if request.method == 'POST':
        form = SettingsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dtesv:settings_list')
    else:
        form = SettingsForm()
    return render(request, 'settings.html', {'form': form})

def settings_edit(request, pk):
    setting = Settings.objects.get(pk=pk)
    if request.method == 'POST':
        form = SettingsForm(request.POST, instance=setting)
        if form.is_valid():
            form.save()
            return redirect('dtesv:settings_list')
    else:
        form = SettingsForm(instance=setting)
    return render(request, 'settings_edit.html', {'form': form})

def settings_delete(request, pk):
    setting = Settings.objects.get(pk=pk)
    if request.method == 'POST':
        setting.delete()
        return redirect('dtesv:settings_list')
    return render(request, 'settings.html', {'setting': setting})