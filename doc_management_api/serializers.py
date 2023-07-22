from rest_framework import serializers
from django.contrib.auth.models import User
from doc_management_api.models import *
from personal_document_management.settings import BASE_URL


#create serializers
class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user
    

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128, write_only=True)


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'title', 'description', 'file']

    def validate_file(self, value):
        allowed_formats = ['pdf', 'doc', 'docx', 'txt']  # Allowed file formats
        max_file_size = 5 * 1024 * 1024  # 5 MB (in bytes)

        # Check file format
        ext = value.name.split('.')[-1]
        if ext.lower() not in allowed_formats:
            raise serializers.ValidationError(f'File format not supported. Allowed formats: {", ".join(allowed_formats)}')

        # Check file size
        if value.size > max_file_size:
            raise serializers.ValidationError('File size exceeds the maximum allowed limit.')

        return value
    

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'owner', 'title', 'description', 'file', 'shared_with', 'uploaded_at', 'updated_at']
        extra_kwargs = {
            'owner': {'required': False}  # Make the 'owner' field not required during creation
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)  # Get the default representation of the model instance

        file_path = instance.file.url if instance.file else None

        if file_path:
            full_url = f"{BASE_URL}{file_path}"
        else:
            full_url = None

        representation['file'] = full_url  # Add the full URL for the file field to the representation

        return representation



class DocumentSharingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentSharing
        fields = ['id', 'document', 'shared_with', 'shared_at']