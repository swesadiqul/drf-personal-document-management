from django.urls import path
from doc_management_api.views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

#urlpatterns list
urlpatterns = [
    # User Authentication
    path('api/register/', UserRegistrationView.as_view(), name='user-registration'),
    path('api/login/', UserLoginView.as_view(), name='user-login'),

    # Document Management
    path('api/documents/', DocumentListView.as_view(), name='document-list'),
    path('api/documents/<int:pk>/', DocumentDetailView.as_view(), name='document-detail'),
    path('api/documents/upload/', DocumentUploadView.as_view(), name='document-upload'),
    path('api/documents/<int:pk>/download/', DocumentDownloadView.as_view(), name='document-download'),
    path('api/documents/share/', DocumentSharingView.as_view(), name='document-share'),
    path('api/documents/unshare/<int:document_id>/<int:user_id>/', DocumentUnshareView.as_view(), name='document-unshare'),

    # Document Search
    path('api/documents/search/', DocumentSearchView.as_view(), name='document-search'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]
