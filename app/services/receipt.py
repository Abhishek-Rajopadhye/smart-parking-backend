from fastapi import APIRouter, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import smtplib
from app.core.config import settings
from email.message import EmailMessage

router = APIRouter()

async def send_receipt(
    file: UploadFile,
    email: str = Form(...)
):
    """
    Send a receipt via email with the attached PDF file.
    returns a success message if the email is sent successfully.

    Parameters: 
    file (UploadedFile): file which contains the PDF file data
    email (str): The recipient's email address.

    Returns: 
    dict: A dictionary containing the success message if the email is sent successfully.

    Example:
    send_receipt(file, email)
    send a receipt to the email address with the attached PDF file.
    returns a success message if the email is sent successfully.

    """
    msg = EmailMessage()
    msg['Subject'] = "Your Parking Receipt"
    msg['From'] = settings.EMAIL_ADDRESS
    msg['To'] = email
    msg.set_content("Attached is your receipt for Smart Parking. Thank you!")

    # Read PDF and attach it
    pdf_data = await file.read()
    msg.add_attachment(pdf_data, maintype="application",
                       subtype="pdf", filename="booking_receipt.pdf")
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(settings.EMAIL_ADDRESS, settings.EMAIL_PASSWORD)
            smtp.send_message(msg)
        return {"message": "Email sent successfully with PDF!"}
    except Exception as e:
        raise Exception(f"Failed to send email: {str(e)}")
