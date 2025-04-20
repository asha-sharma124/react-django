from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
CustomUser = get_user_model()



class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"detail": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Use email to authenticate user
        user = authenticate(request, username=email, password=password)

        if user is not None:
            # Create JWT tokens for the authenticated user
            refresh = RefreshToken.for_user(user)

            # Add custom claims to the JWT token
            refresh.payload['userId'] = user.id
            refresh.payload['email'] = user.email
            refresh.payload['username'] = user.username

            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "userId": user.id,
                "email": user.email,
                "username": user.username
            }, status=status.HTTP_200_OK)

        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            # Save the user
            user = serializer.save()

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)

            # Ensure the user object has the latest attributes (though it should)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "userId": user.id,  # Make sure you access the ID here
                "email": user.email,  # Access email after save
                "username": user.username  # Access username after save
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
