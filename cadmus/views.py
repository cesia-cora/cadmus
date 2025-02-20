from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.dates import MonthArchiveView, YearArchiveView
from django.views.generic import ListView
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.db import IntegrityError
from django.core.paginator import Paginator
from django.utils import timezone
from django.conf import settings
from datetime import date, datetime, timedelta
from django.utils.html import strip_tags
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from calendar import monthcalendar
#from cryptography.fernet import Fernet, InvalidToken
from .models import *
from .forms import *

"""key = Fernet.generate_key()
print(key.decode())"""

"""key = settings.FERNET_KEY
if key is None:
    raise ValueError("FERNET_KEY environment variable is not set.")
cipher_suite = Fernet(key.encode())

def encrypt_text(text):
    try:
        return cipher_suite.encrypt(text.encode()).decode()
    except Exception as e:
        print(f"Encrypt error: {e}")
        return None

def decrypt_text(encrypted_text):
	try:
		return cipher_suite.decrypt(encrypted_text.encode()).decode()
	except InvalidToken:
		print("Encrypted token is invalid or has been altered.")
	except Exception as e:
		print(f"Encrypt error: {e}")
		return None"""

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
		date_query = self.request.GET.get("date")
		object_list = Entry.objects.filter(
				Q(title__icontains=query) | Q(content__icontains=query)
			)

		if date_query:
			try:
				date = datetime.strptime(date_query, '%Y-%m-%d')
				object_list = object_list.filter(initial_time__date=date)
			except ValueError:
				pass

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
			new_entry.content = new_entry.content
			new_entry.creator = request.user
			new_entry.save()

		return HttpResponseRedirect(reverse("cadmus:index"))

	else:
		return render(request, "cadmus/create_entry.html", {
			"entry_form": entry_form
		})

def entry(request, slug):

	entry = Entry.objects.get(slug=slug)
	entry.content = entry.content

	return render(request, "cadmus/entry.html", {
		"entry": entry
	})

def download_entry(request, slug):

	entry = Entry.objects.get(slug=slug)

	# pdf generator
	filename = f'{entry.slug}'
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = f'attachment; filename="{filename}".pdf"'

	# create canvas object and generate pdf content
	p = canvas.Canvas(response, pagesize=letter)

	y = 700
	page_width, page_height = letter

	p.setFillColorRGB(0.29296875, 0.453125, 0.609375)
	title_height = 40
	p.setFont('Helvetica', 20)
	p.drawString(60, y + title_height, f'{entry.title}')

	p.setFillColorRGB(0.078125, 0.078125, 0.078125)
	p.setFont("Helvetica", 10)
	if entry.initial_time:
		created_at = entry.initial_time.strftime('%B %d %Y %H:%M')
	else:
		created_at = "N/A"
	if entry.last_modified:
		last_updated = entry.last_modified.strftime('%B %d %Y %H:%M')
	else:
		last_updated = "N/A"
	p.drawString(60, y + title_height - 30, f'Created at: {created_at}')
	p.drawString(60, y + title_height - 50, f'Last updated: {last_updated}')
	
	p.setFillColorRGB(0.078125, 0.078125, 0.078125)
	p.setFont('Helvetica', 11)
	content_entry = f'{entry.content}'
	content = strip_tags(content_entry)
	paragraphs = content.split('\n\n')
	line_height = 10
	line_spacing = 10
	max_line_width = page_width - 120

	# Adjust the starting position of the content to avoid overlap
	y = y + title_height - 90

	for i, paragraph in enumerate(paragraphs):
		lines = paragraph.split('\n')
		current_y = y - i * (line_height + line_spacing)
		for line in lines:
			line = line.strip()
			if line:
				words = line.split()
				current_line = ""

				for word in words:
					if p.stringWidth(current_line + " " + word) < max_line_width:
						current_line += " " + word
					else:
						p.drawString(60, current_y, current_line.strip())
						current_line = word
						current_y -= line_height + line_spacing
				if current_line:
					p.drawString(60, current_y, current_line.strip())
					current_y -= line_height + line_spacing

	p.showPage()
	p.save()

	return response

def edit_entry(request, slug):

	entry = Entry.objects.get(slug=slug)
	form = EntryForm(instance=entry)

	if request.method == "POST":
		form = EntryForm(request.POST, instance=entry)

		if form.is_valid():

			form.save()

			return HttpResponseRedirect(reverse("cadmus:entry", args=[slug]))

		else:
			print(form.errors)

	return render(request, "cadmus/update_entry.html", {
		"entry": entry,
		"edit_form": form
	})

def delete_entry(request, slug):

	Entry.objects.get(slug=slug).delete()

	return HttpResponseRedirect(reverse("cadmus:index"))

def archive_month(request):

	return render(request, "cadmus/entry_archive_month.html")

def calendar(request):
	today = date.today()
	year = int(request.GET.get('year', today.year))
	month = int(request.GET.get('month', today.month))

	cal = monthcalendar(year, month)

	start_date = date(year, month, 1)
	end_date = start_date + timedelta(days=31)
	end_date = end_date.replace(day=1) - timedelta(days=1)
	entries = Entry.objects.filter(initial_time__date__range=[start_date, end_date])

	entry_dates = {}

	for entry in entries:
		date_str = entry.initial_time.date().strftime('%Y-%m-%d')
		entry_dates[date_str] = entry

	prev_month = date(year, month, 1) - timedelta(days=1)
	next_month = date(year, month, 28) + timedelta(days=4)
	next_month = next_month - timedelta(days=next_month.day)

	return render(request, "cadmus/calendar.html", {
		"calendar": cal,
		"entry_dates": entry_dates,
		"year": year,
		"month": month,
		"prev_month": prev_month,
		"next_month": next_month
	})

def day_entries(request, year, month, day):
	date = datetime(year, month, day)
	entries = Entry.objects.filter(initial_time__date=date)
	return render(request, 'cadmus/entry_archive_date.html', {
		'entries': entries,
		'date': date
	})