from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path("signup", views.signup, name="signup"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("ve_confirmation/<uidb64>/<token>", views.ve_confirmation, name="ve_confirmation"),
    path("verificationemail", views.verification_email, name="verificationemail"),
    path("forgot_password", views.forgot_password, name="forgot_password"),
    path("fp_confirmation", views.fp_confirmation, name='fp_confirmation'),
    path("reset_password/<uidb64>/<token>", views.reset_password, name="reset_password"),
    path("rp_confirmation", views.rp_confirmation, name="rp_confirmation"),
]