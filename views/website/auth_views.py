from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from decorators.login_decorator import login_required
from django.contrib.auth import login, logout, authenticate
from helpers.mail import send_verification_email, send_reset_email
from helpers.daily_reward import process_daily_reward
from core.models import (
    UserModel,
)

# =========================
# Authentication Views
# =========================
def login_view(request):
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = UserModel.objects.get(email=email)
            if check_password(password, user.password):
                login(request, user)
                # Process daily login reward
                reward_amount = process_daily_reward(user)
                if reward_amount > 0:
                    messages.success(
                        request,
                        f"Welcome {user.username}! You received {reward_amount} gems as a daily login reward!",
                    )
                else:
                    messages.success(request, f"Welcome {user.username}")
                return redirect("/")
            else:
                messages.error(request, "Email or Password is incorrect!")
                return redirect("website_login")
        except UserModel.DoesNotExist:
            messages.error(request, "Email or Password is incorrect!")
            return redirect("website_login")

    return render(request, "website/login.html")


def logout_view(request):
    logout(request)
    messages.success(request, "Logout successfully!")
    return redirect("/")


def register_view(request):
    if request.user.is_authenticated:
        messages.warning(request, "You're already logged in!")
        return redirect("/")

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        existing_user = UserModel.objects.filter(email=email).first()

        if existing_user and not existing_user.is_active:
            send_verification_email(request, existing_user)
            messages.warning(request, "Verification email sent again!")
            return redirect("/")

        if existing_user:
            messages.error(request, "Email already registered!")
            return redirect("register")

        if password != confirm_password:
            messages.warning(request, "Password does not match!")
            return redirect("register")

        user = UserModel.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_active=False,
        )

        send_verification_email(request, user)

        messages.success(request, "Check your email to verify your account.")
        return redirect("/")

    return render(request, "website/register.html")


def verify_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserModel.objects.get(pk=uid)
    except:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        login(request, user)
        messages.success(request, "Account was verified and logged in!")
        return redirect("/")

    messages.error(request, "Invalid or expired link!")
    return redirect("/")


def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user = UserModel.objects.filter(email=email).first()

        if not user:
            messages.error(request, "Email not found!")
            return redirect("forgot_password")

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        reset_url = request.build_absolute_uri(
            reverse("reset_password", kwargs={"uidb64": uid, "token": token})
        )

        send_reset_email(user.email, reset_url)

        messages.success(request, "Password reset link sent to your email.")
        return redirect("/")

    return render(request, "website/forgot_password.html")


def reset_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserModel.objects.get(pk=uid)
    except:
        user = None

    if not user or not default_token_generator.check_token(user, token):
        messages.error(request, "Invalid or expired link!")
        return redirect("/")

    if request.method == "POST":
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("/")

        user.set_password(password)
        user.save()

        messages.success(request, "Password reset successful. Please login.")
        return redirect("/")

    return render(request, "website/reset_password.html")
