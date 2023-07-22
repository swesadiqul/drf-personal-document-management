from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from doc_management_api.serializers import *
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404, Http404
import os
from rest_framework.exceptions import PermissionDenied



# Create your views here.
class UserRegistrationView(APIView):
    def post(self, request, format=None):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Registration successful!', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UserLoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)
            if not user:
                return Response({"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response({"message": "Login successfull !", "token": access_token}, status=status.HTTP_200_OK)
        

class DocumentUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = DocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Check file format
        allowed_formats = ['.pdf', '.doc', '.docx', '.txt']
        ext = os.path.splitext(request.data['file'].name)[1]
        if ext.lower() not in allowed_formats:
            return Response({'error': f'File format not supported. Allowed formats: {", ".join(allowed_formats)}'}, status=400)

        # Check file size
        max_file_size = 5 * 1024 * 1024  # 5 MB (in bytes)
        if request.data['file'].size > max_file_size:
            return Response({'error': 'File size exceeds the maximum allowed limit.'}, status=400)

        serializer.save(owner=request.user)
        return Response(serializer.data, status=201)
    

class DocumentDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, format=None):
        document = get_object_or_404(Document, id=pk)

        # Check if the user has permission to download the document
        if request.user == document.owner or request.user in document.shared_with.all():
            serializer = DocumentSerializer(document)
            return Response(serializer.data)
        else:
            return Response({'error': 'You do not have permission to download this document.'}, status=403)

class DocumentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        documents = Document.objects.filter(owner=request.user)
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)

class DocumentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        document = get_object_or_404(Document, id=pk)
        if document.owner == self.request.user or self.request.user in document.shared_with.all():
            return document
        raise PermissionDenied()

    def get(self, request, pk, format=None):
        document = self.get_object(pk)
        serializer = DocumentSerializer(document)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        document = self.get_object(pk)
        serializer = DocumentSerializer(document, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk, format=None):
        document = self.get_object(pk)
        document.delete()
        return Response(status=204)


class DocumentSharingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        document_id = request.data.get('document_id')
        shared_with_username = request.data.get('shared_with')
        if not document_id or not shared_with_username:
            return Response({'error': 'Please provide both document_id and shared_with.'}, status=400)

        document = get_object_or_404(Document, id=document_id, owner=request.user)
        shared_with_user = get_object_or_404(User, username=shared_with_username)

        if shared_with_user == request.user:
            return Response({'error': 'You cannot share the document with yourself.'}, status=400)

        document.shared_with.add(shared_with_user)
        return Response({'message': 'Document shared successfully.'}, status=201)


class DocumentUnshareView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, document_id, user_id, format=None):
        document = get_object_or_404(Document, id=document_id, owner=request.user)
        shared_with_user = get_object_or_404(User, id=user_id)
        if shared_with_user != request.user:
            document.shared_with.remove(shared_with_user)
            return Response({'message': 'Document unshared successfully.'}, status=204)
        return Response({'error': 'You cannot unshare the document with yourself.'}, status=400)


class DocumentShareView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, document_id, format=None):
        document = get_object_or_404(Document, id=document_id, owner=request.user)
        shared_with_username = request.data.get('shared_with')
        shared_with = get_object_or_404(User, username=shared_with_username)
        sharing_instance, created = DocumentSharing.objects.get_or_create(document=document, shared_with=shared_with)
        serializer = DocumentSharingSerializer(sharing_instance)
        return Response(serializer.data)


class DocumentUnshareView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, document_id, user_id, format=None):
        document = get_object_or_404(Document, id=document_id, owner=request.user)
        shared_with = get_object_or_404(User, id=user_id)
        sharing_instance = get_object_or_404(DocumentSharing, document=document, shared_with=shared_with)
        sharing_instance.delete()
        return Response(status=204)


class DocumentDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, format=None):
        document = get_object_or_404(Document, id=pk)
        user = request.user

        # Admin users can download any document
        if user.is_staff:
            serializer = DocumentSerializer(document)
            return Response(serializer.data)

        # Regular users can download their own documents and shared documents
        if user == document.owner or user in document.shared_with.all():
            serializer = DocumentSerializer(document)
            return Response(serializer.data)

        return Response({'detail': 'You do not have permission to perform this action.'}, status=403)
    

class DocumentSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        query = request.query_params.get('query')
        if not query:
            return Response({'detail': 'Please provide a search query.'}, status=400)

        user = request.user
        documents = Document.objects.filter(owner=user).filter(
            models.Q(title__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(file__icontains=query) |
            models.Q(uploaded_at__icontains=query)
        )
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)