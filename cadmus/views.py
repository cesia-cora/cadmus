from io import BytesIO
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.dates import MonthArchiveView, YearArchiveView
from django.views.generic import ListView
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.urls import reverse
from django.db import IntegrityError, transaction
from django.core.paginator import Paginator
from django.utils import timezone
from django.conf import settings
from datetime import date, datetime, timedelta
from django.utils.html import strip_tags
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.platypus import PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from calendar import monthcalendar
from .models import *
from .forms import *

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
	
	@method_decorator(cache_page(60 * 5))
	def get_queryset(self):
		query = self.request.GET.get("q")
		date_query = self.request.GET.get("date")

		if not query:
			return Entry.objects.none()
			
		object_list = Entry.objects.filter(
				Q(title__icontains=query) | Q(content__icontains=query)
			)

		object_list = object_list.select_related('creator')

		if date_query:
			try:
				date = datetime.strptime(date_query, '%Y-%m-%d')
				object_list = object_list.filter(initial_time__date=date)
			except ValueError:
				pass

		return object_list

@cache_page(60 * 5)
def index(request):
	# add [:number] to limit entries
	entries = Entry.objects.select_related('creator').all().order_by('-initial_time')
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

		return HttpResponseRedirect(reverse("cadmus:index"))

	else:
		return render(request, "cadmus/create_entry.html", {
			"entry_form": entry_form
		})

def entry(request, slug):

	entry = Entry.objects.select_related('creator').get(slug=slug)
	entry.content = entry.decrypted_content

	return render(request, "cadmus/entry.html", {
		"entry": entry
	})

def download_entry(request, slug):

    entry = Entry.objects.select_related('creator').get(slug=slug)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=72)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='DocTitle', parent=styles['Heading1'],
                              fontName='Helvetica-Bold', fontSize=18, spaceAfter=12))
    styles.add(ParagraphStyle(name='Meta', parent=styles['Normal'],
                              fontSize=9, textColor=colors.grey, spaceAfter=8))
    styles.add(ParagraphStyle(name='Body', parent=styles['Normal'],
                              fontSize=11, leading=14))

    if entry.initial_time:
        created_at = entry.initial_time.strftime('%B %d %Y %H:%M')
    else:
        created_at = "N/A"
    if entry.last_modified:
        last_updated = entry.last_modified.strftime('%B %d %Y %H:%M')
    else:
        last_updated = "N/A"

    elements = []
    elements.append(Paragraph(entry.title or "Untitled", styles['DocTitle']))
    elements.append(Paragraph(f'Created: {created_at} — Last updated: {last_updated}', styles['Meta']))

    content = entry.decrypted_content
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

    for para in paragraphs:
        para_html = para.replace('\n', '<br/>')
        elements.append(Paragraph(para_html, styles['Body']))
        elements.append(Spacer(1, 6))

    def header_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.setFillColorRGB(0.2, 0.2, 0.2)
        width, height = letter
        canvas.drawString(doc.leftMargin, height - 36, "Cadmus — Personal Diary")
        canvas.drawRightString(width - doc.rightMargin, 36, f"Page {doc.page}")
        canvas.restoreState()

    doc.build(elements, onFirstPage=header_footer, onLaterPages=header_footer)

    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=\"{entry.slug}.pdf\"'
    response.write(pdf)

    return response

def edit_entry(request, slug):

	entry = Entry.objects.select_related('creator').get(slug=slug)
	entry.content = entry.decrypted_content
	form = EntryForm(instance=entry)

	if request.method == "POST":
		with transaction.atomic():
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

	with transaction.atomic():
		entry = Entry.objects.select_for_update().get(slug=slug)
		entry.delete()

	return HttpResponseRedirect(reverse("cadmus:index"))

def archive_month(request):
	return render(request, "cadmus/entry_archive_month.html")

@cache_page(60 * 5)
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
	entries = Entry.objects.filter(initial_time__date__range=[start_date, end_date]).select_related('creator').only('id', 'initial_time', 'slug', 'title')

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

	entries = Entry.objects.filter(initial_time__gte=start, initial_time__lt=end).select_related('creator').order_by('-initial_time')
	day_date = start.date()

	return render(request, 'cadmus/entry_archive_date.html', {
		'entries': entries,
		'date': day_date
	})


def username_change(request):
	if request.method == "POST":
		with transaction.atomic():
			user = User.objects.select_for_update().get(id=request.user.id)
			form = UsernameChangeForm(user, request.POST)

			if form.is_valid():
				new_username = form.cleaned_data["username"]
				user = request.user
				user.username = new_username
				user.save()
				return redirect("cadmus:index")

	else:
		form = UsernameChangeForm(request.user, initial={"username": request.user.username})
	return render(request, "cadmus/registration/username_change.html", {
		"form": form})

def password_reset(request):

	p_form = PasswordChangeForm(request.user, request.POST)

	if request.method == "POST":
		with transaction.atomic():
			user = User.objects.select_for_update().get(id=request.user.id)
			
			if p_form.is_valid():
				new_password = p_form.cleaned_data["new_password1"]
				user = request.user
				user.set_password(new_password)
				user.save()
				update_session_auth_hash(request, user)
				return redirect("cadmus:index")
	else:
		p_form = PasswordChangeForm(request.user)

	return render(request, "cadmus/registration/password_reset_form.html", {
	"form": p_form})