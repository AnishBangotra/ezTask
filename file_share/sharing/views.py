from django.shortcuts import get_object_or_404
from rest_framework import generics, status, views
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from django.core.mail import send_mail
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import authenticate, login
from django.conf import settings
from itsdangerous import URLSafeTimedSerializer
from .models import User, File
from .utils import send_verification_email, generate_encrypted_url, decrypt_url
from .serializers import UserSerializer, FileSerializer

# Create your views here.

s = URLSafeTimedSerializer(settings.SECRET_KEY)

class SignUpView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = default_token_generator.make_token(user)
        encrypted_url = generate_encrypted_url(user.pk, token)
        verification_url = f"http://127.0.0.1:8000/api/verify/{user.pk}/{token}/"
        send_verification_email(user.email, verification_url)
        return Response({
            "message": "User created successfully. Please verify your email.",                "verification_url": verification_url
        }, status=201)
        return Response(serializer.errors, status=400)


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, encrypted_url, *args, **kwargs):
        data = decrypt_url(encrypted_url)
        if data is None:
            return Response({'message': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)
        
        user_id = data['user_id']
        token = data['token']
        user = get_object_or_404(User, pk=user_id)
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({'message': 'Email verified successfully.'}, status=status.HTTP_200_OK)
        return Response({'message': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)

class CustomAuthToken(ObtainAuthToken):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                token, created = Token.objects.get_or_create(user=user)
                return Response({
                    'token': token.key,
                    'user_id': user.pk,
                    'email': user.email
                })
            else:
                return Response({'error': 'User account is disabled.'}, status=400)
        else:
            return Response({'error': 'Unable to log in with provided credentials.'}, status=400)



class UploadFileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        if user.role != 'ops':
            return Response({"message": "Only Operation Users can upload files."}, status=status.HTTP_403_FORBIDDEN)
        
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        file_extension = file.name.split('.')[-1].lower()
        if file_extension not in ['pptx', 'docx', 'xlsx']:
            return Response({'error': 'Invalid file type.'}, status=status.HTTP_400_BAD_REQUEST)

        file_name = default_storage.save(file.name, ContentFile(file.read()))
        uploaded_file = File(user=user, file=file_name)
        uploaded_file.save()

        return Response({'message': 'File uploaded successfully.'}, status=status.HTTP_201_CREATED)


class ListFilesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return Response({'message': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Ensure the user is a client
        if user.role != 'client':  # Assuming 'role' is a field in your User model to distinguish between ops and client users
            return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        files = File.objects.all()
        serializer = FileSerializer(files, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DownloadFileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, file_id, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            return Response({'message': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)
        if request.user.role != 'client':
            return Response({"msg": "Only client users can download files"}, status=status.HTTP_403_FORBIDDEN)

        try:
            file = File.objects.get(id=file_id)
        except File.DoesNotExist:
            return Response({'message': 'File not found.'}, status=status.HTTP_404_NOT_FOUND)

        encrypted_url = generate_encrypted_url(file.id, user.id)
        download_url = f"http://127.0.0.1:8000/api/download-file/{encrypted_url}/"

        return Response({
            "download-link": download_url,
            "message": "success"
        }, status=status.HTTP_200_OK)

class EncryptedFileDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, encrypted_url, *args, **kwargs):
        data = decrypt_url(encrypted_url)
        if data is None:
            return Response({'message': 'Invalid or expired URL.'}, status=status.HTTP_400_BAD_REQUEST)
        
        file_id = data['file_id']
        user_id = data['user_id']

        if request.user.id != user_id:
            return Response({'message': 'Access denied.'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            file = File.objects.get(id=file_id)
        except File.DoesNotExist:
            return Response({'message': 'File not found.'}, status=status.HTTP_404_NOT_FOUND)

        file_url = file.file.url
        return Response({
            "file_url": file_url,
            "message": "success"
        }, status=status.HTTP_200_OK)