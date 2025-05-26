from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        print(f"Trying to authenticate {email}")  # ← Debug print here

        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            print("User not found")
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            print("Authentication successful")
            return user

        print("Authentication failed: wrong password or inactive")
        return None
