from django.urls import path
from .views import csv_table
urlpatterns = [
    path("C:\xampp\htdocs\NEW\backend", csv_table, name="DatasetsForBackend.csv"),
]
