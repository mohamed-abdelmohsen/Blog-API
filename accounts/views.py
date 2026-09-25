from django.shortcuts import render
from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
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
