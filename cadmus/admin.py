from django.contrib import admin
from .models import *
from django import forms
from concurrency.admin import ConcurrentModelAdmin

class EntryAdminForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = '__all__'

class EntryAdmin(ConcurrentModelAdmin):
    form = EntryAdminForm
    list_display = ('title', 'creator', 'initial_time')
    readonly_fields = ('title', 'slug', 'creator', 'content', 'initial_time', 'last_modified', 'version')

class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator')

admin.site.register(Entry, EntryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(User)