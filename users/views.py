import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from users.serializers import UserSerializer, LoginSerializer
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from django.urls import reverse
from django.shortcuts import render

logger = logging.getLogger(__name__)
# Login view
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    # Deserialize the login data using the LoginSerializer
    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        # Authenticate the user
        user = authenticate(username=username, password=password)

        if user is not None:
            # Generate JWT tokens for the authenticated user
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
        
            # Return the tokens to the client
            return Response({
                'access': access_token,
                'refresh': str(refresh),
                'redirect_url': "/"
            }, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    # Deserialize the request data using the UserSerializer
    serializer = UserSerializer(data=request.data)

    # Validate the incoming data
    if serializer.is_valid():
        # Save the new user to the database
        serializer.save()

        # Return a success response
        return Response({'detail': 'Registration successful'}, status=status.HTTP_201_CREATED)

    # If the data is invalid, return an error response
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Only authenticated users can access their profile
def profile(request):
    # Get the user making the request
    user = request.user
    # Return user information (you can customize what information you want to return)
    return Response({
        'username': user.username,
        'email': user.email,
        'date_joined': user.date_joined,
        'last_login': user.last_login })
    
    
def home(request):
    return render(request, 'index.html')