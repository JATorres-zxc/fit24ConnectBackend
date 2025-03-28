from django.urls import path
from .views import ProfileUpdateView, ProfileDetailView

urlpatterns = [
    path('profile/', ProfileDetailView.as_view(), name='profile-detail'),  # GET profile
    path('profile/update/', ProfileUpdateView.as_view(), name='profile-update'),  # PATCH profile
]
