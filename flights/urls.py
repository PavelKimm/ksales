from django.urls import path

from .views import add_train_data_to_db, add_plane_data_to_db, FlightView

urlpatterns = [
    path('', FlightView.as_view(), name='get-flights-info'),
    path('add-train-data-to-db/', add_train_data_to_db, name='add-train-data-to-db'),
    path('add-plane-data-to-db/', add_plane_data_to_db, name='add-plane-data-to-db')
]
