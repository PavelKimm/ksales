from django.urls import path

from .views import add_data_to_db, FlightView, get_data

urlpatterns = [
    path('', FlightView.as_view(), name='get-flights-info'),
    path('add-data-to-db/', add_data_to_db, name='add-data-to-db'),
    path('get-data/', get_data, name='get-data'),
]
