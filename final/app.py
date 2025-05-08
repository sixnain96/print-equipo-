from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from producto import Producto
from Venta import Venta
from decoradores import rol_requerido
from db_config import get_db_connection
from movimiento import Movimiento
from factura import generar_factura_pdf
from notificador import comprobar_bajo_stock
from otp import verificar_otp, generar_url_qr
from fpdf import FPDF
import os
import datetime
import bcrypt
import pandas as pd
import subprocess 
from backup_manual import *
import time
import pyotp
import qrcode
from dotenv import load_dotenv
load_dotenv()  # Carga el archivo .env

SECRET_ADMIN = os.environ.get("SECRET_ADMIN")
SECRET_EMPLEADO = os.environ.get("SECRET_EMPLEADO")
  
app = Flask(__name__, static_folder="static")
CORS(app) 
app.config['JWT_SECRET_KEY'] = 'mi_clave_secreta'
jwt = JWTManager(app)
producto_obj = Producto()
venta_obj = Venta()
movimiento_obj = Movimiento()
from backup_manual import backup_bp
app.register_blueprint(backup_bp)

# --- AUTENTICACIÓN ---
from flask_jwt_extended import create_access_token

# Ruta para activar 2FA
@app.route('/activar_2fa', methods=['POST'])
@jwt_required()  # Asegura que el usuario esté autenticado
def activar_2fa():
    usuario = get_jwt_identity()  # Obtener el nombre de usuario desde el JWT

    # Consultar el rol del usuario desde la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT rol FROM usuarios WHERE nombre_usuario = %s", (usuario,))
    user = cursor.fetchone()

    if user is None:
        return jsonify({"message": "Usuario no encontrado"}), 404

    rol = user[0]  # Obtener el rol del usuario

    # Generar la clave secreta para 2FA (Base32)
    secret = pyotp.random_base32()  # Esto generará una clave secreta Base32 única

    # Guardar la clave secreta en la base de datos
    cursor.execute("UPDATE usuarios SET clave_2fa = %s WHERE nombre_usuario = %s", (secret, usuario))
    conn.commit()

    # Generar el código QR para Google Authenticator
    totp = pyotp.TOTP(secret)  # Creamos el objeto TOTP con la clave secreta
    uri_qr = totp.provisioning_uri(name=usuario, issuer_name="MiAplicación")  # Generamos la URL para el QR

    # Generar el código QR usando la librería qrcode
    img = qrcode.make(uri_qr)

    # Guardamos la imagen del QR en el servidor (puedes servirla directamente al usuario)
    qr_image_path = f'qr_codes{usuario}_qr.png'
    img.save(qr_image_path)

    cursor.close()
    conn.close()

    # Respondemos con la ruta del código QR generado
    return jsonify({"message": "2FA activado", "qr_image": qr_image_path}), 200
# Ruta de login con 2FA
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password'].encode('utf-8')
    otp = data.get('otp')  # OTP enviado por el usuario desde Google Authenticator

    # Consultar el usuario en la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre_usuario, contraseña, rol, email, clave_2fa FROM usuarios WHERE nombre_usuario = %s", (username,))
    user = cursor.fetchone()

    if user is None:
        return jsonify({"message": "Usuario no encontrado"}), 404

    # Verificar la contraseña
    if bcrypt.checkpw(password, user[2].encode('utf-8')):
        # Si el usuario tiene habilitado 2FA, verificamos el OTP
        if user[5]:  # Si la clave_2fa no es None (es decir, 2FA está activado)
            if not otp:
                return jsonify({"message": "Se requiere un código OTP"}), 400  # OTP requerido si 2FA está activado
            
            # Verificar el OTP
            secret = user[5]  # Recuperamos la clave secreta guardada en la base de datos
            if verificar_otp(secret, otp):  # Usamos la función modularizada para verificar el OTP
                # Generar el token JWT
                token = create_access_token(identity=username, additional_claims={"role": user[3]})
                return jsonify({"message": "Autenticación exitosa", "access_token": token}), 200
            else:
                return jsonify({"message": "Código OTP incorrecto"}), 401
        else:
            # Si 2FA no está habilitado, solo generamos el token JWT
            token = create_access_token(identity=username, additional_claims={"role": user[3]})
            return jsonify({"message": "Autenticación exitosa", "access_token": token,  "role": user[3]}), 200
        

    else:
        return jsonify({"message": "Usuario o contraseña incorrectos"}), 401


