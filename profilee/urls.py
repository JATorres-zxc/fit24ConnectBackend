from django.urls import path
from .views import *

urlpatterns = [
    path('profile/', ProfileDetailView.as_view(), name='profile-detail'),  # GET profile
    path('profile/update/', ProfileUpdateView.as_view(), name='profile-update'),  # PATCH profile
    path('profile/change-password/', ChangePasswordView.as_view(), name='change-password'),
]
