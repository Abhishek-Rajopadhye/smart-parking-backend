from locust import HttpUser, task, between

class BookingUser(HttpUser):
    # Define the wait time between each task
    wait_time = between(1, 3)  # Wait between 1 and 3 seconds between each request
    
    @task
    def book_spot(self):
        # Define the POST request to your /bookings/book-spot endpoint
        payload = {
            "user_id": "111919577987638512190",
            "spot_id": 4,
            "total_slots": 2,
            "start_date_time": "2023-10-01T10:00:00",
            "end_date_time": "2023-10-01T12:00:00",
            "total_amount": 20,
            "receipt": "mock_receipt"
        }
        
        # Perform the POST request
        self.client.post("/bookings/book-spot/", json=payload)
