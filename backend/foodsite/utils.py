from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User

def get_tokens_for_user(user: User):
    # Create the refresh token and access token
    refresh = RefreshToken.for_user(user)
    
    # Add the user id to the access token's payload
    access_token = refresh.access_token
    access_token["user_id"] = user.id  # Add user ID to the token payload
    
    return {
        "access": str(access_token),
        "refresh": str(refresh),
    }
