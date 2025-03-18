from rest_framework import serializers
from .models import CustomUser 

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser             # Serializer target model
        fields = ['id', 'username', 'role', 'unique_id', 'password']  
        # Fields to include
        extra_kwargs = {
            'password': {'write_only': True}  
            # Prevents password from being read via API
        }

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            role=validated_data.get('role', 'S'),
            unique_id=validated_data['unique_id']
        )
        return user
