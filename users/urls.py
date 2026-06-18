from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("admin/", views.admin_dashboard, name="admin_dashboard"),
    path("create/", views.create_user, name="create_user"),
    path("delete/<int:user_id>/", views.delete_user, name="delete_user"),
]
