import csv, io, zipfile

from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from reportlab.pdfgen import canvas

from .models import UserProfile

# Create your views here.
def index(request):
    return HttpResponse("Hello, this is the privacy app index.")

def privacy_policy(request):
    return HttpResponse("This is the privacy policy page.")

def _build_profile_csv(profile: UserProfile)-> bytes:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "full_name","email", "phone", "city", "notes", "is_deleted", "created_at", "deleted_at"])
    writer.writerow([
        profile.id,
        profile.full_name,
        profile.email,
        profile.phone,
        profile.city,
        profile.notes,
        profile.is_deleted,
        profile.created_at.isoformat() if profile.created_at else "",
        profile.deleted_at.isoformat() if profile.deleted_at else "",
    ])
    return buffer.getvalue().encode('utf-8')

def _build_summary_pdf(profile: UserProfile)-> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    c.setTitle("GDPR export summary")

    y = 800
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, y, "GDPR Data Export Summary")
    y -= 40

    c.setFont("Helvetica", 12)
    lines = [
        f"Generated at: {timezone.now().isoformat()}",
        f"Profile ID: {profile.id}",
        f"Full name: {profile.full_name}",
        f"Email: {profile.email}",
        f"Phone: {profile.phone}",
        f"City: {profile.city}",
        f"Notes: {profile.notes}",
        f"Deleted: {profile.is_deleted}",
    ]
     
    for line in lines:
       c.drawString(50, y, line[:110])
       y-=18
       if y<80:
          c.showPage()
          y=800
          c.setFont("Helvetica", 12)
    
    c.showPage()
    c.save()
    return buffer.getvalue()

@require_http_methods(["GET"])
def export_user_zip(request, profile_id: int):
    """
    GDPR export demo:
    Returns a ZIP containing:
      - profile.csv
      - summary.pdf
    """
    try:
        profile = UserProfile.objects.get(id=profile_id)
    except UserProfile.DoesNotExist:
        raise Http404("UserProfile does not exist")

    csv_data = _build_profile_csv(profile)
    pdf_data = _build_summary_pdf(profile)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        zip_file.writestr(f'userprofile_{profile.id}_data.csv', csv_data)
        zip_file.writestr(f'userprofile_{profile.id}_summary.pdf', pdf_data)

    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename=userprofile_{profile.id}_export.zip'
    return response

@csrf_exempt
@require_http_methods(["POST"])
def delete_user_profile(request, profile_id: int):
    """
    GDPR delete demo (two modes):
      - ?mode=anonymize  (default)
      - ?mode=hard
    """
    try:
        profile = UserProfile.objects.get(id=profile_id)
    except UserProfile.DoesNotExist:
        raise Http404("UserProfile does not exist")

    mode = request.GET.get('mode', 'anonymize').lower()

    if mode == 'hard':
        profile.delete()
        return HttpResponse(f"UserProfile {profile_id} hard deleted.")
    
    # Anonymize (default)
    profile.full_name = "Deleted User"
    profile.email = f"deleted_{profile.id}@example.invalid"
    profile.phone = ""
    profile.city = ""
    profile.notes = ""
    profile.is_deleted = True
    profile.deleted_at = timezone.now()
    profile.save(update_fields=["full_name", "email", "phone", "city", "notes", "is_deleted", "deleted_at"])

    return HttpResponse("Anonymized.", content_type="text/plain")