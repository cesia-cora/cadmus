from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.dates import MonthArchiveView, YearArchiveView
from django.views.generic import ListView
from django.db.models import Q
from concurrency.exceptions import RecordModifiedError
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.urls import reverse
from django.db import IntegrityError, transaction
from django.core.paginator import Paginator
from django.utils import timezone
from django.conf import settings
from datetime import date, datetime, timedelta
from calendar import monthcalendar
from .models import *
from .forms import *
from .services import *

class EntryMonthArchiveView(MonthArchiveView):
    queryset = Entry.objects.select_related('creator').all()
    date_field = "initial_time"
    make_object_list = True
    allow_future = True

class EntryYearArchiveView(YearArchiveView):
    queryset = Entry.objects.select_related('creator').all()
    date_field = "initial_time"
    make_object_list = True
    allow_future = True
    
class SearchResultsView(ListView):
	model = Entry
	template_name = 'cadmus/search_results.html'
	
	def get_queryset(self):
		query = self.request.GET.get("q")
		date_query = self.request.GET.get("date")

		if not query:
			return Entry.objects.none()
			
		object_list = Entry.objects.filter(
				Q(title__icontains=query) | Q(content__icontains=query)
			)

		object_list = object_list.filter(creator=self.request.user).select_related('creator')

		if date_query:
			try:
				date = datetime.strptime(date_query, '%Y-%m-%d')
				object_list = object_list.filter(initial_time__date=date)
			except ValueError:
				pass

		return object_list


def index(request):
	# add [:number] to limit entries
	if request.user.is_authenticated:
		entries = Entry.objects.filter(creator=request.user).select_related('creator').all().order_by('-initial_time')
	else:
		entries = Entry.objects.none()

	paginator = Paginator(entries, 5)

	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)

	return render(request, "cadmus/index.html", {
		"page_obj": page_obj
	})

def settings(request):
	return render(request, "cadmus/settings.html")

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
			with transaction.atomic():
				user = User.objects.create_user(username, email, password)  # type: ignore
				user.save()
				login(request, user)

		except IntegrityError:
			return render(request, "cadmus/register.html", {
					"message": "Username already taken."
			})

		return HttpResponseRedirect(reverse("cadmus:index"))

	else:
		return render(request, "cadmus/register.html")

def create_entry(request):

	entry_form = EntryForm(request.POST or None)

	if request.method == "POST":

		if entry_form.is_valid():
			with transaction.atomic():

				new_entry = entry_form.save(commit=False)
				new_entry.creator = request.user
				new_entry.save()
				entry_form.save_m2m()

				new_tags_str = entry_form.cleaned_data.get('new_tags', '')
				for raw in [t.strip() for t in new_tags_str.split(',') if t.strip()]:
					tag, created = Tag.objects.get_or_create(name=raw, creator=request.user)
					new_entry.tags.add(tag)

		return HttpResponseRedirect(reverse("cadmus:index"))

	else:
		return render(request, "cadmus/create_entry.html", {
			"entry_form": entry_form
		})

def entry(request, slug):

	entry = Entry.objects.select_related('creator').get(slug=slug, creator=request.user)
	entry.content = entry.decrypted_content

	return render(request, "cadmus/entry.html", {
		"entry": entry
	})

def edit_entry(request, slug):

	entry = Entry.objects.select_related('creator').get(slug=slug, creator=request.user)
	entry.content = entry.decrypted_content
	form = EntryForm(instance=entry)

	if request.method == "POST":
		try:
			with transaction.atomic():
				form = EntryForm(request.POST, instance=entry)

				if form.is_valid():
					form.save()
					form.save_m2m()

					new_tags_str = form.cleaned_data.get('new_tags', '')
					for raw in [t.strip() for t in new_tags_str.split(',') if t.strip()]:
						tag, created = Tag.objects.get_or_create(name=raw, creator=request.user.id)
						entry.tags.add(tag)

					messages.success(request, "Entry updated successfully.")
					return HttpResponseRedirect(reverse("cadmus:entry", args=[slug]))

				else:
					print(form.errors)
		except RecordModifiedError:
			messages.error(request, "This entry was modified by another session. Please reload and try again.")

	return render(request, "cadmus/update_entry.html", {
		"entry": entry,
		"edit_form": form
	})

