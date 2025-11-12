from django.db import models

class Property(models.Model):
    PROPERTY_TYPES = [
        ('Bedsitter', 'Bedsitter'),
        ('Single Room', 'Single Room'),
        ('One bedroom', 'One bedroom'),
        ('Two bedroom', 'Two bedroom'),
        ('Three bedroom', 'Three bedroom'),
        ('Four bedroom', 'Four bedroom'),
        ('Five bedroom', 'Five bedroom'),
        ('Six bedroom', 'Six bedroom'),
    ]

    title       = models.CharField(max_length=120)
    description = models.TextField()
    location    = models.CharField(max_length=120)
    price       = models.PositiveIntegerField()
    bedrooms    = models.CharField(max_length=20, choices=PROPERTY_TYPES)
    owner_name  = models.CharField(max_length=60)
    owner_phone = models.CharField(max_length=15)
    created_at  = models.DateTimeField(auto_now_add=True)
    available   = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} – {self.location}"


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='property_images/')

    def __str__(self):
        return f"Image for {self.property.title}"