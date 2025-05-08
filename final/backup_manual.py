from flask import Blueprint, send_file, jsonify
from flask_jwt_extended import jwt_required
from decoradores import rol_requerido
import os, datetime, subprocess

# Configuración de conexión
MYSQL_USER = "root"
MYSQL_PASSWORD = ""
MYSQL_DB = "ferreteria"
MYSQL_DUMP_PATH = "mysqldump"  # O C:\\xampp\\mysql\\bin\\mysqldump

# Crear Blueprint
backup_bp = Blueprint('backup_bp', __name__)

@backup_bp.route('/backup/manual', methods=['GET'])
@jwt_required()
@rol_requerido(["admin"])
def backup_manual():
    try:
        nombre_archivo = f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        ruta = os.path.join("backups", nombre_archivo)
        os.makedirs("backups", exist_ok=True)

        comando = [
            MYSQL_DUMP_PATH,
            f"-u{MYSQL_USER}",
            f"-p{MYSQL_PASSWORD}",
            MYSQL_DB
        ]

        with open(ruta, "w", encoding="utf-8") as salida:
            proceso = subprocess.run(comando, stdout=salida, stderr=subprocess.PIPE, shell=True)

        if proceso.returncode != 0:
            return jsonify({"error": "Error al generar el respaldo", "detalle": proceso.stderr.decode()}), 500

        return send_file(ruta, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
