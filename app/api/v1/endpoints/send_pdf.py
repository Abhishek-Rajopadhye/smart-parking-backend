from fastapi import APIRouter, UploadFile, Form
from app.services.receipt import send_receipt
from email.message import EmailMessage

router = APIRouter()

# Use App Password for Gmail

@router.post("/send-receipt-with-pdf")
async def send_receipt_with_pdf(
    file: UploadFile,
    email: str = Form(...)
):
  try:
    send_receipt(file, email)
    return {"message": "Email sent successfully with PDF!"}
  except Exception as e:
    raise Exception(f"Failed to send email: {str(e)}")
