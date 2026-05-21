from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.conf import settings


# =========================
# BASE WRAPPER (REUSABLE)
# =========================
def base_email(content: str) -> str:
    return f"""
    <div style="background:#0B0B0B;padding:20px 10px;font-family:Arial,sans-serif;">
        <div style="
            width:100%;
            max-width:600px;
            margin:0 auto;
            background:#111;
            padding:24px;
            border-radius:12px;
            border:1px solid #1F1F1F;
            box-sizing:border-box;
        ">
            {content}
        </div>
    </div>
    """


# =========================
# VERIFY EMAIL
# =========================
def send_verification_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    verify_url = request.build_absolute_uri(
        reverse("verify_email", kwargs={"uidb64": uid, "token": token})
    )

    content = f"""
        <h1 style="color:#1563df;font-size:22px;margin:0;">
            Verify Account
        </h1>

        <p style="color:#aaa;font-size:14px;line-height:1.6;margin-top:10px;">
            Click the button below to verify your account and get started.
        </p>

        <a href="{verify_url}" style="
            display:block;
            width:100%;
            margin-top:16px;
            padding:12px 18px;
            background:#1563df;
            color:#fff;
            text-decoration:none;
            border-radius:8px;
            font-weight:bold;
            text-align:center;
            box-sizing:border-box;
        ">
            Verify Account
        </a>

        <p style="color:#666;font-size:12px;margin-top:20px;">
            If you didn’t request this, ignore this email.
        </p>
    """

    html = base_email(content)

    msg = EmailMultiAlternatives(
        "Verify Your Account",
        "",
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )
    msg.attach_alternative(html, "text/html")
    msg.send()


# =========================
# RESET PASSWORD EMAIL
# =========================
def send_reset_email(user_email, reset_url):
    content = f"""
        <h1 style="color:#1563df;font-size:22px;margin:0;">
            Reset Password
        </h1>

        <p style="color:#aaa;font-size:14px;line-height:1.6;margin-top:10px;">
            Click the button below to reset your password.
        </p>

        <a href="{reset_url}" style="
            display:block;
            width:100%;
            margin-top:16px;
            padding:12px 18px;
            background:#1563df;
            color:#fff;
            text-decoration:none;
            border-radius:8px;
            font-weight:bold;
            text-align:center;
            box-sizing:border-box;
        ">
            Reset Password
        </a>

        <p style="color:#666;font-size:12px;margin-top:20px;">
            If you didn't request this, ignore this email.
        </p>
    """

    html = base_email(content)

    msg = EmailMultiAlternatives(
        "Reset Your Password",
        "",
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
    )
    msg.attach_alternative(html, "text/html")
    msg.send()
