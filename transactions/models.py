from django.db import models

class Transaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('not selected', 'Not Selected'),
    ]
    TYPE_CHOICES = [
        ('given', 'Given'),
        ('taken', 'Taken'),
    ]

    carrier_name = models.CharField(max_length=100)
    amount = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not selected')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    due_date = models.DateField()
    history = models.TextField(blank=True)

    def __str__(self):
        return f"{self.carrier_name} - {self.amount}g - {self.status}"

class CalculationHistory(models.Model):
    name = models.CharField(max_length=100)
    total = models.FloatField()
    history = models.TextField()  # Store as JSON string
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.created_at:%Y-%m-%d %H:%M})"
