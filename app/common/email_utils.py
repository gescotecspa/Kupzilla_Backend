import base64
import traceback
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment
from flask import current_app

def send_email(subject, recipients, first_name, email, pdf_buffer=None, pdf_filename=None):
    # Crear la instancia de SendGrid
    print(f"Subject: {subject}")
    print(f"Recipients: {recipients}")
    print(f"First Name: {first_name}")
    print(f"Email: {email}")
    print(f"SendGrid API Key: {current_app.config['SENDGRID_API_KEY']}")
    sg = sendgrid.SendGridAPIClient(api_key=current_app.config['SENDGRID_API_KEY'])

    # Crear el correo
    from_email = current_app.config['SMTP_DEFAULT_SENDER']
    to_emails = recipients[0]
    print(f"datos que se envian: {from_email, to_emails, subject}")
    mail = Mail(from_email, to_emails, subject)
    mail.template_id ='d-559af315da884017819eedbaef48082d'

    mail.dynamic_template_data = {
        'first_name': first_name,
        'email': email
    }

    # Adjuntar el PDF si se proporciona
    if pdf_buffer and pdf_filename:
        pdf_buffer.seek(0)
        pdf_content = pdf_buffer.read()

        print(f"Primeros 10 bytes del PDF: {pdf_content[:10]}")
        print(f"PDF Content Length: {len(pdf_content)} bytes")

        if not pdf_content:
            print("El archivo PDF está vacío!")
            return

        encoded_pdf = base64.b64encode(pdf_content).decode('utf-8')

        attachment = Attachment(
            file_content=encoded_pdf,
            file_type="application/pdf",
            file_name=pdf_filename,
            disposition="attachment"
        )

        mail.attachment = attachment
    
    # Enviar el correo
    try:
        response = sg.send(mail)
        print(f"Correo enviado con éxito! Estado: {response.status_code}, Body: {response.body}")
        print(f"Response Headers: {response.headers}")  # Mostrar cabeceras también para más detalles
    except Exception as e:
        print(f"Error al enviar el correo: {str(e)}")


def send_email_partner(subject, recipients, first_name, email, password):
    # Verificar que haya destinatarios
    if not recipients:
        print("Error: No se proporcionaron destinatarios")
        return False

    try:
        sg = sendgrid.SendGridAPIClient(api_key=current_app.config['SENDGRID_API_KEY'])
        
       
        from_email = current_app.config['SMTP_DEFAULT_SENDER'] 
        to_email = recipients[0]  
        print(f"Preparando email para: {to_email}")
        
        mail = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject
        )
        
        # Usar la plantilla de SendGrid
        mail.template_id = 'd-7090c0d32b1741c1ac7dc0b74ead07b4'
        mail.dynamic_template_data = {
            'first_name': first_name,
            'email': email,
            'password': password
        }
        # Enviar el correo
        response = sg.send(mail)
        print(f"Email enviado. Status: {response.status_code}")
        return True
        
    except Exception as e:
        print(f"ERROR al enviar email: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}") 
        return False
    
def send_email_reset_password(subject, recipients, first_name, email, reset_code):
    if not recipients:
        print("Error: No se proporcionaron destinatarios")
        return False

    try:
        sg = sendgrid.SendGridAPIClient(api_key=current_app.config['SENDGRID_API_KEY'])
        
        from_email = current_app.config['SMTP_DEFAULT_SENDER']
        to_email = recipients[0]
        print(f"Preparando email para: {to_email}")
        
        mail = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject
        )
        
        mail.template_id = 'd-80e094dc0ed443c082b324588ebae35b'
        
        mail.dynamic_template_data = {
            'first_name': first_name,
            'email': email,
            'reset_code': reset_code,
            'reset_url': f"https://www.kupzilla.com/reset_password?code={reset_code}"
        }
        
        # Enviar el correo
        response = sg.send(mail)
        print(f"Email enviado. Status: {response.status_code}")
        return True
        
    except Exception as e:
        print(f"ERROR al enviar email: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}") 
        return False