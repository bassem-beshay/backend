from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', views.get_user_profile, name='profile'),
    path('profile/update/', views.update_user_profile, name='update_profile'),
    path('password-reset/', views.request_password_reset, name='password_reset'),
    path('password-reset/confirm/', views.reset_password, name='password_reset_confirm'),
    path('verify-email/<str:uid>/<str:token>/', views.verify_email, name='verify_email'),
    path('google/', views.google_login, name='google_login'),
    path('logout/', views.logout_user, name='logout'),
] 