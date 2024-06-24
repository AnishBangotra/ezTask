from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import File, User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data['role']
        )
        user.set_password(validated_data['password'])
        user.is_active = False  # Initially, user is not active until email is verified
        user.save()
        return user

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ('id', 'filename', 'file', 'uploader')