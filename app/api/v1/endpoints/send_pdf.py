from fastapi import APIRouter, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import smtplib
from email.message import EmailMessage

router = APIRouter()

EMAIL_ADDRESS = "arjunghule6583@gmail.com"
EMAIL_PASSWORD = "rmmf uccn pbti rity"  # Use App Password for Gmail


@router.post("/send-receipt-with-pdf")
async def send_receipt_with_pdf(
    file: UploadFile,
    email: str = Form(...)
):
    msg = EmailMessage()
    print("Sending email to:", email)
    msg['Subject'] = "Your Parking Receipt"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = email
    msg.set_content("Attached is your receipt for Smart Parking. Thank you!")

    # Read PDF and attach it
    pdf_data = await file.read()
    msg.add_attachment(pdf_data, maintype="application",
                       subtype="pdf", filename="booking_receipt.pdf")
    print("PDF attached successfully!")
    try:
        print("Connecting to SMTP server...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            print("Logging in to SMTP server...")
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            print("Sending email...")
            smtp.send_message(msg)
        print("Email sent successfully!!!!!")
        return {"message": "Email sent successfully with PDF!"}
    except Exception as e:
        return {"error": str(e)}
