from django.urls import path
from .views import SignUpView, CustomAuthToken, VerifyEmailView, UploadFileView, ListFilesView, DownloadFileView, EncryptedFileDownloadView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', CustomAuthToken.as_view(), name='login'),
    path('verify/<int:user_id>/<str:token>/>/', VerifyEmailView.as_view(), name='verify_email'),
    path('upload/', UploadFileView.as_view(), name='upload_file'),
    path('files/', ListFilesView.as_view(), name='list_files'),
    path('download-file/<int:file_id>/', DownloadFileView.as_view(), name='get_download_link'),
    path('download-file/<str:encrypted_url>/', EncryptedFileDownloadView.as_view(), name='download_file'),
]
