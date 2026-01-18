from django.contrib import admin
from .models import *
from django import forms

class EntryAdminForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = '__all__'

class EntryAdmin(admin.ModelAdmin):
    form = EntryAdminForm
    list_display = ('title', 'creator', 'initial_time')
    readonly_fields = ('title', 'slug', 'creator', 'content', 'initial_time')

admin.site.register(Entry, EntryAdmin)

admin.site.register(User)