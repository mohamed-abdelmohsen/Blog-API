from django.shortcuts import render
from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from blog.settings import SIMPLE_JWT
from .serializers import RegisterSerializer, UserSerializer, ChangePasswordSerializer
from rest_framework.response import Response

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'message':'user created!',
            'user':UserSerializer(user).data,
            'tokens':{
                'refresh':str(refresh),
                'access':str(refresh.access_token),
            }
            }, status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self,request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'message':'Login successfully',
                'user':UserSerializer(user).data,
                'tokens':{
                    'refresh':str(refresh),
                    'access':str(refresh.access_token)
                }
            }, status.HTTP_200_OK)
        else:
            return Response(
                {'error':'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED
            )
class LogoutView(APIView):
    permission_classes =[permissions.IsAuthenticated]
    def post(self, request):
        try :
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                return Response(
                    {'error':'refresh token is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({
                'message':'Logged out!'
            }, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class LogoutAllView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            tokens = RefreshToken.objects.filter(user=request.user)
            for token in tokens:   

                token.blacklist()
            return Response({
                'message':'Loggedout from all devices'
            }, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e :
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer 
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if not user.check_password(serializer.data.get('old_password')):
                return Response({
                    'error':'wrong password'
                }, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.data.get('new_password'))
            user.save()
            return Response({
                'message':'User Updated!'
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RefreshTokenView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self,request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({
                'error':'refresh token required'
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            refresh = RefreshToken(refresh_token)
            data = {
                'access': str(refresh.access_token),
            }
            
            # Rotate refresh tokens if enabled
            if SIMPLE_JWT.get('ROTATE_REFRESH_TOKENS', False):
                data['refresh'] = str(refresh)
            
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )

        