# --- PRODUCTOS ---
@app.route('/producto/<int:id>', methods=['PUT'])
@jwt_required()
@rol_requerido(["admin"])
def actualizar_producto(id):
    data = request.get_json()

    # Validación de datos
    if data.get('precio_venta') <= 0 or data.get('stock_actual') < 0:
        return jsonify({"message": "El precio de venta debe ser mayor que 0 y el stock no puede ser negativo."}), 400

    producto_obj.actualizar_producto(
        id,
        nombre=data.get('nombre'),
        categoria=data.get('categoria'),
        codigo_sku=data.get('codigo_sku'),
        descripcion=data.get('descripcion'),
        precio_venta=data.get('precio_venta'),
        precio_compra=data.get('precio_compra'),
        stock_actual=data.get('stock_actual'),
        proveedor=data.get('proveedor'),
        ubicacion_almacen=data.get('ubicacion_almacen'),
        cantidad_minima=data.get('cantidad_minima')
    )

    return jsonify({'message': 'Producto actualizado exitosamente'}), 200

@app.route('/producto/<int:id>', methods=['DELETE'])
@jwt_required()
@rol_requerido(["admin"]) 
def eliminar_producto(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Primero, eliminar las ventas relacionadas con el producto
        cursor.execute("DELETE FROM ventas WHERE id_producto = %s", (id,))

        # Luego, eliminar los movimientos de stock asociados al producto
        cursor.execute("DELETE FROM movimientos_stock WHERE id_producto = %s", (id,))

        # Finalmente, eliminar el producto de la tabla productos
        query = "DELETE FROM productos WHERE id = %s"
        cursor.execute(query, (id,))
        
        conn.commit()
        return jsonify({'message': 'Producto y sus ventas y movimientos de stock eliminados exitosamente'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'message': f'Error: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/productos', methods=['GET'])
@jwt_required()
def obtener_productos():
    productos = producto_obj.obtener_productos()
    return jsonify(productos)

@app.route('/productos/buscar', methods=['GET'])
@jwt_required()
def buscar_productos():
    nombre = request.args.get('nombre')
    categoria = request.args.get('categoria')
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM productos WHERE 1=1"
    params = []
    if nombre:
        query += " AND nombre LIKE %s"
        params.append(f"%{nombre}%")
    if categoria:
        query += " AND categoria LIKE %s"
        params.append(f"%{categoria}%")
    cursor.execute(query, params)
    rows = cursor.fetchall()
    columnas = [desc[0] for desc in cursor.description]
    productos = [dict(zip(columnas, row)) for row in rows]
    cursor.close()
    conn.close()
    return jsonify(productos)

# --- EXPORTAR INVENTARIO A PDF ---
@app.route('/reportes/inventario/pdf', methods=['GET'])
@jwt_required()
@rol_requerido(["admin"])
def exportar_inventario_pdf():
    productos = producto_obj.obtener_productos()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, "Reporte de Inventario", ln=True, align='C')
    pdf.cell(0, 10, "", ln=True)
    for prod in productos:
        texto = f"{prod['nombre']} | SKU: {prod['codigo_sku']} | Stock: {prod['stock_actual']} | Precio: ${prod['precio_venta']}"
        pdf.multi_cell(0, 8, texto)
    nombre_archivo = f"reporte_inventario_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    ruta_pdf = os.path.join("archivos", nombre_archivo)
    os.makedirs("archivos", exist_ok=True)
    pdf.output(ruta_pdf)
    return send_file(ruta_pdf, as_attachment=True)

#-----EXPORTAR INVENTARIO A EXCEL----
@app.route('/reportes/inventario/excel', methods=['GET'])
@jwt_required()
@rol_requerido(["admin"])
def exportar_inventario_excel():
    productos = producto_obj.obtener_productos()
    
    if not productos:
        return jsonify({"message": "No hay productos para exportar"}), 404

    df = pd.DataFrame(productos)
    nombre_archivo = f"inventario_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    ruta = os.path.join("reportes_excel", nombre_archivo)
    os.makedirs("reportes_excel", exist_ok=True)
    df.to_excel(ruta, index=False, engine='openpyxl')

    return send_file(ruta, as_attachment=True)

# --- REPORTES ---
@app.route('/reportes/inventario', methods=['GET'])
@jwt_required()
@rol_requerido(["admin"])
def reporte_inventario():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM productos")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT categoria, AVG(stock_actual) FROM productos GROUP BY categoria")
    promedio = cursor.fetchall()
    cursor.execute("SELECT nombre, stock_actual FROM productos ORDER BY stock_actual ASC LIMIT 5")
    bajos = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({
        "total_productos": total,
        "promedio_stock_por_categoria": promedio,
        "productos_con_menos_stock": bajos
    })


