from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .forms import VisitorPassForm
from .models import VisitorPass
import pytesseract
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
import re
from .qr_utils import decode_qr
from datetime import datetime, timedelta
import qrcode
from io import BytesIO
import base64
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as ReportLabImage
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import inch

# Path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text(image):
    try:
        img = Image.open(image)
        extracted_text = pytesseract.image_to_string(img)
        return extracted_text
    except Exception as e:
        print(f"Error: {e}")
        return ""

def match_details(text):
    aadhaar_pattern = r"\b\d{4}\s\d{4}\s\d{4}\b"
    dob_pattern = r"\b(?:0[1-9]|[12][0-9]|3[01])/(?:0[1-9]|1[0-2])/(?:19|20)\d{2}\b"
    gender_pattern = r"\b(?:Male|Female|Other|FEMALE|MALE|OTHER)\b"

    if not isinstance(text, str):
        raise TypeError('Expected string or bytes-like object')

    aadhaar_number = re.search(aadhaar_pattern, text).group() if re.search(aadhaar_pattern, text) else None
    dob = re.search(dob_pattern, text).group() if re.search(dob_pattern, text) else None
    gender = re.search(gender_pattern, text).group() if re.search(gender_pattern, text) else None

    return aadhaar_number, dob, gender

def validate_visit_date(visit_date):
    current_date = datetime.now().date()
    return visit_date > current_date + timedelta(days=1)

def generate_qr_code(visitor_pass):
    pass_details = f"Pass ID: {visitor_pass.visitor_pass_id}\n" \
                   f"Name: {visitor_pass.name}\n" \
                   f"Mobile Number: {visitor_pass.mobile_number}\n" \
                   f"Date of Visiting: {visitor_pass.date_of_visiting}\n" \
                   f"Duration of Visiting: {visitor_pass.duration_of_visiting} hours\n" \
                   f"Aadhaar Number: {visitor_pass.aadhaar_number}\n" \
                   f"Date of Birth: {visitor_pass.dob}\n" \
                   f"Gender: {visitor_pass.gender}\n"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=6,
        border=2,
    )
    qr.add_data(pass_details)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')

    buffer = BytesIO()
    img.save(buffer)
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str

def generate_pdf(visitor_pass):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title with style
    title_style = styles['Title']
    title_style.textColor = colors.blue
    elements.append(Paragraph("Visitor Pass", title_style))
    elements.append(Spacer(1, 0.25 * inch))

    # Visitor details with custom styles
    body_style = styles['BodyText']
    body_style.textColor = colors.black
    details = f"""
        <b>Visitor Pass ID:</b> {visitor_pass.visitor_pass_id}<br/>
        <b>Name:</b> {visitor_pass.name}<br/>
        <b>Mobile Number:</b> {visitor_pass.mobile_number}<br/>
        <b>Date of Visiting:</b> {visitor_pass.date_of_visiting}<br/>
        <b>Duration of Visiting:</b> {visitor_pass.duration_of_visiting} hours<br/>
        <b>Aadhaar Number:</b> {visitor_pass.aadhaar_number}<br/>
        <b>Date of Birth:</b> {visitor_pass.dob}<br/>
        <b>Gender:</b> {visitor_pass.gender}<br/>
    """
    elements.append(Paragraph(details, body_style))
    elements.append(Spacer(1, 0.5 * inch))

    # QR Code
    qr_code = generate_qr_code(visitor_pass)
    img_data = base64.b64decode(qr_code)
    img = Image.open(BytesIO(img_data))
    img_width, img_height = img.size  # Get image dimensions

    # Add image to PDF
    elements.append(ReportLabImage(BytesIO(img_data), width=img_width, height=img_height))

    # Build PDF
    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()
    return pdf

def download_pass(request, pass_id):
    visitor_pass = get_object_or_404(VisitorPass, visitor_pass_id=pass_id)
    pdf = generate_pdf(visitor_pass)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Visitor_Pass_{pass_id}.pdf"'
    return response

def home(request):
    return render(request, 'home/home.html')

