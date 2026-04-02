from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from django.db import IntegrityError, transaction
from .models import Entry, User

def generate_entry_pdf(entry: Entry) -> BytesIO:

    #entry = Entry.objects.select_related('creator').get(slug=slug)

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

    buffer.seek(0)
    return buffer

def change_user_password(user: User, new_password: str) -> None:
    with transaction.atomic():
        db_user = User.objects.select_for_update().get(id=user.id)
        db_user.set_password(new_password)
        db_user.save()

def change_username(user: User, new_username: str) -> None:
    try:
        with transaction.atomic():
            db_user = User.objects.select_for_update().get(id=user.id)
            db_user.username = new_username
            db_user.save()
    except IntegrityError:
        raise ValueError("Username already taken.")