# --- VENTAS ---
@app.route('/venta', methods=['POST'])
@jwt_required()
def agregar_venta():
    data = request.get_json()
    id_producto = data['id_producto']
    cantidad = data['cantidad_vendida']
    usuario = get_jwt_identity()  # Obtener el nombre de usuario desde el JWT
    
    # Verificar si el usuario existe en la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM usuarios WHERE nombre_usuario = %s", (usuario,))
    user = cursor.fetchone()

    if user is None:
        return jsonify({"message": "Usuario no encontrado en la base de datos"}), 404

    id_usuario = user[0]  # Obtener el id del usuario

    # Ahora, procede con la lógica para verificar el producto y registrar la venta
    cursor.execute("SELECT precio_venta FROM productos WHERE id = %s", (id_producto,))
    producto = cursor.fetchone()

    if not producto:
        return jsonify({"message": "Producto no encontrado"}), 404
    
    total = cantidad * producto[0]
    venta_obj.agregar_venta(id_producto, cantidad, total, id_usuario)  # Ahora pasa el id_usuario

    # Reducir stock y registrar el movimiento
    producto_obj.reducir_stock(id_producto, cantidad)
    movimiento_obj.registrar(id_producto, 'salida', cantidad, id_usuario)
    
    # Obtener nombre del producto
    cursor.execute("SELECT nombre FROM productos WHERE id = %s", (id_producto,))
    nombre_producto = cursor.fetchone()[0]

    # Generar factura
    ruta_factura = generar_factura_pdf(id_producto, cantidad, total, id_usuario, nombre_producto)

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({
        "message": "Venta registrada",
        "total_venta": total,
        "factura": ruta_factura
    }), 201

@app.route('/ventas', methods=['GET'])
@jwt_required()
def obtener_ventas():
    ventas = venta_obj.obtener_ventas()
    return jsonify(ventas)

@app.route('/reportes/ventas/totales', methods=['GET'])
@jwt_required()
def reporte_ventas_totales():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM ventas")
    total_ventas = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(total_venta) FROM ventas")
    total_dinero = cursor.fetchone()[0] or 0
    cursor.execute("SELECT MAX(fecha_venta) FROM ventas")
    ultima = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return jsonify({
        "total_ventas": total_ventas,
        "total_dinero_generado": float(total_dinero),
        "fecha_ultima_venta": ultima.strftime("%Y-%m-%d %H:%M:%S") if ultima else None
    })

@app.route('/reportes/ventas/por_mes', methods=['GET'])
@jwt_required()
def reporte_ventas_por_mes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT YEAR(fecha_venta), MONTH(fecha_venta), COUNT(*), SUM(total_venta)
        FROM ventas
        GROUP BY YEAR(fecha_venta), MONTH(fecha_venta)
        ORDER BY YEAR(fecha_venta) DESC, MONTH(fecha_venta) DESC
    """)
    datos = cursor.fetchall()
    reporte = []
    for fila in datos:
        reporte.append({
            "anio": fila[0],
            "mes": fila[1],
            "cantidad_ventas": fila[2],
            "total_mes": float(fila[3])
        })
    cursor.close()
    conn.close()
    return jsonify({"ventas_por_mes": reporte}), 200

# --- ENTRADA DE PRODUCTOS ---
@app.route('/inventario/entrada', methods=['POST'])

@jwt_required()
def entrada_stock():
    data = request.get_json()
    id_producto = data['id_producto']
    cantidad = data['cantidad']
    usuario = get_jwt_identity()

    try:
        producto_obj.agregar_stock(id_producto, cantidad)
        movimiento_obj.registrar(id_producto, 'entrada', cantidad, usuario)
        return jsonify({"message": f"Se agregaron {cantidad} unidades al producto con ID {id_producto}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# --- ALERTAS DE STOCK BAJO ---
@app.route('/alerta/stock', methods=['GET'])
@jwt_required()
def alerta_bajo_stock():
    # Se puede pasar el destinatario como un parámetro opcional
    destinatario = request.args.get('destinatario', None)

    # Si no se pasa un destinatario, usará el valor de CORREO_ALERTAS de las variables de entorno
    if destinatario is None:
        resultado = comprobar_bajo_stock()
    else:
        resultado = comprobar_bajo_stock(destinatario)

    if resultado == "No hay productos con stock bajo.":
        return jsonify({"message": resultado}), 200
    elif resultado:
        return jsonify({"message": "Alerta de stock bajo enviada con éxito."}), 200
    else:
        return jsonify({"message": "Error al enviar alerta de stock bajo."}), 500
@app.route('/dashboard/admin')

def dashboard_admin():
    # Lógica para la página del admin
     print("Entrando a /dashboard/admin")
     return send_file(os.path.join(app.root_path, 'static', 'dashboard-admin.html'))

@app.route('/dashboard/empleado')
 
def dashboard_empleado():
    # Lógica para la página del empleado
    print("Entrando a /dashboard/empleado")
    return send_file(os.path.join(app.root_path, 'static', 'dashboard-empleado.html'))
   
# --- INICIO ---
@app.route('/', methods=['GET'])
def home():
    
    return send_file(os.path.join(app.root_path, 'static', 'login.html'))
if __name__ == '__main__':
    app.run(debug=True)
 
