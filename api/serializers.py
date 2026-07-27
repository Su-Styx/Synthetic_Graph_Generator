# control the response of the api endpoint
from rest_framework import serializers
from api.models import Run
from django.contrib.auth import get_user_model


class RunSerializer(serializers.ModelSerializer):
    class Meta:
        model = Run
        fields ='__all__'



User = get_user_model()

class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "password")

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)  # hashes the password
        user.save()
        return user