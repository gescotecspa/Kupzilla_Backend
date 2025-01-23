import io
import qrcode
import requests
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors

def generate_pdf(name, email, user_id):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Añadir título
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 1 * inch, "Credencial App Cobquecura")

    # Descargar logo desde URL
    logo_url = "https://res.cloudinary.com/dbwmesg3e/image/upload/v1723120005/TurismoApp/logoCCTDC_lugwff.png"
    response = requests.get(logo_url)
    logo_img = Image.open(io.BytesIO(response.content))
    logo_img = logo_img.convert("RGBA")
    white_bg = Image.new("RGBA", logo_img.size, "WHITE")
    white_bg.paste(logo_img, (0, 0), logo_img)
    logo_img = white_bg.convert("RGB")

    # Añadir recuadro tipo tarjeta
    card_x = 0.75 * inch
    card_y = height - 6 * inch
    card_width = width - 1.5 * inch
    card_height = 4 * inch
    c.setStrokeColor(colors.black)
    c.setFillColor(colors.white)
    c.roundRect(card_x, card_y, card_width, card_height, 10, fill=1)

    # Añadir logo alineado a la izquierda dentro de la tarjeta
    logo_width = 2 * inch
    logo_height = 1 * inch
    logo_x = card_x + 0.5 * inch
    logo_y = card_y + card_height - logo_height - 0.5 * inch
    c.drawInlineImage(logo_img, logo_x, logo_y, logo_width, logo_height)

    # Añadir texto debajo del logo y alineado a la izquierda dentro de la tarjeta
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 14)
    text_x = logo_x
    text_y = logo_y - 0.75 * inch  # Ajustar para colocar el texto justo debajo del logo
    c.drawString(text_x, text_y, f"Nombre: {name}")
    c.drawString(text_x, text_y - 0.5 * inch, f"Email: {email}")

    # Añadir código QR con margen derecho
    qr_value = f"{user_id}-{email}"
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(qr_value)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img = img.convert("RGB")
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)

    pil_image = Image.open(img_buffer)
    qr_size = 2 * inch
    qr_margin_right = 0.5 * inch
    c.drawInlineImage(pil_image, card_x + card_width - qr_size - qr_margin_right, card_y + 0.5 * inch, qr_size, qr_size)

    # Guardar PDF
    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer
