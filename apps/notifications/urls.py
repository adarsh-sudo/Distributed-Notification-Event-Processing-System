from django.urls import path
from .views import EventCreateAPIView

urlpatterns = [
    path('events/', EventCreateAPIView.as_view(), name='create-event'),
]