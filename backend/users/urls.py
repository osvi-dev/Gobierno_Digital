from django.urls import path
from .views import UserListView, UserDetailView, UserCSVExportView

urlpatterns = [
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:id>/', UserDetailView.as_view(), name='user-detail'),

    # Ruta para descargar el CSV de usuarios
    path('users/export/csv/', UserCSVExportView.as_view(), name='user-export-csv'),
]
