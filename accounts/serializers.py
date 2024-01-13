from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True,
                                   error_messages={
                                    'blank':
                                    'Email field cannot be empty'})
    username = serializers.CharField(required=True,
                                     error_messages={
                                        'blank':
                                        'Username field cannot be empty'})
    password = serializers.CharField(write_only=True, required=True,
                                     error_messages={
                                        'blank':
                                        'Password field cannot be empty'})

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username',
                  'password', 'location', 'bio', 'phone')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                                    'A user with this username already exists')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                                    'A user with this email already exists')
        return value


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True,
                                     error_messages={
                                        'blank':
                                        'Username field cannot be empty'})
    password = serializers.CharField(required=True,
                                     error_messages={
                                        'blank':
                                        'Password field cannot be empty'})

    def validate(self, data):
        user = authenticate(**data)
        if not user:
            raise serializers.ValidationError("Incorrect Credentials")
        if not user.is_active:
            raise serializers.ValidationError("User account is not active")
        return user
