from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views
from .models import *
from .views import EntryMonthArchiveView, EntryYearArchiveView, SearchResultsView

app_name = 'cadmus'

urlpatterns = [
    path('', views.index, name='index'),
    path('search', SearchResultsView.as_view(), name='search_results'),
    path('create/', views.create_entry, name="create"),
    path('entry/<slug:slug>', views.entry, name='entry'),
    path('entry/<slug:slug>/download', views.download_entry, name='download_entry'),
    path('register', views.register, name="register"),
    path('login', views.login_view, name="login"),
    path('logout', views.logout_view, name="logout"),
    path('entry/<slug:slug>/edit', views.edit_entry, name="edit"),
    path('entry/<slug:slug>/delete', views.delete_entry, name="delete"),
    path('<int:year>', EntryYearArchiveView.as_view(), name="archive_year"),
    path('<int:year>/<int:month>', EntryMonthArchiveView.as_view(month_format='%m'), name="archive_month"),
    path('calendar', views.calendar, name='calendar')
]

# make all static image files available for all templates
urlpatterns += staticfiles_urlpatterns()