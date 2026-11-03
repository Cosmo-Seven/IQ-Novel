from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone
from datetime import timedelta
import secrets

from core.models import UserModel
from decorators.login_decorator import login_required
from helpers.daily_reward import process_daily_reward
from helpers.mail import send_otp_email


# ========================
# Dashboard Login
# ========================
def dashboard_login(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = UserModel.objects.get(email=email)
            if check_password(password, user.password):
                login(request, user)
                
                # Process daily rewards
                reward_amount = process_daily_reward(user)
                if reward_amount > 0:
                    messages.success(request, f"Welcome {user.username}! You received {reward_amount} coupons as daily reward.")
                else:
                    messages.success(request, f"Welcome {user.username}")
                
                return redirect("dashboard")
            else:
                messages.error(request, "Email or Password is incorrect!")
                return redirect("dashboard_login")
        except UserModel.DoesNotExist:
            messages.error(request, "Email or Password is incorrect!")
            return redirect("dashboard_login")

    return render(request, "dashboard/login.html")


# ========================
# Dashboard Logout
# ========================
def dashboard_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("dashboard_login")


# ========================
# User Profile
# ========================
@login_required("dashboard_login")
def profile(request):
    user = get_object_or_404(UserModel, id=request.user.id)

    if request.method == "POST":
        username = request.POST.get("username")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        profile = request.FILES.get("profile")

        user.username = username
        user.phone = phone

        if profile:
            if user.profile:
                user.profile.delete(save=False)
            user.profile = profile

        if password:
            user.set_password(password)
            update_session_auth_hash(request, user)
            messages.success(request, "Password updated successfully!")

        user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("dashboard_profile")

    context = {"user": user}
    return render(request, "dashboard/profile.html", context)


# ========================
# Forgot Password (OTP Flow)
# ========================
# 1. enter email -> 2. send OTP to email -> 3. verify OTP -> 4. set new password
RESET_SESSION_KEY = "pwd_reset"
OTP_TTL_MINUTES = 10
OTP_MAX_ATTEMPTS = 5


def _generate_otp():
    return f"{secrets.randbelow(1_000_000):06d}"


def _clear_reset_state(request):
    request.session.pop(RESET_SESSION_KEY, None)


def forgot_password(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        email = (request.POST.get("email") or "").strip()
        user = UserModel.objects.filter(email__iexact=email).first()

        if not user:
            messages.error(request, "No account found with this email.")
            return redirect("dashboard_forgot_password")

        otp = _generate_otp()
        request.session[RESET_SESSION_KEY] = {
            "email": user.email,
            "otp": make_password(otp),
            "expires": (timezone.now() + timedelta(minutes=OTP_TTL_MINUTES)).timestamp(),
            "attempts": 0,
            "verified": False,
        }
        send_otp_email(user.email, otp, OTP_TTL_MINUTES)

        messages.success(request, f"OTP code has been sent to {user.email}.")
        return redirect("dashboard_verify_otp")

    return render(request, "dashboard/forgot_password.html")


def verify_otp(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    state = request.session.get(RESET_SESSION_KEY)
    if not state:
        messages.error(request, "No OTP request found. Please enter your email again.")
        return redirect("dashboard_forgot_password")
    if state.get("verified"):
        return redirect("dashboard_reset_password")

    if request.method == "POST":
        # Resend — send a fresh OTP to the same email
        if request.POST.get("action") == "resend":
            otp = _generate_otp()
            state["otp"] = make_password(otp)
            state["expires"] = (
                timezone.now() + timedelta(minutes=OTP_TTL_MINUTES)
            ).timestamp()
            state["attempts"] = 0
            request.session[RESET_SESSION_KEY] = state
            send_otp_email(state["email"], otp, OTP_TTL_MINUTES)
            messages.success(request, "A new OTP code has been sent.")
            return redirect("dashboard_verify_otp")

        if timezone.now().timestamp() > state["expires"]:
            _clear_reset_state(request)
            messages.error(request, "The OTP has expired. Please request a new one.")
            return redirect("dashboard_forgot_password")

        if state["attempts"] >= OTP_MAX_ATTEMPTS:
            _clear_reset_state(request)
            messages.error(request, "Too many attempts. Please request a new OTP.")
            return redirect("dashboard_forgot_password")

        otp = (request.POST.get("otp") or "").strip()
        if not check_password(otp, state["otp"]):
            state["attempts"] += 1
            request.session[RESET_SESSION_KEY] = state
            messages.error(request, "Invalid OTP code.")
            return redirect("dashboard_verify_otp")

        state["verified"] = True
        state.pop("otp", None)
        request.session[RESET_SESSION_KEY] = state
        messages.success(request, "OTP verified. Please enter your new password.")
        return redirect("dashboard_reset_password")

    return render(
        request, "dashboard/verify_otp.html", {"email": state.get("email")}
    )


def reset_password(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    state = request.session.get(RESET_SESSION_KEY)
    if not state or not state.get("verified"):
        messages.error(request, "OTP verification required.")
        return redirect("dashboard_forgot_password")

    if request.method == "POST":
        password = request.POST.get("password") or ""
        confirm_password = request.POST.get("confirm_password") or ""

        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters.")
            return redirect("dashboard_reset_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("dashboard_reset_password")

        user = UserModel.objects.filter(email__iexact=state["email"]).first()
        if not user:
            _clear_reset_state(request)
            messages.error(request, "Account not found.")
            return redirect("dashboard_forgot_password")

        user.set_password(password)
        user.save()
        _clear_reset_state(request)

        messages.success(request, "Password changed successfully. Please sign in with your new password.")
        return redirect("dashboard_login")

    return render(
        request, "dashboard/reset_password.html", {"email": state.get("email")}
    )
