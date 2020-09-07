from django.conf import settings
from django.db.models import Max, Min
from rest_framework import serializers

from .models import Carrier, Airport, Flight


class CarrierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrier
        fields = ['type', 'name']


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ['IATA_code', 'city_name']


class FlightSerializer(serializers.ModelSerializer):
    city_from = AirportSerializer()
    city_to = AirportSerializer()
    carrier = CarrierSerializer()

    class Meta:
        model = Flight
        fields = ['id', 'date_start', 'duration', 'price', 'city_from', 'city_to', 'carrier']

