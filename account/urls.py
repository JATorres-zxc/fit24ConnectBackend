from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('trainer-profile/', TrainerProfileView.as_view(), name='trainer-profile'),
    # JWT Token endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('trainers/', TrainerListView.as_view(), name='trainer-list'),
    path('members/', MemberListView.as_view(), name='member-list'),
    path('trainer-status/<int:user_id>/<str:action>/', TrainerStatusUpdateView.as_view(), name='trainer-status-update'),
    path('admin/update-membership-type/<int:pk>/', AdminUpdateMembershipTypeView.as_view(), name='admin-update-membership-type'),
    path('admin/members/<int:user_id>/status/', MembershipStatusUpdateView.as_view(), name='membership-status-update'),
]