def delete_entry(request, slug):

	with transaction.atomic():
		entry = Entry.objects.select_for_update('creator').get(slug=slug, creator=request.user)
		entry.delete()

	return HttpResponseRedirect(reverse("cadmus:index"))

def entries_by_tag(request, slug):
    tag = Tag.objects.get(slug=slug, creator=request.user)
    entries = tag.entries.filter(creator=request.user).order_by('-initial_time')
    paginator = Paginator(entries, 5)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, "cadmus/index.html", {"page_obj": page_obj, "current_tag": tag})

def archive_month(request):
	return render(request, "cadmus/entry_archive_month.html")

def download_entry(request, slug):
    entry = Entry.objects.select_related('creator').get(slug=slug, creator=request.user)

    pdf_buffer = generate_entry_pdf(entry)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=\"{entry.slug}.pdf\"'
    response.write(pdf_buffer.getvalue())
    pdf_buffer.close()

    return response

def calendar(request):
	today = date.today()

	monthpicker = request.GET.get('monthpicker')

	if monthpicker:
		try:
			year, month = map(int, monthpicker.split('-'))
		except ValueError:
			year = int(request.GET.get('year', today.year))
			month = int(request.GET.get('month', today.month))
	else:
		year = int(request.GET.get('year', today.year))
		month = int(request.GET.get('month', today.month))
	
	month_date = date(year, month, 1)
	cal = monthcalendar(year, month)

	start_date = date(year, month, 1)
	end_date = start_date + timedelta(days=31)
	end_date = end_date.replace(day=1) - timedelta(days=1)
	entries = Entry.objects.filter(initial_time__date__range=[start_date, end_date]).select_related(creator=request.user).only('id', 'initial_time', 'slug', 'title')

	entry_dates = {}

	for entry in entries:
		date_str = entry.initial_time.date().strftime('%Y-%m-%d')
		entry_dates[date_str] = entry

	prev_month = month_date - timedelta(days=1)
	next_month = (month_date.replace(day=28) + timedelta(days=4))

	prev_year = date(year - 1, month, 1)
	next_year = date(year + 1, month, 1)

	entry_days = set()
	for e in entries:
		entry_days.add(e.initial_time.day)

	return render(request, "cadmus/calendar.html", {
		"calendar": cal,
		"entry_dates": entry_dates,
		"year": year,
		"month": month,
		"month_date": month_date,
		"prev_month": prev_month,
		"next_month": next_month,
		"prev_year": prev_year,
		"next_year": next_year,
		"entry_days": entry_days
	})

def day_entries(request, year, month, day):
	start = datetime(year, month, day, 0, 0, 0)

	if settings.USE_TZ:
		start = timezone.make_aware(start, timezone.get_current_timezone())
	end = start + timedelta(days=1)

	entries = Entry.objects.filter(initial_time__gte=start, initial_time__lt=end, creator=request.user).select_related(creator=request.user).order_by('-initial_time')
	day_date = start.date()

	return render(request, 'cadmus/entry_archive_date.html', {
		'entries': entries,
		'date': day_date
	})


def username_change(request):
    if request.method == "POST":
        form = UsernameChangeForm(request.user, request.POST)
        
        if form.is_valid():
            try:
                new_username = form.cleaned_data["username"]
                change_username(request.user, new_username)
                return redirect("cadmus:index")
            except ValueError as e:
                form.add_error('username', str(e))
    else:
        form = UsernameChangeForm(request.user, initial={"username": request.user.username})
    
    return render(request, "cadmus/registration/username_change.html", {
		"form": form
		})


def password_reset(request):
    if request.method == "POST":
        p_form = PasswordChangeForm(request.user, request.POST)
        
        if p_form.is_valid():
            try:
                new_password = p_form.cleaned_data["new_password1"]
                change_user_password(request.user, new_password)
                update_session_auth_hash(request, request.user)
                return redirect("cadmus:index")
            except Exception as e:
                p_form.add_error(None, str(e))
    else:
        p_form = PasswordChangeForm(request.user)

    return render(request, "cadmus/registration/password_reset_form.html", {
		"form": p_form
		})