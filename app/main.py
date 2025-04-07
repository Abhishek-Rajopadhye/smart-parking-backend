import fastapi
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import auth, user, booking, spot, parking,review

app = fastapi.FastAPI(title="Smart Parking")

origins = [
"https://smart-parking-backend-4qec.onrender.com",
"https://smart-parking-frontend.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(booking.router, prefix="/bookings", tags=["Bookings"])
app.include_router(spot.router, prefix="/spots", tags=["Spots"])
app.include_router(parking.router,prefix="/spotdetails",tags=["Marker"])
app.include_router(review.router,prefix="/review",tags=["Review"])
