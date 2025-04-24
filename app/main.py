import fastapi
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import auth, user, booking, spot, parking, review, send_pdf, verification

app = fastapi.FastAPI(title="Smart Parking")

origins = [
    "https://smart-parking-frontend.onrender.com",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(booking.router, prefix="/bookings", tags=["Bookings"])
app.include_router(spot.router, prefix="/spots", tags=["Spots"])
app.include_router(parking.router, prefix="/spotdetails", tags=["Marker"])
app.include_router(review.router, prefix="/reviews", tags=["Review"])
app.include_router(send_pdf.router, prefix="/send-pdf", tags=["Send PDF"])
app.include_router(verification.router, prefix="/verfiy-list", tags=["Spot Verification"])
