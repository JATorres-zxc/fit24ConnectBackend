from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        print(f"Trying to authenticate {email}")

        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            print("User not found")
            return None

        if user.check_password(password):
            print("Authentication successful or inactive")
            return user  # Do NOT check is_active here

        print("Authentication failed: wrong password")
        return None
