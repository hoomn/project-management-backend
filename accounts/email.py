from djoser.email import PasswordResetEmail


class CustomPasswordResetEmail(PasswordResetEmail):
    template_name = "accounts/email/password_reset.html"
