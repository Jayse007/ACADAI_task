from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth import authenticate



User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email"),
            password=validated_data["password"],
        )
        return user



class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            username=data["username"],
            password=data["password"],
        )
        if not user:
            raise serializers.ValidationError("Invalid credentials")

        data["user"] = user
        return data


class AuthTokenResponseSerializer(serializers.Serializer):
    token = serializers.CharField(help_text="Authentication token")