from django.urls import path
from . import views

urlpatterns = [
    path('', views.privacy_policy, name='privacy_policy'),
    
    # GDPR demo endpoints
    path("export/<int:profile_id>/", views.export_user_zip, name="export_user_zip"),
    path("delete/<int:profile_id>/", views.delete_user_profile, name="delete_user_profile"),
]