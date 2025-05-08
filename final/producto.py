# producto.py
from db_config import get_db_connection
from flask import Flask, request, jsonify

# Función de validación de producto
def validar_producto(data):
    # Verificar que los campos obligatorios estén presentes
    if not data.get('nombre') or not data.get('categoria') or not data.get('codigo_sku') or not data.get('precio_venta'):
        return {'message': 'Faltan campos obligatorios: nombre, categoria, codigo_sku, precio_venta'}, 400
    
    # Verificar que el precio y el stock no sean negativos
    if data['precio_venta'] <= 0 or data['stock_actual'] <= 0 or data['cantidad_minima'] < 0:
        return {'message': 'El precio, el stock o la cantidad mínima no pueden ser negativos'}, 400
    
    return None  # Si todo está bien, retorna None


class Producto:
    def __init__(self):
        pass

    def agregar_producto(self, nombre, categoria, codigo_sku, descripcion, precio_venta, precio_compra, stock_actual, proveedor, ubicacion_almacen, cantidad_minima):
        """Agrega un nuevo producto a la base de datos."""
        db = get_db_connection()
        cursor = db.cursor()
        
        query = '''
            INSERT INTO productos (nombre, categoria, codigo_sku, descripcion, precio_venta, precio_compra, stock_actual, proveedor, ubicacion_almacen, cantidad_minima)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        
        cursor.execute(query, (nombre, categoria, codigo_sku, descripcion, precio_venta, precio_compra, stock_actual, proveedor, ubicacion_almacen, cantidad_minima))
        db.commit()  # Confirmar cambios en la base de datos
        cursor.close()  # Cerrar el cursor
        db.close()  # Cerrar la conexión a la base de datos

    def actualizar_producto(self, id, nombre=None, categoria=None, codigo_sku=None, descripcion=None, precio_venta=None, precio_compra=None, stock_actual=None, proveedor=None, ubicacion_almacen=None, cantidad_minima=None):
        """Actualiza los datos de un producto existente."""
        db = get_db_connection()
        cursor = db.cursor()
        
        set_clause = []
        params = []
        
        if nombre: set_clause.append("nombre = %s"); params.append(nombre)
        if categoria: set_clause.append("categoria = %s"); params.append(categoria)
        if codigo_sku: set_clause.append("codigo_sku = %s"); params.append(codigo_sku)
        if descripcion: set_clause.append("descripcion = %s"); params.append(descripcion)
        if precio_venta: set_clause.append("precio_venta = %s"); params.append(precio_venta)
        if precio_compra: set_clause.append("precio_compra = %s"); params.append(precio_compra)
        if stock_actual: set_clause.append("stock_actual = %s"); params.append(stock_actual)
        if proveedor: set_clause.append("proveedor = %s"); params.append(proveedor)
        if ubicacion_almacen: set_clause.append("ubicacion_almacen = %s"); params.append(ubicacion_almacen)
        if cantidad_minima is not None: set_clause.append("cantidad_minima = %s"); params.append(cantidad_minima)
        
        set_clause = ", ".join(set_clause)
        params.append(id)

        query = f"UPDATE productos SET {set_clause} WHERE id = %s"
        cursor.execute(query, tuple(params))
        db.commit()
        cursor.close()
        db.close()

    def eliminar_producto(self, id):
        """Elimina un producto de la base de datos."""
        db = get_db_connection()
        cursor = db.cursor()
        query = "DELETE FROM productos WHERE id = %s"
        cursor.execute(query, (id,))
        db.commit()
        cursor.close()
        db.close()

    def obtener_productos(self):
        """Obtiene todos los productos de la base de datos."""
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute('SELECT id, nombre, categoria, codigo_sku, descripcion, precio_venta, precio_compra, stock_actual, proveedor, ubicacion_almacen, cantidad_minima, fecha_ingreso FROM productos')
        rows = cursor.fetchall()

        # Convertir los resultados en diccionarios
        productos = []
        column_names = [desc[0] for desc in cursor.description]
        for row in rows:
            productos.append(dict(zip(column_names, row)))

        cursor.close()
        db.close()
        return productos
    # Modificar agregar_producto para reducir el stock según la venta
    def reducir_stock(self, id_producto, cantidad_vendida):
        db = get_db_connection()
        cursor = db.cursor()
        
        # Reducir el stock
        query = '''
            UPDATE productos
            SET stock_actual = stock_actual - %s
            WHERE id = %s
        '''
        
        cursor.execute(query, (cantidad_vendida, id_producto))
        db.commit()
        cursor.close()
        db.close()
    def agregar_stock(self, id_producto, cantidad):
        db = get_db_connection()
        cursor = db.cursor()
        query = '''
            UPDATE productos
            SET stock_actual = stock_actual + %s
            WHERE id = %s
        '''
        cursor.execute(query, (cantidad, id_producto))
        db.commit()
        cursor.close()
        db.close()
