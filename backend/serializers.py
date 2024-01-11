from rest_framework import serializers
from .models import Chanel
from django.contrib.auth.models import User
from phonenumber_field.formfields import PhoneNumberField
class ChanelSerializer(serializers.ModelSerializer):
    pictures=serializers.ImageField(required=False)
    class Meta:
        model = Chanel
        fields = ['chanel_link','name', 'subscribers','pictures','views']




class LoginFormSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=63,
        label="Логин",
        write_only=True
    )

    password = serializers.CharField(
        max_length=63,
        write_only=True,
        style={'input_type': 'password'},
        label="Пароль"
    )


class RegistrationSerializer(serializers.ModelSerializer):
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email address is already registered. Please use a different one.")
        return value

    class Meta:
        model = User
        fields = ['username', 'email', 'password']



    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )

        return user





