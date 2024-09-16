from rest_framework import serializers
from .models import Chanel,Profile,Ref
from django.contrib.auth.models import User
from phonenumber_field.serializerfields import PhoneNumberField
class ChanelSerializer(serializers.ModelSerializer):
    pictures=serializers.ImageField(required=False)

    class Meta:
        model = Chanel
        fields = ['chanel_link','name', 'subscribers','pictures','chanel_id','description']




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
    phone_number = PhoneNumberField(required=True)


    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email address is already registered. Please use a different one.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'phone_number']



    def create(self, validated_data):
        phone_number = validated_data.pop('phone_number')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        request = self.context.get('request')
        referral_code = request.session.get('referral_code') if request else None


        if referral_code:
            ref=Ref.objects.get(code=referral_code)
            Profile.objects.create(
                username=user,
                first_name=user.username,
                last_name=user.last_name,
                email=user.email,
                phone_number=phone_number,
                recommended_by=ref
            )
        else:
            Profile.objects.create(
                username=user,
                first_name=user.username,
                last_name=user.last_name,
                email=user.email,
                phone_number=phone_number
            )

        if referral_code:
            del request.session['referral_code']
        return user





