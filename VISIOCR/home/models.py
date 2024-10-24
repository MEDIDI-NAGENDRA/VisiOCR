from django.db import models
from datetime import datetime, timedelta

def default_expiry_date():
    return datetime.now() + timedelta(days=1)

class VisitorPass(models.Model):
    visitor_pass_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15)
    date_of_visiting = models.DateField(default=datetime.now)
    duration_of_visiting = models.IntegerField()
    aadhaar_number = models.CharField(max_length=20)
    dob = models.DateField()
    gender = models.CharField(max_length=10, default='Male')
    expiry_date = models.DateField(default=default_expiry_date)  # Define default value here

    def __str__(self):
        return self.name
