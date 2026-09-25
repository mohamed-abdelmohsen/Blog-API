from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length = 128,
        min_length = 8,
        write_only = True,
        style = {'input_typee':'password'}
    )

    password2 = serializers.CharField(
        max_length = 128,
        min_length = 8,
        write_only = True,
        style = {'input_typee':'password'}
    )
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password2']
        extra_kwargs = {
            'password':{'write_only':True},
            'email':{'required':True}
        }
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password':'Password fields didn\'t match'})
        password = attrs.get('password')
        try:
            validate_password(password)
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({'password':list(e.messages)})
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email':'Email already exists!'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            username = validated_data['username'],
            email = validated_data['email'],
            password = validated_data['password']
        )
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    new_password2 = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({'password':'Password fields didn\'t match'})
        try:
            validate_password('new_password')
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({'new_password':list(e.messages)})
        return attrs