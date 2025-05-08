import pyotp

def generar_url_qr(secret, username):
    """
    Genera una URL de configuración para el código QR de Google Authenticator.
    :param secret: La clave secreta del usuario
    :param username: El nombre del usuario para identificar el dispositivo en la aplicación
    :return: URI para el código QR
    """
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=username, issuer_name="Mi Aplicación")
    return uri

def verificar_otp(secret, otp):
    """
    Verifica si el OTP proporcionado es válido.
    :param secret: La clave secreta del usuario
    :param otp: El OTP enviado por el usuario desde Google Authenticator
    :return: True si el OTP es válido, False si no lo es
    """
    totp = pyotp.TOTP(secret)
    return totp.verify(otp)