def generate_pass(request):
    if request.method == 'POST':
        form = VisitorPassForm(request.POST, request.FILES)
        if form.is_valid():
            visitor_pass = form.save(commit=False)
            aadhaar_image = form.cleaned_data['aadhaar_image']

            extracted_text = extract_text(aadhaar_image)
            if not isinstance(extracted_text, str):
                form.add_error('aadhaar_image', 'Failed to extract text from the Aadhaar image.')
                return render(request, 'home/generate_pass.html', {'form': form})

            aadhaar_number, dob, gender = match_details(extracted_text)

            if aadhaar_number is None:
                form.add_error('aadhaar_image', 'Aadhaar number could not be extracted from the image.')
                return render(request, 'home/generate_pass.html', {'form': form})

            if not validate_visit_date(visitor_pass.date_of_visiting):
                form.add_error('date_of_visiting', 'Date of visiting must be at least 24 hours ahead of the current date.')
                return render(request, 'home/generate_pass.html', {'form': form})

            visitor_pass.visitor_pass_id = datetime.now().strftime('%Y%m%d%H%M%S')
            visitor_pass.aadhaar_number = aadhaar_number
            if dob:
                visitor_pass.dob = datetime.strptime(dob, '%d/%m/%Y').date()
            else:
                form.add_error('aadhaar_image', 'Failed to extract date of birth from Aadhaar image.')
                return render(request, 'home/generate_pass.html', {'form': form})

            if gender:
                visitor_pass.gender = gender
            else:
                form.add_error('aadhaar_image', 'Failed to extract gender from Aadhaar image.')
                return render(request, 'home/generate_pass.html', {'form': form})

            visitor_pass.save()
            qr_code = generate_qr_code(visitor_pass)
            return render(request, 'home/visitor_pass.html', {'visitor_pass': visitor_pass, 'qr_code': qr_code})

    else:
        form = VisitorPassForm()
    return render(request, 'home/generate_pass.html', {'form': form})

def validate_pass(request):
    if request.method == 'POST':
        qr_image = request.FILES.get('qr_image')
        
        if not qr_image:
            return render(request, 'home/validate_pass.html', {'status': "No QR code image uploaded."})
        
        try:
            # Ensure the image file is in a compatible format for OpenCV
            if isinstance(qr_image, InMemoryUploadedFile):
                qr_image.file.seek(0)
            
            extracted_text = decode_qr(qr_image)
            print(f"Extracted Text: {extracted_text}")  # Debugging log
        except Exception as e:
            return render(request, 'home/validate_pass.html', {'status': f"Error extracting text: {e}"})
        
        if extracted_text:
            pass_id_pattern = r"Pass ID: (\d+)"
            pass_id_match = re.search(pass_id_pattern, extracted_text)
            
            if pass_id_match:
                pass_id = pass_id_match.group(1)
                print(f"Pass ID: {pass_id}")  # Debugging log
                
                try:
                    visitor_pass = VisitorPass.objects.get(visitor_pass_id=pass_id)
                    current_date = datetime.now().date()
                    
                    if current_date > visitor_pass.date_of_visiting:
                        status = "Expired"
                    else:
                        status = "Active"
                    
                    return render(request, 'home/validate_pass.html', {'visitor_pass': visitor_pass, 'status': status})
                except VisitorPass.DoesNotExist:
                    return render(request, 'home/validate_pass.html', {'status': "Visitor Pass not found."})
            else:
                return render(request, 'home/validate_pass.html', {'status': "Pass ID not found in QR Code."})
        else:
            return render(request, 'home/validate_pass.html', {'status': "Invalid QR Code."})

    return render(request, 'home/validate_pass.html')

def view_and_download_pass(request):
    visitor_pass = None
    status_message = None
    qr_code = None

    if request.method == 'POST':
        pass_id = request.POST.get('pass_id')
        try:
            visitor_pass = VisitorPass.objects.get(visitor_pass_id=pass_id)
            qr_code = generate_qr_code(visitor_pass)
        except VisitorPass.DoesNotExist:
            status_message = "Visitor Pass not found."

    return render(request, 'home/view_and_download_pass.html', {
        'visitor_pass': visitor_pass,
        'status_message': status_message,
        'qr_code': qr_code
    })
