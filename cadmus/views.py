from cmath import log
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic.dates import MonthArchiveView, YearArchiveView
from django.views.generic import ListView
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db import IntegrityError
from django.core.paginator import Paginator
from .models import *
from .forms import *

class EntryMonthArchiveView(MonthArchiveView):
    queryset = Entry.objects.all()
    date_field = "initial_time"
    make_object_list = True
    allow_future = True

class EntryYearArchiveView(YearArchiveView):
    queryset = Entry.objects.all()
    date_field = "initial_time"
    make_object_list = True
    allow_future = True
    
class SearchResultsView(ListView):
	model = Entry
	template_name = 'cadmus/search_results.html'
	
	def get_queryset(self):
		query = self.request.GET.get("q")
		object_list = Entry.objects.filter(
				Q(title__icontains=query) | Q(content__icontains=query)
			)
		return object_list

def index(request):
	# add [:number] to limit entries
	entries = Entry.objects.all().order_by('-initial_time')
	paginator = Paginator(entries, 5)

	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)

	return render(request, "cadmus/index.html", {
		"page_obj": page_obj
	})

# def all_entries(request):

# 	entries = Entry.objects.all()
# 	paginator = Paginator(entries, 12)

# 	page_number = request.GET.get('page')
# 	page_obj = paginator.get_page(page_number)

# 	return render(request, "cadmus/all_entries.html", {
# 		"page_obj": page_obj,
# 	})


def login_view(request):
	if request.method == "POST":

		username = request.POST["username"]
		password = request.POST["password"]
		user = authenticate(request, username = username, password = password)

		if user is not None:
			login(request, user)
			return HttpResponseRedirect(reverse("cadmus:index"))

		else:
			return render(request, "cadmus/login.html", {
				"message": "Invalid username and/or password."
			})

	else:
		return render(request, "cadmus/login.html")


def logout_view(request):
	logout(request)
	return HttpResponseRedirect(reverse("cadmus:index"))

def register(request):

	if request.method == "POST":
		username = request.POST["username"]
		email = request.POST["email"]

		password = request.POST["password"]
		confirmation = request.POST["confirmation"]

		if password != confirmation:
			return render(request, "cadmus/register.html", {
				"message": "Passwords must match."
			})

		try:
			user = User.objects.create_user(username, email, password)  # type: ignore
			user.save()

		except IntegrityError:
			return render(request, "cadmus/register.html", {
					"message": "Username already taken."
			})

		login(request, user)
		return HttpResponseRedirect(reverse("cadmus:index"))

	else:
		return render(request, "cadmus/register.html")

def create_entry(request):

	entry_form = EntryForm(request.POST or None)

	if request.method == "POST":

		if entry_form.is_valid():

			new_entry = entry_form.save(commit=False)
			new_entry.creator = request.user
			new_entry.save()

		return HttpResponseRedirect(reverse("cadmus:index"))

	else:
		return render(request, "cadmus/create_entry.html", {
			"entry_form": entry_form
		})

def entry(request, slug):

	entry = Entry.objects.get(slug=slug)

	return render(request, "cadmus/entry.html", {
		"entry": entry
	})

def edit_entry(request, slug):

	entry = Entry.objects.get(slug=slug)
	form = EntryForm(instance=entry)

	if request.method == "POST":
		form = EntryForm(request.POST or None, instance=entry)

		if form.is_valid():

			update_entry = form.save(commit=False)
			update_entry.save()

			return HttpResponseRedirect(reverse("cadmus:index"))

	return render(request, "cadmus/update_entry.html", {
		"entry": entry,
		"edit_form": form
	})

def delete_entry(request, slug):

	Entry.objects.get(slug=slug).delete()

	return HttpResponseRedirect(reverse("cadmus:index"))

def archive_month(request):

	return render(request, "cadmus/entry_archive_month.html")