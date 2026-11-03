import secrets
from datetime import timedelta

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.utils import timezone
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.contrib.auth.hashers import check_password, make_password
from decorators.login_decorator import login_required
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from helpers.mail import send_verification_email, send_reset_email, send_otp_email
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
                        f"Welcome {user.username}! You received {reward_amount} coupons as a daily login reward!",
                    )
                else:
                    messages.success(request, f"Welcome {user.username}")
                return redirect("/")
            else:
                messages.error(request, "Email or Password is incorrect!")
                return render(request, "website/login.html", {"email": email})
        except UserModel.DoesNotExist:
            messages.error(request, "Email or Password is incorrect!")
            return render(request, "website/login.html", {"email": email})

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

        # Validate required fields
        if not username or not email or not password or not confirm_password:
            messages.error(request, "All fields are required!")
            return render(
                request,
                "website/register.html",
                {"username": username, "email": email},
            )

        # Validate email is not empty or just whitespace
        email = email.strip()
        if not email:
            messages.error(request, "Email is required!")
            return render(
                request,
                "website/register.html",
                {"username": username, "email": email},
            )

        # Validate username is not empty
        username = username.strip()
        if not username:
            messages.error(request, "Username is required!")
            return render(
                request,
                "website/register.html",
                {"username": username, "email": email},
            )

        existing_user = UserModel.objects.filter(email=email).first()

        if existing_user and not existing_user.is_active:
            send_verification_email(request, existing_user)
            messages.warning(request, "Verification email sent again!")
            return redirect("/")

        if existing_user:
            messages.error(request, "Email already registered!")
            return render(
                request,
                "website/register.html",
                {"username": username, "email": email},
            )

        if password != confirm_password:
            messages.warning(request, "Password does not match!")
            return render(
                request,
                "website/register.html",
                {"username": username, "email": email},
            )

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


# =========================
# Change Password (OTP Flow) — Profile Page
# =========================
# 1. confirm email -> 2. send OTP to email -> 3. verify OTP -> 4. set new password
CHANGE_PWD_SESSION_KEY = "website_change_pwd"
OTP_TTL_MINUTES = 10
OTP_MAX_ATTEMPTS = 5


def _change_pwd_redirect():
    return redirect(f"{reverse('website_profile')}?tab=password")


def _generate_otp():
    return f"{secrets.randbelow(1_000_000):06d}"


def _clear_change_pwd_state(request):
    request.session.pop(CHANGE_PWD_SESSION_KEY, None)


def change_password_step(request):
    """Current step of the change password flow shown on the profile page."""
    state = request.session.get(CHANGE_PWD_SESSION_KEY)
    if not state:
        return 1
    return 3 if state.get("verified") else 2


def change_password(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Please login to change your password.")
        return redirect("website_login")

    if request.method != "POST":
        return redirect("website_profile")

    state = request.session.get(CHANGE_PWD_SESSION_KEY)
    action = request.POST.get("action")

    # Step 1 -> send a fresh OTP to the logged-in user's email
    if action == "send_otp":
        otp = _generate_otp()
        request.session[CHANGE_PWD_SESSION_KEY] = {
            "otp": make_password(otp),
            "expires": (timezone.now() + timedelta(minutes=OTP_TTL_MINUTES)).timestamp(),
            "attempts": 0,
            "verified": False,
        }
        send_otp_email(request.user.email, otp, OTP_TTL_MINUTES)
        messages.success(request, f"OTP code has been sent to {request.user.email}.")
        return _change_pwd_redirect()

    if not state:
        messages.error(request, "Please request an OTP code first.")
        return _change_pwd_redirect()

    # Resend a new OTP to the same email
    if action == "resend_otp":
        otp = _generate_otp()
        state["otp"] = make_password(otp)
        state["expires"] = (
            timezone.now() + timedelta(minutes=OTP_TTL_MINUTES)
        ).timestamp()
        state["attempts"] = 0
        state["verified"] = False
        request.session[CHANGE_PWD_SESSION_KEY] = state
        send_otp_email(request.user.email, otp, OTP_TTL_MINUTES)
        messages.success(request, "A new OTP code has been sent.")
        return _change_pwd_redirect()

    # Step 2 -> verify the OTP
    if action == "verify_otp":
        if timezone.now().timestamp() > state["expires"]:
            _clear_change_pwd_state(request)
            messages.error(request, "The OTP has expired. Please request a new one.")
            return _change_pwd_redirect()

        if state["attempts"] >= OTP_MAX_ATTEMPTS:
            _clear_change_pwd_state(request)
            messages.error(request, "Too many attempts. Please request a new OTP.")
            return _change_pwd_redirect()

        otp = (request.POST.get("otp") or "").strip()
        if not check_password(otp, state["otp"]):
            state["attempts"] += 1
            request.session[CHANGE_PWD_SESSION_KEY] = state
            messages.error(request, "Invalid OTP code.")
            return _change_pwd_redirect()

        state["verified"] = True
        state.pop("otp", None)
        request.session[CHANGE_PWD_SESSION_KEY] = state
        messages.success(request, "Code verified. Please set your new password.")
        return _change_pwd_redirect()

    # Step 3 -> set the new password
    if action == "reset":
        if not state.get("verified"):
            messages.error(request, "Please verify your identity first.")
            return _change_pwd_redirect()

        password = request.POST.get("password") or ""
        confirm_password = request.POST.get("confirm_password") or ""

        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters.")
            return _change_pwd_redirect()

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return _change_pwd_redirect()

        user = request.user
        user.set_password(password)
        user.save()
        update_session_auth_hash(request, user)
        _clear_change_pwd_state(request)

        messages.success(request, "Password changed successfully.")
        return redirect("website_profile")

    return _change_pwd_redirect()
