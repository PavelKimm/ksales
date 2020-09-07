from django.db import models


class Carrier(models.Model):
    AIRPLANE = 'AP'
    TRAIN = 'TR'
    BUS = 'BS'
    TAXI = 'TX'
    TRANSPORT_TYPE_CHOICES = [
        (AIRPLANE, 'Airplane'),
        (TRAIN, 'Train'),
        (BUS, 'Bus'),
        (TAXI, 'Taxi')
    ]

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=2, choices=TRANSPORT_TYPE_CHOICES, default=AIRPLANE)

    def __str__(self):
        return self.name


class Airport(models.Model):
    IATA_code = models.CharField(max_length=3, unique=True)
    city_name = models.CharField(max_length=128)

    def __str__(self):
        return self.city_name


class Flight(models.Model):
    city_from = models.ForeignKey(to=Airport, on_delete=models.CASCADE, related_name='flights_from')
    city_to = models.ForeignKey(to=Airport, on_delete=models.CASCADE, related_name='flights_to')
    date_start = models.CharField(max_length=10)
    duration = models.CharField(max_length=10)
    price = models.FloatField()
    carrier = models.ForeignKey(to=Carrier, on_delete=models.CASCADE)
