from flask_jwt_extended import get_jwt
from functools import wraps
from flask import jsonify

def rol_requerido(roles_permitidos):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            if claims.get("role") in roles_permitidos:
                return func(*args, **kwargs)
            else:
                return jsonify({"message": "Acceso denegado: no tienes el rol necesario"}), 403
        return wrapper
    return decorator
