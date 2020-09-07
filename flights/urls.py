from django.urls import path

from .views import add_data_to_db, FlightView

urlpatterns = [
    path('', FlightView.as_view(), name='get-flights-info'),
    path('add-data-to-db/', add_data_to_db, name='add-data-to-db'),
]
