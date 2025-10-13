from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("indepth/", views.indepth, name="indepth"),
    path("promotions/", views.promotions, name="promotions"),
    path("settings/", views.settings_view, name="settings"),
    path("profile/", views.profile, name="profile"),
    path("products/", views.products, name="products"),
]
